from flask_restx import Namespace, fields

# Namespace acts as part of an api (with the same methods as api)
fund_ns = Namespace("fund", description="application operations")

# Data models belonging to 'fund' namespace
questions_model = fund_ns.model('questions', {
    'question': fields.String(required=True, description='The questions and corresponding answers'),
    'category:': fields.String(required=True, description='Category'),
    'fields': fields.Raw(required=True)
})

application_model_inbound = fund_ns.model('application_inbound', {
    'name': fields.String(required=True, description='Required: The name of the fund.'),
    'questions': fields.Nested(
        questions_model,
        required=True,
        description='Required: The payload of application questions and answers.'
    ),
    'metadata': fields.String(required=True, description='Fund metadata.')
})

# The model marshals for a single conforming object or a List of conforming objects
application_model_outbound = fund_ns.model('application_outbound', {
    'id': fields.String(required=True),
    'name': fields.String(required=True, description='Required: The name of the fund.'),
    'questions': fields.Nested(
        questions_model,
        required=True,
        description='Required: The payload of application questions and answers.'
    ),
    'date_submitted': fields.String(required=True)
})
