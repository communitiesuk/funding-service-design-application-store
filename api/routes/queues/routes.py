# from config import Config
from uuid import uuid4

from config import Config
from db.queries import get_application
from external_services.aws import _SQS_CLIENT
from flask.views import MethodView

# from flask import request


class QueueView(MethodView):
    def post_submitted_application_to_assessment(self, application_id=None):
        application_with_form_json = get_application(application_id, as_json=True, include_forms=True)
        # check to see if application has status submitted
        if application_with_form_json["status"] == "SUBMITTED":
            application_attributes = {
                "application_id": {"StringValue": application_id, "DataType": "String"},
            }

            # Submit message to queue, in a future state this can
            # trigger the assessment service to import the application
            #  (currently assessment is using a CRON timer to pick up messages,
            # not a webhook for triggers)

            message_submitted_id = _SQS_CLIENT.submit_single_message(
                queue_url=Config.AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL,
                message=application_with_form_json,
                extra_attributes=application_attributes,
                message_group_id="import_applications_group",
                message_deduplication_id=str(uuid4()),  # ensures message uniqueness
            )

            return f"Message queued, message_id is: {message_submitted_id}.", 201
        else:
            return {
                "code": 400,
                "message": "Application must be submitted before it can be assessed",
            }, 400
