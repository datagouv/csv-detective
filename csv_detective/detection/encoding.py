import logging
from time import time
from typing import Any, BinaryIO

from charset_normalizer import detect

from csv_detective.utils import display_logs_depending_process_time


def detect_encoding(binary_file: BinaryIO, verbose: bool = False) -> str:
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
        encoding: Any = "utf-8"
        confidence: Any = 1
    except Exception:
        encoding_dict = detect(read) or {}
        encoding = encoding_dict.get("encoding")
        confidence = encoding_dict.get("confidence") or 0
    if not encoding:
        raise ValueError(
            "Could not detect the file's encoding. Consider specifying it in the routine call."
        )
    if verbose:
        message = f'Detected encoding: "{encoding}"'
        message += f" in {round(time() - start, 3)}s (confidence: {round(float(confidence) * 100)}%)"
        display_logs_depending_process_time(
            message,
            time() - start,
        )
    return str(encoding)
