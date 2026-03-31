import logging
from io import BytesIO
from time import time

from charset_normalizer import detect

from csv_detective.utils import display_logs_depending_process_time


def detect_encoding(binary_file: BytesIO, verbose: bool = False) -> str:
    """
    Detects file encoding using charset_normalizer
    """
    if verbose:
        start = time()
        logging.info("Detecting encoding")
    read = binary_file.read()
    try:
        # utf-8 is the most common encoding, we should start there
        read.decode("utf-8")
        encoding_dict = {"encoding": "utf-8", "confidence": 1}
    except Exception:
        encoding_dict = detect(read)
    if not encoding_dict["encoding"]:
        raise ValueError(
            "Could not detect the file's encoding. Consider specifying it in the routine call."
        )
    if verbose:
        message = f'Detected encoding: "{encoding_dict["encoding"]}"'
        message += f" in {round(time() - start, 3)}s (confidence: {round(encoding_dict['confidence'] * 100)}%)"
        display_logs_depending_process_time(
            message,
            time() - start,
        )
    return encoding_dict["encoding"]
