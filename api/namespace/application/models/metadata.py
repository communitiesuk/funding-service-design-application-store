from api.namespace.application.application_ns import application_ns
from flask_restx import fields

metadata = application_ns.model(
    "metadata",
    {
        "paymentSkipped": fields.String(
            description="Shows payment process has been skipped",
            example="false"
        ),
    },
)