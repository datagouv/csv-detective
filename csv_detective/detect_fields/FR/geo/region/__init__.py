from frformat import Region, Options, Millesime

PROPORTION = 1
 
_extra_valid_values_set = frozenset({
        "alsace",
        "aquitaine",
        "ara",
        "aura",
        "auvergne",
        "auvergne et rhone alpes",
        "auvergne rhone alpes",
        "basse normandie",
        "bfc",
        "bourgogne",
        "bourgogne et franche comte",
        "bourgogne franche comte",
        "bretagne",
        "centre",
        "centre val de loire",
        "champagne ardenne",
        "corse",
        "franche comte",
        "ge",
        "nouvelle aquitaine",
        "grand est",
        "guadeloupe",
        "guyane",
        "haute normandie",
        "hauts de france",
        "hdf",
        "ile de france",
        "languedoc roussillon",
        "la reunion",
        "la reunion",
        "limousin",
        "lorraine",
        "martinique",
        "mayotte",
        "midi pyrenees",
        "nord pas de calais",
        "normandie",
        "npdc",
        "occitanie",
        "paca",
        "pays de la loire",
        "picardie",
        "poitou charentes",
        "provence alpes cote d azur",
        "reunion",
        "rhone alpes",
        })


_options = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
    extra_valid_values=_extra_valid_values_set
)
_region = Region(Millesime.LATEST, _options)


def _is(val):
    '''Match avec le nom des regions'''
    return _region.is_valid(val)
