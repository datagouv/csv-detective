from __future__ import annotations

import csv
import gzip
from collections.abc import Iterator
from io import BytesIO, TextIOWrapper
from typing import BinaryIO, TextIO

import pandas as pd

from csv_detective.utils import is_url

DEFAULT_NA_VALUES = list(pd._libs.parsers.STR_NA_VALUES)


def _normalize_column_names(names: list[str]) -> list[str]:
    return [name if name else f"Unnamed: {idx}" for idx, name in enumerate(names)]


def _get_null_values(
    na_values: list[str] | str | None,
    keep_default_na: bool,
) -> set[str]:
    values: list[str] = []
    if keep_default_na:
        values.extend(DEFAULT_NA_VALUES)
    if na_values is None:
        return set(values)
    if isinstance(na_values, list):
        values.extend(na_values)
    else:
        values.append(na_values)
    return set(values)


def _read_header_names(file_obj: TextIO, sep: str, skiprows: int | None) -> list[str]:
    for _ in range(skiprows or 0):
        file_obj.readline()
    header_line = file_obj.readline()
    return _normalize_column_names(next(csv.reader([header_line], delimiter=sep)))


def _rows_to_dataframe(
    rows: list[list[str]],
    column_names: list[str],
    null_values: set[str],
) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=column_names).astype(str)
    width = len(column_names)
    padded_rows = [row[:width] + [""] * max(0, width - len(row)) for row in rows]
    dataframe = pd.DataFrame(padded_rows, columns=column_names, dtype=object)
    if null_values:
        dataframe = dataframe.replace(list(null_values), pd.NA)
    for column in dataframe.columns:
        dataframe[column] = dataframe[column].map(
            lambda value: pd.NA if pd.isna(value) else str(value)
        )
    return dataframe


def _open_text_file(
    filepath_or_buffer: str | TextIO | BinaryIO,
    encoding: str | None,
    compression: str | None,
) -> tuple[TextIO, bool]:
    if isinstance(filepath_or_buffer, str):
        if compression == "gzip" or filepath_or_buffer.endswith(".gz"):
            return (
                gzip.open(filepath_or_buffer, mode="rt", encoding=encoding or "utf-8", newline=""),
                True,
            )
        return open(filepath_or_buffer, encoding=encoding or "utf-8", newline=""), True

    filepath_or_buffer.seek(0)
    if isinstance(filepath_or_buffer, (BytesIO, BinaryIO)) and not isinstance(
        filepath_or_buffer, TextIO
    ):
        text_file = TextIOWrapper(filepath_or_buffer, encoding=encoding or "utf-8", newline="")
        return text_file, False
    return filepath_or_buffer, False


def _iter_csv_rows(
    file_obj: TextIO,
    sep: str,
    skiprows: int | None,
    column_names: list[str],
) -> Iterator[list[str]]:
    for _ in range(skiprows or 0):
        file_obj.readline()
    file_obj.readline()  # header row already parsed separately
    reader = csv.reader(file_obj, delimiter=sep)
    for row in reader:
        yield row


def _read_csv_pandas(
    filepath_or_buffer: str | TextIO | BinaryIO,
    *,
    sep: str,
    dtype: type | str | None,
    encoding: str | None,
    skiprows: int | None,
    nrows: int | None,
    chunksize: int | None,
    compression: str | None,
    na_values: list[str] | str | None,
    keep_default_na: bool,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    return pd.read_csv(
        filepath_or_buffer,
        sep=sep,
        dtype=dtype,
        encoding=encoding,
        skiprows=skiprows,
        nrows=nrows,
        chunksize=chunksize,
        compression=compression,
        na_values=na_values,
        keep_default_na=keep_default_na,
        engine="c",
    )


def _read_csv_stdlib(
    filepath_or_buffer: str | TextIO | BinaryIO,
    *,
    sep: str,
    encoding: str | None,
    skiprows: int | None,
    nrows: int | None,
    chunksize: int | None,
    compression: str | None,
    na_values: list[str] | str | None,
    keep_default_na: bool,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    file_obj, must_close = _open_text_file(filepath_or_buffer, encoding, compression)
    try:
        column_names = _read_header_names(file_obj, sep, skiprows)
        file_obj.seek(0)
        null_values = _get_null_values(na_values, keep_default_na)
        row_iterator = _iter_csv_rows(file_obj, sep, skiprows, column_names)

        def _consume(max_rows: int) -> pd.DataFrame:
            rows = []
            for _ in range(max_rows):
                try:
                    rows.append(next(row_iterator))
                except StopIteration:
                    break
            return _rows_to_dataframe(rows, column_names, null_values)

        if chunksize is not None:

            def _chunk_iterator() -> Iterator[pd.DataFrame]:
                try:
                    while True:
                        chunk = _consume(chunksize)
                        if chunk.empty:
                            break
                        yield chunk
                finally:
                    if must_close:
                        file_obj.close()

            return _chunk_iterator()

        try:
            limit = nrows if nrows is not None else None
            if limit is None:
                rows = list(row_iterator)
                return _rows_to_dataframe(rows, column_names, null_values)
            return _consume(limit)
        finally:
            if must_close:
                file_obj.close()
    except Exception:
        if must_close:
            file_obj.close()
        raise


def read_csv(
    filepath_or_buffer: str | TextIO | BinaryIO,
    *,
    sep: str = ",",
    dtype: type | str | None = str,
    encoding: str | None = None,
    skiprows: int | None = None,
    nrows: int | None = None,
    chunksize: int | None = None,
    compression: str | None = None,
    na_values: list[str] | str | None = None,
    keep_default_na: bool = True,
    **kwargs,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    if kwargs:
        raise TypeError(f"Unsupported read_csv arguments: {', '.join(sorted(kwargs))}")

    if isinstance(filepath_or_buffer, str) and is_url(filepath_or_buffer):
        return _read_csv_pandas(
            filepath_or_buffer,
            sep=sep,
            dtype=dtype,
            encoding=encoding,
            skiprows=skiprows,
            nrows=nrows,
            chunksize=chunksize,
            compression=compression,
            na_values=na_values,
            keep_default_na=keep_default_na,
        )

    if compression not in (None, "infer", "gzip") and not (
        isinstance(filepath_or_buffer, str) and filepath_or_buffer.endswith(".gz")
    ):
        return _read_csv_pandas(
            filepath_or_buffer,
            sep=sep,
            dtype=dtype,
            encoding=encoding,
            skiprows=skiprows,
            nrows=nrows,
            chunksize=chunksize,
            compression=compression,
            na_values=na_values,
            keep_default_na=keep_default_na,
        )

    return _read_csv_stdlib(
        filepath_or_buffer,
        sep=sep,
        encoding=encoding,
        skiprows=skiprows,
        nrows=nrows,
        chunksize=chunksize,
        compression=compression,
        na_values=na_values,
        keep_default_na=keep_default_na,
    )
