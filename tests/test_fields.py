import pandas as pd
from numpy import random

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
    longitude_l93,
    pays,
    region,
)
from csv_detective.detect_fields.FR.other import (
    code_csp_insee,
    code_rna,
    code_waldec,
    csp_insee,
    sexe,
    siren,
    tel_fr,
)
from csv_detective.detect_fields.FR.temp import jour_de_la_semaine
from csv_detective.detect_fields.geo import (
    iso_country_code_alpha2,
    iso_country_code_alpha3,
    iso_country_code_numeric,
)
from csv_detective.detect_fields.other import (
    email,
    json,
    mongo_object_id,
    url,
    uuid,
    int as test_int,
    float as test_float,
)
from csv_detective.detect_fields.temp import date, datetime_iso, datetime_rfc822, year
from csv_detective.detection import (
    detect_continuous_variable,
    detetect_categorical_variable,
)
from csv_detective.explore_csv import return_all_tests


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

    res, _ = detetect_categorical_variable(df)
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


# csp_insee
def test_match_csp_insee():
    val = "employes de la poste"
    assert csp_insee._is(val)


def test_do_not_match_csp_insee():
    val = "super-heros"
    assert not csp_insee._is(val)


# code_csp_insee
def test_match_code_csp_insee():
    val = "121f"
    assert code_csp_insee._is(val)


def test_do_not_match_code_csp_insee():
    val = "121x"
    assert not code_csp_insee._is(val)


# sexe
def test_match_sexe():
    val = "homme"
    assert sexe._is(val)


def test_do_not_match_sexe():
    val = "hermaphrodite"
    assert not sexe._is(val)


# tel_fr
def test_match_tel_fr():
    val = "0134643467"
    assert tel_fr._is(val)


def test_do_not_match_tel_fr():
    val = "3345689715"
    assert not tel_fr._is(val)


# email
def test_match_email():
    val = "cdo_intern@data.gouv.fr"
    assert email._is(val)


def test_do_not_match_email():
    val = "cdo@@gouv.sfd"
    assert not email._is(val)


# uuid
def test_match_uuid():
    val = "884762be-51f3-44c3-b811-1e14c5d89262"
    assert uuid._is(val)


def test_do_not_match_uuid():
    val = "0610928327"
    assert not uuid._is(val)


# Mongo ObjectId
def test_match_mongo_object_id():
    val = "62320e50f981bc2b57bcc044"
    assert mongo_object_id._is(val)


def test_do_not_match_mongo_object_id():
    val = "884762be-51f3-44c3-b811-1e14c5d89262"
    assert not mongo_object_id._is(val)


# url
def test_match_url():
    val = "www.etalab.data.gouv.fr"
    assert url._is(val)


def test_do_not_match_url():
    val = "c est une phrase"
    assert not url._is(val)


# adresse
def test_match_adresse():
    val = "rue du martyr"
    assert adresse._is(val)


def test_do_not_match_adresse():
    val = "bonjour les amis"
    assert not adresse._is(val)


# code_commune_insee
def test_match_code_commune_insee():
    val = "91471"
    assert code_commune_insee._is(val)


def test_do_not_match_code_commune_insee():
    val = "914712"
    assert not code_commune_insee._is(val)


# code_postal
def test_match_code_postal():
    val = "75020"
    assert code_postal._is(val)


def test_do_not_match_code_postal():
    val = "77777"
    assert not code_postal._is(val)


# code_departement
def test_match_code_departement():
    vals = ["75", "2A", "2a", "974"]
    for val in vals:
        assert code_departement._is(val)


def test_do_not_match_code_departement():
    val = "00"
    assert not code_departement._is(val)


# code_fantoir
def test_match_code_fantoir():
    vals = ["7755A", "B150B", "ZA04C", "ZB03D"]
    for val in vals:
        assert code_fantoir._is(val)


def test_do_not_match_code_fantoir():
    vals = ["7755", "ZA99A"]
    for val in vals:
        assert not code_fantoir._is(val)


# code_region
def test_match_code_region():
    val = "32"
    assert code_region._is(val)


def test_do_not_match_code_region():
    val = "55"
    assert not code_region._is(val)


# commune
def test_match_commune():
    val = "saint denis"
    assert commune._is(val)


def test_do_not_match_commune():
    val = "new york"
    assert not commune._is(val)


# departement
def test_match_departement():
    val = "essonne"
    assert departement._is(val)


def test_do_not_match_departement():
    val = "new york"
    assert not departement._is(val)


# insee_canton
def test_match_canton():
    val = "nantua"
    assert insee_canton._is(val)


def test_do_not_match_canton():
    val = "new york"
    assert not departement._is(val)


# latitude_l93
def test_match_latitude_l93():
    vals = ["6037008", "7123528.5", "7124528,5"]
    for val in vals:
        assert latitude_l93._is(val)


def test_do_not_match_latitude_93():
    vals = ["0", "-6734529.6", "7245669.8", "3422674,78", "32_34"]
    for val in vals:
        assert not latitude_l93._is(val)


# longitude_l93
def test_match_longitude_l93():
    vals = ["0", "-154", "1265783,45", "34723.4"]
    for val in vals:
        assert longitude_l93._is(val)


def test_do_not_match_longitude_93():
    vals = ["1456669.8", "-776225", "346_3214"]
    for val in vals:
        assert not longitude_l93._is(val)


# pays
def test_match_pays():
    val = "france"
    assert pays._is(val)


def test_do_not_match_pays():
    val = "new york"
    assert not pays._is(val)


# region
def test_match_region():
    val = "bretagne"
    assert region._is(val)


def test_do_not_match_region():
    val = "jambon beurre"
    assert not region._is(val)


# iso_country_code
def test_match_iso_country_code():
    val = "FR"
    assert iso_country_code_alpha2._is(val)


def test_do_not_match_iso_country_code():
    val = "XX"
    assert not iso_country_code_alpha2._is(val)


# iso_country_code alpha-3
def test_match_iso_country_code_alpha3():
    val = "FRA"
    assert iso_country_code_alpha3._is(val)


def test_do_not_match_iso_country_code_alpha3():
    val = "ABC"
    assert not iso_country_code_alpha3._is(val)


# iso_country_code numerique
def test_match_iso_country_code_numeric():
    val = "250"
    assert iso_country_code_numeric._is(val)


def test_do_not_match_iso_country_code_numeric():
    val = "003"
    assert not iso_country_code_numeric._is(val)


# jour de la semaine
def test_match_jour_de_la_semaine():
    val = "lundi"
    assert jour_de_la_semaine._is(val)


def test_do_not_match_jour_de_la_semaine():
    val = "jour de la biere"
    assert not jour_de_la_semaine._is(val)


# year
def test_match_year():
    val = "2015"
    assert year._is(val)


def test_do_not_match_year():
    val = "20166"
    assert not year._is(val)


# date
def test_match_date():
    val = "1960-08-07"
    assert date._is(val)
    val = "12/02/2007"
    assert date._is(val)
    val = "15 jan 1985"
    assert date._is(val)
    val = "15 décembre 1985"
    assert date._is(val)
    val = "02 05 2003"
    assert date._is(val)
    val = "20030502"
    assert date._is(val)
    val = "1993-12/02"
    assert date._is(val)


def test_do_not_match_date():
    val = "1993-1993-1993"
    assert not date._is(val)
    val = "39-10-1993"
    assert not date._is(val)
    val = "19-15-1993"
    assert not date._is(val)
    val = "15 tambour 1985"
    assert not date._is(val)
    val = "12152003"
    assert not date._is(val)
    val = "20031512"
    assert not date._is(val)
    val = "02052003"
    assert not date._is(val)


# datetime
def test_match_datetime():
    val = "2021-06-22T10:20:10"
    assert datetime_iso._is(val)
    val = "2021-06-22T30:20:10"
    assert not datetime_iso._is(val)

    val = "Sun, 06 Nov 1994 08:49:37 GMT"
    assert datetime_rfc822._is(val)


# siren
def test_match_siren():
    val = "552 100 554"
    assert siren._is(val)


def test_do_not_match_siren():
    val = "42"
    assert not siren._is(val)


# rna
def test_match_rna():
    val = "W751515517"
    assert code_rna._is(val)


def test_do_not_match_rna():
    vals = [
        "W111111111111111111111111111111111111",
        "w143788974",
        "W12",
        "678W23456",
        "165789325",
        "Wa1#89sf&h",
    ]
    for val in vals:
        assert not code_rna._is(val)


def test_match_waldec():
    val = "751P00188854"
    assert code_waldec._is(val)


def test_do_not_match_waldec():
    val = "AA751PEE00188854"
    assert not code_waldec._is(val)


# json
def test_match_json():
    val = '{"pomme": "fruit", "reponse": 42}'
    assert json._is(val)
    val = "[1,2,3,4]"
    assert json._is(val)


def test_do_not_match_json():
    val = '{"coordinates": [45.783753, 3.049342], "citycode": "63870"}'
    assert not json._is(val)
    val = "666"
    assert not json._is(val)


# int
def test_match_int():
    for val in ["1", "0", "1764", "-24"]:
        assert test_int._is(val)


def test_not_match_int():
    for val in ["01053", "1.2", "123_456", "+35"]:
        assert not test_int._is(val)


# float
def test_match_float():
    for val in ["1", "0", "1764", "-24", "1.2", "1863.23", "-12.7"]:
        assert test_float._is(val)


def test_not_match_float():
    for val in ["01053", "01053.89", "1e3", "123_456", "123_456.78", "+35", "+35.9"]:
        assert not test_float._is(val)
