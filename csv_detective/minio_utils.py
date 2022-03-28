
import os
from minio import Minio


def get_client(minio_url: str, minio_user: str=None, minio_password: str=None) -> Minio:
    if minio_user is None:
        minio_user = os.environ['MINIO_USER']
    if minio_password is None:
        minio_password = os.environ['MINIO_PASSWORD']

    return Minio(
        minio_url,
        access_key=minio_user,
        secret_key=minio_password,
        secure=True
    )


def download_minio_file(
    client: Minio,
    minio_bucket: str,
    minio_key: str,
    target_filename: str
) -> None:
    client.fget_object(minio_bucket, minio_key, target_filename)


def upload_minio_file(client: Minio, minio_bucket: str, minio_key: str, filepath: str):
    client.fput_object(
       minio_bucket,
       minio_key,
       filepath,
       content_type='text/csv; charset=utf-8',
       metadata={'Content-Disposition': 'inline'}
    )