import gzip
from typing import BinaryIO
from io import BytesIO


def unzip(binary_file: BinaryIO, engine: str) -> BytesIO:
    if engine == "gzip":
        with gzip.open(binary_file, mode="rb") as decompressed:
            file_content = decompressed.read()
    else:
        raise NotImplementedError(f"{engine} is not yet supported")
    return BytesIO(file_content)
