from datetime import date as _date
from datetime import datetime as _datetime
from unittest.mock import patch

import pandas as pd
import pytest
from numpy import random

from csv_detective import routine
from csv_detective.detection.variables import (
    detect_categorical_variable,
    detect_continuous_variable,
)
from csv_detective.format import FormatsManager
from csv_detective.formats.date import (
    date_format_candidates,
    datetime_format_candidates,
    resolve_date_format,
)
from csv_detective.formats.float import float_casting
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
        assert all(isinstance(key, bool) and isinstance(vals, list) for key, vals in valid.items())
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
            name: ([v for v in format._test_values[True] if isinstance(v, str)] * 100)[:100]
            + ["not_suitable"]
            for name, format in fmtm.formats.items()
            if format.proportion == 1
        }
    )
    # testing columns for all formats
    returned_table, _ = col_test(table, fmtm.formats, limited_output=True)
    # the analysis should have found no match on any format
    assert all(returned_table[col].sum() == 0 for col in table.columns)


@pytest.mark.parametrize(
    "value, expected_formats",
    [
        ("1960-08-07", {"%Y-%m-%d"}),
        ("20030502", {"%Y%m%d"}),
        ("2003.05.02", {"%Y.%m.%d"}),
        # day and month both <= 12: the value alone can't tell the two orders apart
        ("12/02/2007", {"%d/%m/%Y", "%m/%d/%Y"}),
        ("02 05 2003", {"%d %m %Y", "%m %d %Y"}),
        # the first component is above 12, it can only be a day
        ("25/03/2024", {"%d/%m/%Y"}),
        # the second component is above 12, it can only be a day
        ("03/25/2024", {"%m/%d/%Y"}),
        # neither component can be a month
        ("19/15/1993", set()),
        ("15 jan 1985", set()),
        ("1993-12/02", set()),  # mixed separators
    ],
)
def test_date_format_candidates(value, expected_formats):
    assert date_format_candidates(value) == expected_formats


@pytest.mark.parametrize(
    "value, has_tz, expected_formats",
    [
        ("2021-06-22 10:20:10", False, {"%Y-%m-%d %H:%M:%S"}),
        ("2030/06/22 00:00:00.0028", False, {"%Y/%m/%d %H:%M:%S.%f"}),
        ("2021-06-22 10:20:10-04:00", True, {"%Y-%m-%d %H:%M:%S%z"}),
        ("2030-06-22 00:00:00.0028+02:00", True, {"%Y-%m-%d %H:%M:%S.%f%z"}),
        ("2000-12-21 10:20:10.1Z", True, {"%Y-%m-%d %H:%M:%S.%f%z"}),
        ("2024-12-19T10:53:36.428000+00:00", True, {"%Y-%m-%dT%H:%M:%S.%f%z"}),
        ("1925_12_20T14:30:00.2763", False, {"%Y_%m_%dT%H:%M:%S.%f"}),
        ("1925 12 20 14:30:00Z", True, {"%Y %m %d %H:%M:%S%z"}),
        # the date part carries the same ambiguity as a plain date
        ("07/03/2024 10:20:10", False, {"%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"}),
        ("12/31/2022 12:00:00", False, {"%m/%d/%Y %H:%M:%S"}),
        ("31/12/2022 12:00:00", False, {"%d/%m/%Y %H:%M:%S"}),
        ("Sun, 06 Nov 1994 08:49:37 GMT", False, set()),  # rfc822
    ],
)
def test_datetime_format_candidates(value, has_tz, expected_formats):
    assert datetime_format_candidates(value, has_tz=has_tz) == expected_formats


@pytest.mark.parametrize(
    "candidates, expected",
    [
        ({"%d/%m/%Y"}, ["%d/%m/%Y"]),
        ({"%m/%d/%Y"}, ["%m/%d/%Y"]),
        ({"%Y-%m-%d"}, ["%Y-%m-%d"]),
        # no value in the column tells the two orders apart: day-first wins
        ({"%d/%m/%Y", "%m/%d/%Y"}, ["%d/%m/%Y"]),
        # values contradict each other, no format fits the whole column
        (set(), None),
    ],
)
def test_resolve_date_format(candidates, expected):
    assert resolve_date_format(candidates) == expected


@pytest.mark.parametrize(
    "values, expected_format, expected_dates",
    [
        # one value where the day is above 12 settles the order for the whole column,
        # including for the values that could have been read either way
        (
            ["07/03/2024", "25/12/2024"],
            ["%d/%m/%Y"],
            [_date(2024, 3, 7), _date(2024, 12, 25)],
        ),
        # and one value where the month is above 12 settles it the other way around
        (
            ["07/03/2024", "12/25/2024"],
            ["%m/%d/%Y"],
            [_date(2024, 7, 3), _date(2024, 12, 25)],
        ),
        # no value settles the order, the French day-first reading is the default
        (
            ["07/03/2024", "01/02/2024"],
            ["%d/%m/%Y"],
            [_date(2024, 3, 7), _date(2024, 2, 1)],
        ),
        # the values contradict each other, no single format reads the whole column
        (
            ["25/12/2024", "12/25/2024"],
            None,
            [_date(2024, 12, 25), _date(2024, 12, 25)],
        ),
    ],
)
def test_date_order_is_settled_by_the_column(tmp_path, values, expected_format, expected_dates):
    file_path = tmp_path / "dates.csv"
    file_path.write_text("date;label\n" + "".join(f"{value};a\n" for value in values * 5))
    analysis, dfs = routine(
        file_path=str(file_path),
        num_rows=-1,
        save_results=False,
        output_df=True,
    )
    assert analysis["columns"]["date"]["python_type"] == "date"
    assert analysis["columns"]["date"]["date_format"] == expected_format
    assert list(pd.concat(list(dfs))["date"]) == expected_dates * 5


def test_date_order_is_settled_beyond_the_first_chunk(tmp_path):
    # the only value that settles the order sits in the last chunk
    values = ["07/03/2024"] * 50 + ["12/25/2024"]
    file_path = tmp_path / "dates.csv"
    file_path.write_text("date;label\n" + "".join(f"{value};a\n" for value in values))
    with (
        patch("csv_detective.parsing.csv.CHUNK_SIZE", 10),
        patch("csv_detective.parsing.columns.CHUNK_SIZE", 10),
    ):
        analysis = routine(file_path=str(file_path), num_rows=-1, save_results=False)
    assert analysis["columns"]["date"]["date_format"] == ["%m/%d/%Y"]


@pytest.mark.parametrize(
    "values, expected_format, expected_datetimes",
    [
        (
            ["07/03/2024 10:20:10", "25/12/2024 10:20:10"],
            ["%d/%m/%Y %H:%M:%S"],
            [_datetime(2024, 3, 7, 10, 20, 10), _datetime(2024, 12, 25, 10, 20, 10)],
        ),
        (
            ["07/03/2024 10:20:10", "12/25/2024 10:20:10"],
            ["%m/%d/%Y %H:%M:%S"],
            [_datetime(2024, 7, 3, 10, 20, 10), _datetime(2024, 12, 25, 10, 20, 10)],
        ),
        (
            ["07/03/2024 10:20:10", "01/02/2024 10:20:10"],
            ["%d/%m/%Y %H:%M:%S"],
            [_datetime(2024, 3, 7, 10, 20, 10), _datetime(2024, 2, 1, 10, 20, 10)],
        ),
    ],
)
def test_datetime_order_is_settled_by_the_column(
    tmp_path, values, expected_format, expected_datetimes
):
    file_path = tmp_path / "datetimes.csv"
    file_path.write_text("datetime;label\n" + "".join(f"{value};a\n" for value in values * 5))
    analysis, dfs = routine(
        file_path=str(file_path),
        num_rows=-1,
        save_results=False,
        output_df=True,
    )
    assert analysis["columns"]["datetime"]["python_type"] == "datetime"
    assert analysis["columns"]["datetime"]["date_format"] == expected_format
    assert list(pd.concat(list(dfs))["datetime"]) == expected_datetimes * 5


@pytest.mark.parametrize(
    "value, _type, date_format, expected",
    [
        ("2022-08-01", "date", ["%Y-%m-%d"], _date(2022, 8, 1)),
        # dateutil interprets 12/02 as MM/DD (US), but csv-detective detects DD/MM
        # strptime with the detected format gives the correct DD/MM interpretation
        ("12/02/2007", "date", ["%d/%m/%Y"], _date(2007, 2, 12)),
        (
            "2024-09-23 17:32:07",
            "datetime",
            ["%Y-%m-%d %H:%M:%S"],
            _datetime(2024, 9, 23, 17, 32, 7),
        ),
    ],
)
def test_cast_with_date_format(value, _type, date_format, expected):
    assert cast(value, _type, date_format=date_format) == expected


@pytest.mark.parametrize(
    "custom_prop, should_crash",
    (
        (2, True),
        ([1], True),
        ({"code_commune": "0.8", "int": 0.8}, True),
        (0.4, False),
        (1, False),
        ({"code_commune": 0.4, "int": 0.8}, False),
    ),
)
def test_custom_proportions(custom_prop, should_crash):
    if should_crash:
        with pytest.raises(ValueError):
            FormatsManager(custom_proportions=custom_prop)
    else:
        custom_fmtm = FormatsManager(custom_proportions=custom_prop)
        if isinstance(custom_prop, (float, int)):
            assert all(fmt.proportion == custom_prop for fmt in custom_fmtm.formats.values())
        else:
            for fmt in fmtm.formats:
                # checking that the specified formats have been set, and the others remain unchanged
                if fmt in custom_prop:
                    assert custom_fmtm.formats[fmt].proportion == custom_prop[fmt]
                else:
                    assert custom_fmtm.formats[fmt].proportion == fmtm.formats[fmt].proportion


def test_float_valid_values():
    float_fmt = fmtm.formats["float"]
    assert all(isinstance(float_casting(val), float) for val in float_fmt._test_values[True])
