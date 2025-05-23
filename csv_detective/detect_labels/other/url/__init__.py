from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "url",
        "url source",
        "site web",
        "source url",
        "site internet",
        "remote url",
        "web",
        "site",
        "lien",
        "site data",
        "lien url",
        "lien vers le fichier",
        "sitweb",
        "interneturl",
    ]
    return header_score(header, words_combinations_list)
