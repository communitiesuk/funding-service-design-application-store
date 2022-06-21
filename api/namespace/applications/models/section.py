from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.models.metadata import metadata
from api.namespace.applications.models.question import question
from api.namespace.applications.models.question import question_status
from flask_restx import fields

section_inbound = applications_ns.model(
    "section_inbound",
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
                description=("The payload of application questions and answers."),
            ),
        ),
        "metadata": fields.Nested(metadata, description="Application metadata"),
    },
)

section = applications_ns.model(
    "section",
    {
        "section_name": fields.String(
            required=True,
            description="The name of the section",
            example="about-you",
        ),
        "status": fields.String(
            description="The completion status of the section",
            example="IN_PROGRESS",
        ),
        "questions": fields.List(
            fields.Nested(
                question,
                required=True,
                description=("The payload of application questions and answers."),
            ),
        ),
        "metadata": fields.Nested(metadata, description="Application metadata"),
    },
)

section_status = applications_ns.model(
    "section_status",
    {
        "section_name": fields.String(
            required=True,
            description="The name of the section",
            example="about-you",
        ),
        "status": fields.String(
            description="The completion status of the section",
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
