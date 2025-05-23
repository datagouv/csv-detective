from re import finditer


def camel_case_split(identifier: str):
    matches = finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return " ".join([m.group(0) for m in matches])


translate_dict = {
    " ": ["-", "_", "'", ",", "  "],
    "a": ["à", "â"],
    "c": ["ç"],
    "e": ["é", "è", "ê", "Ã©"],
    "i": ["î", "ï"],
    "o": ["ô", "ö"],
    "u": ["ù", "û", "ü"],
}


# Process text
def _process_text(val: str):
    """Traitement des chaînes de caractères pour les standardiser.
    Plusieurs alternatives ont été testées : .translate, unidecode.unidecode,
    des méthodes hybrides, mais aucune ne s'est avérée plus performante."""
    val = camel_case_split(val)
    val = val.lower()
    for target in translate_dict:
        for source in translate_dict[target]:
            val = val.replace(source, target)
    val = val.strip()
    return val


def is_word_in_string(word: str, string: str):
    # if the substring is too short, the test can become irrelevant
    return len(word) > 2 and word in string


def header_score(header: str, words_combinations_list: list[str]) -> float:
    """Returns:
    - 1 if the header is exactly in the specified list
    - 0.5 if any of the words is within the header
    - 0 otherwise"""
    processed_header = _process_text(header)

    header_matches_words_combination = float(
        any(
            words_combination == processed_header for words_combination in words_combinations_list
        )
    )
    words_combination_in_header = 0.5 * (
        any(
            is_word_in_string(
                words_combination, processed_header
            ) for words_combination in words_combinations_list
        )
    )

    return max(header_matches_words_combination, words_combination_in_header)
