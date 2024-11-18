from frformat import Region, Options, Millesime

PROPORTION = 1

_extra_valid_values_set = frozenset({
        "alsace",
        "aquitaine",
        "ara",
        "aura",
        "auvergne",
        "auvergne et rhone alpes",
        "basse normandie",
        "bfc",
        "bourgogne",
        "bourgogne et franche comte",
        "centre",
        "champagne ardenne",
        "franche comte",
        "ge",
        "haute normandie",
        "hdf",
        "languedoc roussillon",
        "limousin",
        "lorraine",
        "midi pyrenees",
        "nord pas de calais",
        "npdc",
        "paca",
        "picardie",
        "poitou charentes",
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
    """Match avec le nom des regions"""
    return isinstance(val, str) and _region.is_valid(val)
