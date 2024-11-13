from typing import Callable
import pandas as pd
import logging
from time import time

logging.basicConfig(level=logging.INFO)


def display_logs_depending_process_time(prompt: str, duration: float):
    '''
    Print colored logs according to the time the operation took.
    '''
    logging.addLevelName(logging.CRITICAL, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
    logging.addLevelName(logging.WARN, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARN))

    threshold_warn = 1
    threshold_critical = 3

    if duration < threshold_warn:
        logging.info(prompt)
    elif duration < threshold_critical:
        logging.warn(prompt)
    else:
        logging.critical(prompt)


def test_col_val(
    serie: pd.Series,
    test_func: Callable,
    proportion: float = 0.9,
    skipna: bool = True,
    limited_output: bool = False,
    verbose: bool = False,
):
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
                        # print(serie.name, ': check OK')
                        pass
                    else:
                        return 0.0
                return 1.0
            else:
                # if we have a proportion, statistically it's OK to analyse up to 10k rows
                # (arbitrary number) and get a significant result
                to_analyse = min(ser_len, 10000)
                result = apply_test_func(serie, test_func, to_analyse).sum() / to_analyse
                return result if result >= proportion else 0.0
    finally:
        if verbose and time() - start > 3:
            display_logs_depending_process_time(
                f"\t/!\\ Column '{serie.name}' took too long ({round(time() - start, 3)}s)",
                time() - start
            )


def test_col_label(label: str, test_func: Callable, proportion: float = 1, limited_output: bool = False):
    """Tests label (from header) using test_func.
    - proportion :  indicates the minimum score to pass the test for the serie
    to be detected as a certain format
    """
    if not limited_output:
        return test_func(label)
    else:
        result = test_func(label)
        return result if result >= proportion else 0


def test_col(table: pd.DataFrame, all_tests: list, limited_output: bool, skipna: bool = True, verbose: bool = False):
    # Initialising dict for tests
    if verbose:
        start = time()
        logging.info("Testing columns to get types")
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split(".")[-1]
        test_funcs[name] = {"func": test._is, "prop": test.PROPORTION}
    return_table = pd.DataFrame(columns=table.columns)
    for idx, (key, value) in enumerate(test_funcs.items()):
        if verbose:
            start_type = time()
            logging.info(f"\t- Starting with type '{key}'")
        # improvement lead : put the longest tests behind and make them only if previous tests not satisfactory
        # => the following needs to change, "apply" means all columns are tested for one type at once
        return_table.loc[key] = table.apply(
            lambda serie: test_col_val(
                serie,
                value["func"],
                value["prop"],
                skipna=skipna,
                limited_output=limited_output,
                verbose=verbose,
            )
        )
        if verbose:
            display_logs_depending_process_time(
                f'\t> Done with type "{key}" in {round(time() - start_type, 3)}s ({idx+1}/{len(test_funcs)})',
                time() - start_type
            )
    if verbose:
        display_logs_depending_process_time(f"Done testing columns in {round(time() - start, 3)}s", time() - start)
    return return_table


def test_label(table: pd.DataFrame, all_tests: list, limited_output: bool, verbose: bool = False):
    # Initialising dict for tests
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
            test_col_label(
                col_name, value["func"], value["prop"], limited_output=limited_output
            )
            for col_name in table.columns
        ]
        if verbose:
            display_logs_depending_process_time(
                f'\t- Done with type "{key}" in {round(time() - start_type, 3)}s ({idx+1}/{len(test_funcs)})',
                time() - start_type
            )
    if verbose:
        display_logs_depending_process_time(f"Done testing labels in {round(time() - start, 3)}s", time() - start)
    return return_table


def prepare_output_dict(return_table: pd.DataFrame, limited_output: bool):
    return_dict_cols = return_table.to_dict("dict")
    return_dict_cols_intermediary = {}
    for column_name in return_dict_cols:
        return_dict_cols_intermediary[column_name] = []
        for detected_value_type in return_dict_cols[column_name]:
            if return_dict_cols[column_name][detected_value_type] == 0:
                continue
            dict_tmp = {}
            dict_tmp["format"] = detected_value_type
            dict_tmp["score"] = return_dict_cols[column_name][detected_value_type]
            return_dict_cols_intermediary[column_name].append(dict_tmp)

        # Clean dict using priorities
        formats_detected = {
            x["format"] for x in return_dict_cols_intermediary[column_name]
        }
        formats_to_remove = set()
        # Deprioritise float and int detection vs others
        if len(formats_detected - {"float", "int"}) > 0:
            formats_to_remove = formats_to_remove.union({"float", "int"})
        if "int" in formats_detected:
            formats_to_remove.add("float")
        if "latitude_wgs_fr_metropole" in formats_detected:
            formats_to_remove.add("latitude_l93")
            formats_to_remove.add("latitude_wgs")
        if "longitude_wgs_fr_metropole" in formats_detected:
            formats_to_remove.add("longitude_l93")
            formats_to_remove.add("longitude_wgs")
        if "longitude_wgs" in formats_detected:
            formats_to_remove.add("longitude_l93")
        if "code_region" in formats_detected:
            formats_to_remove.add("code_departement")

        formats_to_keep = formats_detected - formats_to_remove

        detections = return_dict_cols_intermediary[column_name]
        detections = [x for x in detections if x["format"] in formats_to_keep]
        if not limited_output:
            return_dict_cols_intermediary[column_name] = detections
        else:
            return_dict_cols_intermediary[column_name] = (
                max(detections, key=lambda x: x["score"])
                if len(detections) > 0
                else {"format": "string", "score": 1.0}
            )

    return return_dict_cols_intermediary


def full_word_strictly_inside_string(word: str, string: str):
    return (
        (" " + word + " " in string)
        or (string.startswith(word + " "))
        or (string.endswith(" " + word))
    )
