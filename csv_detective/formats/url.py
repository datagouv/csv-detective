import re

proportion = 1
labels = [
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

pattern = re.compile(
    r"^((https?|ftp)://|www\.)(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})"
    r"(/[A-Za-z\u00C0-\u024F\u1E00-\u1EFF0-9\s._~:/?#[@!$&'()*+,;=%-]*)?$"
)


def _is(val):
    if not isinstance(val, str):
        return False
    return bool(pattern.match(val))


_test_values = {
    True: [
        "www.data.gouv.fr",
        "http://data.gouv.fr",
        "https://www.youtube.com/@data-gouv-fr",
        (
            "https://tabular-api.data.gouv.fr/api/resources/"
            "aaaaaaaa-1111-bbbb-2222-cccccccccccc/data/"
            "?score__greater=0.9&decompte__exact=13"
        ),
        "https://une-ville.fr/délibérations/2025/Doc avec espaces et àccëñts.pdf",
    ],
    False: ["tmp@data.gouv.fr"],
}
