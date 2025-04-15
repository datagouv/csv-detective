import logging
from time import time
from io import BytesIO

from cchardet import detect

from csv_detective.utils import display_logs_depending_process_time


def detect_encoding(binary_file: BytesIO, verbose: bool = False) -> str:
    """
    Detects file encoding using faust-cchardet (forked from the original cchardet)
    """
    if verbose:
        start = time()
        logging.info("Detecting encoding")
    encoding_dict = detect(binary_file.read())
    if not encoding_dict["encoding"]:
        raise ValueError("Could not detect the file's encoding. Consider specifying it in the routine call.")
    if verbose:
        message = f'Detected encoding: "{encoding_dict["encoding"]}"'
        message += f' in {round(time() - start, 3)}s (confidence: {round(encoding_dict["confidence"]*100)}%)'
        display_logs_depending_process_time(
            message,
            time() - start,
        )
    return encoding_dict['encoding']
