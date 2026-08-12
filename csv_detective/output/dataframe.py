import json
from datetime import date, datetime
from functools import partial
from time import time
from typing import Iterator

import pandas as pd
import pyarrow.parquet as pq

from csv_detective.formats.binary import binary_casting
from csv_detective.formats.bool import bool_casting
from csv_detective.formats.date import date_casting, parse
from csv_detective.formats.float import float_casting
from csv_detective.parsing.csv import CHUNK_SIZE
from csv_detective.utils import display_logs_depending_process_time


def date_from(value: str, date_format: str | None) -> datetime | None:
    if date_format is None:
        # No format to read the value with. Unreachable from an analysis this version produced
        # for a date column, but reachable from one it did not: validate_then_detect casts with
        # the caller's previous_analysis when it is still valid, and those were generated before
        # the inference existed. It is also the path of datetime_rfc822, which has no inference,
        # and of columns detected with a tolerant custom proportion.
        # This is what keeps dateutil/dateparser as dependencies; dropping it means requiring
        # every stored analysis to be regenerated.
        return date_casting(value)
    return parse(value, date_format)


def cast(
    value: str,
    _type: str,
    date_format: str | None = None,
) -> str | int | float | bool | date | datetime | bytes | None:
    if not isinstance(value, str) or value in pd._libs.parsers.STR_NA_VALUES:
        # STR_NA_VALUES are directly ingested as NaN by pandas, we avoid trying to cast them (into int for instance)
        return None
    match _type:
        case "string":
            # not used here, convenience for external use (cc hydra)
            return value
        case "int":
            return int(value)
        case "float":
            return float_casting(value)
        case "bool":
            return bool_casting(value)
        case "json":
            # in hydra json are given to postgres as strings, conversion is done by postgres
            return json.loads(value)
        case "date":
            _date = date_from(value, date_format)
            return _date.date() if _date else None
        case "datetime":
            return date_from(value, date_format)
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
            df[col_name] = df[col_name].apply(
                partial(
                    cast,
                    _type=detection["python_type"],
                    date_format=detection.get("date_format"),
                )
            )
    if verbose:
        display_logs_depending_process_time(
            f"Casting columns completed in {round(time() - start, 3)}s",
            time() - start,
        )
    return df


def cast_df_chunks(
    df: pd.DataFrame | pq.ParquetFile,
    analysis: dict,
    file_path: str,
    cast_json: bool = True,
    na_values: list[str] | None = None,
    verbose: bool = False,
) -> Iterator[pd.DataFrame]:
    if analysis.get("engine") or analysis["total_lines"] <= CHUNK_SIZE:
        # the file is loaded in one chunk, so returning the cast df
        if analysis.get("engine") == "parquet":
            yield pd.read_parquet(file_path)
        else:
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
            na_values=na_values,
        )
        for chunk in chunks:
            yield cast_df(
                df=chunk,
                columns=analysis["columns"],
                cast_json=cast_json,
                verbose=verbose,
            )
