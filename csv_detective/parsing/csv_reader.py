import csv
from collections.abc import Iterator
from io import BytesIO, TextIOWrapper
from typing import BinaryIO, TextIO

import pandas as pd
import pyarrow as pa
import pyarrow.csv as pacsv

from csv_detective.utils import is_url

CSV_ENGINE = "pyarrow"


def _get_null_values(
    na_values: list[str] | str | None,
    keep_default_na: bool,
) -> list[str]:
    values: list[str] = []
    if keep_default_na:
        values.extend(pd._libs.parsers.STR_NA_VALUES)
    if na_values is None:
        return values
    if isinstance(na_values, list):
        values.extend(na_values)
    else:
        values.append(na_values)
    return list(dict.fromkeys(values))


def _normalize_column_names(names: list[str]) -> list[str]:
    return [name if name else f"Unnamed: {idx}" for idx, name in enumerate(names)]


def _read_header_names(
    filepath_or_buffer: str | TextIO | BinaryIO,
    sep: str,
    skiprows: int | None,
    encoding: str | None,
) -> list[str]:
    if isinstance(filepath_or_buffer, str):
        with open(filepath_or_buffer, encoding=encoding or "utf-8", newline="") as file:
            return _read_header_from_textio(file, sep, skiprows)
    filepath_or_buffer.seek(0)
    position = filepath_or_buffer.tell()
    try:
        if isinstance(filepath_or_buffer, (BytesIO, BinaryIO)) and not isinstance(
            filepath_or_buffer, TextIO
        ):
            text_file = TextIOWrapper(filepath_or_buffer, encoding=encoding or "utf-8", newline="")
            try:
                return _read_header_from_textio(text_file, sep, skiprows)
            finally:
                text_file.detach()
        return _read_header_from_textio(filepath_or_buffer, sep, skiprows)
    finally:
        filepath_or_buffer.seek(position)


def _read_header_from_textio(file: TextIO, sep: str, skiprows: int | None) -> list[str]:
    for _ in range(skiprows or 0):
        file.readline()
    header_line = file.readline()
    return _normalize_column_names(next(csv.reader([header_line], delimiter=sep)))


def _prepare_source(
    filepath_or_buffer: str | TextIO | BinaryIO,
    encoding: str | None,
) -> str | BytesIO:
    if isinstance(filepath_or_buffer, str):
        return filepath_or_buffer
    filepath_or_buffer.seek(0)
    content = filepath_or_buffer.read()
    if isinstance(content, str):
        return BytesIO(content.encode(encoding or "utf-8"))
    return BytesIO(content)


def _build_read_options(
    skiprows: int | None,
    column_names: list[str],
    encoding: str | None,
) -> pacsv.ReadOptions:
    # When column names are provided explicitly, also skip the header row itself.
    return pacsv.ReadOptions(
        skip_rows=(skiprows or 0) + 1,
        column_names=column_names,
        encoding=encoding or "utf-8",
        autogenerate_column_names=False,
    )


def _build_convert_options(
    column_names: list[str],
    na_values: list[str] | str | None,
    keep_default_na: bool,
) -> pacsv.ConvertOptions:
    return pacsv.ConvertOptions(
        column_types={name: pa.string() for name in column_names},
        strings_can_be_null=True,
        null_values=_get_null_values(na_values, keep_default_na),
        include_missing_columns=True,
    )


def _table_to_dataframe(table: pa.Table) -> pd.DataFrame:
    dataframe = table.to_pandas(strings_to_categorical=False)
    for column in dataframe.columns:
        dataframe[column] = dataframe[column].astype(str)
    return dataframe


def _iter_pyarrow_chunks(
    source: str | BytesIO,
    sep: str,
    skiprows: int | None,
    column_names: list[str],
    encoding: str | None,
    na_values: list[str] | str | None,
    keep_default_na: bool,
    chunksize: int,
) -> Iterator[pd.DataFrame]:
    read_options = _build_read_options(skiprows, column_names, encoding)
    parse_options = pacsv.ParseOptions(delimiter=sep)
    convert_options = _build_convert_options(column_names, na_values, keep_default_na)
    reader = pacsv.open_csv(
        source,
        read_options=read_options,
        parse_options=parse_options,
        convert_options=convert_options,
    )

    buffered_batches: list[pa.RecordBatch] = []
    buffered_rows = 0
    while True:
        try:
            batch = reader.read_next_batch()
        except StopIteration:
            break
        buffered_batches.append(batch)
        buffered_rows += batch.num_rows
        while buffered_rows >= chunksize:
            table = pa.Table.from_batches(buffered_batches)
            yield _table_to_dataframe(table.slice(0, chunksize))
            table = table.slice(chunksize)
            buffered_batches = table.to_batches()
            buffered_rows = table.num_rows

    if buffered_batches:
        yield _table_to_dataframe(pa.Table.from_batches(buffered_batches))


def _read_pyarrow_limited_rows(
    source: str | BytesIO,
    sep: str,
    skiprows: int | None,
    column_names: list[str],
    encoding: str | None,
    na_values: list[str] | str | None,
    keep_default_na: bool,
    nrows: int,
) -> pd.DataFrame:
    read_options = _build_read_options(skiprows, column_names, encoding)
    parse_options = pacsv.ParseOptions(delimiter=sep)
    convert_options = _build_convert_options(column_names, na_values, keep_default_na)
    reader = pacsv.open_csv(
        source,
        read_options=read_options,
        parse_options=parse_options,
        convert_options=convert_options,
    )

    buffered_batches: list[pa.RecordBatch] = []
    buffered_rows = 0
    while buffered_rows < nrows:
        try:
            batch = reader.read_next_batch()
        except StopIteration:
            break
        buffered_batches.append(batch)
        buffered_rows += batch.num_rows

    if not buffered_batches:
        return _table_to_dataframe(pa.table({name: pa.array([], type=pa.string()) for name in column_names}))

    table = pa.Table.from_batches(buffered_batches)
    return _table_to_dataframe(table.slice(0, nrows))


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
    engine: str = CSV_ENGINE,
    **kwargs,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    if kwargs:
        raise TypeError(f"Unsupported read_csv arguments: {', '.join(sorted(kwargs))}")
    if engine != "pyarrow":
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
            engine=engine,
        )

    if isinstance(filepath_or_buffer, str) and is_url(filepath_or_buffer):
        # pandas handles URL fetching (including urllib mocks in tests).
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

    if compression not in (None, "infer"):
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

    column_names = _read_header_names(filepath_or_buffer, sep, skiprows, encoding)
    source = _prepare_source(filepath_or_buffer, encoding)

    if chunksize is not None:
        return _iter_pyarrow_chunks(
            source,
            sep,
            skiprows,
            column_names,
            encoding,
            na_values,
            keep_default_na,
            chunksize,
        )
    if nrows is not None:
        return _read_pyarrow_limited_rows(
            source,
            sep,
            skiprows,
            column_names,
            encoding,
            na_values,
            keep_default_na,
            nrows,
        )

    read_options = _build_read_options(skiprows, column_names, encoding)
    parse_options = pacsv.ParseOptions(delimiter=sep)
    convert_options = _build_convert_options(column_names, na_values, keep_default_na)
    table = pacsv.read_csv(
        source,
        read_options=read_options,
        parse_options=parse_options,
        convert_options=convert_options,
    )
    return _table_to_dataframe(table)
