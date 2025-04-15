import logging
from typing import TextIO
from time import time

from csv_detective.utils import display_logs_depending_process_time


def detect_extra_columns(file: TextIO, sep: str):
    """regarde s'il y a des colonnes en trop
    Attention, file ne doit pas avoir de ligne vide"""
    file.seek(0)
    retour = False
    nb_useless_col = 99999

    for i in range(10):
        line = file.readline()
        # regarde si on a un retour
        if retour:
            assert line[-1] == "\n"
        if line[-1] == "\n":
            retour = True

        # regarde le nombre de derniere colonne inutile
        deb = 0 + retour
        line = line[::-1][deb:]
        k = 0
        for sign in line:
            if sign != sep:
                break
            k += 1
        if k == 0:
            return 0, retour
        nb_useless_col = min(k, nb_useless_col)
    return nb_useless_col, retour


def detect_heading_columns(file: TextIO, sep: str, verbose: bool = False) -> int:
    """Tests first 10 lines to see if there are empty heading columns"""
    if verbose:
        start = time()
        logging.info("Detecting heading columns")
    file.seek(0)
    return_int = float("Inf")
    for i in range(10):
        line = file.readline()
        return_int = min(return_int, len(line) - len(line.strip(sep)))
        if return_int == 0:
            if verbose:
                display_logs_depending_process_time(
                    f'No heading column detected in {round(time() - start, 3)}s',
                    time() - start,
                )
            return 0
    if verbose:
        display_logs_depending_process_time(
            f'{return_int} heading columns detected in {round(time() - start, 3)}s',
            time() - start,
        )
    return return_int


def detect_trailing_columns(file: TextIO, sep: str, heading_columns: int, verbose: bool = False) -> int:
    """Tests first 10 lines to see if there are empty trailing columns"""
    if verbose:
        start = time()
        logging.info("Detecting trailing columns")
    file.seek(0)
    return_int = float("Inf")
    for i in range(10):
        line = file.readline()
        return_int = min(
            return_int,
            len(line.replace("\n", ""))
            - len(line.replace("\n", "").strip(sep))
            - heading_columns,
        )
        if return_int == 0:
            if verbose:
                display_logs_depending_process_time(
                    f'No trailing column detected in {round(time() - start, 3)}s',
                    time() - start,
                )
            return 0
    if verbose:
        display_logs_depending_process_time(
            f'{return_int} trailing columns detected in {round(time() - start, 3)}s',
            time() - start,
        )
    return return_int
