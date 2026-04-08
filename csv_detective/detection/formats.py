from collections import Counter, defaultdict

import numpy as np
import pandas as pd

from csv_detective.detection.variables import (
    detect_categorical_variable,
    # detect_continuous_variable,
)
from csv_detective.format import Format, FormatsManager
from csv_detective.formats.date import detect_strptime_format, detect_strptime_format_datetime
from csv_detective.output.utils import prepare_output_dict
from csv_detective.parsing.columns import (
    MAX_NUMBER_CATEGORICAL_VALUES,
    handle_empty_columns,
    test_col,
    test_col_chunks,
    test_label,
)

DATE_FORMAT_COVERAGE_THRESHOLD = 0.95


def _detect_date_formats_for_columns(
    analysis: dict,
    table: pd.DataFrame | None,
    col_values: dict[str, pd.Series] | None,
) -> None:
    columns = analysis.get("columns", {})
    for col_name, detection in columns.items():
        if isinstance(detection, list):
            # limited_output=False: list of detections, take the first date/datetime one
            detection = next(
                (d for d in detection if d.get("python_type") in ("date", "datetime")),
                None,
            )
            if detection is None:
                continue

        if detection.get("python_type") not in ("date", "datetime"):
            continue

        if col_values is not None and col_name in col_values:
            value_counts = col_values[col_name].dropna()
        elif table is not None and col_name in table.columns:
            value_counts = table[col_name].value_counts(dropna=True)
        else:
            detection["date_format"] = None
            continue

        detect_func = (
            detect_strptime_format
            if detection["python_type"] == "date"
            else detect_strptime_format_datetime
        )

        format_counts: Counter[str | None] = Counter()
        total = 0
        for val, count in value_counts.items():
            if not isinstance(val, str):
                continue
            fmt = detect_func(val)
            format_counts[fmt] += count
            total += count

        if total == 0:
            detection["date_format"] = None
            continue

        known_formats = [(fmt, count) for fmt, count in format_counts.items() if fmt is not None]
        known_formats.sort(key=lambda x: -x[1])
        known_total = sum(c for _, c in known_formats)

        if known_total / total >= DATE_FORMAT_COVERAGE_THRESHOLD and len(known_formats) <= 3:
            detection["date_format"] = [fmt for fmt, _ in known_formats]
        else:
            detection["date_format"] = None


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

    # Perform testing on labels
    scores_table_labels = test_label(analysis["header"], formats, limited_output, verbose=verbose)
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

    _detect_date_formats_for_columns(
        analysis,
        table=table if not in_chunks else None,
        col_values=col_values,
    )

    return analysis, col_values
