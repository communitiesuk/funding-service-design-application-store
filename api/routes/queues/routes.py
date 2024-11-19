# from config import Config
import json
from uuid import uuid4

from flask import current_app
from flask.views import MethodView

from config import Config
from db.queries import get_application


class QueueView(MethodView):
    def post_submitted_application_to_assessment(self, application_id=None):
        application_with_form_json = get_application(application_id, as_json=True, include_forms=True)
        # check to see if application has status submitted
        if application_with_form_json["status"] == "SUBMITTED":
            application_attributes = {
                "application_id": {"StringValue": application_id, "DataType": "String"},
                "S3Key": {
                    "StringValue": "assessment",
                    "DataType": "String",
                },
            }

            """
            Submit message to queue, in a future state this can
            trigger the assessment service to import the application
            (currently assessment is using a CRON timer to pick up messages,
            not a webhook for triggers)
            """
            try:
                sqs_extended_client = self._get_sqs_client()
                message_id = sqs_extended_client.submit_single_message(
                    queue_url=Config.AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL,
                    message=json.dumps(application_with_form_json),
                    message_group_id="import_applications_group",
                    message_deduplication_id=str(uuid4()),  # ensures message uniqueness
                    extra_attributes=application_attributes,
                )
                current_app.logger.info(
                    "Message sent to SQS queue and message id is [{message_id}]",
                    extra=dict(message_id=message_id),
                )
                return f"Message queued, message_id is: {message_id}.", 201
            except Exception as e:
                current_app.logger.error("An error occurred while sending message")
                current_app.logger.error(e)
                return {
                    "code": 500,
                    "message": "Message failed",
                }, 500
        else:
            return {
                "code": 400,
                "message": "Application must be submitted before it can be assessed",
            }, 400

    def _get_sqs_client(self):
        sqs_extended_client = current_app.extensions["sqs_extended_client"]
        if sqs_extended_client is not None:
            return sqs_extended_client
        current_app.logger.error("An error occurred while sending message since client is not available")
