import boto3
import logging

from botocore.client import Config
from botocore.exceptions import ClientError


def get_minio_url(netloc: str, bucket: str, key: str) -> str:
    """Returns location of given resource in minio once it is saved"""
    return netloc + "/" + bucket + "/" + key


def get_s3_client(url: str, minio_user: str, minio_pwd: str) -> boto3.client:
    return boto3.client(
        "s3",
        endpoint_url=url,
        aws_access_key_id=minio_user,
        aws_secret_access_key=minio_pwd,
        config=Config(signature_version="s3v4"),
    )


def download_from_minio(
    netloc: str, bucket: str, key: str, filepath: str, minio_user: str, minio_pwd: str
) -> None:
    logging.info("Downloading from minio")
    s3 = get_s3_client(netloc, minio_user, minio_pwd)
    try:
        s3.download_file(bucket, key, filepath)
        logging.info(
            f"Resource downloaded from minio at {get_minio_url(netloc, bucket, key)}"
        )
    except ClientError as e:
        logging.error(e)


def upload_to_minio(
    netloc: str, bucket: str, key: str, filepath: str, minio_user: str, minio_pwd: str
) -> None:
    logging.info("Saving to minio")
    s3 = get_s3_client(netloc, minio_user, minio_pwd)
    try:
        s3.upload_file(filepath, bucket, key)
        logging.info(
            f"Resource saved into minio at {get_minio_url(netloc, bucket, key)}"
        )
    except ClientError as e:
        logging.error(e)
