from datetime import date as _date
from datetime import datetime as _datetime
from unittest.mock import patch

import pandas as pd
import pytest
from numpy import random

from csv_detective.detection.variables import (
    detect_categorical_variable,
    detect_continuous_variable,
)
from csv_detective.format import FormatsManager
from csv_detective.output.dataframe import cast
from csv_detective.output.utils import prepare_output_dict
from csv_detective.parsing.columns import test_col as col_test  # to prevent pytest from testing it

fmtm = FormatsManager()


def test_all_format_funcs_return_bool():
    for format in fmtm.formats.values():
        for tmp in ["a", "9", "3.14", "[]", float("nan"), "2021-06-22 10:20:10"]:
            assert isinstance(format.func(tmp), bool)


# categorical
def test_detect_categorical_variable():
    categorical_col = ["type_a"] * 33 + ["type_b"] * 33 + ["type_c"] * 34
    categorical_col2 = [str(k // 20) for k in range(100)]
    not_categorical_col = [i for i in range(100)]

    df_dict = {
        "cat": categorical_col,
        "cat2": categorical_col2,
        "not_cat": not_categorical_col,
    }
    df = pd.DataFrame(df_dict, dtype=str)

    res, _ = detect_categorical_variable(df)
    assert len(res) and all(k in res for k in ["cat", "cat2"])


# continuous
def test_detect_continuous_variable():
    continuous_col = random.random(100)
    continuous_col_2 = [1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7, 21, 3] * 10
    not_continuous_col = ["type_a"] * 33 + ["type_b"] * 33 + ["type_c"] * 34

    df_dict = {"cont": continuous_col, "not_cont": not_continuous_col}
    df_dict_2 = {"cont": continuous_col_2, "not_cont": not_continuous_col}

    df = pd.DataFrame(df_dict, dtype=str)
    df2 = pd.DataFrame(df_dict_2, dtype=str)

    res = detect_continuous_variable(df)
    res2 = detect_continuous_variable(df2, continuous_th=0.65)
    assert res.values and res.values[0] == "cont"
    assert res2.values and res2.values[0] == "cont"


# we could also have a function here to add all True values of (almost)
# each field to the False values of all others (to do when parenthood is added)


def test_all_fields_have_tests():
    for format in fmtm.formats.values():
        valid = format._test_values
        # checking structure
        assert all(
            isinstance(key, bool)
            and isinstance(vals, list)
            and all(isinstance(val, str) for val in vals)
            for key, vals in valid.items()
        )
        # checking that we have valid and invalid cases for each
        assert all(b in valid.keys() for b in [True, False])


# this is based on the _test_values of each <format>.py file
@pytest.mark.parametrize(
    "args",
    (
        (format.func, value, valid)
        for valid in [True, False]
        for format in fmtm.formats.values()
        for value in format._test_values[valid]
    ),
)
def test_fields_with_values(args):
    func, value, valid = args
    assert func(value) is valid


@pytest.mark.parametrize(
    "args",
    (
        ("Valeur", "string", str),
        ("-17", "int", int),
        ("1.9", "float", float),
        ("oui", "bool", bool),
        ("[1, 2]", "json", list),
        ('{"a": 1}', "json", dict),
        ("2022-08-01", "date", _date),
        ("2024-09-23 17:32:07", "datetime", _datetime),
        ("2024-09-23 17:32:07+02:00", "datetime", _datetime),
        ("N/A", "int", None),
        ("nan", "bool", None),
        ("", "date", None),  # all NaN-like values should be cast as None for all type
    ),
)
def test_cast(args):
    value, detected_type, cast_type = args
    if cast_type is None:
        assert cast(value, detected_type) is None
    else:
        assert isinstance(cast(value, detected_type), cast_type)


@pytest.mark.parametrize(
    "args",
    (
        # there is a specific numerical format => specific wins
        ({"int": 1, "float": 1, "latitude_wgs": 1}, "latitude_wgs"),
        # scores are equal for related formats => priority wins
        ({"int": 1, "float": 1}, "int"),
        # score is lower for priority format => secondary wins
        ({"int": 0.5, "float": 1}, "float"),
        # score is lower for priority format, but is 1 => priority wins
        ({"int": 1, "float": 1.25}, "int"),
        # two rounds of priority => highest priority wins
        ({"latlon_wgs": 1, "lonlat_wgs": 1, "json": 1}, "latlon_wgs"),
        # no detection => default to string
        ({}, "string"),
    ),
)
def test_priority(args):
    detections, expected = args
    col = "col1"
    output = prepare_output_dict(pd.DataFrame({col: detections}), limited_output=True)
    assert output[col]["format"] == expected


@pytest.mark.parametrize(
    "args",
    (
        ("1996-02-13", fmtm.formats["date"]),
        ("28/01/2000", fmtm.formats["date"]),
        ("2025-08-20T14:30:00+02:00", fmtm.formats["datetime_aware"]),
        ("2025/08/20 14:30:00.2763-12:00", fmtm.formats["datetime_aware"]),
        ("1925_12_20T14:30:00.2763", fmtm.formats["datetime_naive"]),
        ("1925 12 20 14:30:00Z", fmtm.formats["datetime_aware"]),
    ),
)
def test_early_detection(args):
    value, format = args
    with patch("csv_detective.formats.date.date_casting") as mock_func:
        res = format.func(value)
        assert res
        mock_func.assert_not_called()


def test_all_proportion_1():
    # building a table that uses only correct values for these formats, except on one row
    table = pd.DataFrame(
        {
            name: (format._test_values[True] * 100)[:100] + ["not_suitable"]
            for name, format in fmtm.formats.items()
            if format.proportion == 1
        }
    )
    # testing columns for all formats
    returned_table = col_test(table, fmtm.formats, limited_output=True)
    # the analysis should have found no match on any format
    assert all(returned_table[col].sum() == 0 for col in table.columns)
