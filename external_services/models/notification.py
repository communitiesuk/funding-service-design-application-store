import json
from uuid import uuid4

from config import Config
from external_services.exceptions import NotificationError
from flask import current_app


class Notification:
    """
    Class for holding Notification operations
    """

    @staticmethod
    def send(template_type: str, to_email: str, full_name: str, content: dict):
        """
        Sends a notification using the Gov.UK Notify Service

        Args:
            template_type: (str) A key of the template to use in the
                DLUHC notifications service (which maps to a
                Notify Service template key)
            to_email: (str) The email to send the notification to
            content: (dict) A dictionary of content to send to
                fill out the notification template
        """
        url = Config.NOTIFICATION_SERVICE_HOST + Config.SEND_ENDPOINT
        json_payload = {
            "type": template_type,
            "to": to_email,
            "full_name": full_name,
            "content": content,
        }
        current_app.logger.info(
            f"Sending application to notification service. endpoint '{url}',"
            f" json payload '{template_type}' to '{to_email}'."
        )
        try:
            sqs_extended_client = Notification._get_sqs_client()
            message_id = sqs_extended_client.submit_single_message(
                queue_url=Config.AWS_SQS_NOTIF_APP_PRIMARY_QUEUE_URL,
                message=json.dumps(json_payload),
                message_group_id="notification",
                message_deduplication_id=str(uuid4()),  # ensures message uniqueness
            )
            current_app.logger.info(f"Message sent to SQS queue and message id is [{message_id}]")
            return message_id
        except Exception as e:
            current_app.logger.error("An error occurred while sending message")
            current_app.logger.error(e)
            raise NotificationError(message="Sorry, the notification could not be sent")

    @staticmethod
    def _get_sqs_client():
        sqs_extended_client = current_app.extensions["sqs_extended_client"]
        if sqs_extended_client is not None:
            return sqs_extended_client
        current_app.logger.error("An error occurred while sending message since client is not available")
