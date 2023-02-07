from csv_detective.detect_labels.other import money


# money labels
def test_money_labels():
    header = "Montant total"
    assert money._is(header) == 1.0
