import json
from datetime import date, datetime
from time import time
from typing import Optional, Union

import pandas as pd

from csv_detective.detect_fields.other.booleen import bool_casting
from csv_detective.detect_fields.other.float import float_casting
from csv_detective.detect_fields.temp.date import date_casting
from csv_detective.utils import display_logs_depending_process_time


def cast(value: str, _type: str) -> Optional[Union[str, float, bool, date, datetime]]:
    if not isinstance(value, str) or not value:
        # None is the current default value in hydra, should we keep this?
        return None
    if _type == "float":
        return float_casting(value)
    if _type == "bool":
        return bool_casting(value)
    if _type == "json":
        # in hydra json are given to postgres as strings, conversion is done by postgres
        return json.loads(value)
    if _type == "date":
        _date = date_casting(value)
        return _date.date() if _date else None
    if _type == "datetime":
        return date_casting(value)
    raise ValueError(f"Unknown type `{_type}`")


def cast_df(
    df: pd.DataFrame, columns: dict, cast_json: bool = True, verbose: bool = False
) -> pd.DataFrame:
    # for efficiency this modifies the dataframe in place as we don't need it anymore afterwards
    if verbose:
        start = time()
    for col_name, detection in columns.items():
        if detection["python_type"] == "string" or (
            detection["python_type"] == "json" and not cast_json
        ):
            # no change if detected type is string
            continue
        elif detection["python_type"] == "int":
            # to allow having ints and NaN in the same column
            df[col_name] = df[col_name].astype(pd.Int64Dtype())
        else:
            df[col_name] = df[col_name].apply(lambda col: cast(col, _type=detection["python_type"]))
    if verbose:
        display_logs_depending_process_time(
            f"Casting columns completed in {round(time() - start, 3)}s",
            time() - start,
        )
    return df
