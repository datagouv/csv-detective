import logging
import math
from typing import Optional


def display_logs_depending_process_time(prompt: str, duration: float):
    '''
    Print colored logs according to the time the operation took.
    '''
    logging.addLevelName(logging.CRITICAL, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
    logging.addLevelName(logging.WARN, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARN))

    threshold_warn = 1
    threshold_critical = 3

    if duration < threshold_warn:
        logging.info(prompt)
    elif duration < threshold_critical:
        logging.warning(prompt)
    else:
        logging.critical(prompt)


def is_url(file_path: str) -> bool:
    # could be more sophisticated if needed
    return file_path.startswith('http')


def prevent_nan(value: float) -> Optional[float]:
    if math.isnan(value):
        return None
    return value


def full_word_strictly_inside_string(word: str, string: str):
    return (
        word == string
        or (" " + word + " " in string)
        or (string.startswith(word + " "))
        or (string.endswith(" " + word))
    )
