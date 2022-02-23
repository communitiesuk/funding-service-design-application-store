from flask_restx import Api
from application_store_api.namespace_fund import fund_ns

application_store_api = Api(
    title='Funding Service Design Application Store API',
    version="0.1",
    description='A simple Funding Service Design Application Store API',
)

application_store_api.add_namespace(fund_ns)
