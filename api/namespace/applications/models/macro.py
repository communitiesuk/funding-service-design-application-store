from api.namespace.applications.applications_ns import applications_ns
from flask_restx import fields

macro = applications_ns.model(
    "macro_post",
    {
        "account_id": fields.String(
            required=True,
            description="The associated account",
            example="dfgdfg45et5ed",
        ),
        "application_id": fields.String(
            required=True,
            description=(
                "The application id associated with this macro application"
            ),
            example="dfgdfg45et5ed",
        ),
        "sections": fields.List(fields.String()),
    },
)
