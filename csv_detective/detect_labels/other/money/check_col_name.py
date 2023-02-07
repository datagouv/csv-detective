def is_col_name_related_to_money(name):
    # TODO : make this a little bit more clever (spacy ?)
    col_name_related_to_money = False
    money_themes = ['budget', 'salaire', 'euro', 'euros', 'prêt', 'montant']
    # TODO attention 'européeen' est détecté OK
    for theme in money_themes:
        col_name_related_to_money = col_name_related_to_money or (theme in name)
    return col_name_related_to_money
