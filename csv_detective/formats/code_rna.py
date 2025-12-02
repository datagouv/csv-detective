from frformat import CodeRNA

proportion = 0.9
tags = ["fr"]
labels = [
    "code rna",
    "rna",
    "n° inscription association",
    "identifiant association",
]

_code_rna = CodeRNA()


def _is(val):
    return isinstance(val, str) and _code_rna.is_valid(val)


_test_values = {
    True: ["W751515517"],
    False: [
        "W111111111111111111111111111111111111",
        "w143788974",
        "W12",
        "678W23456",
        "165789325",
        "Wa1#89sf&h",
    ],
}
