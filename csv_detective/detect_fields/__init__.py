# flake8: noqa
from .FR.other import (
    code_csp_insee,
    csp_insee,
    sexe,
    siren,
    tel_fr,
    uai,
    siret,
    insee_ape700,
    date_fr,
    code_import,
    code_waldec,
    code_rna,
)

from .other import (
    email,
    url,
    booleen,
    money,
    mongo_object_id,
    percent,
    twitter,
    float,
    int,
    uuid,
    json,
)

from .FR.geo import (
    adresse,
    code_commune_insee,
    code_postal,
    commune,
    departement,
    pays,
    region,
    code_departement,
    code_fantoir,
    longitude_wgs_fr_metropole,
    latitude_wgs_fr_metropole,
    code_region,
    latitude_l93,
    longitude_l93,
    insee_canton,
)

from .geo import (
    iso_country_code_alpha2,
    iso_country_code_alpha3,
    iso_country_code_numeric,
    latitude_wgs,
    longitude_wgs,
    latlon_wgs,
    json_geojson,
)

from .FR.temp import jour_de_la_semaine, mois_de_annee
from .temp import year, date, datetime, datetime_iso, datetime_rfc822
