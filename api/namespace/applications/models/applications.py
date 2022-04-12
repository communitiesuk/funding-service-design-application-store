from api.namespace.applications.applications_ns import applications_ns
from flask_restx import fields

applications_result = applications_ns.model(
    "applications_result",
    {
        "id": fields.String(description="The id of the application."),
        "status": fields.String(
            description="The status of the application", example="NOT_STARTED"
        ),
        "fund_id": fields.String(
            description="The id of the fund", example="funding-service-design"
        ),
        "round_id": fields.String(
            description="The id of the round", example="spring"
        ),
        "date_submitted": fields.String(
            description="The datetime the application was submitted",
            example="2022-12-25 00:00:00",
        ),
        "assessment_deadline": fields.String(
            description="The assessment deadline for this application's round",
            example="2022-12-25 00:00:00",
        ),
    },
)
