import logging
import re
from time import time
from typing import Callable

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from more_itertools import peekable

from csv_detective.format import Format
from csv_detective.parsing.csv import CHUNK_SIZE
from csv_detective.utils import display_logs_depending_process_time

# above this threshold, a column is not considered categorical
MAX_NUMBER_CATEGORICAL_VALUES = 25


def handle_empty_columns(return_table: pd.DataFrame):
    # handling that empty columns score 1 everywhere
    for col in return_table.columns:
        if sum(return_table[col]) == len(return_table):
            return_table[col] = 0.0


def test_col_val(
    serie: pd.Series,
    format: Format,
    skipna: bool = True,
    limited_output: bool = False,
    verbose: bool = False,
) -> float:
    """Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are considered True
    for the serie to be detected as a certain format
    """
    if verbose:
        start = time()

    # TODO : change for a cleaner method and only test columns in modules labels
    def apply_test_func(serie: pd.Series, test_func: Callable, _range: int):
        return serie.sample(n=_range).apply(test_func)

    try:
        if skipna:
            serie = serie.dropna()
        ser_len = len(serie)
        if ser_len == 0:
            # being here means the whole column is NaN, so if skipna it's a pass
            return 1.0 if skipna else 0.0
        if not limited_output or format.proportion < 1:
            # we want or have to go through the whole column to have the proportion
            value_counts = serie.value_counts()
            unique_results = value_counts.index.to_series().apply(format.func)
            result: float = (unique_results * value_counts.values).sum() / ser_len
            return result if result >= format.proportion else 0.0
        else:
            # the whole column has to be valid so we have early stops (1 then 5 rows)
            # to not waste time if directly unsuccessful
            for _range in [
                min(1, ser_len),
                min(5, ser_len),
            ]:
                if not all(apply_test_func(serie, format.func, _range)):
                    return 0.0
            return float(all(format.func(v) for v in serie.unique()))
    finally:
        if verbose and time() - start > 3:
            display_logs_depending_process_time(
                f"\t/!\\ Column '{serie.name}' took too long ({round(time() - start, 3)}s)",
                time() - start,
            )


def test_col(
    table: pd.DataFrame,
    formats: dict[str, Format],
    limited_output: bool,
    skipna: bool = True,
    verbose: bool = False,
):
    if verbose:
        start = time()
        logging.info("Testing columns to get formats")
    return_table = pd.DataFrame(columns=table.columns)
    for idx, (label, format) in enumerate(formats.items()):
        if verbose:
            start_type = time()
            logging.info(f"\t- Starting with format '{label}'")
        # improvement lead : put the longest tests behind and make them only if previous tests not satisfactory
        # => the following needs to change, "apply" means all columns are tested for one type at once
        for col in table.columns:
            return_table.loc[label, col] = test_col_val(
                table[col],
                format,
                skipna=skipna,
                limited_output=limited_output,
                verbose=verbose,
            )
        if verbose:
            display_logs_depending_process_time(
                f'\t> Done with format "{label}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(formats)})',
                time() - start_type,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done testing columns in {round(time() - start, 3)}s", time() - start
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


def _build_remaining_tests_per_col(
    return_table: pd.DataFrame,
    mandatory_label_skip: dict[str, set[str]],
    known_columns: dict[str, str] = {},
) -> dict[str, list[str]]:
    # returns a dict with the table's columns as keys and the list of remaining format labels to apply
    return {
        col: [
            fmt_label
            for fmt_label in return_table.index
            # for parquet we know for sure some column types
            if known_columns.get(col) != fmt_label
            and return_table.loc[fmt_label, col] > 0
            and fmt_label not in mandatory_label_skip.get(col, set())
        ]
        for col in return_table.columns
    }


def test_col_chunks(
    table: pd.DataFrame,
    file_path: str,
    analysis: dict,
    formats: dict[str, Format],
    limited_output: bool,
    skipna: bool = True,
    additional_na_values: list[str] | None = None,
    verbose: bool = False,
) -> tuple[pd.DataFrame, dict, dict[str, pd.Series]]:
    if verbose:
        start = time()
        logging.info("Testing columns to get formats on chunks")

    # analysing the sample to get a first guess
    return_table = test_col(table, formats, limited_output, skipna=skipna, verbose=verbose)
    # mandatory_label formats are zeroed out at the end if the label doesn't match,
    # so there's no point running the expensive field tests on those columns
    mandatory_label_skip: dict[str, set[str]] = {
        col: {
            fmt_label
            for fmt_label, fmt in formats.items()
            if fmt.mandatory_label and fmt.is_valid_label(col) == 0
        }
        for col in table.columns
    }
    handle_empty_columns(return_table)
    empty_cols = {col for col in table.columns if table[col].dropna().empty}
    remaining_tests_per_col = _build_remaining_tests_per_col(return_table, mandatory_label_skip)

    # hashing rows to get nb_duplicates
    row_hashes_count = pd.util.hash_pandas_object(table, index=False).value_counts()
    # getting values for profile to read the file only once
    col_values = {col: table[col].value_counts(dropna=False) for col in table.columns}

    # only csv files can end up here, can't chunk excel
    chunks = pd.read_csv(
        file_path,
        dtype=str,
        encoding=analysis["encoding"],
        sep=analysis["separator"],
        skiprows=analysis["header_row_idx"],
        compression=analysis.get("compression"),
        chunksize=CHUNK_SIZE,
        na_values=additional_na_values,
    )
    analysis["total_lines"] = CHUNK_SIZE
    batch, batch_number = [], 1
    iterator = peekable(enumerate(chunks))
    while iterator:
        idx, chunk = next(iterator)
        if idx == 0:
            # we have read and analysed the first chunk already
            continue
        if len(batch) < 10:
            # it's too slow to process chunks directly, but we want to keep the first analysis
            # on a "small" chunk, so partial analyses are done on batches of chunks
            batch.append(chunk)
            # we don't know when the chunks end, and doing one additionnal step
            # for the final batch is ugly
            try:
                iterator.peek()
                continue
            except StopIteration:
                pass
        if verbose:
            logging.info(f"> Testing batch number {batch_number}")
        batch = pd.concat(batch, ignore_index=True)
        analysis["total_lines"] += len(batch)
        row_hashes_count = row_hashes_count.add(
            pd.util.hash_pandas_object(batch, index=False).value_counts(),
            fill_value=0,
        )
        for col in batch.columns:
            col_values[col] = col_values[col].add(
                batch[col].value_counts(dropna=False),
                fill_value=0,
            )
        for col in list(empty_cols):
            if not batch[col].dropna().empty:
                empty_cols.discard(col)
                remaining_tests_per_col[col] = [
                    fmt_label
                    for fmt_label in formats.keys()
                    if fmt_label not in mandatory_label_skip.get(col, set())
                ]
        if not any(remaining_tests for remaining_tests in remaining_tests_per_col.values()):
            # no more potential tests to do on any column, early stop
            break
        for col, fmt_labels in remaining_tests_per_col.items():
            # testing each column with the tests that are still competing
            # after previous batchs analyses
            for label in fmt_labels:
                batch_col_test = test_col_val(
                    batch[col],
                    formats[label],
                    limited_output=limited_output,
                    skipna=skipna,
                )
                return_table.loc[label, col] = (
                    # if this batch's column tested 0 then test fails overall
                    0
                    if batch_col_test == 0
                    # otherwise updating the score with weighted average
                    else ((return_table.loc[label, col] * idx + batch_col_test) / (idx + 1))
                )
        remaining_tests_per_col = _build_remaining_tests_per_col(return_table, mandatory_label_skip)
        batch, batch_number = [], batch_number + 1
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    analysis["categorical"] = [
        col for col, values in col_values.items() if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
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
    limited_output: bool,
    skipna: bool = True,
    verbose: bool = False,
):
    if verbose:
        start = time()
        logging.info("Testing columns to get formats on chunks")

    columns = build_known_columns(table)
    mandatory_label_skip: dict[str, set[str]] = {
        col: {
            fmt_label
            for fmt_label, fmt in formats.items()
            if fmt.mandatory_label and fmt.is_valid_label(col) == 0
        }
        for col in columns.keys()
    }
    remaining_tests_per_col = {
        col: {
            fmt_label
            for fmt_label, fmt in formats.items()
            # keeping formats that have the valid python type
            if fmt.python_type == pytype
            # except if the column label doesn't fit
            and fmt_label not in mandatory_label_skip.get(col, set())
            # we already know pure types are valid, only formats remain
            and fmt_label != pytype
        }
        for col, pytype in columns.items()
    }
    return_table = pd.DataFrame(columns=columns.keys(), index=formats.keys())
    for col, pytype in columns.items():
        if pytype != "string":
            # setting types that we know are 100% valid from metadata
            return_table.loc[pytype, col] = 1

    row_hashes_count = pd.Series()
    col_values = {col: pd.Series() for col in columns.keys()}
    # we keep the same chunk size as for csv
    for idx, batch in enumerate(table.iter_batches(CHUNK_SIZE * 10)):
        if verbose:
            logging.info(f"> Testing batch number {idx + 1}")
        batch = batch.to_pandas()
        str_batch = batch.map(
            # not simply using astype(str) because lists are numpy arrays, cast as str they lose their commas
            lambda x: str(x.tolist()) if isinstance(x, np.ndarray) else str(x)
        )
        row_hashes_count = row_hashes_count.add(
            pd.util.hash_pandas_object(str_batch, index=False).value_counts(),
            fill_value=0,
        )
        for col in batch.columns:
            col_values[col] = col_values[col].add(
                str_batch[col].value_counts(dropna=False),
                fill_value=0,
            )
        if not any(remaining_tests for remaining_tests in remaining_tests_per_col.values()):
            # no more potential tests to do on any column, early stop
            break
        for col, fmt_labels in remaining_tests_per_col.items():
            # testing each column with the tests that are still competing
            # after previous batchs analyses
            for label in fmt_labels:
                batch_col_test = test_col_val(
                    batch[col],
                    formats[label],
                    limited_output=limited_output,
                    skipna=skipna,
                )
                return_table.loc[label, col] = (
                    # if this batch's column tested 0 then test fails overall
                    0
                    if batch_col_test == 0
                    # set the first score
                    else batch_col_test
                    if pd.isna(return_table.loc[label, col])
                    # otherwise updating the score with weighted average
                    else ((return_table.loc[label, col] * idx + batch_col_test) / (idx + 1))
                )
        remaining_tests_per_col = _build_remaining_tests_per_col(
            return_table, mandatory_label_skip, known_columns=columns
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
