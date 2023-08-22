from _helpers import submit_message
from flask import request
from flask.views import MethodView
from config import Config
from db.queries import get_application

class QueueView(MethodView):
    def post_submitted_application_to_assessment(self, application_id = None):

        application_with_form_json = get_application(
            application_id, as_json=True, include_forms=True
        )
        # check to see if application has status submitted
        if application_with_form_json["status"] == "SUBMITTED":
            application_attributes = {
                "application_id": {"StringValue": application_id, "DataType": "String"},
            }

            # Submit message to queue, in a future state this can trigger the assessment service to import the application
            #  (currently assessment is using a CRON timer to pick up messages, not a webhook for triggers) 
            message_submitted = submit_message(Config.SUBMIT_APPLICATION_TO_ASSESSMENT_QUEUE_NAME, application_with_form_json, application_attributes)

            return f"Message queued, message_id is: {message_submitted}.", 201
        else:
            return {"code": 400, "message": "Application must be submitted before it can be assessed"}, 400
