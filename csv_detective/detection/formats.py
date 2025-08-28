import logging
from collections import defaultdict
from typing import Union

import numpy as np
import pandas as pd

from csv_detective.detection.variables import (
    detect_categorical_variable,
    # detect_continuous_variable,
)
from csv_detective.load_tests import return_all_tests
from csv_detective.output.utils import prepare_output_dict
from csv_detective.parsing.columns import MAX_ROWS_ANALYSIS, test_col, test_label
from csv_detective.validate import validate

# above this threshold, a column is not considered categorical
MAX_NUMBER_CATEGORICAL_VALUES = 25


def detect_formats(
    table: pd.DataFrame,
    analysis: dict,
    file_path: str,
    user_input_tests: Union[str, list[str]] = "ALL",
    limited_output: bool = True,
    skipna: bool = True,
    verbose: bool = False,
):
    on_sample = len(table) > MAX_ROWS_ANALYSIS
    if on_sample:
        if verbose:
            logging.warning(f"File is too long, analysing a sample of {MAX_ROWS_ANALYSIS} rows")
        table = build_sample(table)

    if table.empty:
        res_categorical = []
        # res_continuous = []
    else:
        # Detects columns that are categorical
        res_categorical, categorical_mask = detect_categorical_variable(
            table,
            max_number_categorical_values=MAX_NUMBER_CATEGORICAL_VALUES,
            verbose=verbose,
        )
        res_categorical = list(res_categorical)
        # Detect columns that are continuous (we already know the categorical) :
        # we don't need this for now, cuts processing time
        # res_continuous = list(
        #     detect_continuous_variable(table.iloc[:, ~categorical_mask.values], verbose=verbose)
        # )

    analysis.update(
        {
            "categorical": res_categorical,
            # "continuous": res_continuous,
        }
    )

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
    scores_table_fields = test_col(
        table, all_tests_fields, limited_output, skipna=skipna, verbose=verbose
    )
    analysis["columns_fields"] = prepare_output_dict(scores_table_fields, limited_output)

    # Perform testing on labels
    scores_table_labels = test_label(table, all_tests_labels, limited_output, verbose=verbose)
    analysis["columns_labels"] = prepare_output_dict(scores_table_labels, limited_output)

    # Multiply the results of the fields by 1 + 0.5 * the results of the labels.
    # This is because the fields are more important than the labels and yields a max
    # of 1.5 for the final score.
    scores_table = scores_table_fields * (
        1 + scores_table_labels.reindex(index=scores_table_fields.index, fill_value=0).values / 2
    )

    # To reduce false positives: ensure these formats are detected only if the label yields
    # a detection (skipping the ones that have been excluded by the users).
    formats_with_mandatory_label = [
        f
        for f in [
            "code_departement",
            "code_commune_insee",
            "code_postal",
            "latitude_wgs",
            "longitude_wgs",
            "latitude_wgs_fr_metropole",
            "longitude_wgs_fr_metropole",
            "latitude_l93",
            "longitude_l93",
        ]
        if f in scores_table.index
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
        "datetime_aware": "datetime",
        "datetime_naive": "datetime",
        "datetime_rfc822": "datetime",
        "date": "date",
        "latitude_l93": "float",
        "latitude_wgs": "float",
        "latitude_wgs_fr_metropole": "float",
        "longitude_l93": "float",
        "longitude_wgs": "float",
        "longitude_wgs_fr_metropole": "float",
    }

    if not limited_output:
        for detection_method in ["columns_fields", "columns_labels", "columns"]:
            analysis[detection_method] = {
                col_name: [
                    {
                        "python_type": metier_to_python_type.get(detection["format"], "string"),
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
                    "python_type": metier_to_python_type.get(detection["format"], "string"),
                    **detection,
                }
                for col_name, detection in analysis[detection_method].items()
            }

        # Add detection with formats as keys
        analysis["formats"] = defaultdict(list)
        for header, col_metadata in analysis["columns"].items():
            analysis["formats"][col_metadata["format"]].append(header)

    if on_sample:
        if verbose:
            logging.warning("Validating that analysis on the sample works on the whole file")
        is_valid, _, _ = validate(
            file_path=file_path,
            previous_analysis=analysis,
            num_rows=-1,
            encoding=analysis.get("encoding"),
            sep=analysis.get("separator"),
            sheet_name=analysis.get("sheet_name"),
            verbose=verbose,
            skipna=skipna,
        )
        if not is_valid:
            raise ValueError("Could not infer detected formats on the whole file")

    return analysis


def build_sample(table: pd.DataFrame) -> pd.DataFrame:
    """
    building a sample of MAX_ROWS_ANALYSIS rows that contains at least one representative of
    the min and max values of each column, and one case of NaN if the column contains any.
    """
    samples = []
    
    for col in table.columns:
        try:
            # Get min value row
            min_rows = table.loc[table[col] == table[col].dropna().min()]
            if len(min_rows) > 0:
                samples.append(min_rows.iloc[[0]])
        except (ValueError, IndexError):
            pass  # Skip if we can't get min value
            
        try:
            # Get max value row
            max_rows = table.loc[table[col] == table[col].dropna().max()]
            if len(max_rows) > 0:
                samples.append(max_rows.iloc[[0]])
        except (ValueError, IndexError):
            pass  # Skip if we can't get max value
            
        try:
            # Get NaN row if column has any
            nan_rows = table.loc[table[col].isna()]
            if len(nan_rows) > 0:
                samples.append(nan_rows.iloc[[0]])
        except (ValueError, IndexError):
            pass  # Skip if we can't get NaN value
    
    if samples:
        samples = pd.concat(samples, ignore_index=True)
        remaining_rows: int = MAX_ROWS_ANALYSIS - len(samples)
        if remaining_rows > 0:
            additional_sample = table.sample(n=remaining_rows, random_state=1)
            return pd.concat([samples, additional_sample], ignore_index=True)
        return samples
    else:
        # Fallback if no samples could be created
        return table.sample(n=min(MAX_ROWS_ANALYSIS, len(table)), random_state=1)
