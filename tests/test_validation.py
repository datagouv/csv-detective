import json
from unittest.mock import MagicMock, patch

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
        ((True, dict), {}),
        ((False, None), {"separator": "|"}),
        ((False, None), {"encoding": "unknown"}),
        ((False, None), {"header": ["a", "b"]}),
        (
            (False, None),
            {
                "columns.NUMCOM": {
                    "python_type": "int",
                    "format": "int",
                    "score": 1.0,
                },
            },
        ),
    ),
)
def test_validation(_params):
    (should_be_valid, analysis_type), modif_previous_analysis = _params
    with open("tests/data/a_test_file.json", "r") as f:
        previous_analysis = json.load(f)
    for dotkey in modif_previous_analysis:
        keys = dotkey.split(".")
        set_nested_value(previous_analysis, keys, modif_previous_analysis[dotkey])
    is_valid, analysis, col_values = validate(
        "tests/data/a_test_file.csv",
        previous_analysis=previous_analysis,
    )
    assert is_valid == should_be_valid
    if analysis_type is None:
        assert analysis is None
    else:
        assert isinstance(analysis, analysis_type)
    if should_be_valid:
        assert isinstance(col_values, dict)
    else:
        assert col_values is None


@pytest.mark.parametrize(
    "_params",
    (
        # int: proportion = 1, should fail (early)
        ("12", "1.2", {"python_type": "int", "format": "int", "score": 1.5}, False),
        # siren: proportion = 0.9, should fail (later)
        (
            "130025265",
            "A13794BC",
            {"python_type": "string", "format": "siren", "score": 1.5},
            False,
        ),
        # siret: proportion = 0.8, should succeed
        (
            "13002526500013",
            "A13794BC",
            {"python_type": "string", "format": "siret", "score": 1.5},
            True,
        ),
    ),
)
def test_validation_with_proportions(_params):
    # testing the behaviour for a file that has 15% invalid values, but all in a single chunk
    valid_value, invalid_value, detected, should_be_valid = _params
    url = f"http://example.com/test.csv"
    expected_content = "col\n"
    for _ in range(60):
        # 60 rows of valid values
        expected_content += f"{valid_value}\n"
    for _ in range(15):
        # 15 rows of invalid values
        expected_content += f"{invalid_value}\n"
    for _ in range(25):
        # 25 rows of valid values
        expected_content += f"{valid_value}\n"
    previous_analysis = {
        "encoding": "utf-8",
        "separator": ",",
        "header_row_idx": 0,
        "header": ["col"],
        "columns": {"col": detected},
        # just setting these keys when validation is successful, they're not used for the validation itself
        "categorical": [],
        "columns_fields": {},
        "columns_labels": {},
        "formats": {},
    }
    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("csv_detective.validate.VALIDATION_CHUNK_SIZE", 10),
    ):
        mock_response = MagicMock()
        mock_response.read.return_value = expected_content.encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        is_valid, *_ = validate(
            file_path=url,
            previous_analysis=previous_analysis,
        )
    assert is_valid == should_be_valid


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
