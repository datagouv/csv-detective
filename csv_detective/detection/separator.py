import csv
import logging
from time import time
from typing import TextIO

from csv_detective.utils import display_logs_depending_process_time


def detect_separator(file: TextIO, verbose: bool = False) -> str:
    """Detects csv separator"""
    # TODO: add a robust detection:
    # si on a un point virgule comme texte et \t comme séparateur, on renvoie
    # pour l'instant un point virgule
    if verbose:
        start = time()
        logging.info("Detecting separator")
    file.seek(0)
    header = file.readline()
    possible_separators = [";", ",", "|", "\t"]
    sep_count = dict()
    for sep in possible_separators:
        sep_count[sep] = header.count(sep)
    sep = max(sep_count, key=sep_count.get)
    # testing that the first 10 (arbitrary) rows all have the same number of fields
    # as the header. Prevents downstream unwanted behaviour where pandas can load
    # the file (in a weird way) but the process is irrelevant.
    file.seek(0)
    reader = csv.reader(file, delimiter=sep)
    rows_lengths = set()
    for idx, row in enumerate(reader):
        if idx > 10:
            break
        rows_lengths.add(len(row))
    if len(rows_lengths) > 1:
        raise ValueError(
            f"Number of columns is not even across the first 10 rows (detected separator: {sep})."
        )

    if verbose:
        display_logs_depending_process_time(
            f'Detected separator: "{sep}" in {round(time() - start, 3)}s',
            time() - start,
        )
    return sep
