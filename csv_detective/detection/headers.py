import logging
from time import time
from typing import TextIO

from csv_detective.utils import display_logs_depending_process_time


def detect_headers(file: TextIO, sep: str, verbose: bool = False) -> tuple[int, list | None]:
    """Tests 10 first rows for possible header (in case header is not 1st row)"""
    if verbose:
        start = time()
        logging.info("Detecting headers")
    file.seek(0)
    for i in range(10):
        row = file.readline()
        position = file.tell()
        headers = [c for c in row.replace("\n", "").split(sep) if c]
        if not any(col == "" for col in headers):
            next_row = file.readline()
            file.seek(position)
            if row != next_row:
                if verbose:
                    display_logs_depending_process_time(
                        f"Detected headers in {round(time() - start, 3)}s",
                        time() - start,
                    )
                return i, headers
    raise ValueError("Could not retrieve headers")
