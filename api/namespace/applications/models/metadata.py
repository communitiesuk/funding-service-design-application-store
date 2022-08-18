from api.namespace.applications.applications_ns import applications_ns
from flask_restx import fields

metadata = applications_ns.model(
    "metadata",
    {  
        "form_name": fields.String(
                description="The form json file name"
        ),
        "paymentSkipped": fields.String(
            description="Shows payment process has been skipped",
            example="false",
        ),
    },
)
