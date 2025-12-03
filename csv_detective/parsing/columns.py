import logging
from time import time
from typing import Callable

import pandas as pd
from more_itertools import peekable

from csv_detective.format import Format
from csv_detective.parsing.csv import CHUNK_SIZE
from csv_detective.utils import display_logs_depending_process_time

# above this threshold, a column is not considered categorical
MAX_NUMBER_CATEGORICAL_VALUES = 25


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
            serie = serie.loc[serie.notnull()]
        ser_len = len(serie)
        if ser_len == 0:
            # being here means the whole column is NaN, so if skipna it's a pass
            return 1.0 if skipna else 0.0
        if not limited_output or format.proportion < 1:
            # we want or have to go through the whole column to have the proportion
            result: float = serie.apply(format.func).sum() / ser_len
            return result if result >= format.proportion else 0.0
        else:
            # the whole column has to be valid so we have early stops (1 then 5 rows)
            # to not waste time if directly unsuccessful
            for _range in [
                min(1, ser_len),
                min(5, ser_len),
                ser_len,
            ]:
                if not all(apply_test_func(serie, format.func, _range)):
                    return 0.0
            return 1.0
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
                f'\t> Done with type "{label}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(formats)})',
                time() - start_type,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done testing columns in {round(time() - start, 3)}s", time() - start
        )
    return return_table


def test_label(
    columns: list[str], formats: dict[str, Format], limited_output: bool, verbose: bool = False
):
    if verbose:
        start = time()
        logging.info("Testing labels to get types")

    return_table = pd.DataFrame(columns=columns)
    for idx, (label, format) in enumerate(formats.items()):
        if verbose:
            start_type = time()
        return_table.loc[label] = [format.is_valid_label(col_name) for col_name in columns]
        if verbose:
            display_logs_depending_process_time(
                f'\t- Done with type "{label}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(formats)})',
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
    limited_output: bool,
    skipna: bool = True,
    verbose: bool = False,
) -> tuple[pd.DataFrame, dict, dict[str, pd.Series]]:
    def build_remaining_tests_per_col(return_table: pd.DataFrame) -> dict[str, list[str]]:
        # returns a dict with the table's columns as keys and the list of remaining format labels to apply
        return {
            col: [
                fmt_label
                for fmt_label in return_table.index
                if return_table.loc[fmt_label, col] > 0
            ]
            for col in return_table.columns
        }

    if verbose:
        start = time()
        logging.info("Testing columns to get formats on chunks")

    # analysing the sample to get a first guess
    return_table = test_col(table, formats, limited_output, skipna=skipna, verbose=verbose)
    remaining_tests_per_col = build_remaining_tests_per_col(return_table)

    # hashing rows to get nb_duplicates
    row_hashes_count = table.apply(lambda row: hash(tuple(row)), axis=1).value_counts()
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
            batch.apply(lambda row: hash(tuple(row)), axis=1).value_counts(),
            fill_value=0,
        )
        for col in batch.columns:
            col_values[col] = col_values[col].add(
                batch[col].value_counts(dropna=False),
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
                    # otherwise updating the score with weighted average
                    else ((return_table.loc[label, col] * idx + batch_col_test) / (idx + 1))
                )
        remaining_tests_per_col = build_remaining_tests_per_col(return_table)
        batch, batch_number = [], batch_number + 1
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    analysis["categorical"] = [
        col for col, values in col_values.items() if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
    ]
    # handling that empty columns score 1 everywhere
    for col in return_table.columns:
        if sum(return_table[col]) == len(return_table):
            return_table[col] = 0
    if verbose:
        display_logs_depending_process_time(
            f"Done testing chunks in {round(time() - start, 3)}s", time() - start
        )
    return return_table, analysis, col_values
