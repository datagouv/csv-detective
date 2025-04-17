import pandas as pd
import pytest
import responses

from csv_detective import routine


def test_columns_output_on_file():
    output = routine(
        file_path="tests/data/a_test_file.csv",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert isinstance(output, dict)
    assert output["separator"] == ";"
    assert output["header_row_idx"] == 2
    assert output["header"] == [
        "NUMCOM",
        "NOMCOM",
        "NUMDEP",
        "NOMDEP",
        "NUMEPCI",
        "NOMEPCI",
        "TXCOUVGLO_COM_2014",
        "TXCOUVGLO_DEP_2014",
        "TXCOUVGLO_EPCI_2014",
        "STRUCTURED_INFO",
        "GEO_INFO",
    ]
    assert output["total_lines"] == 404
    assert output["nb_duplicates"] == 7
    assert output["columns"]["NOMCOM"]["format"] == "commune"
    assert output["columns"]["NOMDEP"]["format"] == "departement"
    assert output["columns"]["NUMEPCI"]["format"] == "siren"
    assert output["columns"]["STRUCTURED_INFO"]["python_type"] == "json"
    assert output["columns"]["STRUCTURED_INFO"]["format"] == "json"
    assert output["columns"]["GEO_INFO"]["python_type"] == "json"
    assert output["columns"]["GEO_INFO"]["format"] == "json_geojson"


def test_profile_output_on_file():
    output = routine(
        file_path="tests/data/a_test_file.csv",
        num_rows=-1,
        output_profile=True,
        save_results=False,
    )
    assert all(
        [
            c in list(output["profile"]["TXCOUVGLO_COM_2014"].keys())
            for c in [
                "min",
                "max",
                "mean",
                "std",
                "tops",
                "nb_distinct",
                "nb_missing_values",
            ]
        ]
    )
    assert not any(
        [
            c in list(output["profile"]["NUMCOM"].keys())
            for c in [
                    "min",
                    "max",
                    "mean",
                    "std",
            ]
        ]
    )
    assert output["profile"]["TXCOUVGLO_COM_2014"]["min"] == 0.0
    assert output["profile"]["TXCOUVGLO_COM_2014"]["max"] == 200.2
    assert round(output["profile"]["TXCOUVGLO_COM_2014"]["mean"]) == 60
    assert round(output["profile"]["TXCOUVGLO_COM_2014"]["std"]) == 36
    assert output["profile"]["TXCOUVGLO_COM_2014"]["nb_distinct"] == 290
    assert output["profile"]["TXCOUVGLO_COM_2014"]["nb_missing_values"] == 3
    assert output["profile"]["GEO_INFO"]["nb_distinct"] == 1


def test_profile_with_num_rows():
    with pytest.raises(ValueError):
        routine(
            file_path="tests/data/a_test_file.csv",
            num_rows=50,
            output_profile=True,
            save_results=False,
        )


def test_exception_different_number_of_columns():
    """
    A ValueError should be raised if the number of columns differs between the first rows
    """
    with pytest.raises(ValueError):
        routine(
            file_path="tests/data/c_test_file.csv",
            num_rows=-1,
            output_profile=True,
            save_results=False,
        )


def test_code_dep_reg_on_file():
    output = routine(
        file_path="tests/data/b_test_file.csv",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert isinstance(output, dict)
    assert output["columns"]["code_departement"]["format"] == "code_departement"
    assert output["columns"]["code_region"]["format"] == "code_region"


def test_schema_on_file():
    output = routine(
        file_path="tests/data/b_test_file.csv",
        num_rows=-1,
        output_schema=True,
        save_results=False,
    )
    assert isinstance(output, dict)
    is_column_dep = False
    is_column_reg = False
    for item in output["schema"]["fields"]:
        if item["name"] == "code_departement":
            is_column_dep = True
            assert item["description"] == "Le code INSEE du département"
            assert item["type"] == "string"
            assert item["formatFR"] == "code_departement"
            assert item["constraints"]["pattern"] == "^(([013-9]\\d|2[AB1-9])$|9\\d{2}$)"
        if item["name"] == "code_region":
            is_column_reg = True
            assert item["description"] == "Le code INSEE de la région"
            assert item["type"] == "string"
            assert item["formatFR"] == "code_region"
            assert item["constraints"]["pattern"] == "^\\d{2}$"
    assert is_column_dep
    assert is_column_reg


params_csv = [
    ("csv_file", {"engine": None, "sheet_name": None}),
    ("file.csv.gz", {"engine": None, "sheet_name": None, "separator": ",", "columns.len": 3}),
]
params_others = [
    ("file.ods", {"engine": "odf"}),
    # this is a "tricked" xls file that is actually read as odf
    ("file.xls", {"engine": "odf"}),
    # this file has an empty first row; check if the sheet we consider is the largest
    ("file.xlsx", {"engine": "openpyxl", "header_row_idx": 1, "sheet_name": "REI_1987"}),
    ("xlsx_file", {"engine": "openpyxl"}),
]


@pytest.mark.parametrize("params", params_csv + params_others)
def test_non_csv_files(params):
    file_name, checks = params
    _ = routine(
        file_path=f"tests/data/{file_name}",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    for k, v in checks.items():
        if v is None:
            assert not _.get(k)
        elif "." in k:
            key, func = k.split(".")
            assert eval(func)(_[key]) == v
        else:
            assert _[k] == v


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.mark.parametrize(
    "params",
    # ideally we'd like to do the same with params_others but pandas.read_excel uses urllib
    # which doesn't support the way we mock the response, TBC
    params_csv + [("a_test_file.csv", {"separator": ";", "header_row_idx": 2, "total_lines": 404})]
)
def test_urls(mocked_responses, params):
    file_name, checks = params
    url = f"http://example.com/{file_name}"
    mocked_responses.get(
        url,
        body=open(f"tests/data/{file_name}", "rb").read(),
        status=200,
    )
    _ = routine(
        file_path=url,
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    for k, v in checks.items():
        if v is None:
            assert not _.get(k)
        elif "." in k:
            key, func = k.split(".")
            assert eval(func)(_[key]) == v
        else:
            assert _[k] == v


@pytest.mark.parametrize(
    "expected_type",
    (
        (True, "int"),
        (False, "string"),
    ),
)
def test_nan_values(expected_type):
    # if skipping NaN, the column contains only ints
    skipna, expected_type = expected_type
    output = routine(
        file_path="tests/data/b_test_file.csv",
        num_rows=-1,
        save_results=False,
        skipna=skipna,
    )
    assert output["columns"]["partly_empty"]["python_type"] == expected_type


def test_output_df():
    output, df = routine(
        file_path="tests/data/b_test_file.csv",
        num_rows=-1,
        output_profile=False,
        save_results=False,
        output_df=True,
    )
    assert isinstance(output, dict)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6
    assert df["partly_empty"].dtype == pd.Int64Dtype()


@pytest.mark.parametrize(
    "cast_json",
    (
        (True, dict),
        (False, str),
    ),
)
def test_cast_json(mocked_responses, cast_json):
    cast_json, expected_type = cast_json
    expected_content = 'id,a_simple_dict\n1,{"a": 1}\n2,{"b": 2}\n3,{"c": 3}\n'
    mocked_responses.get(
        'http://example.com/test.csv',
        body=expected_content,
        status=200,
    )
    analysis, df = routine(
        file_path='http://example.com/test.csv',
        num_rows=-1,
        output_profile=False,
        save_results=False,
        output_df=True,
        cast_json=cast_json,
    )
    assert analysis['columns']["a_simple_dict"]["python_type"] == "json"
    assert isinstance(df["a_simple_dict"][0], expected_type)
