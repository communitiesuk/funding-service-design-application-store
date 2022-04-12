from api.namespace.applications.applications_ns import applications_ns
from flask_restx import fields
from api.namespace.applications.models.field import field

question = applications_ns.model(
    "question",
    {
        "question": fields.String(
            required=True,
            description="The questions and corresponding answers",
            example="About you"
        ),
        "status": fields.String(
            required=False,
            description="Status",
            example="COMPLETED"
        ),
        "fields": fields.List(
            fields.Nested(
                field,
                description="Individual question fields",
            )
        ),
        "category": fields.String(
            required=False,
            description="Category",
            example="abcxyz"
        ),
        "index": fields.Integer(
            required=False,
            description="Index",
            example=0
        ),
    },
)

question_status = applications_ns.model(
    "question_status",
    {
        "question": fields.String(
            required=True,
            description="The questions and corresponding answers",
            example="About you"
        ),
        "status": fields.String(
            required=False,
            description="Status",
            example="COMPLETED"
        ),
    },
)