from time import time

from csv_detective.io.parquet import ParquetTable, load_parquet
from csv_detective.utils import display_logs_depending_process_time


def parse_parquet(file_path: str, verbose: bool = False) -> tuple[ParquetTable, dict]:
    if verbose:
        start = time()
    table = load_parquet(file_path)
    analysis = {
        "engine": "parquet",
        "header": table.column_names,
        "total_lines": table.num_rows,
    }
    if verbose:
        display_logs_depending_process_time(
            f"Table parsed successfully in {round(time() - start, 3)}s",
            time() - start,
        )
    return table, analysis
