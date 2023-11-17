import pandas as pd
import numpy as np
from cchardet import detect
from ast import literal_eval
import logging
from time import time
from csv_detective.utils import display_logs_depending_process_time
from csv_detective.detect_fields.other.float import float_casting

logging.basicConfig(level=logging.INFO)

def detect_continuous_variable(table, continuous_th=0.9, verbose: bool = False):
    """
    Detects whether a column contains continuous variables. We consider a continuous column
    one that contains
    a considerable amount of float values.
    We removed the integers as we then end up with postal codes, insee codes, and all sort
    of codes and types.
    This is not optimal but it will do for now.
    :param table:
    :return:
    """

    def check_threshold(serie, continuous_th):
        count = serie.value_counts().to_dict()
        total_nb = len(serie)
        if float in count:
            nb_floats = count[float]
        else:
            return False
        if nb_floats / total_nb >= continuous_th:
            return True
        else:
            return False

    def parses_to_integer(value):
        try:
            value = value.replace(",", ".")
            value = literal_eval(value)
            return type(value)
        # flake8: noqa
        except:
            return False

    if verbose:
        start = time()
        logging.info("Detecting continuous columns")
    res = table.apply(
        lambda serie: check_threshold(serie.apply(parses_to_integer), continuous_th)
    )
    if verbose:
        display_logs_depending_process_time(
            f"Detected {sum(res)} continuous columns in {round(time() - start, 3)}s",
            time() - start
        )
    return res.index[res]


def detetect_categorical_variable(
    table, threshold_pct_categorical=0.05, max_number_categorical_values=25, verbose: bool = False
):
    """
    Heuristically detects whether a table (df) contains categorical values according to
    the number of unique values contained.
    As the idea of detecting categorical values is to then try to learn models to predict
    them, we limit categorical values to at most 25 different modes. Postal code, insee code,
    code region and so on, may be thus not
    considered categorical values.
    :param table:
    :param threshold_pct_categorical:
    :param max_number_categorical_values:
    :return:
    """

    def abs_number_different_values(column_values):
        return column_values.nunique()

    def rel_number_different_values(column_values):
        return column_values.nunique() / len(column_values)

    def detect_categorical(column_values):
        abs_unique_values = abs_number_different_values(column_values)
        rel_unique_values = rel_number_different_values(column_values)
        if abs_unique_values < max_number_categorical_values:
            if rel_unique_values < threshold_pct_categorical:
                return True
        return False

    if verbose:
        start = time()
        logging.info("Detecting categorical columns")
    res = table.apply(lambda serie: detect_categorical(serie))
    if verbose:
        display_logs_depending_process_time(
            f"Detected {sum(res)} categorical columns out of {len(table.columns)} in {round(time() - start, 3)}s",
            time() - start
        )
    return res.index[res], res


def detect_separator(file, verbose: bool = False):
    """Detects csv separator"""
    # TODO: add a robust detection:
    # si on a un point virgule comme texte et \t comme séparateur, on renvoit
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
    if verbose:
        display_logs_depending_process_time(
            f'Detected separator: "{sep}" in {round(time() - start, 3)}s',
            time() - start
        )
    return sep


def detect_encoding(the_file, verbose: bool = False):
    """
    Detects file encoding using faust-cchardet (forked from the original cchardet)
    """
    if verbose:
        start = time()
        logging.info("Detecting encoding")
    encoding_dict = detect(the_file.read())
    if verbose:
        message = f'Detected encoding: "{encoding_dict["encoding"]}"'
        message += f' in {round(time() - start, 3)}s (confidence: {round(encoding_dict["confidence"]*100)}%)'
        display_logs_depending_process_time(
            message,
            time() - start
        )
    return encoding_dict['encoding']


def parse_table(the_file, encoding, sep, num_rows, skiprows, random_state=42, verbose : bool = False):
    # Takes care of some problems
    if verbose:
        start = time()
        logging.info("Parsing table")
    table = None

    if not isinstance(the_file, str):
        the_file.seek(0)

    total_lines = None
    for encoding in [encoding, "ISO-8859-1", "utf-8"]:
        # TODO : modification systematique
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
        logging.error("  >> encoding not found")
        return table, "NA", "NA"
    if verbose:
        display_logs_depending_process_time(
            f'Table parsed successfully in {round(time() - start, 3)}s',
            time() - start
        )
    return table, total_lines, nb_duplicates


def create_profile(table, dict_cols_fields, sep, encoding, num_rows, skiprows, verbose: bool = False):
    if verbose:
        start = time()
        logging.info("Creating profile")
    map_python_types = {
        "string": str,
        "int": float,
        "float": float,
    }

    if num_rows > 0:
        raise Exception("To create profiles num_rows has to be set to -1")
    else:
        safe_table = table.copy()
        dtypes = {
            k: map_python_types.get(v["python_type"], str)
            for k, v in dict_cols_fields.items()
        }
        for c in safe_table.columns:
            if dtypes[c] == float:
                safe_table[c] = safe_table[c].apply(
                    lambda s: float_casting(s) if isinstance(s, str) else s
                )
        profile = {}
        for c in safe_table.columns:
            profile[c] = {}
            if map_python_types.get(dict_cols_fields[c]["python_type"], str) in [
                float,
                int,
            ]:
                profile[c].update(
                    min=map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                        safe_table[c].min()
                    ),
                    max=map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                        safe_table[c].max()
                    ),
                    mean=map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                        safe_table[c].mean()
                    ),
                    std=map_python_types.get(dict_cols_fields[c]["python_type"], str)(
                        safe_table[c].std()
                    ),
                )
            tops_bruts = safe_table[safe_table[c].notna()][c] \
                    .value_counts(dropna=True) \
                    .reset_index() \
                    .iloc[:10] \
                    .to_dict(orient="records")
            tops = []
            for tb in tops_bruts:
                top = {}
                top["count"] = tb[c]
                top["value"] = tb["index"]
                tops.append(top)
            profile[c].update(
                tops=tops,
                nb_distinct=safe_table[c].nunique(),
                nb_missing_values=len(safe_table[c].loc[safe_table[c].isna()]),
            )
        if verbose:
            display_logs_depending_process_time(
                f"Created profile in {round(time() - start, 3)}s",
                time() - start
            )
        return profile


def detect_extra_columns(file, sep):
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


def detect_headers(file, sep, verbose: bool = False):
    """Tests 10 first rows for possible header (header not in 1st line)"""
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
                        time() - start
                    )
                return i, chaine
    if verbose:
        logging.info(f'No header detected')
    return 0, None


def detect_heading_columns(file, sep, verbose : bool = False):
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
                    time() - start
                )
            return 0
    if verbose:
        display_logs_depending_process_time(
            f'{return_int} heading columns detected in {round(time() - start, 3)}s',
            time() - start
        )
    return return_int


def detect_trailing_columns(file, sep, heading_columns, verbose : bool = False):
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
                    time() - start
                )
            return 0
    if verbose:
        display_logs_depending_process_time(
            f'{return_int} trailing columns detected in {round(time() - start, 3)}s',
            time() - start
        )
    return return_int
