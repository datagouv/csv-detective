from time import time
from typing import Optional

import magic
import requests

from csv_detective.utils import display_logs_depending_process_time, is_url

COMPRESSION_ENGINES = ["gzip"]
EXCEL_ENGINES = ["openpyxl", "xlrd", "odf"]
engine_to_file = {
    "openpyxl": "Excel",
    "xlrd": "old Excel",
    "odf": "OpenOffice",
    "gzip": "csv.gz",
}


def detect_engine(file_path: str, verbose=False) -> Optional[str]:
    if verbose:
        start = time()
    mapping = {
        "application/gzip": "gzip",
        "application/x-gzip": "gzip",
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'openpyxl',
        'application/vnd.ms-excel': 'xlrd',
        'application/vnd.oasis.opendocument.spreadsheet': 'odf',
        # all these files could be recognized as zip, may need to check all cases then
        'application/zip': 'openpyxl',
    }
    # if none of the above, we move forwards with the csv process
    if is_url(file_path):
        remote_content = requests.get(file_path).content
        engine = mapping.get(magic.from_buffer(remote_content, mime=True))
    else:
        engine = mapping.get(magic.from_file(file_path, mime=True))
    if verbose:
        message = (
            f"File is not csv, detected {engine_to_file.get(engine, 'csv')}"
            if engine else "Processing the file as a csv"
        )
        display_logs_depending_process_time(
            message,
            time() - start,
        )
    return engine
