# from config import Config
import contextlib
from uuid import uuid4

from config import Config
from db.queries import get_application
from external_services.aws import _SQS_CLIENT
from flask.views import MethodView


# from flask import request


class QueueView(MethodView):
    def post_submitted_application_to_assessment(self, application_id=None):

        application_with_form_json = get_application(
            application_id, as_json=True, include_forms=True
        )
        # check to see if application has status submitted
        if application_with_form_json["status"] == "SUBMITTED":
            application_attributes = {
                "application_id": {"StringValue": application_id, "DataType": "String"},
            }

            # Submit message to queue, in a future state this can
            # trigger the assessment service to import the application
            #  (currently assessment is using a CRON timer to pick up messages,
            # not a webhook for triggers)

            # TODO: (FS-3703) Revisit this part after AWS migration
            # 'MessageGroupId' & 'MessageDeduplicationId' are mandatary parameters to be provided on PAAS,
            # while they are not acceptable parameters on localstack queue
            message_submitted_id = _SQS_CLIENT.submit_single_message(
                queue_url=Config.AWS_SQS_IMPORT_APP_PRIMARY_QUEUE_URL,
                message=application_with_form_json,
                extra_attributes=application_attributes,
                message_group_id="import_applications_group",
                message_deduplication_id=str(uuid4()),
            )

            return f"Message queued, message_id is: {message_submitted_id}.", 201
        else:
            return {
                "code": 400,
                "message": "Application must be submitted before it can be assessed",
            }, 400

    def health_check(self, queue_prefix: str = None) -> dict[str, bool]:
        queue_name_to_status_dict = {
            q: False for q in _SQS_CLIENT.get_queues(prefix=queue_prefix)
        }
        for queue_name in queue_name_to_status_dict.keys():
            # normally against bare except, but this is for health check
            with contextlib.suppress(Exception):
                queue_url = _SQS_CLIENT.get_queue_url(queue_name)
                message_id = _SQS_CLIENT.submit_single_message(
                    queue_url=queue_url,
                    message={},  # empty body for health check
                    message_group_id="health_check",
                )
                if messages := _SQS_CLIENT.receive_messages(queue_url, max_number=1):
                    if message := next(
                        (m for m in messages if m["MessageId"] == message_id), None
                    ):
                        delete_resp = _SQS_CLIENT.delete_messages(
                            queue_url, [message["ReceiptHandle"]]
                        )
                        queue_name_to_status_dict[queue_name] = (
                            len(delete_resp.get("Successful") or []) == 1
                        )
        return queue_name_to_status_dict
