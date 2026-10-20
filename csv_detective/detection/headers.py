import logging
from time import time
from typing import TextIO

from csv_detective.utils import display_logs_depending_process_time


def detect_header_position(file: TextIO, verbose: bool = False) -> int:
    """Tests 10 first rows for possible header (in case header is not 1st row)"""
    if verbose:
        start = time()
        logging.info("Detecting header position")
    file.seek(0)
    for i in range(10):
        row = file.readline()
        position = file.tell()
        next_row = file.readline()
        file.seek(position)
        if row != next_row:
            if verbose:
                display_logs_depending_process_time(
                    f"Detected header position in {round(time() - start, 3)}s",
                    time() - start,
                )
            return i
    raise ValueError("Could not accurately retrieve headers position")
