import pytest

from csv_detective.format import FormatsManager

fmtm = FormatsManager()

# money labels
def test_money_labels():
    header = "Montant total"
    assert fmtm.formats["money"].is_valid_label(header) == 0.5


@pytest.mark.parametrize(
    "params",
    [
        ("latitude", 1.0),
        ("lat", 1.0),
        ("coord_lat", 0.5),
        ("y", 1.0),
        ("nb_cycles", 0.0),
    ],
)
def test_latitude(params):
    header, expected = params
    assert expected == fmtm.formats["latitude_wgs"].is_valid_label(header)
