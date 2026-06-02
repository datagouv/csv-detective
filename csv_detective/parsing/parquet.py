from io import BytesIO
from time import time

import pyarrow.parquet as pq
import requests

from csv_detective.utils import (
    display_logs_depending_process_time,
    is_url,
)


def parse_parquet(file_path: str, verbose: bool = False) -> tuple[pq.ParquetFile, dict]:
    if verbose:
        start = time()
    if is_url(file_path):
        r = requests.get(file_path)
        r.raise_for_status()
        table = pq.ParquetFile(BytesIO(r.content))
    else:
        table = pq.ParquetFile(file_path)
    analysis = {
        "engine": "parquet",
        "header": [col.name for col in table.schema_arrow],
        "total_lines": table.metadata.num_rows,
    }
    if verbose:
        display_logs_depending_process_time(
            f"Table parsed successfully in {round(time() - start, 3)}s",
            time() - start,
        )
    return table, analysis
