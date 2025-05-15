import json

import pandas as pd
import pytest

from csv_detective.explore_csv import validate_then_detect
from csv_detective.validate import validate


def set_nested_value(source_dict: dict, key_chain: list[str], value):
    current_dict = source_dict
    for key in key_chain[:-1]:
        if key not in current_dict:
            current_dict[key] = {}
        current_dict = current_dict[key]
    current_dict[key_chain[-1]] = value


def get_nested_value(source_dict: dict, key_chain: list[str]):
    result = source_dict
    for k in key_chain:
        result = result[k]
    return result


@pytest.mark.parametrize(
    "_params",
    (
        ((True, pd.DataFrame, dict), {}),
        ((False, None, None), {"separator": "|"}),
        ((False, None, None), {"encoding": "unknown"}),
        ((False, None, None), {"header": ["a", "b"]}),
        ((False, pd.DataFrame, dict), {
            "columns.NUMCOM": {
                "python_type": "int",
                "format": "int",
                "score": 1.0,
            },
        }),
    ),
)
def test_validation(_params):
    (should_be_valid, table_type, analysis_type), modif_previous_analysis = _params
    with open("tests/data/a_test_file.json", "r") as f:
        previous_analysis = json.load(f)
    for dotkey in modif_previous_analysis:
        keys = dotkey.split(".")
        set_nested_value(previous_analysis, keys, modif_previous_analysis[dotkey])
    is_valid, table, analysis = validate(
        "tests/data/a_test_file.csv",
        previous_analysis=previous_analysis,
        num_rows=-1,
        sep=previous_analysis.get("separator"),
        encoding=previous_analysis.get("encoding"),
    )
    assert is_valid == should_be_valid
    if table_type is None:
        assert table is None
    else:
        assert isinstance(table, table_type)
    if analysis_type is None:
        assert analysis is None
    else:
        assert isinstance(analysis, analysis_type)


@pytest.mark.parametrize(
    "modif_previous_analysis",
    (
        {"separator": "|"},
        {"encoding": "unknown"},
        {"header": ["a", "b"]},
        {"total_lines": 100},
        {
            "columns.NUMCOM": {
                "python_type": "int",
                "format": "int",
                "score": 1.0,
            },
        },
    ),
)
def test_validate_then_detect(modif_previous_analysis):
    with open("tests/data/a_test_file.json", "r") as f:
        previous_analysis = json.load(f)
    valid_values = {}
    for dotkey in modif_previous_analysis:
        keys = dotkey.split(".")
        valid_values[dotkey] = get_nested_value(previous_analysis, keys)
        set_nested_value(previous_analysis, keys, modif_previous_analysis[dotkey])
    analysis = validate_then_detect(
        "tests/data/a_test_file.csv",
        previous_analysis=previous_analysis,
        num_rows=-1,
        output_profile=True,
        save_results=False,
    )
    # checking that if not valid, the analysis has managed to retrieve the right values
    for dotkey in modif_previous_analysis:
        assert get_nested_value(analysis, dotkey.split(".")) == valid_values[dotkey]
