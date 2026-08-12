import logging
import re
from time import time

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from csv_detective.format import Format
from csv_detective.parsing.csv import CHUNK_SIZE
from csv_detective.utils import display_logs_depending_process_time

# above this threshold, a column is not considered categorical
MAX_NUMBER_CATEGORICAL_VALUES = 25
RATIO_CATEGORICAL_VALUES = 0.05
# the file is re-read by batches of that many chunks: each add() realigns the running index, which
# holds every distinct value seen so far, so counting once per chunk would dominate the reading
CHUNKS_PER_BATCH = 10


def handle_empty_columns(return_table: pd.DataFrame):
    # handling that empty columns score 1 everywhere
    for col in return_table.columns:
        if sum(return_table[col]) == len(return_table):
            return_table[col] = 0.0


def count_values(serie: pd.Series) -> pd.Series:
    """How many times the column holds each of its distinct values."""
    return serie.value_counts(dropna=False)


def _testable_values(values: pd.Series, skipna: bool) -> pd.Series:
    # NaNs are not values to test: with skipna they don't count at all, and without they are
    # failures, which is what any format would return on them anyway
    if skipna:
        values = values[values.index.notna()]
    # most frequent first, so that a format that does not fit the column runs out of its failure
    # budget in as few tests as possible
    return values.sort_values(ascending=False)


def score_column(values: pd.Series, total: float, format: Format) -> float:
    """The share of the column the format reads, 0.0 if it cannot reach its own proportion.

    `values` counts every distinct value of the *whole* column, so the total is known up front:
    that is what lets us give up as soon as the failures put the threshold out of reach, instead
    of reading every value of every column for every format.
    """
    max_failures = (1 - format.proportion) * total
    failing = 0
    for value, count in values.items():
        if not format.func(value):
            failing += count
            if failing > max_failures:
                return 0.0
    return 1 - failing / total


def score_columns(
    col_values: dict[str, pd.Series],
    formats: dict[str, Format],
    *,
    skipna: bool = True,
    skipped_labels: dict[str, set[str]] | None = None,
    known_columns: dict[str, str] | None = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Scores every column against every format, from the value counts of the whole file.

    `skipped_labels` lists, per column, the formats that are out of the running whatever the
    values hold, so that the expensive field tests are not run on them.
    """
    if verbose:
        start = time()
        logging.info("Scoring columns against every format")
    return_table = pd.DataFrame(columns=list(col_values.keys()), index=list(formats.keys()))
    for col, raw_values in col_values.items():
        start_col = time()
        values = _testable_values(raw_values, skipna)
        total = values.sum()
        if not total:
            # an empty column fits every format, including the ones we would otherwise skip:
            # handle_empty_columns needs to see them all agree to settle the case
            return_table[col] = 1.0
            continue
        skipped = (skipped_labels or {}).get(col, set())
        known_label = (known_columns or {}).get(col)
        for label, format in formats.items():
            if label == known_label:
                # the file's own metadata already tells us this column is of that type
                return_table.loc[label, col] = 1.0
            elif label in skipped:
                return_table.loc[label, col] = 0.0
            else:
                return_table.loc[label, col] = score_column(values, total, format)
        if verbose and time() - start_col > 3:
            display_logs_depending_process_time(
                f"\t/!\\ Column '{col}' took too long ({round(time() - start_col, 3)}s)",
                time() - start_col,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done scoring columns in {round(time() - start, 3)}s", time() - start
        )
    return return_table


def test_label(columns: list[str], formats: dict[str, Format], verbose: bool = False):
    if verbose:
        start = time()
        logging.info("Testing labels to get formats")

    return_table = pd.DataFrame(columns=columns)
    for idx, (label, format) in enumerate(formats.items()):
        if verbose:
            start_type = time()
        return_table.loc[label] = [format.is_valid_label(col_name) for col_name in columns]
        if verbose:
            display_logs_depending_process_time(
                f'\t- Done with format "{label}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(formats)})',
                time() - start_type,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done testing labels in {round(time() - start, 3)}s", time() - start
        )
    return return_table


def test_col_chunks(
    table: pd.DataFrame,
    file_path: str,
    analysis: dict,
    formats: dict[str, Format],
    skipna: bool = True,
    na_values: list[str] | None = None,
    verbose: bool = False,
) -> tuple[pd.DataFrame, dict, dict[str, pd.Series]]:
    if verbose:
        start = time()
        logging.info("Reading the file to count the values of each column")

    # hashing rows to get nb_duplicates
    row_hashes_count = pd.Series()
    # getting values for profile to read the file only once
    col_values = {col: pd.Series() for col in table.columns}
    analysis["total_lines"] = 0

    # only csv files can end up here, can't chunk excel
    chunks = pd.read_csv(
        file_path,
        dtype=str,
        encoding=analysis["encoding"],
        sep=analysis["separator"],
        skiprows=analysis["header_row_idx"],
        compression=analysis.get("compression"),
        chunksize=CHUNK_SIZE * CHUNKS_PER_BATCH,
        na_values=na_values,
    )
    for idx, batch in enumerate(chunks):
        if verbose:
            logging.info(f"> Reading batch number {idx + 1}")
        analysis["total_lines"] += len(batch)
        row_hashes_count = row_hashes_count.add(
            pd.util.hash_pandas_object(batch, index=False).value_counts(),
            fill_value=0,
        )
        for col in batch.columns:
            col_values[col] = col_values[col].add(count_values(batch[col]), fill_value=0)

    # Formats are scored once, here, on the counts of the whole file rather than chunk by chunk.
    # Averaging chunk scores gave a short chunk the same weight as a long one, and no format could
    # ever be ruled out mid-file since the batches left could always bring it back up. With the
    # totals in hand the score is exact, and a format is dropped as soon as it has failed on more
    # values than its proportion allows.
    return_table = score_columns(
        col_values,
        formats,
        skipna=skipna,
        skipped_labels={
            # mandatory_label formats are zeroed out at the end if the label doesn't match,
            # so there's no point running the expensive field tests on those columns
            col: {
                fmt_label
                for fmt_label, fmt in formats.items()
                if fmt.mandatory_label and fmt.is_valid_label(col) == 0
            }
            for col in table.columns
        },
        verbose=verbose,
    )
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    analysis["categorical"] = [
        col
        for col, values in col_values.items()
        if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
        or (len(values) / sum(values)) <= RATIO_CATEGORICAL_VALUES
    ]
    handle_empty_columns(return_table)
    if verbose:
        display_logs_depending_process_time(
            f"Done testing chunks in {round(time() - start, 3)}s", time() - start
        )
    return return_table, analysis, col_values


PYARROW_TYPE_TO_PYTHON = {
    # using regex because of bits-differing types (e.g. int32 and int64)
    # the "^" makes sure we don't consider the types of elements within structured objects (lists, dicts)
    "string$": "string",  # large_string also exists
    "^double": "float",
    "^float": "float",
    "^decimal": "float",
    "^int": "int",
    "^uint": "int",
    "^bool": "bool",
    "^date": "date",
    "^struct": "json",  # dictionary
    "^list": "json",
    "^binary": "binary",
    r"^timestamp\[\ws\]": "datetime_naive",
    r"^timestamp\[\ws,": "datetime_aware",  # the rest of the field depends on the timezone
}


def build_known_columns(table: pq.ParquetFile):
    columns = {}
    for col in table.schema_arrow:
        col_type = str(col.type)
        if col_type.startswith("dictionary"):
            # dictionaries are for columns with repeated values
            # we need to dig deeper to get the type
            col_type = str(col.type.value_type)
        try:
            columns[col.name] = next(
                pytype
                for pyartype, pytype in PYARROW_TYPE_TO_PYTHON.items()
                if re.search(pyartype, col_type)
            )
        except StopIteration:
            raise ValueError(f"Unknown pyarrow type: {col.type}")
    return columns


def test_parquet_cols(
    table: pq.ParquetFile,
    formats: dict[str, Format],
    analysis: dict,
    skipna: bool = True,
    verbose: bool = False,
):
    if verbose:
        start = time()
        logging.info("Testing columns to get formats on chunks")

    columns = build_known_columns(table)
    row_hashes_count = pd.Series()
    col_values = {col: pd.Series() for col in columns.keys()}
    # we keep the same chunk size as for csv
    for idx, batch in enumerate(table.iter_batches(CHUNK_SIZE * 10)):
        if verbose:
            logging.info(f"> Reading batch number {idx + 1}")
        # a null in an integer column is enough to have it read as floats, and counted as
        # "2015.0" instead of "2015", which no format expecting an integer reads: asking for
        # objects keeps the integers, and casting settles the columns pandas typed on its own
        batch = batch.to_pandas(integer_object_nulls=True).astype(object)
        str_batch = batch.map(
            # not simply using astype(str) because lists are numpy arrays, cast as str they lose their commas
            lambda x: str(x.tolist()) if isinstance(x, np.ndarray) else str(x),
            # nulls have to stay null: cast as str they would become the value "nan", which every
            # format is asked about and fails on, sinking the whole column
            na_action="ignore",
        )
        row_hashes_count = row_hashes_count.add(
            pd.util.hash_pandas_object(str_batch, index=False).value_counts(),
            fill_value=0,
        )
        for col in batch.columns:
            col_values[col] = col_values[col].add(count_values(str_batch[col]), fill_value=0)

    return_table = score_columns(
        col_values,
        formats,
        skipna=skipna,
        skipped_labels={
            # the metadata gives the type away, so only the formats of that type can apply, and
            # mandatory_label formats are zeroed out at the end if the label doesn't match anyway
            col: {
                fmt_label
                for fmt_label, fmt in formats.items()
                if fmt.python_type != pytype
                or (fmt.mandatory_label and fmt.is_valid_label(col) == 0)
            }
            for col, pytype in columns.items()
        },
        known_columns=columns,
        verbose=verbose,
    )
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    analysis["categorical"] = [
        col for col, values in col_values.items() if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
    ]
    handle_empty_columns(return_table)
    if verbose:
        display_logs_depending_process_time(
            f"Done testing chunks in {round(time() - start, 3)}s", time() - start
        )
    return return_table.fillna(0), analysis, col_values
