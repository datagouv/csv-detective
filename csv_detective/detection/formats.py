from collections import defaultdict

import numpy as np
import pandas as pd

from csv_detective.detection.variables import (
    detect_categorical_variable,
    # detect_continuous_variable,
)
from csv_detective.format import Format, FormatsManager
from csv_detective.output.utils import (
    extract_unique_from_multicat,
    prepare_output_dict,
)
from csv_detective.parsing.columns import (
    MAX_NUMBER_CATEGORICAL_VALUES,
    handle_empty_columns,
    test_col,
    test_col_chunks,
    test_label,
)


def detect_formats(
    table: pd.DataFrame,
    analysis: dict,
    file_path: str,
    tags: list[str] | None = None,
    limited_output: bool = True,
    skipna: bool = True,
    custom_proportions: float | int | dict[str, float | int] | None = None,
    verbose: bool = False,
) -> tuple[dict, dict[str, pd.Series] | None]:
    fmtm = FormatsManager(custom_proportions=custom_proportions)
    in_chunks = analysis.get("total_lines") is None

    # list testing to be performed
    formats: dict[str, Format] = (
        fmtm.get_formats_from_tags(tags) if tags is not None else fmtm.formats
    )

    # if no testing then return
    if len(formats) == 0:
        return analysis, None

    # Perform testing on fields
    if not in_chunks:
        # table is small enough to be tested in one go
        scores_table_fields = test_col(
            table=table,
            formats=formats,
            limited_output=limited_output,
            skipna=skipna,
            verbose=verbose,
        )
        handle_empty_columns(scores_table_fields)
        res_categorical, _ = detect_categorical_variable(
            table,
            max_number_categorical_values=MAX_NUMBER_CATEGORICAL_VALUES,
            verbose=verbose,
        )
        analysis["categorical"] = res_categorical
        col_values = None
    else:
        scores_table_fields, analysis, col_values = test_col_chunks(
            table=table,
            file_path=file_path,
            analysis=analysis,
            formats=formats,
            limited_output=limited_output,
            skipna=skipna,
            verbose=verbose,
        )
    analysis["columns_fields"] = prepare_output_dict(scores_table_fields, limited_output)
    analysis["unique_values"] = {}
    if not in_chunks:
        for col in table.columns:
            if (
                analysis["columns_fields"][col]["format"] == "json" 
                and all(value.startswith("[") for value in table[col])
            ):
                unique = extract_unique_from_multicat(table[col])
                if unique is not None:
                    analysis["unique_values"][col] = unique
            elif table[col].nunique() <= MAX_NUMBER_CATEGORICAL_VALUES:
                analysis["unique_values"][col] = list(table[col].dropna().unique())
    else:
        for col in col_values.keys():
            if (
                analysis["columns_fields"][col]["format"] == "json" 
                and all(value.startswith("[") for value in col_values[col].index)
            ):
                unique = extract_unique_from_multicat(col_values[col].index.to_series())
                if unique is not None:
                    analysis["unique_values"][col] = unique
            elif len(col_values[col]) <= MAX_NUMBER_CATEGORICAL_VALUES:
                analysis["unique_values"][col] = list(col_values[col].index.dropna())

    # Perform testing on labels
    scores_table_labels = test_label(analysis["header"], formats, verbose=verbose)
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
        f for f in fmtm.get_formats_with_mandatory_label() if f in scores_table.index
    ]
    scores_table.loc[formats_with_mandatory_label, :] = np.where(
        scores_table_labels.loc[formats_with_mandatory_label, :],
        scores_table.loc[formats_with_mandatory_label, :],
        0,
    )
    analysis["columns"] = prepare_output_dict(scores_table, limited_output)

    if not limited_output:
        for detection_method in ["columns_fields", "columns_labels", "columns"]:
            analysis[detection_method] = {
                col_name: [
                    {
                        "python_type": (
                            "string"
                            if detection["format"] == "string"
                            else fmtm.formats[detection["format"]].python_type
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
                    "python_type": (
                        "string"
                        if detection["format"] == "string"
                        else fmtm.formats[detection["format"]].python_type
                    ),
                    **detection,
                }
                for col_name, detection in analysis[detection_method].items()
            }

        # Add detection with formats as keys
        analysis["formats"] = defaultdict(list)
        for header, col_metadata in analysis["columns"].items():
            analysis["formats"][col_metadata["format"]].append(header)

    return analysis, col_values
