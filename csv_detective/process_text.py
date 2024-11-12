from re import finditer


def camel_case_split(identifier: str):
    matches = finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return " ".join([m.group(0) for m in matches])


# Process text
def _process_text(val: str):
    """Traitement des chaînes de caractères pour les standardiser.
    Plusieurs alternatives ont été testées : .translate, unidecode.unidecode,
    des méthodes hybrides, mais aucune ne s'est avérée plus performante."""
    val = camel_case_split(val)
    val = val.lower()
    val = val.replace("-", " ")
    val = val.replace("_", " ")
    val = val.replace("'", " ")
    val = val.replace(",", " ")
    val = val.replace("  ", " ")
    val = val.replace("à", "a")
    val = val.replace("â", "a")
    val = val.replace("ç", "c")
    val = val.replace("Ã©", "e")
    val = val.replace("é", "e")
    val = val.replace("è", "e")
    val = val.replace("ê", "e")
    val = val.replace("î", "i")
    val = val.replace("ï", "i")
    val = val.replace("ô", "o")
    val = val.replace("ö", "o")
    val = val.replace("î", "i")
    val = val.replace("û", "u")
    val = val.replace("ù", "u")
    val = val.replace("ü", "u")
    val = val.strip()
    return val
