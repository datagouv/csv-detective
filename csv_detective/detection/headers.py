import logging
from time import time
from typing import Optional, TextIO

from csv_detective.utils import display_logs_depending_process_time


def detect_headers(file: TextIO, sep: str, verbose: bool = False) -> tuple[int, Optional[list]]:
    """Tests 10 first rows for possible header (in case header is not 1st row)"""
    if verbose:
        start = time()
        logging.info("Detecting headers")
    file.seek(0)
    for i in range(10):
        header = file.readline()
        position = file.tell()
        chaine = [c for c in header.replace("\n", "").split(sep) if c]
        if chaine[-1] not in ["", "\n"] and all(
            [mot not in ["", "\n"] for mot in chaine[1:-1]]
        ):
            next_row = file.readline()
            file.seek(position)
            if header != next_row:
                if verbose:
                    display_logs_depending_process_time(
                        f'Detected headers in {round(time() - start, 3)}s',
                        time() - start,
                    )
                return i, chaine
    if verbose:
        logging.info('No header detected')
    return 0, None
