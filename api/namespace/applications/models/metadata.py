from api.namespace.applications.applications_ns import applications_ns
from flask_restx import fields

metadata = applications_ns.model(
    "metadata",
    {
        "paymentSkipped": fields.String(
            description="Shows payment process has been skipped",
            example="false"
        ),
    },
)