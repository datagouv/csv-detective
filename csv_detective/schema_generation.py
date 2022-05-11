from botocore.exceptions import ClientError
from datetime import datetime
import json
import os
import tempfile

from csv_detective.s3_utils import get_s3_client, download_from_minio, upload_to_minio

def generate_table_schema(analysis_report: dict, url: str, bucket: str, key: str, minio_user: str, minio_pwd: str) -> None:
    publish_new_version = True

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
                        publish_new_version = False
    else:
        new_version = '0.0.1'

    if publish_new_version:
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

        upload_to_minio(url, bucket, f'{key}_{new_version}.json', tableschema_file.name, minio_user, minio_pwd)
        os.unlink(tableschema_file.name)
