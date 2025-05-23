from csv_detective.parsing.text import header_score

PROPORTION = 0.5


def _is(header: str) -> float:
    words_combinations_list = [
        "email",
        "mail",
        "courriel",
        "contact",
        "mel",
        "lieucourriel",
        "coordinates.emailcontact",
        "e mail",
        "mo mail",
        "adresse mail",
        "adresse email",
    ]
    return header_score(header, words_combinations_list)
