import pytest

from csv_detective.format import FormatsManager

fmtm = FormatsManager()


# money column names
def test_money_column_names():
    column_name = "Montant total"
    assert fmtm.formats["money"].column_name_score(column_name) == 0.5


@pytest.mark.parametrize(
    "params",
    [
        ("latitude", 1.0),
        ("lat", 0.75),
        ("coord_lat", 0.375),
        ("y", 0.5),
        ("nb_cycles", 0.0),
    ],
)
def test_latitude(params):
    column_name, expected = params
    assert expected == fmtm.formats["latitude_wgs"].column_name_score(column_name)


def test_former_names_still_work():
    latitude = fmtm.formats["latitude_wgs"]
    with pytest.deprecated_call():
        assert latitude.labels == latitude.column_names
    with pytest.deprecated_call():
        assert latitude.mandatory_label is True
    with pytest.deprecated_call():
        assert latitude.is_valid_label("latitude") == 1.0
    with pytest.deprecated_call():
        assert (
            fmtm.get_formats_with_mandatory_label() == fmtm.get_formats_with_mandatory_column_name()
        )
