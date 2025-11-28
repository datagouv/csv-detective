from frformat import CodeRNA

proportion = 0.9
tags = ["fr"]
labels = ["code waldec", "waldec"]

_code_rna = CodeRNA()


def _is(val):
    return isinstance(val, str) and _code_rna.is_valid(val)


_test_values = {
    True: ["W123456789", "W2D1234567"],
    False: ["AA751PEE00188854"],
}
