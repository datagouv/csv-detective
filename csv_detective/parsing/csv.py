import logging
from time import time
from typing import TextIO

import pandas as pd

from csv_detective.utils import display_logs_depending_process_time

# the number of rows for the first analysis, and the number of rows per chunk of the df iterator
CHUNK_SIZE = int(1e4)


def parse_csv(
    the_file: TextIO,
    encoding: str,
    sep: str,
    num_rows: int,
    skiprows: int,
    random_state: int = 42,
    verbose: bool = False,
) -> tuple[pd.DataFrame, int | None, int | None]:
    if verbose:
        start = time()
        logging.info("Parsing table")

    if not isinstance(the_file, str):
        the_file.seek(0)

    try:
        table = pd.read_csv(
            the_file,
            sep=sep,
            dtype=str,
            encoding=encoding,
            skiprows=skiprows,
            nrows=CHUNK_SIZE,
        )
        total_lines = len(table)
        # branch between small and big files starts here
        if total_lines == CHUNK_SIZE:
            if verbose:
                logging.warning(f"File is too long, analysing in chunks of {CHUNK_SIZE} rows")
            total_lines, nb_duplicates = None, None
        else:
            nb_duplicates = len(table.loc[table.duplicated()])
        if num_rows > 0:
            num_rows = min(num_rows, total_lines or len(table))
            table = table.sample(num_rows, random_state=random_state)
    except Exception as e:
        raise ValueError("Could not load file") from e
    if verbose:
        display_logs_depending_process_time(
            f"Table parsed successfully in {round(time() - start, 3)}s",
            time() - start,
        )
    return table, total_lines, nb_duplicates
