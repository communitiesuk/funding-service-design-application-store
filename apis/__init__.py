from flask_restx import Api
from apis.namespaces.fund import api as fund_api

api = Api(
    title='Funding Service Design Application Store MVC API',
    version="0.1",
    description='A simple Funding Service Design Application Store API',
)

api.add_namespace(fund_api)