import re

proportion = 0.9
labels = {
    "email": 1,
    "mail": 1,
    "courriel": 1,
    "contact": 1,
    "mel": 1,
    "lieucourriel": 1,
    "coordinates.emailcontact": 1,
    "e mail": 1,
    "mo mail": 1,
    "adresse mail": 1,
    "adresse email": 1,
}


def _is(val):
    return isinstance(val, str) and bool(
        re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", val, re.IGNORECASE)
    )


_test_values = {
    True: ["cdo_intern@data.gouv.fr", "P.NOM@CIE.LONGDOMAIN"],
    False: ["cdo@@gouv.sfd"],
}
