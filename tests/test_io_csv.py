import pandas as pd

from csv_detective.io.csv import read_csv


def test_read_csv_respects_skiprows_and_leading_zeros():
    dataframe = read_csv(
        "tests/data/a_test_file.csv",
        sep=";",
        skiprows=2,
        nrows=3,
        encoding="utf-8",
    )
    assert dataframe.iloc[0]["NUMCOM"] == "01001"


def test_read_csv_chunks():
    chunks = read_csv(
        "tests/data/a_test_file.csv",
        sep=";",
        skiprows=2,
        chunksize=100,
        encoding="utf-8",
    )
    first_chunk = next(chunks)
    assert isinstance(first_chunk, pd.DataFrame)
    assert len(first_chunk) == 100


def test_read_csv_unnamed_columns():
    from io import StringIO

    content = "col1,col2,\n1,2,\n3,4,"
    dataframe = read_csv(StringIO(content), sep=",", skiprows=0)
    assert list(dataframe.columns) == ["col1", "col2", "Unnamed: 2"]
