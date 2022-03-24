from flask_restx import fields
from flask_restx import Namespace

"""
Namespace acts as part of an api (with the same methods as api)
"""


fund_ns = Namespace("fund", description="application operations")


question_model = fund_ns.model(
    "question",
    {
        "question": fields.String(
            required=True,
            description="The questions and corresponding answers",
        ),
        "fields": fields.Raw(required=True),
        "category": fields.String(required=False, description="Category"),
        "index": fields.Integer(required=False, description="Index"),
    },
)

application_model_inbound = fund_ns.model(
    "application_inbound",
    {
        "name": fields.String(
            required=True, description="Required: The name of the fund."
        ),
        "questions": fields.List(
            fields.Nested(
                question_model,
                required=True,
                description=(
                    "Required: The payload of application questions and"
                    " answers."
                ),
            ),
        ),
        "metadata": fields.String(
            required=False, description="Fund metadata."
        ),
    },
)

question_status_model = fund_ns.model(
    "question",
    {
        "question": fields.String(
            required=False,
        ),
        "status": fields.String(required=False),
    },
)


application_get_status_model = fund_ns.model(
    "questions_status",
    {
        "application_id": fields.String(
            required=True, description="Required: application id of the fund."
        ),
        "questions": fields.Nested(question_status_model, required=False),
    },
)
