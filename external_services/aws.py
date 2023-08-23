import json
from collections import namedtuple
from datetime import datetime
from os import getenv

import boto3
from config import Config
from flask import current_app

_KEY_PARTS = ("application_id", "form", "path", "component_id", "filename")
_S3_CLIENT = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
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


def _get_queue_url(sqs_client, queue_name):
    response = sqs_client.get_queue_url(
        QueueName=queue_name,
    )
    return response["QueueUrl"]


def submit_message_to_queue(queue_name, message, extra_attributes: dict = None):
    current_app.logger.info(f"Attempting to place message on queue '{queue_name}'.")
    try:
        SQS_CUSTOM_ATTRIBUTES = {
            "message_created_at": {
                "StringValue": str(datetime.now()),
                "DataType": "String",
            },
        }
        # add extra message attributes (if provided)
        if extra_attributes:
            for key, value in extra_attributes.items():
                SQS_CUSTOM_ATTRIBUTES[key] = value

        sqs_client = boto3.client(
            "sqs",
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION,
            endpoint_url=Config.AWS_ENDPOINT_OVERRIDE
            if hasattr(Config, "AWS_ENDPOINT_OVERRIDE")
            else None,  # optional local override
        )

        queue_url = _get_queue_url(sqs_client, queue_name)
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes=SQS_CUSTOM_ATTRIBUTES,
        )
        message_id = response["MessageId"]
        current_app.logger.info(
            f"Message (id: {message_id}) submitted to queue: {queue_name}."
        )
        return message_id
    except Exception as e:
        current_app.logger.error(
            f"Error whilst staging onto queue '{queue_name}', message with attributes"
            f" '{str(extra_attributes)}'."
        )
        return str(e), 500, {"x-error": "Error"}
