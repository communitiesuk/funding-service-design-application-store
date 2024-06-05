import unittest
from unittest import mock
from unittest.mock import MagicMock

import boto3
import pytest
from config import Config
from external_services.exceptions import NotificationError
from external_services.models.notification import Notification
from fsd_utils import NotifyConstants
from fsd_utils.services.aws_extended_client import SQSExtendedClient
from moto import mock_aws


class NotificationTest(unittest.TestCase):
    @mock_aws
    @pytest.mark.usefixtures("live_server")
    def test_notification_send_success(self):
        with mock.patch("external_services.models.notification.Notification._get_sqs_client") as mock_get_sqs_client:
            template_type = Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION
            to_email = "test@example.com"
            full_name = "John"
            contents = {
                NotifyConstants.APPLICATION_FIELD: "Funding name",
                NotifyConstants.MAGIC_LINK_CONTACT_HELP_EMAIL_FIELD: "test_gmail.com",
            }
            sqs_extended_client = SQSExtendedClient(
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_REGION,
                large_payload_support=Config.AWS_MSG_BUCKET_NAME,
                always_through_s3=True,
                delete_payload_from_s3=True,
                logger=MagicMock(),
            )
            s3_connection = boto3.client(
                "s3", region_name="us-east-1", aws_access_key_id="test_accesstoken", aws_secret_access_key="secret_key"
            )
            sqs_connection = boto3.client(
                "sqs", region_name="us-east-1", aws_access_key_id="test_accesstoken", aws_secret_access_key="secret_key"
            )
            s3_connection.create_bucket(Bucket=Config.AWS_MSG_BUCKET_NAME)
            queue_response = sqs_connection.create_queue(QueueName="notif-queue.fifo", Attributes={"FifoQueue": "true"})
            sqs_extended_client.sqs_client = sqs_connection
            sqs_extended_client.s3_client = s3_connection
            Config.AWS_SQS_NOTIF_APP_PRIMARY_QUEUE_URL = queue_response["QueueUrl"]
            mock_get_sqs_client.return_value = sqs_extended_client
            result = Notification.send(template_type, to_email, full_name, contents)
            assert result is not None

    @mock_aws
    @pytest.mark.usefixtures("live_server")
    def test_notification_send_failure(self):
        with mock.patch("external_services.models.notification.Notification._get_sqs_client") as mock_get_sqs_client:
            template_type = Config.NOTIFY_TEMPLATE_SUBMIT_APPLICATION
            to_email = "test@example.com"
            full_name = "John"
            contents = {
                NotifyConstants.APPLICATION_FIELD: "Funding name",
                NotifyConstants.MAGIC_LINK_CONTACT_HELP_EMAIL_FIELD: "test_gmail.com",
            }
            sqs_extended_client = MagicMock()
            mock_get_sqs_client.return_value = sqs_extended_client
            sqs_extended_client.submit_single_message.side_effect = Exception("SQS Error")
            with pytest.raises(NotificationError, match="Sorry, the notification could not be sent"):
                Notification.send(template_type, to_email, full_name, contents)

    def test_notification_error_custom_message(self):
        custom_message = "Custom error message"
        error = NotificationError(custom_message)
        assert str(error) == custom_message

    def test_notification_error_default_message(self):
        error = NotificationError()
        assert str(error) == "Sorry, there was a problem posting to the notification service"
