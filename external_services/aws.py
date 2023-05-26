import contextlib
from collections import namedtuple

import boto3
from config import Config

_S3_CLIENT = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION,
)


FileData = namedtuple(
    "FileData", ["application_id", "form", "path", "component_id", "filename"]
)


def list_files_by_prefix(prefix: str) -> list[FileData]:
    objects_response = _S3_CLIENT.list_objects_v2(
        Bucket=Config.AWS_BUCKET_NAME,
        Prefix=prefix,
    )

    if not objects_response.get("Contents"):
        return []

    files = []
    keys = [file["Key"] for file in objects_response["Contents"]]
    for key in keys:
        with contextlib.suppress(ValueError):  # if we don't have a valid key, skip it
            application_id, form, path, component_id, filename = key.split("/")
            files.append(
                FileData(
                    application_id=application_id,
                    form=form,
                    path=path,
                    component_id=component_id,
                    filename=filename,
                )
            )
    return files
