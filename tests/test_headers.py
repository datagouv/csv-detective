import pytest

from csv_detective.format import FormatsManager

fmtm = FormatsManager()


# money headers
def test_money_headers():
    header = "Montant total"
    assert fmtm.formats["money"].header_score(header) == 0.5


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
    header, expected = params
    assert expected == fmtm.formats["latitude_wgs"].header_score(header)


def test_former_names_still_work():
    latitude = fmtm.formats["latitude_wgs"]
    with pytest.deprecated_call():
        assert latitude.labels == latitude.headers
    with pytest.deprecated_call():
        assert latitude.mandatory_label is True
    with pytest.deprecated_call():
        assert latitude.is_valid_label("latitude") == 1.0
    with pytest.deprecated_call():
        assert fmtm.get_formats_with_mandatory_label() == fmtm.get_formats_with_mandatory_header()
