from frformat import Region, Options

PROPORTION = 1


def _is(val):
    '''Match avec le nom des regions'''
    lenient_region_set = {
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
        }

    options = Options(
        ignore_case=True,
        ignore_non_alphanumeric=True,
        ignore_extra_white_space=True,
        ignore_accents=True,
        extra_valid_values=lenient_region_set
    )
    return Region.is_valid(val, options)
