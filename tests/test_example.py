
import re
from uuid import UUID
from csv_detective import create_example_csv_file


def test_example_creation():
    fields = [
        {
            "name": "id_unique",
            "type": "id",
        },
        {
            "name": "nom_modele",
            "type": "str",
            "args": {"length": 20},
        },
        {
            "name": "siret",
            "type": "str",
            "args": {"pattern": "^\\d{14}$"},
        },
        {
            "name": "type_producteur",
            "type": "str",
            "args": {"enum": ["privé", "public", "association"]},
        },
        {
            "name": "date_creation",
            "type": "date",
            "args": {
                "date_range": ["1996-02-13", "2000-01-28"],
                "format": "%Y-%m-%d",
            },
        },
        {
            "name": "url_produit",
            "type": "url",
        },
        {
            "name": "nb_produits",
            "type": "int",
        },
        {
            "name": "note",
            "type": "float",
            "args": {"num_range": [1, 20]}
        },
    ]
    df = create_example_csv_file(
        fields=fields,
        file_length=5,
        output_name=None,
    )
    assert len(df) == 5
    assert all(UUID(_) for _ in df["id_unique"])
    assert all(len(_) == 20 for _ in df["nom_modele"])
    assert all(re.match("^\\d{14}$", _) for _ in df["siret"])
    assert all(_ in ["privé", "public", "association"] for _ in df["type_producteur"])
    assert all(_ >= "1996-02-13" and _ <= "2000-01-28" for _ in df["date_creation"])
    assert all(_.startswith("http") for _ in df["url_produit"])
    assert all(isinstance(_, int) for _ in df["nb_produits"])
    assert all(_ >= 1 and _ <= 20 for _ in df["note"])


def test_example_from_tableschema():
    df = create_example_csv_file(
        schema_path="https://schema.data.gouv.fr/schemas/etalab/schema-irve-statique/2.3.1/schema-statique.json",
        output_name=None,
    )
    assert len(df) == 10
