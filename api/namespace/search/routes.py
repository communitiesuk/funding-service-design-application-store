from api.namespace.fund.data_store.store import APPLICATIONS
from api.namespace.search.search_ns import search_ns
from flask_restx import reqparse
from flask_restx import Resource


@search_ns.route("")
class Application(Resource):
    """
    GET all relevant applications with endpoint '/search?{params}'
    """
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "id_contains", type=str, help="Application id contains string"
    )
    query_params_parser.add_argument(
        "order_by", type=str, help="Order results by parameter"
    )
    query_params_parser.add_argument(
        "order_rev", type=str, help="Order results by descending (default) or ascending (order_rev=1)"
    )
    query_params_parser.add_argument(
        "status_only", type=str, help="Only return results with given status"
    )

    @search_ns.doc("get_applications", parser=query_params_parser)
    def get(self):
        args = self.query_params_parser.parse_args()
        return APPLICATIONS.search_applications(args)
