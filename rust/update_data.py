#!/usr/bin/env python3
"""Extract reference data from frformat for the Rust implementation.

Run with: uv run python rust/update_data.py
"""

import os

from frformat import (
    CodeCommuneInsee,
    CodeDepartement,
    CodePostal,
    CodeRegion,
    Commune,
    Departement,
    Millesime,
    Options,
    Region,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

REGION_EXTRAS = frozenset(
    {
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
    }
)

OPTS_FULL = Options(
    ignore_case=True,
    ignore_accents=True,
    replace_non_alphanumeric_with_space=True,
    ignore_extra_whitespace=True,
)
OPTS_CASE = Options(ignore_case=True)


def write_values(name, values):
    path = os.path.join(DATA_DIR, f"{name}.txt")
    sorted_values = sorted(values)
    with open(path, "w") as f:
        f.write("\n".join(sorted_values))
    print(f"  {name}: {len(sorted_values)} values")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Extracting reference data from frformat...")

    write_values("communes", Commune(Millesime.LATEST, OPTS_FULL)._normalized_values)
    write_values("departements", Departement(Millesime.LATEST, OPTS_FULL)._normalized_values)
    write_values(
        "regions",
        Region(
            Millesime.LATEST,
            Options(
                ignore_case=True,
                ignore_accents=True,
                replace_non_alphanumeric_with_space=True,
                ignore_extra_whitespace=True,
                extra_valid_values=REGION_EXTRAS,
            ),
        )._normalized_values,
    )
    write_values("codes_postaux", CodePostal()._normalized_values)
    write_values("codes_communes", CodeCommuneInsee(Millesime.LATEST)._normalized_values)
    write_values("codes_departements", CodeDepartement(Millesime.LATEST, OPTS_CASE)._normalized_values)
    write_values("codes_regions", CodeRegion(Millesime.LATEST)._normalized_values)

    print("Done.")


if __name__ == "__main__":
    main()
