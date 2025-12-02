proportion = 1
tags = ["temp"]
labels = [
    "year",
    "annee",
    "annee depot",
    "an nais",
    "exercice",
    "data year",
    "annee de publication",
    "exercice comptable",
    "annee de naissance",
    "annee ouverture",
]


def _is(val):
    try:
        val = int(val)
    except ValueError:
        return False
    return (1800 <= val) and (val <= 2100)


_test_values = {
    True: ["2015"],
    False: ["20166", "123"],
}
