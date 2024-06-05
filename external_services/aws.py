from collections import namedtuple
from os import getenv

import boto3
from config import Config

_KEY_PARTS = ("application_id", "form", "path", "component_id", "filename")

if getenv("PRIMARY_QUEUE_URL", "Primary Queue URL Not Set") == "Primary Queue URL Not Set":
    _S3_CLIENT = boto3.client(
        "s3",
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION,
        endpoint_url=getenv("AWS_ENDPOINT_OVERRIDE", None),
    )
else:
    _S3_CLIENT = boto3.client(
        "s3",
        region_name=Config.AWS_REGION,
        endpoint_url=getenv("AWS_ENDPOINT_OVERRIDE", None),
    )

FileData = namedtuple("FileData", _KEY_PARTS)


def list_files_by_prefix(prefix: str) -> list[FileData]:
    objects_response = _S3_CLIENT.list_objects_v2(
        Bucket=Config.AWS_BUCKET_NAME,
        Prefix=prefix,
    )

    contents = objects_response.get("Contents") or []
    return [
        FileData(*key_parts)
        for key in [file["Key"] for file in contents]
        if len(key_parts := key.split("/")) == len(_KEY_PARTS)
    ]
