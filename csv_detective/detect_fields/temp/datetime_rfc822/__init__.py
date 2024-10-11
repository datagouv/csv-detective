import re

PROPORTION = 1


def _is(val):
    '''Renvoie True si val peut être une date au format rfc822, False sinon
    Exemple: Tue, 19 Dec 2023 15:30:45 +0000'''

    return isinstance(val, str) and bool(
        re.match(
            r'^[A-Za-z]{3}, (0[1-9]|[1-2][0-9]|3[01]) [A-Za-z]{3} \d{4} '
            r'([0-2])([0-9]):([0-5])([0-9]):([0-5])([0-9]) '
            r'(ut|gmt|est|edt|cst|cdt|mst|mdt|pst|pdt|[+\-](0[0-9]|1[0-3])00)$',
            val.lower(),
            re.IGNORECASE
        )
    )
