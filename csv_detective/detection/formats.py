from collections import defaultdict
from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

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
    test_parquet_cols,
)


def _winning_format(detections: dict | list[dict], limited_output: bool) -> str:
    """The format that won for a column, whatever shape prepare_output_dict produced."""
    if limited_output:
        return detections["format"]
    return max(detections, key=lambda d: d["score"], default={"format": "string"})["format"]


def _infer_column_formats(
    formats: dict[str, Format],
    scores_table_fields: pd.DataFrame,
    values_of: Callable[[str], Iterable[Any]],
) -> dict[str, dict[str, str]]:
    """Runs the column-wide inference of the formats that have one, and zeroes those that fail.

    A format that cannot say how to read the whole column has not detected it: the value-by-value
    test only says that each value looks valid on its own, not that a single format reads them all.
    """
    inferable = [
        (label, fmt)
        for label, fmt in formats.items()
        if fmt.infer is not None
        # a format the user made tolerant cannot be pinned down: asking for a single format that
        # reads every value contradicts the proportion of failures they just allowed
        and fmt.proportion == 1
        and label in scores_table_fields.index
    ]
    inferred: dict[str, dict[str, str]] = {}
    for col in scores_table_fields.columns:
        candidates = [
            (label, fmt) for label, fmt in inferable if scores_table_fields.loc[label, col]
        ]
        if not candidates:
            continue
        values = list(values_of(col))
        for label, fmt in candidates:
            column_format = fmt.infer(values)
            if column_format is None:
                scores_table_fields.loc[label, col] = 0.0
            else:
                inferred.setdefault(col, {})[label] = column_format
    return inferred


def detect_formats(
    table: pd.DataFrame | pq.ParquetFile,
    analysis: dict,
    file_path: str,
    tags: list[str] | None = None,
    limited_output: bool = True,
    skipna: bool = True,
    custom_proportions: float | int | dict[str, float | int] | None = None,
    na_values: list[str] | None = None,
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
    if analysis.get("engine") == "parquet":
        # parquet has its own process as typed columns allow shortcuts
        scores_table_fields, analysis, col_values = test_parquet_cols(
            table=table,
            formats=formats,
            analysis=analysis,
            limited_output=limited_output,
            skipna=skipna,
            verbose=verbose,
        )
    elif not in_chunks:
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
            na_values=na_values,
            verbose=verbose,
        )
    if analysis.get("engine") == "parquet":
        # parquet types columns itself, so there is nothing to infer and nothing to read the
        # format with: cast_df_chunks hands the file over to pandas untouched
        inferred_formats: dict[str, dict[str, str]] = {}
    else:
        inferred_formats = _infer_column_formats(
            formats,
            scores_table_fields,
            (lambda col: table[col].dropna().unique())
            if col_values is None
            else (lambda col: col_values[col].index.dropna()),
        )
    analysis["columns_fields"] = prepare_output_dict(scores_table_fields, limited_output)
    analysis["unique_values"] = {}
    if col_values is None:
        for col in table.columns:
            if _winning_format(analysis["columns_fields"][col], limited_output) == "json" and all(
                value.startswith("[") for value in table[col]
            ):
                unique = extract_unique_from_multicat(table[col])
                if unique is not None:
                    analysis["unique_values"][col] = unique
            elif table[col].nunique() <= MAX_NUMBER_CATEGORICAL_VALUES:
                analysis["unique_values"][col] = list(table[col].dropna().unique())
    else:
        for col in col_values.keys():
            if _winning_format(analysis["columns_fields"][col], limited_output) == "json" and all(
                value.startswith("[") for value in col_values[col].index
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

    for col_name, detections in analysis["columns"].items():
        for detection in [detections] if limited_output else detections:
            column_format = inferred_formats.get(col_name, {}).get(detection["format"])
            if column_format is not None:
                detection["date_format"] = column_format

    return analysis, col_values
