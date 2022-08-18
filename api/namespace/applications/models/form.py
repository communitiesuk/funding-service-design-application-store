from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.models.metadata import metadata
from api.namespace.applications.models.question import question
from api.namespace.applications.models.question import question_status
from flask_restx import fields

form_inbound = applications_ns.model(
    "form_inbound",
    {
        "name": fields.String(
            required=True,
            description="The name of the fund",
            example="Funding Service Design",
        ),
        "questions": fields.List(
            fields.Nested(
                question,
                required=True,
                description=(
                    "The payload of application questions and answers."
                ),
            ),
        ),
        "metadata": fields.Nested(
            metadata, description="Application metadata"
        ),
    },
)

form_outbound = applications_ns.model(
    "form_outbound",
    {
        "form_name": fields.String(
            required=True,
            description="The name of the form (the form json file name)",
            example="about-you",
        ),
        "status": fields.String(
            description="The completion status of the form",
            example="IN_PROGRESS",
        ),
        "questions": fields.List(
            fields.Nested(
                question,
                required=True,
                description=(
                    "The payload of application questions and answers."
                ),
            ),
        ),
        "metadata": fields.Nested(
            metadata, description="Application metadata"
        ),
    },
)

form_status = applications_ns.model(
    "form_status",
    {
        "form_name": fields.String(
            required=True,
            description="The name of the form",
            example="about-you",
        ),
        "status": fields.String(
            description="The completion status of the form",
            example="IN_PROGRESS",
        ),
        "questions": fields.List(
            fields.Nested(
                question_status,
                required=True,
                description="The completion status of each question.",
            ),
        ),
    },
)
