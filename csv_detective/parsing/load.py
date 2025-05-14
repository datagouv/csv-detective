from io import BytesIO, StringIO
from typing import Optional, Union

import pandas as pd
import requests

from csv_detective.detection.columns import detect_heading_columns, detect_trailing_columns
from csv_detective.detection.encoding import detect_encoding
from csv_detective.detection.engine import (
    COMPRESSION_ENGINES,
    EXCEL_ENGINES,
    detect_engine,
)
from csv_detective.detection.headers import detect_headers
from csv_detective.detection.separator import detect_separator
from csv_detective.utils import is_url
from .compression import unzip
from .csv import parse_csv
from .excel import (
    XLS_LIKE_EXT,
    parse_excel,
)


def load_file(
    file_path: str,
    num_rows: int = 500,
    encoding: Optional[str] = None,
    sep: Optional[str] = None,
    verbose: bool = False,
    sheet_name: Optional[Union[str, int]] = None,
) -> tuple[pd.DataFrame, dict]:
    file_name = file_path.split('/')[-1]
    engine = None
    if '.' not in file_name or not file_name.endswith("csv"):
        # file has no extension, we'll investigate how to read it
        engine = detect_engine(file_path, verbose=verbose)

    if engine in EXCEL_ENGINES or any([file_path.endswith(k) for k in XLS_LIKE_EXT]):
        table, total_lines, nb_duplicates, sheet_name, engine, header_row_idx = parse_excel(
            file_path=file_path,
            num_rows=num_rows,
            engine=engine,
            sheet_name=sheet_name,
            verbose=verbose,
        )
        header = table.columns.to_list()
        analysis = {
            "engine": engine,
            "sheet_name": sheet_name,
        }
    else:
        # fetching or reading file as binary
        if is_url(file_path):
            r = requests.get(file_path, allow_redirects=True)
            r.raise_for_status()
            binary_file = BytesIO(r.content)
        else:
            binary_file = open(file_path, "rb")
        # handling compression
        if engine in COMPRESSION_ENGINES:
            binary_file: BytesIO = unzip(binary_file=binary_file, engine=engine)
        # detecting encoding if not specified
        if encoding is None:
            encoding: str = detect_encoding(binary_file, verbose=verbose)
            binary_file.seek(0)
        # decoding and reading file
        if is_url(file_path) or engine in COMPRESSION_ENGINES:
            str_file = StringIO(binary_file.read().decode(encoding=encoding))
        else:
            str_file = open(file_path, "r", encoding=encoding)
        if sep is None:
            sep = detect_separator(str_file, verbose=verbose)
        header_row_idx, header = detect_headers(str_file, sep, verbose=verbose)
        if header is None:
            return {"error": True}
        elif isinstance(header, list):
            if any([x is None for x in header]):
                return {"error": True}
        heading_columns = detect_heading_columns(str_file, sep, verbose=verbose)
        trailing_columns = detect_trailing_columns(str_file, sep, heading_columns, verbose=verbose)
        table, total_lines, nb_duplicates = parse_csv(
            str_file, encoding, sep, num_rows, header_row_idx, verbose=verbose
        )
        analysis = {
            "encoding": encoding,
            "separator": sep,
            "heading_columns": heading_columns,
            "trailing_columns": trailing_columns,
        }
    analysis.update({
        "header_row_idx": header_row_idx,
        "header": header,
        "total_lines": total_lines,
        "nb_duplicates": nb_duplicates,
    })
    return table, analysis
