import json
from datetime import date, datetime
from time import time
from typing import Iterator

import pandas as pd

from csv_detective.formats.binary import binary_casting
from csv_detective.formats.booleen import bool_casting
from csv_detective.formats.date import date_casting
from csv_detective.formats.float import float_casting
from csv_detective.parsing.csv import CHUNK_SIZE
from csv_detective.utils import display_logs_depending_process_time


def cast(value: str, _type: str) -> str | float | bool | date | datetime | bytes | None:
    if not isinstance(value, str) or not value:
        # None is the current default value in hydra, should we keep this?
        return None
    match _type:
        case "float":
            return float_casting(value)
        case "bool":
            return bool_casting(value)
        case "json":
            # in hydra json are given to postgres as strings, conversion is done by postgres
            return json.loads(value)
        case "date":
            _date = date_casting(value)
            return _date.date() if _date else None
        case "datetime":
            return date_casting(value)
        case "binary":
            return binary_casting(value)
        case _:
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


def cast_df_chunks(
    df: pd.DataFrame,
    analysis: dict,
    file_path: str,
    cast_json: bool = True,
    verbose: bool = False,
) -> Iterator[pd.DataFrame]:
    if analysis.get("engine") or analysis["total_lines"] <= CHUNK_SIZE:
        # the file is loaded in one chunk, so returning the cast df
        yield cast_df(
            df=df,
            columns=analysis["columns"],
            cast_json=cast_json,
            verbose=verbose,
        )
    else:
        # loading the csv in chunks using the analysis
        chunks = pd.read_csv(
            file_path,
            dtype=str,
            sep=analysis["separator"],
            encoding=analysis["encoding"],
            skiprows=analysis["header_row_idx"],
            compression=analysis.get("compression"),
            chunksize=CHUNK_SIZE,
        )
        for chunk in chunks:
            yield cast_df(
                df=chunk,
                columns=analysis["columns"],
                cast_json=cast_json,
                verbose=verbose,
            )
