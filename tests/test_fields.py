from datetime import date as _date, datetime as _datetime

from numpy import random
import pandas as pd
import pytest

from csv_detective.detect_fields.FR.geo import (
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
    region,
)
from csv_detective.detect_fields.FR.other import (
    code_csp_insee,
    code_rna,
    code_import,
    code_waldec,
    csp_insee,
    date_fr,
    insee_ape700,
    sexe,
    siren,
    siret,
    tel_fr,
    uai,
)
from csv_detective.detect_fields.FR.temp import jour_de_la_semaine, mois_de_annee
from csv_detective.detect_fields.geo import (
    iso_country_code_alpha2,
    iso_country_code_alpha3,
    iso_country_code_numeric,
    json_geojson,
    latitude_wgs,
    latlon_wgs,
    longitude_wgs,
)
from csv_detective.detect_fields.other import (
    booleen,
    email,
    json,
    money,
    mongo_object_id,
    percent,
    twitter,
    url,
    uuid,
    int as test_int,
    float as test_float,
)
from csv_detective.detect_fields.temp import date, datetime, datetime_iso, datetime_rfc822, year
from csv_detective.detection.variables import (
    detect_continuous_variable,
    detect_categorical_variable,
)
from csv_detective.load_tests import return_all_tests
from csv_detective.output.dataframe import cast


def test_all_tests_return_bool():
    all_tests = return_all_tests("ALL", "detect_fields")
    for test in all_tests:
        for tmp in ["a", "9", "3.14", "[]", float("nan")]:
            assert isinstance(test._is(tmp), bool)


# categorical
def test_detetect_categorical_variable():
    categorical_col = ["type_a"] * 33 + ["type_b"] * 33 + ["type_c"] * 34
    categorical_col2 = [str(k // 20) for k in range(100)]
    not_categorical_col = [i for i in range(100)]

    df_dict = {
        "cat": categorical_col,
        "cat2": categorical_col2,
        "not_cat": not_categorical_col,
    }
    df = pd.DataFrame(df_dict, dtype="unicode")

    res, _ = detect_categorical_variable(df)
    assert len(res.values) and all(k in res.values for k in ["cat", "cat2"])


# continuous
def test_detect_continuous_variable():
    continuous_col = random.random(100)
    continuous_col_2 = [1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7, 21, 3] * 10
    not_continuous_col = ["type_a"] * 33 + ["type_b"] * 33 + ["type_c"] * 34

    df_dict = {"cont": continuous_col, "not_cont": not_continuous_col}
    df_dict_2 = {"cont": continuous_col_2, "not_cont": not_continuous_col}

    df = pd.DataFrame(df_dict, dtype="unicode")
    df2 = pd.DataFrame(df_dict_2, dtype="unicode")

    res = detect_continuous_variable(df)
    res2 = detect_continuous_variable(df2, continuous_th=0.65)
    assert res.values and res.values[0] == "cont"
    assert res2.values and res2.values[0] == "cont"


fields = {
    adresse: {
        True: ["rue du martyr"],
        False: ["un batiment"],
    },
    code_commune_insee: {
        True: ["91471", "01053"],
        False: ["914712", "01000"],
    },
    code_departement: {
        True: ["75", "2A", "2b", "974", "01"],
        False: ["00", "96", "101"],
    },
    code_fantoir: {
        True: ["7755A", "B150B", "ZA04C", "ZB03D"],
        False: ["7755", "ZA99A"],
    },
    code_postal: {
        True: ["75020", "01000"],
        False: ["77777", "018339"],
    },
    code_region: {
        True: ["32"],
        False: ["55"],
    },
    commune: {
        True: ["saint denis"],
        False: ["new york", "lion"],
    },
    departement: {
        True: ["essonne"],
        False: ["alabama", "auvergne"],
    },
    insee_canton: {
        True: ["nantua"],
        False: ["california"],
    },
    latitude_l93: {
        True: ["6037008", "7123528.5", "7124528,5"],
        False: ["0", "-6734529.6", "7245669.8", "3422674,78", "32_34"],
    },
    longitude_l93: {
        True: ["0", "-154", "1265783,45", "34723.4"],
        False: ["1456669.8", "-776225", "346_3214"],
    },
    latitude_wgs_fr_metropole: {
        True: ["42.5"],
        False: ["22.5", "62.5"],
    },
    longitude_wgs_fr_metropole: {
        True: ["-2.5"],
        False: ["12.8"],
    },
    pays: {
        True: ["france", "italie"],
        False: ["amerique", "paris"],
    },
    region: {
        True: ["bretagne", "ile-de-france"],
        False: ["baviere", "overgne"],
    },
    code_csp_insee: {
        True: ["121f"],
        False: ["121x"],
    },
    code_rna: {
        True: ["W751515517"],
        False: [
            "W111111111111111111111111111111111111",
            "w143788974",
            "W12",
            "678W23456",
            "165789325",
            "Wa1#89sf&h",
        ],
    },
    code_import: {
        True: ["123S1871092288"],
        False: ["AA751PEE00188854", "W123456789"],
    },
    code_waldec: {
        True: ["W123456789", "W2D1234567"],
        False: ["AA751PEE00188854"],
    },
    csp_insee: {
        True: ["employes de la poste"],
        False: ["super-heros"],
    },
    sexe: {
        True: ["homme"],
        False: ["hermaphrodite"],
    },
    siren: {
        True: ["552 100 554", "552100554"],
        False: ["42"],
    },
    siret: {
        True: ["13002526500013", "130 025 265 00013"],
        False: ["13002526500012"],
    },
    uai: {
        True: ["0422170F"],
        False: ["04292E"],
    },
    date_fr: {
        True: ["13 fevrier 1996"],
        False: ["44 march 2025"],
    },
    insee_ape700: {
        True: ["0116Z"],
        False: ["0116A"]
    },
    tel_fr: {
        True: ["0134643467"],
        False: ["6625388263", "01288398"],
    },
    jour_de_la_semaine: {
        True: ["lundi"],
        False: ["jour de la biere"],
    },
    mois_de_annee: {
        True: ["juin", "décembre"],
        False: ["november"],
    },
    iso_country_code_alpha2: {
        True: ["FR"],
        False: ["XX", "A", "FRA"],
    },
    iso_country_code_alpha3: {
        True: ["FRA"],
        False: ["XXX", "FR", "A"],
    },
    iso_country_code_numeric: {
        True: ["250"],
        False: ["003"],
    },
    json_geojson: {
        True: [
            '{"coordinates": [45.783753, 3.049342], "type": "63870"}',
            '{"geometry": {"coordinates": [45.783753, 3.049342]}}',
        ],
        False: ['{"pomme": "fruit", "reponse": 42}'],
    },
    latitude_wgs: {
        True: ["43.2", "-22"],
        False: ["100"],
    },
    latlon_wgs: {
        True: ["43.2,-22.6", "-10.7,140", "-40.7, 10.8"],
        False: ["0.1,192", "-102, 92"],
    },
    longitude_wgs: {
        True: ["120", "-20.2"],
        False: ["-200"],
    },
    booleen: {
        True: ["oui", "0", "1", "yes", "false", "True"],
        False: ["nein", "ja", "2", "-0"],
    },
    email: {
        True: ["cdo_intern@data.gouv.fr"],
        False: ["cdo@@gouv.sfd"],
    },
    json: {
        True: ['{"pomme": "fruit", "reponse": 42}', "[1,2,3,4]"],
        False: ['{"coordinates": [45.783753, 3.049342], "citycode": "63870"}', "{zefib:"],
    },
    money: {
        True: ["120€", "-20.2$"],
        False: ["200", "100 euros"],
    },
    mongo_object_id: {
        True: ["62320e50f981bc2b57bcc044"],
        False: ["884762be-51f3-44c3-b811-1e14c5d89262", "0230240284a66e"],
    },
    percent: {
        True: ["120%", "-20.2%"],
        False: ["200", "100 pourcents"],
    },
    twitter: {
        True: ["@accueil1"],
        False: ["adresse@mail"],
    },
    url: {
        True: [
            "www.data.gouv.fr",
            "http://data.gouv.fr",
            "https://www.youtube.com/@data-gouv-fr",
            (
                "https://tabular-api.data.gouv.fr/api/resources/"
                "aaaaaaaa-1111-bbbb-2222-cccccccccccc/data/"
                "?score__greater=0.9&decompte__exact=13"
            ),
        ],
        False: ["tmp@data.gouv.fr"],
    },
    uuid: {
        True: ["884762be-51f3-44c3-b811-1e14c5d89262"],
        False: ["0610928327"],
    },
    test_int: {
        True: ["1", "0", "1764", "-24"],
        False: ["01053", "1.2", "123_456", "+35"],
    },
    test_float: {
        True: ["1", "0", "1764", "-24", "1.2", "1863.23", "-12.7", "0.1"],
        False: ["01053", "01053.89", "1e3", "123_456", "123_456.78", "+35", "+35.9"],
    },
    date: {
        True: [
            "1960-08-07",
            "12/02/2007",
            "15 jan 1985",
            "15 décembre 1985",
            "02 05 2003",
            "20030502",
            "1993-12/02",
        ],
        False: [
            "1993-1993-1993",
            "39-10-1993",
            "19-15-1993",
            "15 tambour 1985",
            "12152003",
            "20031512",
            "02052003",
        ],
    },
    datetime: {
        True: ["2021-06-22T10:20:10"],
        False: ["2021-06-22T30:20:10", "Sun, 06 Nov 1994 08:49:37 GMT"],
    },
    datetime_iso: {
        True: ["2021-06-22T10:20:10"],
        False: ["2021-06-22T30:20:10", "Sun, 06 Nov 1994 08:49:37 GMT"],
    },
    datetime_rfc822: {
        True: ["Sun, 06 Nov 1994 08:49:37 GMT"],
        False: ["2021-06-22T10:20:10"],
    },
    year: {
        True: ["2015"],
        False: ["20166"],
    },
}

# we could also have a function here to add all True values of (almost)
# each field to the False values of all others


def test_all_fields_have_tests():
    all_tests = return_all_tests("ALL", "detect_fields")
    for test in all_tests:
        assert fields.get(test)


@pytest.mark.parametrize(
    "args",
    (
        (field, value, valid)
        for field in fields
        for valid in [True, False]
        for value in fields[field][valid]
    ),
)
def test_fields_with_values(args):
    field, value, valid = args
    assert field._is(value) is valid


@pytest.mark.parametrize(
    "args",
    (
        ("1.9", "float", float),
        ("oui", "bool", bool),
        ("[1, 2]", "json", list),
        ('{"a": 1}', "json", dict),
        ("2022-08-01", "date", _date),
        ("2024-09-23 17:32:07", "datetime", _datetime),
    ),
)
def test_cast(args):
    value, detected_type, cast_type = args
    assert isinstance(cast(value, detected_type), cast_type)
