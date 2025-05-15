import json

import pandas as pd
import pytest

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
        ((False, pd.DataFrame, dict), {"separator": "|"}),
        ((False, None, None), {"encoding": "unknown"}),
        ((False, pd.DataFrame, dict), {"columns": {
            "a": {
                "python_type": "int",
                "format": "int",
                "score": 1.0,
            },
            "b": {
                "python_type": "string",
                "format": "siret",
                "score": 1.0,
            },
        }}),
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
