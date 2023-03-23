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
    serie, test_func, proportion=0.9, skipna=True, num_rows=-1, output_mode="ALL"
):
    """Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
         - num_rows : number of rows to sample from the file for analysis ; -1 for analysis of the whole file
    for the serie to be detected as a certain format
    """

    # TODO : change for a cleaner method and only test columns in modules labels
    def apply_test_func(serie, test_func, _range):
        try:
            return serie.sample(frac=1).iloc[_range].apply(test_func)
        except AttributeError:  # .name n'est pas trouvé
            return test_func(serie.iloc[_range])

    serie = serie[serie.notnull()]
    ser_len = len(serie)
    if num_rows > 0:
        ser_len = min(ser_len, num_rows)
    _range = range(0, ser_len)
    if ser_len == 0:
        return 0.0
    if output_mode == "ALL":
        result = apply_test_func(serie, test_func, _range).sum() / ser_len
        return result if result >= proportion else 0.0
    else:
        if proportion == 1:  # Then try first 1 value, then 5, then all
            for _range in [
                range(0, min(1, ser_len)),
                range(min(1, ser_len), min(5, ser_len)),
                range(min(5, ser_len), min(num_rows, ser_len))
                if num_rows > 0
                else range(min(5, ser_len), ser_len),
            ]:  # Pour ne pas faire d'opérations inutiles, on commence par 1,
                # puis 5 puis num_rows valeurs
                if all(apply_test_func(serie, test_func, _range)):
                    pass
                else:
                    return 0.0
            return 1.0
        else:
            result = apply_test_func(serie, test_func, _range).sum() / ser_len
            return result if result >= proportion else 0.0


def test_col_label(label, test_func, proportion=1, output_mode="ALL"):
    """Tests label (from header) using test_func.
    - proportion :  indicates the minimum score to pass the test for the serie
    to be detected as a certain format
    """
    if output_mode == "ALL":
        return test_func(label)
    else:
        result = test_func(label)
        return result if result >= proportion else 0


def test_col(table, all_tests, num_rows, output_mode, verbose: bool = False):
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
        # When analysis of all file is requested (num_rows = -1) we fix a threshold of
        # 1000 rows for every checks outside int or float format
        if num_rows == -1:
            local_num_rows = 1000
        else:
            local_num_rows = min(num_rows, 1000)
        # For checks detecting dates, int or float format, we analyze the whole file (because
        # error can be generated afterward when exploiting this data into a database)
        if key in [
            "int",
            "float",
            "date",
            "datetime_iso",
            "datetime_rfc822",
            "longitude",
            "longitude_l93",
            "longitude_wgs",
            "longitude_wgs_fr_metropole",
            "latitude",
            "latitude_l93",
            "latitude_wgs",
            "latitude_wgs_fr_metropole",
            "iso_country_code_numeric",
        ]:
            local_num_rows = max(-1, num_rows)
        # improvement lead : put the longest tests behind and make them only if previous tests not satisfactory
        # => the following needs to change, "apply" means all columns are tested for one type at once
        return_table.loc[key] = table.apply(
            lambda serie: test_col_val(
                serie,
                value["func"],
                value["prop"],
                num_rows=local_num_rows,
                output_mode=output_mode,
            )
        )
        if verbose:
            display_logs_depending_process_time(
                f'\t- Done with type "{key}" in {round(time() - start_type, 3)}s ({idx+1}/{len(test_funcs)})',
                time() - start_type
            )
    if verbose:
        display_logs_depending_process_time(f"Done testing columns in {round(time() - start, 3)}s", time() - start)
    return return_table


def test_label(table, all_tests, output_mode, verbose: bool = False):
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
                col_name, value["func"], value["prop"], output_mode=output_mode
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


def prepare_output_dict(return_table, output_mode):
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
        if output_mode == "ALL":
            return_dict_cols_intermediary[column_name] = detections
        if output_mode == "LIMITED":
            return_dict_cols_intermediary[column_name] = (
                max(detections, key=lambda x: x["score"])
                if len(detections) > 0
                else {"format": "string", "score": 1.0}
            )

    return return_dict_cols_intermediary


def full_word_strictly_inside_string(word, string):
    return (
        (" " + word + " " in string)
        or (string.startswith(word + " "))
        or (string.endswith(" " + word))
    )
