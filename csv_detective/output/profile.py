from collections import defaultdict
import logging
from time import time

import pandas as pd

from csv_detective.detect_fields.other.float import float_casting
from csv_detective.utils import display_logs_depending_process_time, prevent_nan


def create_profile(
    table: pd.DataFrame,
    dict_cols_fields: dict,
    num_rows: int,
    limited_output: bool = True,
    verbose: bool = False,
) -> dict:
    if verbose:
        start = time()
        logging.info("Creating profile")
    map_python_types = {
        "string": str,
        "int": float,
        "float": float,
    }

    if num_rows > 0:
        raise ValueError("To create profiles num_rows has to be set to -1")
    safe_table = table.copy()
    if not limited_output:
        dict_cols_fields = {
            k: v[0] if v else {'python_type': 'string', 'format': 'string', 'score': 1.0}
            for k, v in dict_cols_fields.items()
        }
    dtypes = {
        k: map_python_types.get(v["python_type"], str)
        for k, v in dict_cols_fields.items()
    }
    for c in safe_table.columns:
        if dtypes[c] == float:
            safe_table[c] = safe_table[c].apply(
                lambda s: float_casting(s) if isinstance(s, str) else s
            )
    profile = defaultdict(dict)
    for c in safe_table.columns:
        if map_python_types.get(dict_cols_fields[c]["python_type"], str) in [
            float,
            int,
        ]:
            profile[c].update(
                min=prevent_nan(map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                    safe_table[c].min()
                )),
                max=prevent_nan(map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                    safe_table[c].max()
                )),
                mean=prevent_nan(map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                    safe_table[c].mean()
                )),
                std=prevent_nan(map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                    safe_table[c].std()
                )),
            )
        tops_bruts = (
            safe_table[safe_table[c].notna()][c]
            .value_counts(dropna=True)
            .reset_index()
            .iloc[:10]
            .to_dict(orient="records")
        )
        tops = []
        for tb in tops_bruts:
            tops.append({
                "count": tb["count"],
                "value": tb[c],
            })
        profile[c].update(
            tops=tops,
            nb_distinct=safe_table[c].nunique(),
            nb_missing_values=len(safe_table[c].loc[safe_table[c].isna()]),
        )
    if verbose:
        display_logs_depending_process_time(
            f"Created profile in {round(time() - start, 3)}s",
            time() - start,
        )
    return profile
