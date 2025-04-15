from datetime import datetime
import json
import logging
import os
import tempfile
from time import time
from typing import Optional

from botocore.exceptions import ClientError

from csv_detective.s3_utils import get_s3_client, download_from_minio, upload_to_minio
from csv_detective.utils import display_logs_depending_process_time


def get_description(format: str) -> str:
    """Returns generic description for specific field"""
    format_to_desc = {
        "adresse": "Adresse",
        "code_commune_insee": "Le code INSEE de la commune",
        "code_departement": "Le code INSEE du département",
        "code_region": "Le code INSEE de la région",
        "code_fantoir": "Le code FANTOIR de la voie ou du lieu-dit",
        "code_postal": "Le code postal",
        "commune": "Le nom de la commune",
        "departement": "Le nom du département",
        "insee_canton": "Le nom du canton",
        "latitude_l93": "La latitude au format Lambert 93",
        "latitude_wgs_fr_metropole": (
            "La latitude au format WGS. Ne concerne que des latitudes "
            "de la métropole française"
        ),
        "longitude_l93": "La longitude au format Lambert 93",
        "longitude_wgs_fr_metropole": (
            "La longitude au format WGS. Ne concerne que des longitudes "
            "de la métropole française"
        ),
        "pays": "Le nom du pays",
        "region": "Le nom de la région",
        "code_csp_insee": "Le code de Catégorie Socio-professionnel INSEE",
        "code_rna": "Le code RNA de l'association",
        "code_waldec": "Le code WALDEC de l'association",
        "csp_insee": "La catégorie socio-professionnel INSEE",
        "date_fr": "Data au format français",
        "sexe": "Le sexe",
        "siren": "Le numéro SIREN à 9 chiffres de l'entreprise (unité légale)",
        "siret": "Le numéro SIRET à 14 chiffres de l'établissement d'une entreprise",
        "tel_fr": "Le numéro de téléphone français",
        "uai": "Le numéro UAI (Unité Administrative Immatriculée) de l'établissement scolaire",
        "jour_de_la_semaine": "Le jour de la semaine",
        "mois_de_annee": "Le mois de l'année",
        "latitude_wgs": "La latitude au format WGS",
        "longitude_wgs": "La longitude au format WGS",
        "latlon_wgs": "Les coordonnées XY (latitude et longitude)",
        "booleen": "Booléen",
        "email": "L'adresse couriel (email)",
        "float": "Nombre flottant (à virgule)",
        "int": "Nombre entier",
        "json": "Chaîne de caractère json",
        "mongo_object_id": "Identifiant de base de donnée Mongo",
        "twitter": "Compte Twitter",
        "url": "Adresse URL",
        "uuid": "Identifiant unique au format UUID",
        "date": "Date",
        "datetime_iso": "Date au format datetime (ISO)",
        "datetime_rfc822": "Date au format datetime (RFC822)",
        "year": "Année",
    }
    return format_to_desc.get(format, "")


def get_pattern(format: str) -> str:
    """Returns the pattern for a particular format"""
    format_to_pattern = {
        "siren": r"^\d{9}$",
        "siret": r"^\d{14}$",
        "code_commune_insee": r"^([013-9]\d|2[AB1-9])\d{3}$",
        "code_postal": r"^([013-9]\d|2[AB1-9])\d{3}$",
        "code_departement": r"^(([013-9]\d|2[AB1-9])$|9\d{2}$)",
        "code_region": r"^\d{2}$",
        "code_rna": r"^[wW]\d{9}$",
        "code_waldec": (
            r"^\d{3}\D\d{1,10}$|^\d\D\d\D\d{10}$|^\d{3}\D{3}\d{1,10}$|^\d{3}\D\d{4}\D\d{1,10}"
            r"$|^\d{3}\D\d{2}[-]\d{3}$|^\d\D\d\D\d{2}\D\d{1,8}$"
        ),
        "uai": r"^(0[0-8][0-9]|09[0-5]|9[78][0-9]|[67]20)[0-9]{4}[A-Z]$",
        "email": r"^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$",
        "twitter": r'^@[A-Za-z0-9_]+$',
        "mongo_object_id": r'^[0-9a-fA-F]{24}$',
        "uuid": r'^[{]?[0-9a-fA-F]{8}' + '-?([0-9a-fA-F]{4}-?)' + '{3}[0-9a-fA-F]{12}[}]?$',
        "url": (
            r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]'
            r'{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
        )
    }
    if format in format_to_pattern:
        return {"pattern": format_to_pattern[format]}
    else:
        return {}


def get_validata_type(format: str) -> str:
    """Returns the validata type for a given format"""
    metier_to_validata_type = {
        "booleen": "boolean",
        "int": "integer",
        "float": "number",
        "string": "string",
        "date": "date",
        "datetime_iso": "datetime",
        "datetime_rfc822": "datetime",
        "json_geojson": "geojson",
        "latitude": "number",
        "latitude_l93": "number",
        "latitude_wgs": "number",
        "latitude_wgs_fr_metropole": "number",
        "latlon_wgs": "geo_point",
        "longitude": "number",
        "longitude_l93": "number",
        "longitude_wgs": "number",
        "longitude_wgs_fr_metropole": "number",
        "year": "year",
    }
    return metier_to_validata_type.get(format, "string")


def get_example(format: str) -> str:
    """Returns the example for a given format"""
    format_to_example = {
        "booleen": "true",
        "int": 42,
        "float": 42.42,
        "string": "Lorem ipsum dolor sit amet",
        "adresse": "28 rue Ledion, 75014 Paris",
        "insee_canton": "Pont-d'Ain",
        "code_commune_insee": "27501",
        "code_csp_insee": "233c",
        "code_departement": "2A",
        "code_fantoir": "A633",
        "code_postal": "75014",
        "code_region": "52",
        "code_rna": "W123456789",
        #        'code_waldec': TODO: add code_waldec
        "commune": "Joyeux",
        "csp_insee": "anciens agriculteurs exploitants",
        "date": "2020-01-01",
        "date_fr": "12 janvier 2020",
        "datetime_iso": "2020-01-01T00:00:00",
        "datetime_rfc822": "Tue, 1 Jan 2020 00:00:00 +0000",
        "departement": "Ain",
        "email": "example@example.com",
        "insee_ape700": "0130Z",
        "iso_country_code_alpha2": "FR",
        "iso_country_code_alpha3": "FRA",
        "iso_country_code_numeric": 250,
        "jour_de_la_semaine": "lundi",
        "json_geojson": '{"type": "Point", "coordinates": [0, 0]}',
        "latitude": 42.42,
        "latitude_l93": 6037008,
        "latitude_wgs": 42.42,
        "latitude_wgs_fr_metropole": 41.3,
        "latlon_wgs": "42.42, 0.0",
        "longitude": 0.0,
        "longitude_l93": -357823,
        "longitude_wgs": 0.0,
        "longitude_wgs_fr_metropole": 1.2,
        "mois_de_annee": "janvier",
        "mongo_object_id": "507f191e810c19729de860ea",
        "pays": "France",
        "region": "nouvelle aquitaine",
        "sexe": "h",
        "siren": "362521879",
        "siret": "56894100056",
        "tel_fr": "+33123456789",
        "twitter": "@Etalab",
        "uai": "0470009E",
        "url": "https://www.data.gouv.fr",
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "year": "2020",
    }
    return format_to_example.get(format, "")


def get_constraints(format: str) -> dict:
    """Returns the constraints for a given format"""
    pattern_constraints = get_pattern(format)
    extra_constraints = {}
    if format == "latitude_l93":
        extra_constraints = {"minimum": 6037008, "maximum": 7230728}
    if format == "longitude_l93":
        extra_constraints = {"minimum": -357823, "maximum": 7230728}
    if format == "latitude_wgs_fr_metropole":
        extra_constraints = {"minimum": 41.3, "maximum": 51.3}
    if format == "longitude_wgs_fr_metropole":
        extra_constraints = {"minimum": -5.5, "maximum": 9.8}

    return {"required": False, **pattern_constraints, **extra_constraints}


def generate_table_schema(
    analysis_report: dict,
    save_file: bool,
    netloc: Optional[str] = None,
    bucket: Optional[str] = None,
    key: Optional[str] = None,
    minio_user: Optional[str] = None,
    minio_pwd: Optional[str] = None,
    verbose: bool = False
) -> dict:
    """Generates a table schema from the analysis report

    Args:
        analysis_report (dict): The analysis report from csv_detective
        save_file (bool): indicate if schema should be saved into minio or just returned
        netloc (str): The netloc of the minio instance to upload the tableschema
        bucket (str): The bucket to save the schema in
        key (str): The key to save the schema in (without extension as we will append
        version number and extension)
        minio_user (str): The minio user
        minio_pwd (str): The minio password

    Returns:
    """
    if verbose:
        start = time()
        logging.info("Creating table schema")
    fields = [
        {
            "name": header,
            "description": get_description(field_report["format"]),
            "example": get_example(field_report["format"]),
            "type": get_validata_type(field_report["format"]),
            "formatFR": field_report["format"],
            "constraints": get_constraints(field_report["format"])
        }
        for header, field_report in analysis_report["columns"].items()
    ]

    new_version = "0.0.1"

    schema = {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "name": "",
        "title": "",
        "description": "",
        "countryCode": "FR",
        "homepage": "",
        "path": "https://github.com/etalab/csv-detective",
        "resources": [],
        "sources": [
            {
                "title": "Spécification Tableschema",
                "path": "https://specs.frictionlessdata.io/table-schema"
            },
            {
                "title": "schema.data.gouv.fr",
                "path": "https://schema.data.gouv.fr"
            }
        ],
        "created": datetime.today().strftime("%Y-%m-%d"),
        "lastModified": datetime.today().strftime("%Y-%m-%d"),
        "version": new_version,
        "contributors": [
            {
                "title": "Table schema bot",
                "email": "schema@data.gouv.fr",
                "organisation": "data.gouv.fr",
                "role": "author",
            },
        ],
        "fields": fields,
        "missingValues": [""],
    }

    if verbose:
        display_logs_depending_process_time(f'Created schema in {round(time() - start, 3)}s', time() - start)

    if not save_file:
        return schema

    if save_file:
        if not all([netloc, key, bucket, minio_user, minio_pwd]):
            raise Exception(
                "To save schema into minio, parameters : netloc, key, bucket, "
                "minio_user, minio_pwd should be provided"
            )

        # Create bucket if does not exist
        client = get_s3_client(netloc, minio_user, minio_pwd)
        try:
            client.head_bucket(Bucket=bucket)
        except ClientError:
            client.create_bucket(Bucket=bucket)

        tableschema_objects = client.list_objects(Bucket=bucket, Prefix=key, Delimiter="/")
        if "Contents" in tableschema_objects:
            tableschema_keys = [
                tableschema["Key"]
                for tableschema in client.list_objects(
                    Bucket=bucket, Prefix=key, Delimiter="/"
                )["Contents"]
            ]
            tableschema_versions = [
                os.path.splitext(tableschema_key)[0].split("_")[-1]
                for tableschema_key in tableschema_keys
            ]
            latest_version = max(tableschema_versions)

            with tempfile.NamedTemporaryFile() as latest_schema_file:
                with open(latest_schema_file.name, "w") as fp:
                    download_from_minio(
                        netloc,
                        bucket,
                        f"{key}_{latest_version}.json",
                        latest_schema_file.name,
                        minio_user,
                        minio_pwd,
                    )
                    # Check if files are different
                    with open(latest_schema_file.name, "r") as fp:
                        latest_schema = json.load(fp)
                        if latest_schema["fields"] != fields:
                            latest_version_split = latest_version.split(".")
                            new_version = (
                                latest_version_split[0]
                                + "."
                                + latest_version_split[1]
                                + "."
                                + str(int(latest_version_split[2]) + 1)
                            )
                        else:
                            return None

            schema["version"] = new_version

        tableschema_file = tempfile.NamedTemporaryFile(delete=False)
        with open(tableschema_file.name, "w") as fp:
            json.dump(schema, fp, indent=4)

        new_version_key = f"{key}_{new_version}.json"
        upload_to_minio(
            netloc, bucket, new_version_key, tableschema_file.name, minio_user, minio_pwd
        )
        os.unlink(tableschema_file.name)
        return {"netloc": netloc, "bucket": bucket, "key": new_version_key}
