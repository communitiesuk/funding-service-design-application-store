import boto3
from config import Config
from uuid import uuid4
from datetime import datetime


def get_queue_url(sqs_client, queue_name):
    response = sqs_client.get_queue_url(
        QueueName=queue_name,
    )
    return response["QueueUrl"]



def submit_message(queue_name, message):
    sqs_client = boto3.client(
        "sqs",
        region_name=Config.AWS_REGION,
        endpoint_url=Config.AWS_ENDPOINT_OVERRIDE  # Set the LocalStack SQS endpoint
    )

    custom_attributes = {
        'id': {
            'StringValue': str(uuid4()),
            'DataType': 'String'
        },
        'datetime': {
            'StringValue': str(datetime.now()),
            'DataType': 'String'
        }
    }

    queue_url = get_queue_url(sqs_client, queue_name)
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message,
        DelaySeconds=123,
        MessageAttributes=custom_attributes
    )
    print(response)