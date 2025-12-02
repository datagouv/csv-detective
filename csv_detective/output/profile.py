import logging
from collections import defaultdict
from time import time

import numpy as np
import pandas as pd

from csv_detective.formats.float import float_casting
from csv_detective.utils import cast_prevent_nan, display_logs_depending_process_time


def create_profile(
    table: pd.DataFrame,
    columns: dict,
    num_rows: int,
    limited_output: bool = True,
    cast_json: bool = True,
    verbose: bool = False,
    _col_values: dict[str, pd.Series] | None = None,
) -> dict:
    if verbose:
        start = time()
        logging.info("Creating profile")

    if num_rows > 0:
        raise ValueError("To create profiles num_rows has to be set to -1")
    if not limited_output:
        columns = {
            k: v[0] if v else {"python_type": "string", "format": "string", "score": 1.0}
            for k, v in columns.items()
        }
    # value_counts().reset_index() tries to insert a "count" column, and fails if it's already here
    _count_col = "count"
    while _count_col in table.columns:
        _count_col = "_" + _count_col
    profile = defaultdict(dict)
    for c in table.columns:
        # for numerical formats we want min, max, mean, std
        if columns[c]["python_type"] in ["float", "int"]:
            # if we have read the file in chunks we already have what we need
            if _col_values is None:
                # we locally cast the column to perform the operations,
                # using the same method as in cast_df
                cast_col = (
                    table[c].astype(pd.Int64Dtype())
                    if columns[c]["python_type"] == "int"
                    else table[c].apply(lambda x: float_casting(x) if isinstance(x, str) else pd.NA)
                )
                stats = {
                    "min": cast_prevent_nan(cast_col.min(), columns[c]["python_type"]),
                    "mean": cast_prevent_nan(cast_col.mean(), columns[c]["python_type"]),
                    "max": cast_prevent_nan(cast_col.max(), columns[c]["python_type"]),
                    "std": cast_prevent_nan(cast_col.std(), columns[c]["python_type"]),
                }
            else:
                cast_col = _col_values[c].reset_index()
                cast_col = cast_col.loc[cast_col[c].notna()]
                cast_col[c] = (
                    cast_col[c].astype(pd.Int64Dtype())
                    if columns[c]["python_type"] == "int"
                    else cast_col[c].apply(
                        lambda x: float_casting(x) if isinstance(x, str) else pd.NA
                    )
                )
                stats = {
                    "min": cast_prevent_nan(cast_col[c].min(), columns[c]["python_type"]),
                    "mean": cast_prevent_nan(
                        (cast_col[c] * cast_col["count"]).sum() / sum(cast_col["count"]),
                        columns[c]["python_type"],
                    ),
                    "max": cast_prevent_nan(cast_col[c].max(), columns[c]["python_type"]),
                }
                stats["std"] = cast_prevent_nan(
                    np.sqrt(
                        sum(cast_col["count"] * (cast_col[c] - stats["mean"]) ** 2)
                        / sum(cast_col["count"])
                    ),
                    columns[c]["python_type"],
                )
            profile[c].update(**stats)
            del cast_col
        # for all formats we want most frequent values, nb unique values and nb missing values
        tops_bruts = (
            (table[c].value_counts() if _col_values is None else _col_values[c].sort_values())
            .reset_index(name=_count_col)
            .iloc[:10]
            .to_dict(orient="records")
        )
        profile[c].update(
            tops=[
                {
                    "count": tb[_count_col],
                    "value": tb[c],
                }
                for tb in tops_bruts
            ],
            nb_distinct=(
                (
                    table[c].nunique()
                    if columns[c]["python_type"] != "json" or not cast_json
                    # a column containing cast json is not serializable
                    else table[c].astype(str).nunique()
                )
                if _col_values is None
                else len(_col_values)
            ),
            nb_missing_values=(
                len(table[c].loc[table[c].isna()])
                if _col_values is None
                else (_col_values[c].loc[pd.NA] if pd.NA in _col_values[c].index else 0)
            ),
        )
    if verbose:
        display_logs_depending_process_time(
            f"Created profile in {round(time() - start, 3)}s",
            time() - start,
        )
    del _col_values
    return profile
