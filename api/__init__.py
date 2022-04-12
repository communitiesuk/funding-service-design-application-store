from api.namespace.applications.routes import applications_ns
from flask_restx import Api

api = Api(
    title="Funding Service Design Application Store API",
    version="0.1.0",
    description="A simple Funding Service Design Application Store API",
)

api.add_namespace(applications_ns)
