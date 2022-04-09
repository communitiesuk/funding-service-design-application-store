from api.namespace.application.application_ns import application_ns
from api.namespace.application.models.question import question
from api.namespace.application.models.question import question_status
from api.namespace.application.models.metadata import metadata

from flask_restx import fields

application_inbound = application_ns.model(
    "application_inbound",
    {
        "name": fields.String(
            required=True,
            description="The name of the fund",
            example="Funding Service Design"
        ),
        "questions": fields.List(
            fields.Nested(
                question,
                required=True,
                description=(
                    "The payload of application questions and"
                    " answers."
                ),
            ),
        ),
        "metadata": fields.Nested(
            metadata,
            description="Application metadata"
        ),
    },
)

application_full = application_ns.model(
    "application_full",
    {
        "id": fields.String(
            description="The id of the application.",
        ),
        "status": fields.String(
            description="The status of the application",
            example="NOT_STARTED"
        ),
        "fund_id": fields.String(
            description="The id of the fund",
            example="funding-service-design"
        ),
        "fund_name": fields.String(
            description="The name of the fund",
            example="Funding Service Design"
        ),
        "round_id": fields.String(
            description="The id of the round",
            example="spring"
        ),
        "date_submitted": fields.String(
            description="The datetime the application was submitted",
            example="2022-12-25 00:00:00"
        ),
        "assessment_deadline": fields.String(
            description="The assessment deadline for this application's round",
            example="2022-12-25 00:00:00"
        ),
        "questions": fields.List(
            fields.Nested(
                question,
                description=(
                    "Application questions and answers."
                ),
            ),
        ),
        "metadata": fields.Nested(
            metadata,
            description="Application metadata"
        ),
    },
)

application_status = application_ns.model(
    "application_status",
    {
        "id": fields.String(
            description="The id of the application"
        ),
        "status": fields.String(
            description="The status of the application"
        ),
        "fund_id": fields.String(
            description="The id of the fund"
        ),
        "fund_name": fields.String(
            description="The name of the fund"
        ),
        "round_id": fields.String(
            description="The id of the round"
        ),
        "date_submitted": fields.String(
            description="The datetime the application was submitted"
        ),
        "assessment_deadline": fields.String(
            description="The assessment deadline for this application's round"
        ),
        "questions": fields.List(
            fields.Nested(
                question_status,
                description=(
                    "Questions and their assessment status"
                ),
            ),
        ),
    },
)