import json
import logging
import os
import tempfile
from time import time
from typing import Optional, Union

import pandas as pd

from .detection.formats import detect_formats
from .output import generate_output, generate_table_schema
from .parsing.load import load_file
from .s3_utils import download_from_minio, upload_to_minio
from .utils import display_logs_depending_process_time, is_url
from .validate import validate

logging.basicConfig(level=logging.INFO)


def routine(
    file_path: str,
    num_rows: int = 500,
    user_input_tests: Union[str, list[str]] = "ALL",
    limited_output: bool = True,
    save_results: Union[bool, str] = True,
    encoding: Optional[str] = None,
    sep: Optional[str] = None,
    skipna: bool = True,
    output_profile: bool = False,
    output_schema: bool = False,
    output_df: bool = False,
    cast_json: bool = True,
    verbose: bool = False,
    sheet_name: Optional[Union[str, int]] = None,
) -> Union[dict, tuple[dict, pd.DataFrame]]:
    """Returns a dict with information about the csv table and possible
    column contents, and if requested the DataFrame with columns cast according to analysis.

    Args:
        file_path: local path to CSV file if not using Minio
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

    if not (isinstance(save_results, bool) or (isinstance(save_results, str) and save_results.endswith(".json"))):
        raise ValueError("`save_results` must be a bool or a valid path to a json file.")

    if verbose:
        start_routine = time()
        if is_url(file_path):
            logging.info("Path recognized as a URL")

    table, analysis = load_file(
        file_path=file_path,
        num_rows=num_rows,
        encoding=encoding,
        sep=sep,
        verbose=verbose,
        sheet_name=sheet_name,
    )

    analysis = detect_formats(
        table=table,
        analysis=analysis,
        user_input_tests=user_input_tests,
        limited_output=limited_output,
        skipna=skipna,
        verbose=verbose,
    )

    try:
        return generate_output(
            table=table,
            analysis=analysis,
            file_path=file_path,
            num_rows=num_rows,
            limited_output=limited_output,
            save_results=save_results,
            output_profile=output_profile,
            output_schema=output_schema,
            output_df=output_df,
            cast_json=cast_json,
            verbose=verbose,
            sheet_name=sheet_name,
        )
    finally:
        if verbose:
            display_logs_depending_process_time(
                f"Routine completed in {round(time() - start_routine, 3)}s",
                time() - start_routine
            )


def validate_then_detect(
    file_path: str,
    previous_analysis: dict,
    num_rows: int = 500,
    user_input_tests: Union[str, list[str]] = "ALL",
    limited_output: bool = True,
    save_results: Union[bool, str] = True,
    skipna: bool = True,
    output_profile: bool = False,
    output_schema: bool = False,
    output_df: bool = False,
    cast_json: bool = True,
    verbose: bool = False,
):

    if verbose:
        start_routine = time()
        if is_url(file_path):
            logging.info("Path recognized as a URL")

    is_valid, table, analysis = validate(
        file_path=file_path,
        previous_analysis=previous_analysis,
        num_rows=num_rows,
        encoding=previous_analysis.get("encoding"),
        sep=previous_analysis.get("separator"),
        sheet_name=previous_analysis.get("sheet_name"),
        verbose=verbose,
        skipna=skipna,
    )
    if analysis is None:
        # if loading failed in validate, we load it from scratch
        table, analysis = load_file(
            file_path=file_path,
            num_rows=num_rows,
            verbose=verbose,
        )
    if not is_valid:
        analysis = detect_formats(
            table=table,
            analysis=analysis,
            user_input_tests=user_input_tests,
            limited_output=limited_output,
            skipna=skipna,
            verbose=verbose,
        )
    try:
        return generate_output(
            table=table,
            analysis=analysis,
            file_path=file_path,
            num_rows=num_rows,
            limited_output=limited_output,
            save_results=save_results,
            output_profile=output_profile,
            output_schema=output_schema,
            output_df=output_df,
            cast_json=cast_json,
            verbose=verbose,
            sheet_name=analysis.get("sheet_name"),
        )
    finally:
        if verbose:
            display_logs_depending_process_time(
                f"Process completed in {round(time() - start_routine, 3)}s",
                time() - start_routine
            )


def routine_minio(
    csv_minio_location: dict[str, str],
    output_minio_location: dict[str, str],
    tableschema_minio_location: dict[str, str],
    minio_user: str,
    minio_pwd: str,
    **kwargs,
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
        kwargs: arguments for routine

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

    file_path = tempfile.NamedTemporaryFile(delete=False).name
    download_from_minio(
        netloc=csv_minio_location["netloc"],
        bucket=csv_minio_location["bucket"],
        key=csv_minio_location["key"],
        filepath=file_path,
        minio_user=minio_user,
        minio_pwd=minio_pwd,
    )

    analysis = routine(
        file_path,
        save_results=True,
        **kwargs,
    )

    # Write report JSON file.
    output_path_to_store_minio_file = os.path.splitext(file_path)[0] + ".json"
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
    os.remove(file_path)

    generate_table_schema(
        analysis_report=analysis,
        save_file=True,
        netloc=tableschema_minio_location["netloc"],
        bucket=tableschema_minio_location["bucket"],
        key=tableschema_minio_location["key"],
        minio_user=minio_user,
        minio_pwd=minio_pwd,
    )

    return analysis
