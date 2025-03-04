"""
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs
"""

from typing import Dict, List, Union
from collections import defaultdict
import json
import numpy as np
import os
import tempfile
import logging
from time import time
import requests
from io import StringIO
import pandas as pd

# flake8: noqa
from csv_detective import detect_fields, detect_labels
from csv_detective.s3_utils import download_from_minio, upload_to_minio
from csv_detective.schema_generation import generate_table_schema
from csv_detective.utils import (
    cast_df,
    display_logs_depending_process_time,
    prepare_output_dict,
    test_col,
    test_label,
)
from .detection import (
    detect_engine,
    detect_separator,
    detect_encoding,
    detect_headers,
    detect_heading_columns,
    detect_trailing_columns,
    parse_table,
    parse_excel,
    create_profile,
    detetect_categorical_variable,
    # detect_continuous_variable,
    is_url,
    XLS_LIKE_EXT,
)


logging.basicConfig(level=logging.INFO)


def get_all_packages(detect_type) -> list:
    root_dir = os.path.dirname(os.path.abspath(__file__)) + "/" + detect_type
    modules = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file = os.path.join(dirpath, filename).replace(root_dir, "")
            if file.endswith("__init__.py"):
                module = (
                    file.replace("__init__.py", "")
                    .replace("/", ".").replace("\\", ".")[:-1]
                )
                if module:
                    modules.append(detect_type + module)
    return modules


def return_all_tests(
    user_input_tests: Union[str, list],
    detect_type: str,
) -> list:
    """
    returns all tests that have a method _is and are listed in the user_input_tests
    the function can select a sub_package from csv_detective
    user_input_tests may look like this:
        - "ALL": all possible tests are made
        - "FR.other.siren" (or any other path-like string to one of the tests, or a group of tests, like "FR.geo"):
        this specifc (group of) test(s) only
        - ["FR.temp.mois_de_annee", "geo", ...]: only the specified tests will be made ; you may also skip
        specific (groups of) tests by add "-" at the start (e.g "-temp.date")
    """
    assert detect_type in ["detect_fields", "detect_labels"]
    all_packages = get_all_packages(detect_type=detect_type)

    if isinstance(user_input_tests, str):
        user_input_tests = [user_input_tests]
    if "ALL" in user_input_tests or all(x[0] == "-" for x in user_input_tests):
        tests_to_do = [detect_type]
    else:
        tests_to_do = [
            f"{detect_type}.{x}" for x in user_input_tests if x[0] != "-"
        ]
    tests_skipped = [
        f"{detect_type}.{x[1:]}" for x in user_input_tests if x[0] == "-"
    ]
    all_tests = [
        # this is why we need to import detect_fields/labels
        eval(x) for x in all_packages
        if any([y == x[: len(y)] for y in tests_to_do])
        and all([y != x[: len(y)] for y in tests_skipped])
    ]
    # to remove groups of tests
    all_tests = [
        test for test in all_tests if "_is" in dir(test)
    ]
    return all_tests


def routine(
    csv_file_path: str,
    num_rows: int = 500,
    user_input_tests: Union[str, List[str]] = "ALL",
    limited_output: bool = True,
    save_results: Union[bool, str] = True,
    encoding: str = None,
    sep: str = None,
    skipna: bool = True,
    output_profile: bool = False,
    output_schema: bool = False,
    output_df: bool = False,
    cast_json: bool = True,
    verbose: bool = False,
    sheet_name: Union[str, int] = None,
) -> Union[dict, tuple[dict, pd.DataFrame]]:
    """Returns a dict with information about the csv table and possible
    column contents.

    Args:
        csv_file_path: local path to CSV file if not using Minio
        num_rows: number of rows to sample from the file for analysis ; -1 for analysis
        of the whole file
        user_input_tests: tests to run on the file
        limited_output: whether or not to return all possible types or only the most likely one for each column
        save_results: whether or not to save the results in a json file, or the path where to dump the output
        output_profile: whether or not to add the 'profile' field to the output
        output_schema: whether or not to add the 'schema' field to the output (tableschema)
        output_df: whether or not to return the loaded DataFrame along with the analysis report
        cast_json: whether or not to cast json columns into objects (otherwise they are returned as strings)
        verbose: whether or not to print process logs in console 
        sheet_name: if reading multi-sheet file (xls-like), which sheet to consider
        skipna: whether to keep NaN (empty cells) for tests

    Returns:
        dict: a dict with information about the csv and possible types for each column
    """
    if not csv_file_path:
        raise ValueError("csv_file_path is required.")
    
    if not (isinstance(save_results, bool) or (isinstance(save_results, str) and save_results.endswith(".json"))):
        raise ValueError("`save_results` must be a bool or a valid path to a json file.")

    if verbose:
        start_routine = time()
        if is_url(csv_file_path):
            logging.info("Path recognized as a URL")

    file_name = csv_file_path.split('/')[-1]
    engine = None
    if '.' not in file_name:
        # file has no extension, we'll investigate how to read it
        engine = detect_engine(csv_file_path, verbose=verbose)

    is_xls_like = False
    if engine or any([csv_file_path.endswith(k) for k in XLS_LIKE_EXT]):
        is_xls_like = True
        encoding, sep, heading_columns, trailing_columns = None, None, None, None
        table, total_lines, nb_duplicates, sheet_name, engine, header_row_idx = parse_excel(
            csv_file_path=csv_file_path,
            num_rows=num_rows,
            engine=engine,
            sheet_name=sheet_name,
            verbose=verbose,
        )
        header = table.columns.to_list()
    else:
        if encoding is None:
            encoding = detect_encoding(csv_file_path, verbose=verbose)
        if is_url(csv_file_path):
            r = requests.get(csv_file_path, allow_redirects=True)
            r.raise_for_status()
            str_file = StringIO(r.content.decode(encoding=encoding))
        else:
            str_file = open(csv_file_path, "r", encoding=encoding)
        if sep is None:
            sep = detect_separator(str_file, verbose=verbose)
        header_row_idx, header = detect_headers(str_file, sep, verbose=verbose)
        if header is None:
            return {"error": True}
        elif isinstance(header, list):
            if any([x is None for x in header]):
                return {"error": True}
        heading_columns = detect_heading_columns(str_file, sep, verbose=verbose)
        trailing_columns = detect_trailing_columns(str_file, sep, heading_columns, verbose=verbose)
        table, total_lines, nb_duplicates = parse_table(
            str_file, encoding, sep, num_rows, header_row_idx, verbose=verbose
        )

    if table.empty:
        res_categorical = []
        # res_continuous = []
    else:
        # Detects columns that are categorical
        res_categorical, categorical_mask = detetect_categorical_variable(table, verbose=verbose)
        res_categorical = list(res_categorical)
        # Detect columns that are continuous (we already know the categorical) : we don't need this for now, cuts processing time
        # res_continuous = list(
        #     detect_continuous_variable(table.iloc[:, ~categorical_mask.values], verbose=verbose)
        # )

    # Creating return dictionary
    analysis = {
        "header_row_idx": header_row_idx,
        "header": header,
        "total_lines": total_lines,
        "nb_duplicates": nb_duplicates,
        "heading_columns": heading_columns,
        "trailing_columns": trailing_columns,
        "categorical": res_categorical,
        # "continuous": res_continuous,
    }
    # this is only relevant for xls-like
    if is_xls_like:
        analysis["engine"] = engine
        analysis["sheet_name"] = sheet_name
    # this is only relevant for csv
    else:
        analysis["encoding"] = encoding
        analysis["separator"] = sep

    # list testing to be performed
    all_tests_fields = return_all_tests(
        user_input_tests, detect_type="detect_fields"
    )  # list all tests for the fields
    all_tests_labels = return_all_tests(
        user_input_tests, detect_type="detect_labels"
    )  # list all tests for the labels

    # if no testing then return
    if not all_tests_fields and not all_tests_labels:
        return analysis

    # Perform testing on fields
    scores_table_fields = test_col(table, all_tests_fields, limited_output, skipna=skipna, verbose=verbose)
    analysis["columns_fields"] = prepare_output_dict(scores_table_fields, limited_output)

    # Perform testing on labels
    scores_table_labels = test_label(table, all_tests_labels, limited_output, verbose=verbose)
    analysis["columns_labels"] = prepare_output_dict(scores_table_labels, limited_output)

    # Multiply the results of the fields by 1 + 0.5 * the results of the labels.
    # This is because the fields are more important than the labels and yields a max
    # of 1.5 for the final score.
    scores_table = scores_table_fields * (
        1
        + scores_table_labels.reindex(
            index=scores_table_fields.index, fill_value=0
        ).values / 2
    )

    # To reduce false positives: ensure these formats are detected only if the label yields
    # a detection (skipping the ones that have been excluded by the users).
    formats_with_mandatory_label = [
        f for f in [
            "code_departement",
            "code_commune_insee",
            "code_postal",
            "latitude_wgs",
            "longitude_wgs",
            "latitude_wgs_fr_metropole",
            "longitude_wgs_fr_metropole",
            "latitude_l93",
            "longitude_l93",
        ] if f in scores_table.index
    ]
    scores_table.loc[formats_with_mandatory_label, :] = np.where(
        scores_table_labels.loc[formats_with_mandatory_label, :],
        scores_table.loc[formats_with_mandatory_label, :],
        0,
    )
    analysis["columns"] = prepare_output_dict(scores_table, limited_output)

    metier_to_python_type = {
        "booleen": "bool",
        "int": "int",
        "float": "float",
        "string": "string",
        "json": "json",
        "json_geojson": "json",
        "datetime": "datetime",
        "datetime_iso": "datetime",
        "datetime_rfc822": "datetime",
        "date": "date",
        "latitude": "float",
        "latitude_l93": "float",
        "latitude_wgs": "float",
        "latitude_wgs_fr_metropole": "float",
        "longitude": "float",
        "longitude_l93": "float",
        "longitude_wgs": "float",
        "longitude_wgs_fr_metropole": "float",
    }

    if not limited_output:
        for detection_method in ["columns_fields", "columns_labels", "columns"]:
            analysis[detection_method] = {
                col_name: [
                    {
                        "python_type": metier_to_python_type.get(
                            detection["format"], "string"
                        ),
                        **detection,
                    }
                    for detection in detections
                ]
                for col_name, detections in analysis[detection_method].items()
            }
    else:
        for detection_method in ["columns_fields", "columns_labels", "columns"]:
            analysis[detection_method] = {
                col_name: {
                    "python_type": metier_to_python_type.get(
                        detection["format"], "string"
                    ),
                    **detection,
                }
                for col_name, detection in analysis[detection_method].items()
            }

        # Add detection with formats as keys
        analysis["formats"] = defaultdict(list)
        for header, col_metadata in analysis["columns"].items():
            analysis["formats"][col_metadata["format"]].append(header)

    if output_profile:
        analysis["profile"] = create_profile(
            table=table,
            dict_cols_fields=analysis["columns"],
            num_rows=num_rows,
            limited_output=limited_output,
            verbose=verbose,
        )

    if save_results:
        if isinstance(save_results, str):
            output_path = save_results
        else:
            output_path = os.path.splitext(csv_file_path)[0]
            if is_url(output_path):
                output_path = output_path.split('/')[-1]
            if is_xls_like:
                output_path += "_sheet-" + str(sheet_name)
            output_path += ".json"
        with open(output_path, "w", encoding="utf8") as fp:
            json.dump(analysis, fp, indent=4, separators=(",", ": "), ensure_ascii=False)

    if output_schema:
        analysis["schema"] = generate_table_schema(
            analysis,
            save_file=False,
            verbose=verbose
        )
    if verbose:
        display_logs_depending_process_time(
            f'Routine completed in {round(time() - start_routine, 3)}s',
            time() - start_routine
        )
    if output_df:
        return analysis, cast_df(
            df=table,
            columns=analysis["columns"],
            cast_json=cast_json,
            verbose=verbose,
        )
    return analysis


def routine_minio(
    csv_minio_location: Dict[str, str],
    output_minio_location: Dict[str, str],
    tableschema_minio_location: Dict[str, str],
    minio_user: str,
    minio_pwd: str,
    num_rows: int = 500,
    user_input_tests: Union[str, List[str]] = "ALL",
    encoding: str = None,
    sep: str = None,
):
    """Returns a dict with information about the csv table and possible
    column contents.

    Args:
        csv_minio_location: dict with Minio URL, bucket and key of the CSV file
        output_minio_location: Minio URL, bucket and key to store output file. None if
        not uploading to Minio.
        tableschema_minio_location: Minio URL, bucket and key to store tableschema file.
        None if not uploading the tableschema to Minio.
        minio_user: user name for the minio instance
        minio_pwd: password for the minio instance
        num_rows: number of rows to sample from the file for analysis ; -1 for analysis of
        the whole file
        user_input_tests: tests to run on the file
        output_mode: LIMITED or ALL, whether or not to return all possible types or only
        the most likely one for each column

    Returns:
        dict: a dict with information about the csv and possible types for each column
    """

    if (
        (
            any(
                [
                    location_dict is not None
                    for location_dict in [
                        csv_minio_location,
                        output_minio_location,
                        tableschema_minio_location,
                    ]
                ]
            )
        )
        and (minio_user is None)
        or (minio_pwd is None)
    ):
        raise ValueError("Minio credentials are required if using Minio")

    for location_dict in [
        csv_minio_location,
        output_minio_location,
        tableschema_minio_location,
    ]:
        if location_dict is not None:
            if any(
                [
                    (location_key not in location_dict)
                    or (location_dict[location_key] is None)
                    for location_key in ["netloc", "bucket", "key"]
                ]
            ):
                raise ValueError("Minio location dict must contain url, bucket and key")

    csv_file_path = tempfile.NamedTemporaryFile(delete=False).name
    download_from_minio(
        netloc=csv_minio_location["netloc"],
        bucket=csv_minio_location["bucket"],
        key=csv_minio_location["key"],
        filepath=csv_file_path,
        minio_user=minio_user,
        minio_pwd=minio_pwd,
    )

    analysis = routine(
        csv_file_path,
        num_rows,
        user_input_tests,
        output_mode="LIMITED",
        save_results=True,
        encoding=encoding,
        sep=sep,
    )

    # Write report JSON file.
    output_path_to_store_minio_file = os.path.splitext(csv_file_path)[0] + ".json"
    with open(output_path_to_store_minio_file, "w", encoding="utf8") as fp:
        json.dump(analysis, fp, indent=4, separators=(",", ": "))

    upload_to_minio(
        netloc=output_minio_location["netloc"],
        bucket=output_minio_location["bucket"],
        key=output_minio_location["key"],
        filepath=output_path_to_store_minio_file,
        minio_user=minio_user,
        minio_pwd=minio_pwd,
    )

    os.remove(output_path_to_store_minio_file)
    os.remove(csv_file_path)

    generate_table_schema(
        analysis,
        True,
        netloc=tableschema_minio_location["netloc"],
        bucket=tableschema_minio_location["bucket"],
        key=tableschema_minio_location["key"],
        minio_user=minio_user,
        minio_pwd=minio_pwd,
    )

    return analysis
