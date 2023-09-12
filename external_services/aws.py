import json
from collections import namedtuple
from datetime import datetime
from os import getenv
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
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
    _SQS_CLIENT = boto3.client(
        "sqs",
        aws_access_key_id=Config.AWS_SQS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SQS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_SQS_REGION,
        endpoint_url=getenv("AWS_ENDPOINT_OVERRIDE", None),
    )
else:
    _S3_CLIENT = boto3.client(
        "s3",
        region_name=Config.AWS_REGION,
        endpoint_url=getenv("AWS_ENDPOINT_OVERRIDE", None),
    )
    _SQS_CLIENT = boto3.client(
        "sqs",
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


def get_queues(prefix=None):
    """
    Gets a list of SQS queues. When a prefix is specified, only queues with names
    that start with the prefix are returned.

    :param prefix: The prefix used to restrict the list of returned queues.
    :return: A list of Queue names.
    """
    if prefix:
        queues = _SQS_CLIENT.list_queues(QueueNamePrefix=prefix)["QueueUrls"]
    else:
        queues = _SQS_CLIENT.list_queues()["QueueUrls"]
    if queues:
        print(f"Got queues: {', '.join([q for q in queues])}")
        queue_names = [url.split("/")[-1] for url in queues]
        return queue_names
    else:
        print("No queues found.")
        return []


def remove_queue(queue_url):
    """
    Removes an SQS queue. When run against an AWS account, it can take up to
    60 seconds before the queue is actually deleted.

    :param queue: The queue to delete.
    :return: None
    """
    try:
        _SQS_CLIENT.delete_queue(QueueUrl=queue_url)
        print(f"Deleted queue with URL={queue_url}.")
    except ClientError as error:
        print(f"Couldn't delete queue with URL={queue_url}!")
        raise error


def _get_queue_url(sqs_client, queue_name):
    response = sqs_client.get_queue_url(
        QueueName=queue_name,
    )
    return response["QueueUrl"]


def submit_message_to_queue(message, extra_attributes: dict = None):
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

        queue_url = Config.AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL or _get_queue_url(
            _SQS_CLIENT,
            getenv("AWS_SQS_QUEUE_NAME", "fsd-queue"),
        )
        print(f"Attempting to place message on queue '{queue_url}'.")

        # TODO: Revisit this part after AWS migration
        if "docker" in queue_url or "local" in queue_url:  # if running on localstack
            response = _SQS_CLIENT.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                MessageAttributes=SQS_CUSTOM_ATTRIBUTES,
            )
        else:
            response = _SQS_CLIENT.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                MessageAttributes=SQS_CUSTOM_ATTRIBUTES,
                MessageGroupId="import_applications_group",
                MessageDeduplicationId=str(uuid4()),
            )
        message_id = response["MessageId"]
        print(f"Message (id: {message_id}) submitted to queue: {queue_url}.")
        return message_id
    except Exception as e:
        print(
            "Error whilst staging onto queue"
            f" '{queue_url}', message with"
            f" attributes '{str(extra_attributes)}'."
            f" Error : {str(e)}"
        )
        return str(e), 500, {"x-error": "Error"}
