class NotificationError(Exception):
    """Exception raises an an error

    Attributes:
        message -- explanation of the error
    """

    def __init__(
        self,
        message="Sorry, there was a problem posting to the notification service",
    ):
        self.message = message
        super().__init__(self.message)
