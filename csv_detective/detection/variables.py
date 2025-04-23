from ast import literal_eval
import logging
from time import time

import pandas as pd

from csv_detective.utils import display_logs_depending_process_time


def detect_continuous_variable(table: pd.DataFrame, continuous_th: float = 0.9, verbose: bool = False):
    """
    Detects whether a column contains continuous variables. We consider a continuous column
    one that contains a considerable amount of float values.
    We removed the integers as we then end up with postal codes, insee codes, and all sort
    of codes and types.
    This is not optimal but it will do for now.
    """
    # if we need this again in the future, could be first based on columns detected as int/float to cut time

    def check_threshold(serie: pd.Series, continuous_th: float) -> bool:
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

    def parses_to_integer(value: str):
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
            time() - start,
        )
    return res.index[res]


def detect_categorical_variable(
    table: pd.DataFrame,
    threshold_pct_categorical: float = 0.05,
    max_number_categorical_values: int = 25,
    verbose: bool = False,
):
    """
    Heuristically detects whether a table (df) contains categorical values according to
    the number of unique values contained.
    As the idea of detecting categorical values is to then try to learn models to predict
    them, we limit categorical values to at most 25 different modes or at most 5% disparity.
    Postal code, insee code, code region and so on, may be thus not considered categorical values.
    :param table:
    :param threshold_pct_categorical:
    :param max_number_categorical_values:
    :return:
    """

    def abs_number_different_values(column_values: pd.Series):
        return column_values.nunique()

    def rel_number_different_values(column_values: pd.Series):
        return column_values.nunique() / len(column_values)

    def detect_categorical(column_values: pd.Series):
        abs_unique_values = abs_number_different_values(column_values)
        rel_unique_values = rel_number_different_values(column_values)
        if (
            abs_unique_values <= max_number_categorical_values
            or rel_unique_values <= threshold_pct_categorical
        ):
            return True
        return False

    if verbose:
        start = time()
        logging.info("Detecting categorical columns")
    res = table.apply(lambda serie: detect_categorical(serie))
    if verbose:
        display_logs_depending_process_time(
            f"Detected {sum(res)} categorical columns out of {len(table.columns)} in {round(time() - start, 3)}s",
            time() - start,
        )
    return res.index[res], res
