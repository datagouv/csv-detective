from botocore.exceptions import ClientError
from datetime import datetime
import json
import os
import tempfile

from csv_detective.s3_utils import get_s3_client, download_from_minio, upload_to_minio


def get_constraints(format: str) -> dict:
    """Returns the constraints for a given format"""
    extra_constraints = {}
    if format == "code_commune_insee":
        extra_constraints = {
            "pattern": "^[0-9]{5}$"
        }
    if format == "code_departement":
        extra_constraints = {
            "pattern": "^(0[13-9]|[1-8]{2}|9[0-6]|2[a-bA-B]|97[1-6])$"
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


def generate_table_schema(analysis_report: dict, url: str, bucket: str, key: str, minio_user: str, minio_pwd: str) -> None:
    """Generates a table schema from the analysis report

    Args:
        analysis_report (dict): The analysis report from csv_detective
        url (str): The url of the minio instance to upload the tableschema
        bucket (str): The bucket to save the schema in
        key (str): The key to save the schema in (without extension as we will append version number and extension)
        minio_user (str): The minio user
        minio_pwd (str): The minio password

    Returns:
        """
    fields = [{"name": header,
        "description": "",
        "example": "",
        "type": field_report["format"],
        "constraints": {
          "required": False
        }
    } for header, field_report in analysis_report["columns"].items()]

    # Create bucket if does not exist
    client = get_s3_client(url, minio_user, minio_pwd)
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
                download_from_minio(url, bucket, f"{key}_{latest_version}.json", latest_schema_file.name, minio_user, minio_pwd)
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
    upload_to_minio(url, bucket, new_version_key, tableschema_file.name, minio_user, minio_pwd)
    os.unlink(tableschema_file.name)
    return {
        'url': url,
        'bucket': bucket,
        'key': new_version_key
    }
