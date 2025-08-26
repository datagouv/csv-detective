import logging
from collections import defaultdict
from time import time

import pandas as pd

from csv_detective.detect_fields.other.float import float_casting
from csv_detective.utils import cast_prevent_nan, display_logs_depending_process_time


def create_profile(
    table: pd.DataFrame,
    columns: dict,
    num_rows: int,
    limited_output: bool = True,
    cast_json: bool = True,
    verbose: bool = False,
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
    profile = defaultdict(dict)
    for c in table.columns:
        # for numerical formats we want min, max, mean, std
        if columns[c]["python_type"] in ["float", "int"]:
            # we locally cast the column to perform the operations, using the same method as in cast_df
            cast_col = (
                table[c].astype(pd.Int64Dtype())
                if columns[c]["python_type"] == "int"
                else table[c].apply(lambda x: float_casting(x) if isinstance(x, str) else pd.NA)
            )
            profile[c].update(
                min=cast_prevent_nan(cast_col.min(), columns[c]["python_type"]),
                max=cast_prevent_nan(cast_col.max(), columns[c]["python_type"]),
                mean=cast_prevent_nan(cast_col.mean(), columns[c]["python_type"]),
                std=cast_prevent_nan(cast_col.std(), columns[c]["python_type"]),
            )
            del cast_col
        # for all formats we want most frequent values, nb unique values and nb missing values
        tops_bruts = (
            table.loc[table[c].notna(), c]
            .value_counts()
            .reset_index()
            .iloc[:10]
            .to_dict(orient="records")
        )
        profile[c].update(
            tops=[
                {
                    "count": tb["count"],
                    "value": tb[c],
                }
                for tb in tops_bruts
            ],
            nb_distinct=(
                table[c].nunique()
                if columns[c]["python_type"] != "json" or not cast_json
                # a column containing cast json is not serializable
                else table[c].astype(str).nunique()
            ),
            nb_missing_values=len(table[c].loc[table[c].isna()]),
        )
    if verbose:
        display_logs_depending_process_time(
            f"Created profile in {round(time() - start, 3)}s",
            time() - start,
        )
    return profile
