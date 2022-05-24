from config import NOTIFICATION_SERVICE_HOST
from config import SEND_ENDPOINT
from external_services.data import post_data


class Notification(object):
    @classmethod
    def send(cls, template_type: str, to_email: str, content: dict):

        url = NOTIFICATION_SERVICE_HOST + SEND_ENDPOINT
        params = {"type": template_type, "to": to_email, "content": content}
        response = post_data(url, params)
        if response:
            return True
        raise NotificationError(
            message="Sorry, the notification could not be sent"
        )


class NotificationError(Exception):
    """Exception raised for errors in Notification management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem please try later"):
        self.message = message
        super().__init__(self.message)
