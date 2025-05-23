import pytest

from csv_detective.detect_labels import latitude_wgs, money


# money labels
def test_money_labels():
    header = "Montant total"
    assert money._is(header) == 0.5


@pytest.mark.parametrize(
    "params", [
        ("latitude", 1.0),
        ("lat", 1.0),
        ("coord_lat", 0.5),
        ("y", 1.0),
        ("nb_cycles", 0.0),
    ]
)
def test_latitude(params):
    header, expected = params
    assert expected == latitude_wgs._is(header)
