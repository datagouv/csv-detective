import logging
from time import time
from typing import Callable

import pandas as pd

from csv_detective.parsing.csv import CHUNK_SIZE
from csv_detective.utils import display_logs_depending_process_time

# above this threshold, a column is not considered categorical
MAX_NUMBER_CATEGORICAL_VALUES = 25


def test_col_val(
    serie: pd.Series,
    test_func: Callable,
    proportion: float = 0.9,
    skipna: bool = True,
    limited_output: bool = False,
    verbose: bool = False,
) -> float:
    """Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain format
    """
    if verbose:
        start = time()

    # TODO : change for a cleaner method and only test columns in modules labels
    def apply_test_func(serie: pd.Series, test_func: Callable, _range: int):
        return serie.sample(n=_range).apply(test_func)

    try:
        if skipna:
            serie = serie[serie.notnull()]
        ser_len = len(serie)
        if ser_len == 0:
            # being here means the whole column is NaN, so if skipna it's a pass
            return 1.0 if skipna else 0.0
        if not limited_output:
            result = apply_test_func(serie, test_func, ser_len).sum() / ser_len
            return result if result >= proportion else 0.0
        else:
            if proportion == 1:
                # early stops (1 then 5 rows) to not waste time if directly unsuccessful
                for _range in [
                    min(1, ser_len),
                    min(5, ser_len),
                    ser_len,
                ]:
                    if not all(apply_test_func(serie, test_func, _range)):
                        return 0.0
                return 1.0
            else:
                result = apply_test_func(serie, test_func, ser_len).sum() / ser_len
                return result if result >= proportion else 0.0
    finally:
        if verbose and time() - start > 3:
            display_logs_depending_process_time(
                f"\t/!\\ Column '{serie.name}' took too long ({round(time() - start, 3)}s)",
                time() - start,
            )


def test_col_label(
    label: str, test_func: Callable, proportion: float = 1, limited_output: bool = False
):
    """Tests label (from header) using test_func.
    - proportion :  indicates the minimum score to pass the test for the serie
    to be detected as a certain format
    """
    if not limited_output:
        return test_func(label)
    else:
        result = test_func(label)
        return result if result >= proportion else 0


def test_col(
    table: pd.DataFrame,
    all_tests: dict[str, dict],
    limited_output: bool,
    skipna: bool = True,
    verbose: bool = False,
):
    if verbose:
        start = time()
        logging.info("Testing columns to get types")
    return_table = pd.DataFrame(columns=table.columns)
    for idx, (name, attributes) in enumerate(all_tests.items()):
        if verbose:
            start_type = time()
            logging.info(f"\t- Starting with type '{name}'")
        # improvement lead : put the longest tests behind and make them only if previous tests not satisfactory
        # => the following needs to change, "apply" means all columns are tested for one type at once
        return_table.loc[name] = table.apply(
            lambda serie: test_col_val(
                serie,
                attributes["func"],
                attributes["prop"],
                skipna=skipna,
                limited_output=limited_output,
                verbose=verbose,
            )
        )
        if verbose:
            display_logs_depending_process_time(
                f'\t> Done with type "{name}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(all_tests)})',
                time() - start_type,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done testing columns in {round(time() - start, 3)}s", time() - start
        )
    return return_table


def test_label(columns: list[str], all_tests: dict[str, dict], limited_output: bool, verbose: bool = False):
    if verbose:
        start = time()
        logging.info("Testing labels to get types")

    return_table = pd.DataFrame(columns=columns)
    for idx, (key, value) in enumerate(all_tests.items()):
        if verbose:
            start_type = time()
        return_table.loc[key] = [
            test_col_label(col_name, value["func"], value["prop"], limited_output=limited_output)
            for col_name in columns
        ]
        if verbose:
            display_logs_depending_process_time(
                f'\t- Done with type "{key}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(all_tests)})',
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
    all_tests: list,
    limited_output: bool,
    skipna: bool = True,
    verbose: bool = False,
) -> tuple[pd.DataFrame, dict]:
    def build_remaining_tests_per_col(return_table: pd.DataFrame) -> dict[str, list[str]]:
        return {
            col: [
                test for test in return_table.index if return_table.loc[test, col] > 0
            ]
            for col in return_table.columns
        }

    if verbose:
        start = time()
        logging.info("Testing columns to get types on chunks")

    # analysing the sample to get a first guess
    return_table = test_col(table, all_tests, limited_output, skipna=skipna, verbose=verbose)
    remaining_tests_per_col = build_remaining_tests_per_col(return_table)

    # hashing rows to get nb_duplicates
    row_hashes_count = table.apply(lambda row: hash(tuple(row)), axis=1).value_counts()
    # getting values for profile if specified
    col_values = {
        col: table[col].value_counts(dropna=False)
        for col in table.columns
    }

    # only csv files can end up here, can't chunk excel
    chunks = pd.read_csv(
        file_path,
        dtype=str,
        encoding=analysis["encoding"],
        sep=analysis["separator"],
        compression=analysis.get("compression"),
        chunksize=CHUNK_SIZE,
    )
    analysis["total_lines"] = CHUNK_SIZE
    for idx, chunk in enumerate(chunks):
        if idx == 0:
            # we have read and analysed the first chunk already
            continue
        if verbose:
            logging.info(f"> Testing chunk number {idx + 1}")
        analysis["total_lines"] += len(chunk)
        row_hashes_count = row_hashes_count.add(
            chunk.apply(lambda row: hash(tuple(row)), axis=1).value_counts(),
            fill_value=0,
        )
        for col in chunk.columns:
            col_values[col] = col_values[col].add(chunk[col].value_counts(dropna=False))
        if not any(remaining_tests for remaining_tests in remaining_tests_per_col.values()):
            # no more potential tests to do on any column, early stop
            break
        for col, tests in remaining_tests_per_col.items():
            # testing each column with the tests that are still competing
            # after previous chunks analyses
            for test in tests:
                chunk_col_test = test_col_val(
                    chunk[col],
                    all_tests[test]["func"],
                    all_tests[test]["prop"],
                    limited_output=limited_output,
                    skipna=skipna,
                )
                return_table.loc[test, col] = (
                    # if this chunk's column tested 0 then test fails overall
                    0 if chunk_col_test == 0
                    # otherwise updating the score with weighted average
                    else (
                        (return_table.loc[test, col] * idx + chunk_col_test)
                        / (idx + 1)
                    )
                )
        remaining_tests_per_col = build_remaining_tests_per_col(return_table)
    analysis["nb_duplicates"] = sum(row_hashes_count > 1)
    analysis["categorical"] = [
        col for col, values in col_values.items()
        if len(values) <= MAX_NUMBER_CATEGORICAL_VALUES
    ]
    # handling that empty columns score 1 everywhere
    for col in return_table.columns:
        if sum(return_table[col]) == len(return_table):
            return_table[col] = 0
    if verbose:
        display_logs_depending_process_time(
            f"Done testing chunks in {round(time() - start, 3)}s", time() - start
        )
    return return_table, analysis
