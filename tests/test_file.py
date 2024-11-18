from csv_detective import routine
import pytest
import responses


def test_columns_output_on_file():
    output = routine(
        csv_file_path="tests/a_test_file.csv",
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
    assert output["total_lines"] == 414
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
        csv_file_path="tests/a_test_file.csv",
        num_rows=-1,
        output_profile=True,
        save_results=False,
    )
    assert all(
        [
            c in list(output["profile"]["NUMCOM"].keys())
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
    assert len(output["profile"]["NOMCOM"].keys()) == 3
    assert output["profile"]["NUMCOM"]["min"] == 1001
    assert output["profile"]["NUMCOM"]["max"] == 6125
    assert round(output["profile"]["NUMCOM"]["mean"]) == 1245
    assert round(output["profile"]["NUMCOM"]["std"]) == 363
    assert output["profile"]["TXCOUVGLO_COM_2014"]["nb_distinct"] == 296
    assert output["profile"]["TXCOUVGLO_COM_2014"]["nb_missing_values"] == 3
    assert output["profile"]["GEO_INFO"]["nb_distinct"] == 1


def test_exception():
    with pytest.raises(ValueError):
        routine(
            csv_file_path="tests/a_test_file.csv",
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
            csv_file_path="tests/c_test_file.csv",
            num_rows=-1,
            output_profile=True,
            save_results=False,
        )


def test_code_dep_reg_on_file():
    output = routine(
        csv_file_path="tests/b_test_file.csv",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert isinstance(output, dict)
    assert output["columns"]["code_departement"]["format"] == "code_departement"
    assert output["columns"]["code_region"]["format"] == "code_region"


def test_schema_on_file():
    output = routine(
        csv_file_path="tests/b_test_file.csv",
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


def test_non_csv_files():
    _ = routine(
        csv_file_path="tests/file.ods",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert _['engine'] == 'odf'

    # this is a "tricked" xls file that is actually read as odf
    _ = routine(
        csv_file_path="tests/file.xls",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert _['engine'] == 'odf'

    _ = routine(
        csv_file_path="tests/file.xlsx",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert _['engine'] == 'openpyxl'
    # this file has an empty first row
    assert _['header_row_idx'] == 1
    # check if the sheet we consider is the largest
    assert _['sheet_name'] == 'REI_1987'

    _ = routine(
        csv_file_path="tests/csv_file",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert not _.get('engine')
    assert not _.get('sheet_name')

    _ = routine(
        csv_file_path="tests/xlsx_file",
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert _['engine'] == 'openpyxl'


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_urls(mocked_responses):
    url = 'http://example.com/test.csv'
    expected_content = 'id,name,first_name\n1,John,Smith\n2,Jane,Doe\n3,Bob,Johnson'
    mocked_responses.get(
        url,
        body=expected_content,
        status=200,
    )
    output = routine(
        csv_file_path=url,
        num_rows=-1,
        output_profile=False,
        save_results=False,
    )
    assert output['header'] == ["id", "name", "first_name"]


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
        csv_file_path="tests/b_test_file.csv",
        num_rows=-1,
        save_results=False,
        skipna=skipna,
    )
    assert output["columns"]["partly_empty"]["python_type"] == expected_type
