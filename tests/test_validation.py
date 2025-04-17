import json

import pandas as pd

from csv_detective.validate import validate


def test_validation():
    with open("tests/data/a_test_file.json", "r") as f:
        previous_analysis = json.load(f)
    is_valid, table, analysis = validate(
        "tests/data/a_test_file.csv",
        previous_analysis=previous_analysis,
        num_rows=-1,
    )
    assert is_valid is True
    assert isinstance(table, pd.DataFrame)
    assert isinstance(analysis, dict)
