from re import finditer


def camel_case_split(identifier):
    matches = finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return " ".join([m.group(0) for m in matches])


# Process text
def _process_text(val):
    """Met le unicode val sous sous sa forme normee"""
    val = camel_case_split(val)
    val = val.lower()
    val = val.replace("-", " ")
    val = val.replace("_", " ")
    val = val.replace("'", " ")
    val = val.replace(",", " ")
    val = val.replace("  ", " ")
    # val = val.replace('\xc3\xa8', 'e')
    # val = val.replace('\xc3\xa9', 'e')
    # val = val.replace('\xc3\xaa', 'e')
    # val = val.replace('\xc3\x8e', 'i')
    # val = val.replace('\xc3\xb4', 'o')
    # val = val.replace('\xc3\xa7', 'c')
    # val = val.replace('\xc3\xa0', 'a')
    # val = val.replace('\xc3\xa2', 'a')
    # val = val.replace('\xc3\xae', 'i')
    val = val.replace("Ã©", "e")
    val = val.replace("é", "e")
    val = val.replace("è", "e")
    val = val.replace("ê", "e")
    val = val.replace("î", "i")
    val = val.replace("ô", "o")
    val = val.replace("ç", "c")
    val = val.replace("à", "a")
    val = val.replace("â", "a")
    val = val.replace("î", "i")

    val = val.strip()

    return val
