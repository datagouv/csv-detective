import pandas as pd

from csv_detective.io.parquet import ParquetTable, load_parquet, rugo_logical_type_to_python


def test_load_parquet_metadata():
    table = load_parquet("tests/data/file.parquet")
    assert isinstance(table, ParquetTable)
    assert table.num_rows == 1000
    assert table.column_names[0] == "inseecommune"


def test_rugo_logical_type_mapping():
    assert rugo_logical_type_to_python("varchar") == "string"
    assert rugo_logical_type_to_python("array<int64>") == "json"
    assert rugo_logical_type_to_python("timestamp[ns]") == "datetime_naive"


def test_iter_batches_returns_dataframe():
    table = load_parquet("tests/data/file.parquet")
    batch = next(table.iter_batches(batch_size=100))
    assert isinstance(batch, pd.DataFrame)
    assert len(batch) == 100
    assert batch.iloc[0]["inseecommune"] == "73327"
