import logging
from collections import defaultdict
from time import time
from typing import Callable

import pandas as pd

from csv_detective.load_tests import build_tests_dicts
from csv_detective.utils import display_logs_depending_process_time

MAX_ROWS_ANALYSIS = int(1e4)


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
            return 0.0
        if not limited_output:
            result = apply_test_func(serie, test_func, ser_len).sum() / ser_len
            return result if result >= proportion else 0.0
        else:
            if proportion == 1:  # Then try first 1 value, then 5, then all
                for _range in [
                    min(1, ser_len),
                    min(5, ser_len),
                    ser_len,
                ]:  # Pour ne pas faire d'opérations inutiles, on commence par 1,
                    # puis 5 valeurs puis la serie complète
                    if all(apply_test_func(serie, test_func, _range)):
                        pass
                    else:
                        return 0.0
                return 1.0
            else:
                # if we have a proportion, statistically it's OK to analyse up to 10k rows
                # (arbitrary number) and get a significant result
                to_analyse = min(ser_len, MAX_ROWS_ANALYSIS)
                result = apply_test_func(serie, test_func, to_analyse).sum() / to_analyse
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
    all_tests: list,
    limited_output: bool,
    skipna: bool = True,
    verbose: bool = False,
):
    if verbose:
        start = time()
        logging.info("Testing columns to get types")
    test_funcs, specific_tests = build_tests_dicts(all_tests)
    results = defaultdict(dict)
    nb_cols = len(table.columns)
    for idx, column in enumerate(table.columns):
        if verbose:
            start_col = time()
            logging.info(f"\t- Starting with column '{column}'")
        tested = set()
        # testing for the most specific formats first (we have early stops in test_col_val)
        for test_name, test_attr in specific_tests.items():
            results[column][test_name] = test_col_val(
                table[column],
                test_attr["func"],
                test_attr["prop"],
                skipna=skipna,
                limited_output=limited_output,
                verbose=verbose,
            )
            tested.add(test_name)
            # should we break if one of the specific tests is successful?
        # performing less and less specific tests if specific ones fail
        # starting with highest scores to set the parents from there
        for test_name in reversed([
            test for test, _ in sorted(
                (tup for tup in results[column].items()),
                key=lambda tup: tup[1],
            )
        ]):
            current = test_name
            parent = test_funcs[current]["parent"]
            while parent is not None:
                if parent in results[column]:
                    # already tested as a parent of a previous test, no need to get higher parents
                    break
                if results[column][current] > 0:
                    # if a child test is successful, we set the parent's score to the same value
                    # this is not perfect: the column can be 50% child but 100% parent
                    # we would have to perform the parent test to know exactly, but this saves much time
                    results[column][parent] = results[column][current]
                else:
                    results[column][parent] = test_col_val(
                        table[column],
                        test_funcs[parent]["func"],
                        test_funcs[parent]["prop"],
                        skipna=skipna,
                        limited_output=limited_output,
                        verbose=verbose,
                    )
                    tested.add(parent)
                current, parent = parent, test_funcs[parent]["parent"]
        if verbose:
            display_logs_depending_process_time(
                f'\t> Done with column "{column}" in {round(time() - start_col, 3)}s'
                f" ({idx + 1}/{nb_cols}), {len(tested)} tests performed",
                time() - start_col,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done testing columns in {round(time() - start, 3)}s", time() - start
        )
    return pd.DataFrame(results)


def test_label(table: pd.DataFrame, all_tests: list, limited_output: bool, verbose: bool = False):
    if verbose:
        start = time()
        logging.info("Testing labels to get types")
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split(".")[-1]
        test_funcs[name] = {"func": test._is, "prop": test.PROPORTION}

    return_table = pd.DataFrame(columns=table.columns)
    for idx, (key, value) in enumerate(test_funcs.items()):
        if verbose:
            start_type = time()
        return_table.loc[key] = [
            test_col_label(col_name, value["func"], value["prop"], limited_output=limited_output)
            for col_name in table.columns
        ]
        if verbose:
            display_logs_depending_process_time(
                f'\t- Done with type "{key}" in {round(time() - start_type, 3)}s ({idx + 1}/{len(test_funcs)})',
                time() - start_type,
            )
    if verbose:
        display_logs_depending_process_time(
            f"Done testing labels in {round(time() - start, 3)}s", time() - start
        )
    return return_table
