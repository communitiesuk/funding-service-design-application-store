from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.models.section import section
from api.namespace.applications.models.section import section_status
from flask_restx import fields


create_application = applications_ns.model(
    "create_application",
    {
        "account_id": fields.String(
            description="The account_id of the owner of the application.",
            example="usera",
        ),
        "fund_id": fields.String(
            description="The id of the fund", example="funding-service-design"
        ),
        "round_id": fields.String(description="The id of the round", example="summer"),
    },
)

application_full = applications_ns.model(
    "application_full",
    {
        "id": fields.String(
            description="The id of the application.",
        ),
        "account_id": fields.String(
            description="The account_id of the owner of the application.",
        ),
        "status": fields.String(
            description="The status of the application", example="NOT_STARTED"
        ),
        "fund_id": fields.String(
            description="The id of the fund", example="funding-service-design"
        ),
        "round_id": fields.String(description="The id of the round", example="spring"),
        "project_name": fields.String(
            description="The name of the project",
            example="Redcar Community Centre",
        ),
        "date_submitted": fields.String(
            description="The datetime the application was submitted",
            example="2022-12-25 00:00:00",
        ),
        "started_at": fields.String(
            description="When the application was started",
            example="2022-12-25 00:00:00",
        ),
        "last_edited": fields.String(
            description="When the application was last edited",
            example="2022-12-25 00:00:00",
        ),
        "sections": fields.List(
            fields.Nested(
                section,
                required=True,
                description="Application section questions and answers.",
            ),
        ),
    },
)

application_result = applications_ns.model(
    "application_result",
    {
        "id": fields.String(description="The id of the application"),
        "status": fields.String(
            description="The status of the application", example="NOT_STARTED"
        ),
        "account_id": fields.String(
            description="The account_id of the owner of the application.",
        ),
        "fund_id": fields.String(
            description="The id of the fund", example="funding-service-design"
        ),
        "round_id": fields.String(description="The id of the round", example="spring"),
        "project_name": fields.String(
            description="The name of the project",
            example="Redcar Community Centre",
        ),
        "date_submitted": fields.String(
            description="The datetime the application was submitted",
            example="2022-12-25 00:00:00",
        ),
        "started_at": fields.String(
            description="When the application was started",
            example="2022-12-25 00:00:00",
        ),
        "last_edited": fields.String(
            description="When the application was last edited",
            example="2022-12-25 00:00:00",
        ),
    },
)

application_status = applications_ns.model(
    "application_status",
    {
        "id": fields.String(description="The id of the application"),
        "status": fields.String(
            description="The status of the application", example="NOT_STARTED"
        ),
        "account_id": fields.String(
            description="The account_id of the owner of the application.",
        ),
        "fund_id": fields.String(
            description="The id of the fund", example="funding-service-design"
        ),
        "round_id": fields.String(description="The id of the round", example="spring"),
        "project_name": fields.String(
            description="The name of the project",
            example="Redcar Community Centre",
        ),
        "date_submitted": fields.String(
            description="The datetime the application was submitted",
            example="2022-12-25 00:00:00",
        ),
        "started_at": fields.String(
            description="When the application was started",
            example="2022-12-25 00:00:00",
        ),
        "last_edited": fields.String(
            description="When the application was last edited",
            example="2022-12-25 00:00:00",
        ),
        "sections": fields.List(
            fields.Nested(
                section_status,
                description="Sections, questions and their completion status",
            ),
        ),
    },
)
