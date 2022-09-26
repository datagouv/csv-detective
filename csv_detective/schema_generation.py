from botocore.exceptions import ClientError
from datetime import datetime
import json
import os
import tempfile

from csv_detective.s3_utils import get_s3_client, download_from_minio, upload_to_minio


def get_validata_type(format: str) -> str:
    """Returns the validata type for a given format"""
    metier_to_validata_type = {
        'booleen': 'boolean',
        'int': 'integer',
        'float': 'number',
        'string': 'string',
        'date': 'date',
        'date_fr': 'date',
        'datetime_iso': 'datetime',
        'datetime_rfc822': 'datetime',
        'json_geojson': 'geojson',
        'latitude': 'number',
        'latitude_l93': 'number',
        'latitude_wgs': 'number',
        'latitude_wgs_fr_metropole': 'number',
        'latlon_wgs': 'geo_point',
        'longitude': 'number',
        'longitude_l93': 'number',
        'longitude_wgs': 'number',
        'longitude_wgs_fr_metropole': 'number',
        'year': 'year',
    }
    return metier_to_validata_type.get(format, 'string')


def get_example(format: str) -> str:
    """Returns the example for a given format"""
    format_to_example = {
        'booleen': 'true',
        'int': 42,
        'float': 42.42,
        'string': 'Lorem ipsum dolor sit amet',
        'adresse': '28 rue Ledion, 75014 Paris',
        'insee_canton': 'Pont-d\'Ain',
        'code_commune_insee': '27501',
        'code_csp_insee': '233c',
        'code_departement': '2A',
        'code_fantoir': 'A633',
        'code_postal': '75014',
        'code_region': '52',
        'code_rna': 'W123456789',
#        'code_waldec': TODO: add code_waldec
        'commune': 'Joyeux',
        'csp_insee': 'anciens agriculteurs exploitants',
        'date': '2020-01-01',
        'date_fr': '12 janvier 2020',
        'datetime_iso': '2020-01-01T00:00:00',
        'datetime_rfc822': 'Tue, 1 Jan 2020 00:00:00 +0000',
        'departement': 'Ain',
        'email': 'example@example.com',
        'insee_ape700': '0130Z',
        'iso_country_code_alpha2': 'FR',
        'iso_country_code_alpha3': 'FRA',
        'iso_country_code_numeric': 250,
        'jour_de_la_semaine': 'lundi',
        'json_geojson': '{"type": "Point", "coordinates": [0, 0]}',
        'latitude': 42.42,
        'latitude_l93': 6037008,
        'latitude_wgs': 42.42,
        'latitude_wgs_fr_metropole': 41.3,
        'latlon_wgs': '42.42, 0.0',
        'longitude': 0.0,
        'longitude_l93': -357823,
        'longitude_wgs': 0.0,
        'longitude_wgs_fr_metropole': 1.2,
        'mois_de_annee': 'janvier',
        'mongo_object_id': '507f191e810c19729de860ea',
        'pays': 'France',
        'region': 'nouvelle aquitaine',
        'sexe': 'h',
        'siren': '362521879',
        'siret': '56894100056',
        'tel_fr': '+33123456789',
        'twitter': '@Etalab',
        'uai': '0470009E',
        'url': 'https://www.data.gouv.fr',
        'uuid': '123e4567-e89b-12d3-a456-426614174000',
        'year': '2020',
    }
    return format_to_example.get(format, "")



def get_constraints(format: str) -> dict:
    """Returns the constraints for a given format"""
    extra_constraints = {}
    if format == "code_commune_insee":
        extra_constraints = {
            "pattern": "^[0-9]{5}$"
        }
    if format == "code_departement":
        extra_constraints = {
            "pattern": "^(0[13-9]|[1-8][0-9]|9[0-6]|2[a-bA-B]|97[1-6])$"
        }
    if format == "code_postal":
        extra_constraints = {
            "pattern": "^[0-9]{5}$"
        }
    if format == "code_fantoir":
        extra_constraints = {
            "pattern": "^[0-9A-Z][0-9]{3}[ABCDEFGHJKLMNPRSTUVWXYZ]$"
        }
    if format == "latitude_l93":
        extra_constraints = {
            "minimum": 6037008,
            "maximum": 7230728
        }
    if format == "longitude_l93":
        extra_constraints = {
            "minimum": -357823,
            "maximum": 7230728
        }
    if format == "latitude_wgs_fr_metropole":
        extra_constraints = {
            "minimum": 41.3,
            "maximum": 51.3
        }
    if format == "longitude_wgs_fr_metropole":
        extra_constraints = {
            "minimum": -5.5,
            "maximum": 9.8
        }
    if format == "siren":
        extra_constraints = {
            "pattern": "^[0-9]{9}$"
        }
    if format == "siret":
        extra_constraints = {
            "pattern": '^[0-9]{14}$'
        }
    return {"required": False, **extra_constraints}


def generate_table_schema(analysis_report: dict, netloc: str, bucket: str, key: str, minio_user: str, minio_pwd: str) -> None:
    """Generates a table schema from the analysis report

    Args:
        analysis_report (dict): The analysis report from csv_detective
        netloc (str): The netloc of the minio instance to upload the tableschema
        bucket (str): The bucket to save the schema in
        key (str): The key to save the schema in (without extension as we will append version number and extension)
        minio_user (str): The minio user
        minio_pwd (str): The minio password

    Returns:
        """
    fields = [{"name": header,
        "description": "",
        "example": get_example(field_report["format"]),
        "type": get_validata_type(field_report["format"]),
        "constraints": {
          "required": False
        }
    } for header, field_report in analysis_report["columns"].items()]

    # Create bucket if does not exist
    client = get_s3_client(netloc, minio_user, minio_pwd)
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)

    tableschema_objects = client.list_objects(Bucket=bucket, Prefix=key, Delimiter='/')
    if 'Contents' in tableschema_objects:
        tableschema_keys = [tableschema['Key'] for tableschema in client.list_objects(Bucket=bucket, Prefix=key, Delimiter='/')['Contents']]
        tableschema_versions = [os.path.splitext(tableschema_key)[0].split('_')[-1] for tableschema_key in tableschema_keys]
        latest_version = max(tableschema_versions)

        with tempfile.NamedTemporaryFile() as latest_schema_file:
            with open(latest_schema_file.name, 'w') as fp:
                download_from_minio(netloc, bucket, f"{key}_{latest_version}.json", latest_schema_file.name, minio_user, minio_pwd)
                # Check if files are different
                with open(latest_schema_file.name, 'r') as fp:
                    latest_schema = json.load(fp)
                    if latest_schema['fields'] != fields:
                        latest_version_split = latest_version.split('.')
                        new_version = latest_version_split[0] + '.' + latest_version_split[1] + '.' + str(int(latest_version_split[2]) + 1)
                    else:
                        return None
    else:
        new_version = '0.0.1'

    schema = {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "name": "",
        "title": "",
        "description": "",
        "countryCode": "FR",
        "homepage": "",
        "path": "",
        "resources": [
          {
            "title": "",
            "path": ""
          }
        ],
        "sources": [],
        "created": datetime.today().strftime('%Y-%m-%d'),
        "lastModified": datetime.today().strftime('%Y-%m-%d'),
        "version": new_version,
        "contributors": [
          {
            "title": "Table schema bot",
            "email": "",
            "organisation": "Etalab",
            "role": "author"
          },
        ],
        "fields": fields,
        "missingValues": [
          ""
        ]
    }

    tableschema_file = tempfile.NamedTemporaryFile(delete=False)
    with open(tableschema_file.name, 'w') as fp:
        json.dump(schema, fp,  indent=4)

    new_version_key = f"{key}_{new_version}.json"
    upload_to_minio(netloc, bucket, new_version_key, tableschema_file.name, minio_user, minio_pwd)
    os.unlink(tableschema_file.name)
    return {
        'netloc': netloc,
        'bucket': bucket,
        'key': new_version_key
    }
