import json
from collections import namedtuple
from datetime import datetime
from os import getenv

import boto3
from botocore.exceptions import ClientError
from config import Config

_KEY_PARTS = ("application_id", "form", "path", "component_id", "filename")
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


def create_sqs_and_dlq_queue():
    """
    Creates an Amazon SQS & DLQ queue.

    :return: (sqs_queue_url, dlq_queue_url)
    """
    # get queue list
    queue_list = get_queues()

    # create DLQ queue if not exists
    dlq_queue_name = getenv("AWS_DLQ_QUEUE_NAME", "fsd-dlq")
    if dlq_queue_name not in queue_list:
        dlq_queue_url = _SQS_CLIENT.create_queue(
            QueueName=dlq_queue_name,
        )["QueueUrl"]
        dlq_queue_arn = _SQS_CLIENT.get_queue_attributes(
            QueueUrl=dlq_queue_url, AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]
    else:
        dlq_queue_url = _SQS_CLIENT.get_queue_url(QueueName=dlq_queue_name)["QueueUrl"]
        dlq_queue_arn = _SQS_CLIENT.get_queue_attributes(
            QueueUrl=dlq_queue_url, AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]

    # create SQS queue if not exists
    sqs_queue_name = getenv("AWS_SQS_QUEUE_NAME", "fsd-queue")
    redrive_policy = {
        "deadLetterTargetArn": dlq_queue_arn,
        "maxReceiveCount": getenv("AWS_DLQ_MAX_RECIEVE_COUNT", "3"),
    }
    if sqs_queue_name not in queue_list:
        sqs_queue_url = _SQS_CLIENT.create_queue(
            QueueName=sqs_queue_name,
            Attributes={"RedrivePolicy": json.dumps(redrive_policy)},
        )
    else:
        sqs_queue_url = _SQS_CLIENT.get_queue_url(QueueName=sqs_queue_name)["QueueUrl"]
        _SQS_CLIENT.set_queue_attributes(
            QueueUrl=sqs_queue_url,
            Attributes={"RedrivePolicy": json.dumps(redrive_policy)},
        )

    return sqs_queue_url, dlq_queue_url


_SQS_QUEUE_URL, _DQL_QUEUE_URL = create_sqs_and_dlq_queue()


def _get_queue_url(sqs_client, queue_name):
    response = sqs_client.get_queue_url(
        QueueName=queue_name,
    )
    return response["QueueUrl"]


def submit_message_to_queue(message, extra_attributes: dict = None):
    print(f"Attempting to place message on queue '{_SQS_QUEUE_URL}'.")
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

        queue_url = _get_queue_url(
            _SQS_CLIENT,
            Config.AWS_SQS_APPLICATION_TO_ASSESSMENT_PRIMARY_QUEUE,
        )
        response = _SQS_CLIENT.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes=SQS_CUSTOM_ATTRIBUTES,
        )
        message_id = response["MessageId"]
        print(
            f"Message (id: {message_id}) submitted to queue:"
            f" {Config.AWS_SQS_APPLICATION_TO_ASSESSMENT_PRIMARY_QUEUE}."
        )
        return message_id
    except Exception as e:
        print(
            "Error whilst staging onto queue"
            f" '{Config.AWS_SQS_APPLICATION_TO_ASSESSMENT_PRIMARY_QUEUE}', message with"
            f" attributes '{str(extra_attributes)}'."
        )
        return str(e), 500, {"x-error": "Error"}


# if __name__ == "__main__":
#     from app import app
#     with app.app_context():
#         print("done")
#         remove_queue(_DQL_QUEUE_URL)
#         remove_queue(_SQS_QUEUE_URL)
