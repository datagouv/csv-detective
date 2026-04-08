"""Fix for validate.py crash on empty columns with pandas StringDtype.

In some pandas versions, pd.Series([], dtype="string").sum() returns ""
instead of 0, causing TypeError when comparing with len(to_check).
The fix is to skip empty columns (after dropna) since there's nothing to validate.
"""

import pandas as pd

from csv_detective.validate import validate


def test_validate_with_all_nan_column_in_csv():
    """Column entirely NaN in a chunk must not crash validate."""
    previous_analysis = {
        "header": ["a", "b"],
        "columns": {
            "a": {"format": "int", "python_type": "int", "score": 1.0},
            "b": {"format": "int", "python_type": "int", "score": 1.0},
        },
        "encoding": "utf-8",
        "separator": "|",
        "header_row_idx": 0,
        "heading_columns": 0,
        "trailing_columns": 0,
        "categorical": [],
        "columns_fields": {},
        "columns_labels": {},
        "formats": {},
    }
    is_valid, _, _ = validate(
        pd.io.common.StringIO("a|b\n1|\n2|\n"),
        previous_analysis,
    )
    assert is_valid
