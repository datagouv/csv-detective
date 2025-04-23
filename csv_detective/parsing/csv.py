import logging
from time import time
from typing import TextIO

import pandas as pd

from csv_detective.utils import display_logs_depending_process_time


def parse_csv(
    the_file: TextIO,
    encoding: str,
    sep: str,
    num_rows: int,
    skiprows: int,
    random_state: int = 42,
    verbose: bool = False,
) -> tuple[pd.DataFrame, int, int]:
    if verbose:
        start = time()
        logging.info("Parsing table")
    table = None

    if not isinstance(the_file, str):
        the_file.seek(0)

    total_lines = None
    for encoding in [encoding, "ISO-8859-1", "utf-8"]:
        if encoding is None:
            continue

        if "ISO-8859" in encoding:
            encoding = "ISO-8859-1"
        try:
            table = pd.read_csv(
                the_file, sep=sep, dtype="unicode", encoding=encoding, skiprows=skiprows
            )
            total_lines = len(table)
            nb_duplicates = len(table.loc[table.duplicated()])
            if num_rows > 0:
                num_rows = min(num_rows - 1, total_lines)
                table = table.sample(num_rows, random_state=random_state)
            # else : table is unchanged
            break
        except TypeError:
            print("Trying encoding : {encoding}".format(encoding=encoding))

    if table is None:
        raise ValueError("Could not load file")
    if verbose:
        display_logs_depending_process_time(
            f'Table parsed successfully in {round(time() - start, 3)}s',
            time() - start,
        )
    return table, total_lines, nb_duplicates
