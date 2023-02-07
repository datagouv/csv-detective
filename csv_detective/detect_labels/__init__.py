# flake8: noqa
from .FR.geo import (
    adresse,
    code_commune_insee,
    code_departement,
    code_fantoir,
    code_postal,
    code_region,
    commune,
    departement,
    insee_canton,
    latitude_l93,
    latitude_wgs_fr_metropole,
    longitude_l93,
    longitude_wgs_fr_metropole,
    pays,
    region
)
from .FR.other import (
    code_csp_insee,
    code_rna,
    code_waldec,
    csp_insee,
    date_fr,
    insee_ape700,
    sexe,
    siren,
    siret,
    tel_fr,
    uai
)
from .FR.temp import jour_de_la_semaine, mois_de_annee
from .geo import (
    iso_country_code_alpha2,
    iso_country_code_alpha3,
    iso_country_code_numeric,
    json_geojson,
    latitude_wgs,
    latlon_wgs,
    longitude_wgs
)
from .other import booleen, email, float, int, money, mongo_object_id, twitter, url, uuid
from .temp import date, datetime_iso, datetime_rfc822, year
