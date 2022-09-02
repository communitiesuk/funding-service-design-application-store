from config import Config
from external_services.http_methods import post_data
from flask import current_app


class Notification(object):
    """
    Class for holding Notification operations
    """

    @staticmethod
    def send(template_type: str, to_email: str, content: dict):
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
        params = {"type": template_type, "to": to_email, "content": content}
        current_app.logger.info(
            f"Sending application to notification service. endpoint: '{url}',"
            f" params: '{params}'."
        )
        response = post_data(url, params)
        current_app.logger.info(
            "application sent to notification service with response:"
            f" '{response}'."
        )
        if response:
            return True
        raise NotificationError(
            message=(
                "Sorry, the notification could not be sent for endpoint:"
                f" '{url}', params: '{params}'."
            )
        )


class NotificationError(Exception):
    """Exception raised for errors in Notification management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem please try later"):
        self.message = message
        super().__init__(self.message)
