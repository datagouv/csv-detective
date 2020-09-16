import pandas as pd
import numpy as np

from csv_detective.detect_labels.other import money

# money labels
def test_money_labels():
    serie = pd.Series(name='montant total', data=['4.0', '1.0', '1.0'])
    assert all(money._is(serie) == np.ones(serie.shape[0]))