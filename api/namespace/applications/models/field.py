from api.namespace.applications.applications_ns import applications_ns
from flask_restx import fields


field = applications_ns.model(
    "field",
    {
        "key": fields.String(
            required=True,
            description="Field key or name attribute",
            example="applicant_name"
        ),
        "title": fields.String(
            required=True,
            description="Field title",
            example="Applicant name"
        ),
        "type": fields.String(
            required=True,
            description="Field type",
            example="text"
        ),
        "answer": fields.String(
            required=True,
            description="Field answer or value",
            example="Applicant"
        ),
    },
)
