from unittest.mock import MagicMock, patch

import pandas as pd

from csv_detective.format import Format, FormatsManager, get_leaf_formats
from csv_detective.parsing.columns import test_col as col_test


def _make_format(name: str, *, parent: str | None = None) -> Format:
    return Format(
        name=name,
        description=name,
        func=MagicMock(return_value=True),
        _test_values={True: ["a"], False: ["b"]},
        parent=parent,
    )


def test_get_leaf_formats_excludes_parents():
    formats = {
        "float": _make_format("float"),
        "latitude_wgs": _make_format("latitude_wgs", parent="float"),
        "latitude_wgs_fr_metropole": _make_format(
            "latitude_wgs_fr_metropole", parent="latitude_wgs"
        ),
        "email": _make_format("email"),
    }
    leaves = get_leaf_formats(formats)
    assert set(leaves) == {"latitude_wgs_fr_metropole", "email"}


def test_parent_score_propagated_when_child_matches():
    child_func = MagicMock(return_value=True)
    parent_func = MagicMock(return_value=True)
    formats = {
        "float": Format(
            name="float",
            description="float",
            func=parent_func,
            _test_values={True: ["1.0"], False: ["x"]},
        ),
        "latitude_wgs": Format(
            name="latitude_wgs",
            description="latitude_wgs",
            func=MagicMock(return_value=True),
            _test_values={True: ["45.0"], False: ["x"]},
            parent="float",
        ),
        "latitude_wgs_fr_metropole": Format(
            name="latitude_wgs_fr_metropole",
            description="latitude_wgs_fr_metropole",
            func=child_func,
            _test_values={True: ["45.0"], False: ["x"]},
            parent="latitude_wgs",
        ),
    }
    table = pd.DataFrame({"col": ["45.0"] * 10})

    with patch(
        "csv_detective.parsing.columns.test_col_val",
        side_effect=lambda serie, fmt, **kwargs: 1.0
        if fmt.name == "latitude_wgs_fr_metropole"
        else 0.0,
    ) as mock_test_col_val:
        result = col_test(table, formats, limited_output=True)

    assert result.loc["latitude_wgs_fr_metropole", "col"] == 1.0
    assert result.loc["latitude_wgs", "col"] == 1.0
    assert result.loc["float", "col"] == 1.0
    tested_formats = {call.args[1].name for call in mock_test_col_val.call_args_list}
    assert tested_formats == {"latitude_wgs_fr_metropole"}


def test_parent_tested_when_child_scores_zero():
    formats = {
        "float": Format(
            name="float",
            description="float",
            func=lambda v: str(v).replace(".", "", 1).isdigit(),
            _test_values={True: ["1.0"], False: ["x"]},
        ),
        "latitude_wgs": Format(
            name="latitude_wgs",
            description="latitude_wgs",
            func=lambda v: False,
            _test_values={True: ["45.0"], False: ["x"]},
            parent="float",
        ),
        "latitude_wgs_fr_metropole": Format(
            name="latitude_wgs_fr_metropole",
            description="latitude_wgs_fr_metropole",
            func=lambda v: False,
            _test_values={True: ["45.0"], False: ["x"]},
            parent="latitude_wgs",
        ),
    }
    table = pd.DataFrame({"col": ["1.0"] * 10})
    result = col_test(table, formats, limited_output=True)

    assert result.loc["latitude_wgs_fr_metropole", "col"] == 0.0
    assert result.loc["latitude_wgs", "col"] == 0.0
    assert result.loc["float", "col"] == 1.0


def test_output_dataframe_includes_all_formats():
    fmtm = FormatsManager()
    table = pd.DataFrame({"a": ["1"], "b": ["test@example.com"]})
    result = col_test(table, fmtm.formats, limited_output=True)

    assert set(result.index) == set(fmtm.formats)
    assert list(result.columns) == ["a", "b"]
    assert all(pd.api.types.is_float_dtype(dtype) for dtype in result.dtypes)


def test_parent_retested_when_child_score_below_parent_proportion():
    formats = {
        "float": Format(
            name="float",
            description="float",
            func=MagicMock(return_value=True),
            _test_values={True: ["1.0"], False: ["x"]},
            proportion=1,
        ),
        "latitude_wgs": Format(
            name="latitude_wgs",
            description="latitude_wgs",
            func=MagicMock(return_value=True),
            _test_values={True: ["45.0"], False: ["x"]},
            parent="float",
            proportion=0.8,
        ),
    }
    table = pd.DataFrame({"col": ["45.0"] * 10})

    with patch(
        "csv_detective.parsing.columns.test_col_val",
        side_effect=lambda serie, fmt, **kwargs: 0.85 if fmt.name == "latitude_wgs" else 1.0,
    ) as mock_test_col_val:
        result = col_test(table, formats, limited_output=True)

    assert result.loc["latitude_wgs", "col"] == 0.85
    assert result.loc["float", "col"] == 1.0
    tested_formats = {call.args[1].name for call in mock_test_col_val.call_args_list}
    assert tested_formats == {"latitude_wgs", "float"}


def test_formats_manager_loads_parent_from_module():
    fmtm = FormatsManager()
    assert fmtm.formats["latitude_wgs_fr_metropole"].parent == "latitude_wgs"
    assert fmtm.formats["geojson"].parent == "json"
    assert fmtm.formats["float"].parent is None
