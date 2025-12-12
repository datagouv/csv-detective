import re

proportion = 1
labels = {
    "url": 1,
    "url source": 1,
    "site web": 1,
    "source url": 1,
    "site internet": 1,
    "remote url": 1,
    "web": 1,
    "site": 1,
    "lien": 1,
    "site data": 1,
    "lien url": 1,
    "lien vers le fichier": 1,
    "sitweb": 1,
    "interneturl": 1,
}

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
