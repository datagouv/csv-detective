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
            "args": {'length': 20},
        },
        {
            "name": "siret",
            "type": "str",
            "args": {'pattern': '^\\d{14}$'},
        },
        {
            "name": "type_producteur",
            "type": "str",
            "args": {'enum': ['privé', 'public', 'association']},
        },
        {
            "name": "date_creation",
            "type": "date",
            "args": {'date_range': ['23-01-2001', '24-04-2002']},
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
            "args": {'num_range': [1, 20]}
        },
    ]
    df = create_example_csv_file(
        fields=fields,
        file_length=5,

    )
    assert len(df) == 5
