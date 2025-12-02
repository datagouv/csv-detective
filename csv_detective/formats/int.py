labels = ["nb", "nombre", "nbre"]
tag = ["type"]


def _is(val):
    """Detects integers"""
    if (
        not isinstance(val, str)
        or any([v in val for v in [".", "_", "+"]])
        or (val.startswith("0") and len(val) > 1)
    ):
        return False
    try:
        int(val)
        return True
    except ValueError:
        return False


_test_values = {
    True: ["1", "0", "1764", "-24"],
    False: ["01053", "1.2", "123_456", "+35"],
}
