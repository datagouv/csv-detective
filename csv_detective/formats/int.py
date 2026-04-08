proportion = 1
description = "Integer"
tag = ["type"]
python_type = "int"
labels = {"nb": 0.75, "nombre": 1, "nbre": 0.75}


def _is(val) -> bool:
    if (
        not isinstance(val, str)
        or any(v in val for v in [".", "_", "+"])
        or (val.startswith("0") and len(val) > 1)
        or len(val) >= 20
    ):
        return False
    try:
        int(val)
        return True
    except ValueError:
        return False


_test_values = {
    True: ["1", "0", "1764", "-24"],
    False: ["01053", "1.2", "123_456", "+35", "14292405299487610865"],
}
