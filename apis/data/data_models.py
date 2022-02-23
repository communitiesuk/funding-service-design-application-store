from flask_restx import fields

# Create data models
questions = {
        'question': fields.String(required=True, description='The questions and corresponding answers')
}
