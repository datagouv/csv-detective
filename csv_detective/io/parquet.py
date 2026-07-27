from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO

import pandas as pd
import requests
from rugo import parquet as rugo_parquet

from csv_detective.utils import is_url

RUGO_TYPE_TO_PYTHON: dict[str, str] = {
    "varchar": "string",
    "int64": "int",
    "int32": "int",
    "float64": "float",
    "float32": "float",
    "boolean": "bool",
    "date32[day]": "date",
    "timestamp[ns]": "datetime_naive",
    "timestamp[us]": "datetime_naive",
    "timestamp[ms]": "datetime_naive",
    "binary": "binary",
}


@dataclass(frozen=True)
class SchemaColumn:
    name: str
    logical_type: str
    physical_type: str
    nullable: bool


def _decode_column_name(name: str | bytes) -> str:
    if isinstance(name, bytes):
        return name.decode("utf-8")
    return name


def rugo_logical_type_to_python(logical_type: str) -> str:
    if logical_type.startswith("array"):
        return "json"
    if logical_type.startswith("timestamp[") and "," in logical_type:
        return "datetime_aware"
    if logical_type in RUGO_TYPE_TO_PYTHON:
        return RUGO_TYPE_TO_PYTHON[logical_type]
    for pattern, python_type in (
        (r"^timestamp\[", "datetime_naive"),
        (r"^decimal", "float"),
        (r"^struct", "json"),
        (r"^map", "json"),
    ):
        if re.search(pattern, logical_type):
            return python_type
    raise ValueError(f"Unknown Rugo logical type: {logical_type}")


def _load_source(file_path: str) -> str | bytes:
    if is_url(file_path):
        response = requests.get(file_path, allow_redirects=True)
        response.raise_for_status()
        return response.content
    return file_path


def _morsel_to_dataframe(morsel) -> pd.DataFrame:
    column_names = [_decode_column_name(name) for name in morsel.column_names]
    data = {
        column_name: morsel.column(raw_name).to_pylist()
        for column_name, raw_name in zip(column_names, morsel.column_names, strict=True)
    }
    return pd.DataFrame(data)


def _iter_morsel_slices(morsel, batch_size: int) -> Iterator[pd.DataFrame]:
    total_rows = len(morsel)
    if total_rows == 0:
        yield pd.DataFrame(columns=[_decode_column_name(name) for name in morsel.column_names])
        return
    for start in range(0, total_rows, batch_size):
        end = min(start + batch_size, total_rows)
        slice_morsel = morsel.slice(start, end - start)
        yield _morsel_to_dataframe(slice_morsel)


class ParquetTable:
    """Parquet file handle backed by Rugo metadata and streaming reads."""

    def __init__(self, source: str | bytes):
        self._source = source
        self._metadata = rugo_parquet.read_metadata(source)

    @property
    def schema_columns(self) -> tuple[SchemaColumn, ...]:
        return tuple(
            SchemaColumn(
                name=column.name,
                logical_type=column.logical_type,
                physical_type=column.physical_type,
                nullable=column.nullable,
            )
            for column in self._metadata.schema_columns
        )

    @property
    def column_names(self) -> list[str]:
        return [column.name for column in self.schema_columns]

    @property
    def num_rows(self) -> int:
        return self._metadata.num_rows

    def iter_batches(self, batch_size: int) -> Iterator[pd.DataFrame]:
        with rugo_parquet.read_parquet(self._source) as reader:
            for morsel in reader:
                yield from _iter_morsel_slices(morsel, batch_size)

    def iter_dataframes(self, batch_size: int) -> Iterator[pd.DataFrame]:
        yield from self.iter_batches(batch_size)

    def read_all(self) -> pd.DataFrame:
        batches = list(self.iter_batches(batch_size=self.num_rows or 1))
        if not batches:
            return pd.DataFrame(columns=self.column_names)
        return pd.concat(batches, ignore_index=True)


def load_parquet(file_path: str) -> ParquetTable:
    return ParquetTable(_load_source(file_path))


def load_parquet_from_buffer(buffer: BinaryIO | BytesIO) -> ParquetTable:
    buffer.seek(0)
    return ParquetTable(buffer.read())
