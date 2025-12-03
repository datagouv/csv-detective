import codecs

proportion = 1
tags = ["type"]
labels = ["bytes", "binary", "image", "encode", "content"]


def binary_casting(val: str) -> bytes:
    return codecs.escape_decode(val[2:-1])[0]


def _is(val) -> bool:
    if isinstance(val, str) and (
        (val.startswith("b'") and val.endswith("'")) or (val.startswith('b"') and val.endswith('"'))
    ):
        try:
            return isinstance(binary_casting(val), bytes)
        except Exception:
            return False
    return False


_test_values = {
    True: ["b'\x01\x01'", 'b"\x01\x01\x00\x00\x00;\xb7\xd4\xc5_)J\xc0\xcb\x16>\x9e\xd1\xc4\x13@"'],
    False: ["bytes", 'b"ytes'],
}
