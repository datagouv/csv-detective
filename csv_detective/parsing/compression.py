import gzip
from io import BytesIO


def unzip(binary_file: BytesIO, engine: str) -> BytesIO:
    if engine == "gzip":
        with gzip.open(binary_file, mode="rb") as binary_file:
            file_content = binary_file.read()
    else:
        raise NotImplementedError(f"{engine} is not yet supported")
    return BytesIO(file_content)
