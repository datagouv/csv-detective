from datetime import date as _date
from datetime import datetime as _datetime
from datetime import timezone as _timezone
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
from csv_detective.formats.date import CUSTOM_PREFIX, MONTH_NAMES, MONTHS, build_month_index, parse
from csv_detective.formats.date import _infer as date_infer
from csv_detective.formats.datetime_aware import _infer as datetime_aware_infer
from csv_detective.formats.datetime_naive import _infer as datetime_naive_infer
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
def test_usual_formats_are_detected(args):
    value, format = args
    assert format.func(value)


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
    returned_table = col_test(table, fmtm.formats, limited_output=True)
    # the analysis should have found no match on any format
    assert all(returned_table[col].sum() == 0 for col in table.columns)


@pytest.mark.parametrize(
    "values, expected_format",
    [
        (["1960-08-07"], "%Y-%m-%d"),
        (["20030502"], "%Y%m%d"),
        (["2003.05.02"], "%Y.%m.%d"),
        # day and month are both <= 12 and nothing tells the two orders apart: day-first wins
        (["12/02/2007"], "%d/%m/%Y"),
        # numeric dates keep a two-digit year, same order as the four-digit form
        (["12/02/85"], "%d/%m/%y"),
        # and it is the shortest shape we read, so no padding either
        (["1/2/85"], "%d/%m/%y"),
        (["1/12/85", "25/2/85"], "%d/%m/%y"),
        (["02 05 2003"], "%d %m %Y"),
        # one value whose day is above 12 settles the order for the whole column
        (["07/03/2024", "25/12/2024"], "%d/%m/%Y"),
        # and one value whose month is above 12 settles it the other way around
        (["07/03/2024", "12/25/2024"], "%m/%d/%Y"),
        # the values contradict each other, no single format reads them all
        (["25/12/2024", "12/25/2024"], None),
        # zero-padding is optional and does not make a second format
        (["1/2/2024", "25/03/2024"], "%d/%m/%Y"),
        # text months, in any of the supported languages and spellings
        (["15 jan 1985", "13 février 1996"], "csvd:%d %b %Y"),
        (["15 janv. 1985"], "csvd:%d %b %Y"),
        (["15-dec-85"], "csvd:%d-%b-%y"),
        # English writes the day with an ordinal suffix
        (["31st december 2022"], "csvd:%d %b %Y"),
        # the year can be followed by the day rather than the month
        (["2022-31-12"], "%Y-%d-%m"),
        # ISO stays the preferred reading when both orders fit
        (["2022-01-12"], "%Y-%m-%d"),
        # "jui" is the prefix of both juin and juillet, it cannot be read
        (["15 jui 1985"], None),
        (["15 tambour 1985"], None),
        # neither component can be a month
        (["19/15/1993"], None),
        # a separator can be more than one character, as long as the value keeps to the same one
        (["1789 / 07 / 14"], "%Y / %m / %d"),
        (["14 / 07 / 89"], "%d / %m / %y"),
        # TODO: a real shape we do not read yet, month first and a comma after the day. The comma
        # is in SEPARATORS, so separator_of sees {" ", ","} and gives up before a template is
        # even picked; reading it means treating that comma as part of the format, the way the
        # full stop of an abbreviated month already is.
        (["Jun 22, 2021"], None),
        # mixed separators, within a value or across the column
        (["1993-12/02"], None),
        (["199302-05"], None),
        (["2003.05.02", "1960-08-07"], None),
    ],
)
def test_date_format_inferred_from_column(values, expected_format):
    assert date_infer(values) == expected_format


@pytest.mark.parametrize(
    "values, aware, expected_format",
    [
        (["2021-06-22 10:20:10"], False, "%Y-%m-%d %H:%M:%S"),
        (["2030/06/22 00:00:00.0028"], False, "%Y/%m/%d %H:%M:%S.%f"),
        (["1925_12_20T14:30:00.2763"], False, "%Y_%m_%dT%H:%M:%S.%f"),
        (["2021-06-22 10:20:10-04:00"], True, "%Y-%m-%d %H:%M:%S%z"),
        (["2000-12-21 10:20:10.1Z"], True, "%Y-%m-%d %H:%M:%S.%f%z"),
        (["2024-12-19T10:53:36.428000+00:00"], True, "%Y-%m-%dT%H:%M:%S.%f%z"),
        (["1925 12 20 14:30:00Z"], True, "%Y %m %d %H:%M:%S%z"),
        # the date part carries the same ambiguity as a plain date, settled the same way
        (["07/03/2024 10:20:10"], False, "%d/%m/%Y %H:%M:%S"),
        (["07/03/2024 10:20:10", "12/25/2024 10:20:10"], False, "%m/%d/%Y %H:%M:%S"),
        # a timezone is required by one format and refused by the other
        (["2021-06-22 10:20:10-04:00"], False, None),
        (["2021-06-22 10:20:10"], True, None),
        (["Sun, 06 Nov 1994 08:49:37 GMT"], False, None),  # rfc822 has its own format
        # a source that only prints the fraction when it is non-zero still has one format
        (
            ["2021-06-22 10:20:10", "2021-06-22 10:20:10.5"],
            False,
            "csvd:%Y-%m-%d %H:%M:%S[.%f]",
        ),
        (
            ["2021-06-22 10:20:10+02:00", "2021-06-22 10:20:10.5+02:00"],
            True,
            "csvd:%Y-%m-%d %H:%M:%S[.%f]%z",
        ),
        # the offset is sometimes spaced out from the time
        (["2021-06-22 10:20:10 +02:00"], True, "%Y-%m-%d %H:%M:%S %z"),
        # a named zone, which %z cannot read; marked because we resolve the name ourselves
        (["1996/06/22 10:20:10 GMT"], True, "csvd:%Y/%m/%d %H:%M:%S %Z"),
        (["1996/06/22 10:20:10 CEST"], True, "csvd:%Y/%m/%d %H:%M:%S %Z"),
        # a name that stands for two different zones leaves us without an offset to apply
        (["1996/06/22 10:20:10 CST"], True, None),
        # the year can be followed by the day here too
        (["2022-31-12 12:00:00.92"], False, "%Y-%d-%m %H:%M:%S.%f"),
        # the time does not have to be padded
        (["2021-06-22 1:2:3"], False, "%Y-%m-%d %H:%M:%S"),
        # nor written with colons at all, next to a packed date
        (["20210622T102010"], False, "%Y%m%dT%H%M%S"),
        # and a value that is nothing but digits packs both parts together
        (["202501010000"], False, "%Y%m%d%H%M"),
        (["20250101000000"], False, "%Y%m%d%H%M%S"),
        # any other run of digits is a number, not a datetime: these are a phone number,
        # a grid connection id and a station id met in real files
        (["0680428426"], False, None),
        (["0000000000000"], False, None),
        (["91000906"], False, None),
        # a packed value has nowhere to carry a zone
        (["202501010000"], True, None),
    ],
)
def test_datetime_format_inferred_from_column(values, aware, expected_format):
    infer = datetime_aware_infer if aware else datetime_naive_infer
    assert infer(values) == expected_format


@pytest.mark.parametrize(
    "value, fmt, expected",
    [
        ("15 décembre 1985", "csvd:%d %b %Y", _datetime(1985, 12, 15)),
        ("15 Janv. 1985", "csvd:%d %b %Y", _datetime(1985, 1, 15)),
        ("15-dec-85", "csvd:%d-%b-%y", _datetime(1985, 12, 15)),
        ("15-dec-05", "csvd:%d-%b-%y", _datetime(2005, 12, 15)),
        # an optional part is read whether the value carries it or not
        ("2021-06-22 10:20:10", "csvd:%Y-%m-%d %H:%M:%S[.%f]", _datetime(2021, 6, 22, 10, 20, 10)),
        (
            "2021-06-22 10:20:10.5",
            "csvd:%Y-%m-%d %H:%M:%S[.%f]",
            _datetime(2021, 6, 22, 10, 20, 10, 500000),
        ),
        ("31st december 2022", "csvd:%d %b %Y", _datetime(2022, 12, 31)),
        (
            "1996/06/22 10:20:10 GMT",
            "csvd:%Y/%m/%d %H:%M:%S %Z",
            _datetime(1996, 6, 22, 10, 20, 10, tzinfo=_timezone.utc),
        ),
        ("31 février 1996", "csvd:%d %b %Y", None),  # not a real day of that month
        ("15 tambour 1985", "csvd:%d %b %Y", None),
        # a separated value is shaped like a date whatever its year: archives and civil
        # registers go back well before 1900, and nothing else reads like "15 dec 1850"
        ("15 dec 1850", "csvd:%d %b %Y", _datetime(1850, 12, 15)),
        ("1850-12-15", "%Y-%m-%d", _datetime(1850, 12, 15)),
        ("12-04-0012", "%d-%m-%Y", _datetime(12, 4, 12)),
        ("9999-12-31", "%Y-%m-%d", _datetime(9999, 12, 31)),  # the usual "no end date" sentinel
        # eight bare digits are just a number, so this shape alone keeps a year window
        ("18501215", "%Y%m%d", None),
        ("21501215", "%Y%m%d", None),
        ("19501215", "%Y%m%d", _datetime(1950, 12, 15)),
    ],
)
def test_parse(value, fmt, expected):
    assert parse(value, fmt) == expected


def test_every_month_name_reads_as_its_own_month():
    for language, months in MONTH_NAMES.items():
        for number, names in enumerate(months, start=1):
            for name in names:
                assert MONTHS.get(name) == number, (
                    f"{name} ({language}) does not read as month {number}"
                )


def test_a_spelling_meaning_two_months_is_dropped():
    # no current entry collides, so this guards the languages a later PR could add
    first = [[f"a{number}"] for number in range(1, 13)]
    second = [[f"b{number}"] for number in range(1, 13)]
    first[0].append("shared")  # january in one language...
    second[4].append("shared")  # ...may in the other
    index = build_month_index({"first": first, "second": second})
    assert "shared" not in index
    assert index["a1"] == 1 and index["b5"] == 5


@pytest.mark.parametrize(
    "value, infer",
    (
        ("1960-08-07", date_infer),
        ("20030502", date_infer),
        ("12/02/2007", date_infer),
        ("12/02/85", date_infer),
        ("2003.05.02", date_infer),
        ("15 décembre 1985", date_infer),
        ("15-dec-85", date_infer),
        ("31st december 2022", date_infer),
        ("2021-06-22 10:20:10", datetime_naive_infer),
        ("2030/06/22 00:00:00.0028", datetime_naive_infer),
        ("1996/06/22 10:20", datetime_naive_infer),
        ("2021-06-22 10:20:10-04:00", datetime_aware_infer),
        ("2000-12-21 10:20:10.1Z", datetime_aware_infer),
        ("2024-12-19T10:53:36.428000+00:00", datetime_aware_infer),
        ("2021-06-22 10:20:10 +02:00", datetime_aware_infer),
        ("1996/06/22 10:20:10 GMT", datetime_aware_infer),
    ),
)
def test_an_unmarked_format_reads_the_same_through_strptime(value, infer):
    """The marker is a contract, so the formats without it have to honour it.

    A consumer reading `date_format` out of an analysis may well hand it to strptime rather than
    call parse(). The marker is what tells it not to; a format that carries no marker yet reads
    differently through strptime would silently give that consumer another date — which is how
    `%Z` used to drop the timezone.
    """
    fmt = infer([value])
    assert fmt is not None, f"{value} should be inferred"
    if fmt.startswith(CUSTOM_PREFIX):
        return
    assert _datetime.strptime(value, fmt) == parse(value, fmt)


@pytest.mark.parametrize(
    "value, infer, expected_format",
    (
        # strptime only knows the abbreviated months of the process locale
        ("15 décembre 1985", date_infer, "csvd:%d %b %Y"),
        # strptime has no syntax for an optional part
        ("2021-06-22 10:20:10", datetime_naive_infer, "csvd:%Y-%m-%d %H:%M:%S[.%f]"),
        # strptime reads the zone name then drops it, leaving a naive datetime
        ("1996/06/22 10:20:10 GMT", datetime_aware_infer, "csvd:%Y/%m/%d %H:%M:%S %Z"),
    ),
)
def test_a_format_strptime_cannot_read_is_marked(value, infer, expected_format):
    # the second value is what forces the optional part, and is dropped for the other two
    values = [value, "2021-06-22 10:20:10.5"] if "[" in expected_format else [value]
    assert infer(values) == expected_format


def test_strptime_silently_drops_the_zone_a_marked_format_keeps():
    # the divergence the marker exists for: no error, just another datetime
    value, fmt = "1996/06/22 10:20:10 GMT", "%Y/%m/%d %H:%M:%S %Z"
    assert _datetime.strptime(value, fmt).tzinfo is None
    assert parse(value, CUSTOM_PREFIX + fmt) == _datetime(
        1996, 6, 22, 10, 20, 10, tzinfo=_timezone.utc
    )


def test_the_year_window_only_guards_the_separator_less_shape():
    # a datetime built on the bare-digits date inherits the window...
    assert parse("21501215T10:20:10", "%Y%m%dT%H:%M:%S") is None
    assert parse("19501215T10:20:10", "%Y%m%dT%H:%M:%S") == _datetime(1950, 12, 15, 10, 20, 10)
    # ...where the same value written with a separator keeps none
    assert parse("2150-12-15 10:20:10", "%Y-%m-%d %H:%M:%S") == _datetime(2150, 12, 15, 10, 20, 10)


@pytest.mark.parametrize(
    "values, expected_format, expected_dates",
    [
        (
            ["07/03/2024", "25/12/2024"],
            "%d/%m/%Y",
            [_date(2024, 3, 7), _date(2024, 12, 25)],
        ),
        (
            ["07/03/2024", "12/25/2024"],
            "%m/%d/%Y",
            [_date(2024, 7, 3), _date(2024, 12, 25)],
        ),
        (
            ["07/03/2024", "01/02/2024"],
            "%d/%m/%Y",
            [_date(2024, 3, 7), _date(2024, 2, 1)],
        ),
        (
            ["15 jan 1985", "13 février 1996"],
            "csvd:%d %b %Y",
            [_date(1985, 1, 15), _date(1996, 2, 13)],
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


def test_column_without_a_single_format_is_not_a_date(tmp_path):
    # the values contradict each other: no format reads them all, so this is not a date column
    values = ["25/12/2024", "12/25/2024"]
    file_path = tmp_path / "dates.csv"
    file_path.write_text("date;label\n" + "".join(f"{value};a\n" for value in values * 5))
    analysis = routine(file_path=str(file_path), num_rows=-1, save_results=False)
    assert analysis["columns"]["date"]["python_type"] == "string"
    assert "date_format" not in analysis["columns"]["date"]


def test_every_detected_date_column_comes_with_a_format(tmp_path):
    values = ["07/03/2024", "25/12/2024"]
    file_path = tmp_path / "dates.csv"
    file_path.write_text(
        "date;datetime;label\n" + "".join(f"{value};{value} 10:20:10;a\n" for value in values * 5)
    )
    analysis = routine(file_path=str(file_path), num_rows=-1, save_results=False)
    for col_name, detection in analysis["columns"].items():
        if detection["python_type"] in ("date", "datetime"):
            assert detection.get("date_format"), f"{col_name} has no format to be read with"


def test_a_tolerant_proportion_keeps_detecting_without_a_format(tmp_path):
    # asking for tolerance contradicts pinning down one format that reads every value:
    # the column stays a date, scored as before, and carries no format
    values = ["07/03/2024"] * 9 + ["not a date"]
    file_path = tmp_path / "dates.csv"
    file_path.write_text("date;label\n" + "".join(f"{value};a\n" for value in values))
    analysis = routine(
        file_path=str(file_path),
        num_rows=-1,
        save_results=False,
        custom_proportions={"date": 0.8},
    )
    assert analysis["columns"]["date"]["python_type"] == "date"
    assert "date_format" not in analysis["columns"]["date"]


def test_dates_in_a_list_output_carry_their_format(tmp_path):
    file_path = tmp_path / "dates.csv"
    file_path.write_text("date;label\n" + "".join("07/03/2024;a\n" for _ in range(10)))
    analysis = routine(
        file_path=str(file_path),
        num_rows=-1,
        save_results=False,
        limited_output=False,
    )
    date_detection = next(
        detection for detection in analysis["columns"]["date"] if detection["format"] == "date"
    )
    assert date_detection["date_format"] == "%d/%m/%Y"


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
    assert analysis["columns"]["date"]["date_format"] == "%m/%d/%Y"


@pytest.mark.parametrize(
    "values, expected_format, expected_datetimes",
    [
        (
            ["07/03/2024 10:20:10", "25/12/2024 10:20:10"],
            "%d/%m/%Y %H:%M:%S",
            [_datetime(2024, 3, 7, 10, 20, 10), _datetime(2024, 12, 25, 10, 20, 10)],
        ),
        (
            ["07/03/2024 10:20:10", "12/25/2024 10:20:10"],
            "%m/%d/%Y %H:%M:%S",
            [_datetime(2024, 7, 3, 10, 20, 10), _datetime(2024, 12, 25, 10, 20, 10)],
        ),
        (
            ["07/03/2024 10:20:10", "01/02/2024 10:20:10"],
            "%d/%m/%Y %H:%M:%S",
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
        ("2022-08-01", "date", "%Y-%m-%d", _date(2022, 8, 1)),
        # dateutil reads 12/02 as MM/DD (US) where the column said DD/MM
        ("12/02/2007", "date", "%d/%m/%Y", _date(2007, 2, 12)),
        ("15 décembre 1985", "date", "csvd:%d %b %Y", _date(1985, 12, 15)),
        (
            "2024-09-23 17:32:07",
            "datetime",
            "%Y-%m-%d %H:%M:%S",
            _datetime(2024, 9, 23, 17, 32, 7),
        ),
        # no format: an analysis generated before the inference existed
        ("2022-08-01", "date", None, _date(2022, 8, 1)),
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
