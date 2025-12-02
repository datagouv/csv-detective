import re

proportion = 0.9
labels = [
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


def _is(val):
    return isinstance(val, str) and bool(
        re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", val, re.IGNORECASE)
    )


_test_values = {
    True: ["cdo_intern@data.gouv.fr", "P.NOM@CIE.LONGDOMAIN"],
    False: ["cdo@@gouv.sfd"],
}
