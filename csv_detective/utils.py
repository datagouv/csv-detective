import logging
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)
logging.addLevelName(
    logging.CRITICAL, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL)
)
logging.addLevelName(logging.WARN, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARN))

THRESHOLD_WARN = 1
THRESHOLD_CRITICAL = 3


def display_logs_depending_process_time(prompt: str, duration: float) -> None:
    """
    Print colored logs according to the time the operation took.
    """
    if duration < THRESHOLD_WARN:
        logging.info(prompt)
    elif duration < THRESHOLD_CRITICAL:
        logging.warning(prompt)
    else:
        logging.critical(prompt)


def is_url(file_path: str) -> bool:
    # could be more sophisticated if needed
    # using the URL detection test was considered but too broad (schema required to use requests)
    return file_path.startswith("http")


def prevent_nan(value: float) -> Optional[float]:
    return None if pd.isna(value) else value
