from flask_restx import Namespace, fields

# Namespace acts as part of an api (with the same methods as api)
fund_ns = Namespace("fund", description="application operations")

# Data models belonging to 'fund' namespace
questionsModel = fund_ns.model('questions', {
        'question': fields.String(required=True, description='The questions and corresponding answers')
})

applicationModel = fund_ns.model('application', {
    'name': fields.String(required=True, description='Required: The name of the fund.'),
    'questions': fields.Nested(
        questionsModel,
        required=True,
        description='Required: The payload of application questions and answers.'
    )
})
