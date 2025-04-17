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
from csv_detective.parsing.columns import test_col, test_label


def detect_formats(
    table: pd.DataFrame,
    analysis: dict,
    user_input_tests: Union[str, list[str]] = "ALL",
    limited_output: bool = True,
    skipna: bool = True,
    verbose: bool = False,
):

    if table.empty:
        res_categorical = []
        # res_continuous = []
    else:
        # Detects columns that are categorical
        res_categorical, categorical_mask = detect_categorical_variable(table, verbose=verbose)
        res_categorical = list(res_categorical)
        # Detect columns that are continuous (we already know the categorical) :
        # we don't need this for now, cuts processing time
        # res_continuous = list(
        #     detect_continuous_variable(table.iloc[:, ~categorical_mask.values], verbose=verbose)
        # )

    analysis.update({
        "categorical": res_categorical,
        # "continuous": res_continuous,
    })

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
    return analysis
