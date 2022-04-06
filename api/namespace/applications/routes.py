from database.store import APPLICATIONS
from api.namespace.applications.applications_ns import applications_ns
from api.namespace.applications.models.applications import applications_result
from flask_restx import reqparse
from flask_restx import Resource
from flask_restx import fields


@applications_ns.route("/search")
class SearchApplications(Resource):
    """
    GET all relevant applications with endpoint '/search?{params}'
    """
    query_params_parser = reqparse.RequestParser()
    query_params_parser.add_argument(
        "id_contains", type=str, help="Application id contains string"
    )
    query_params_parser.add_argument(
        "fund_id", type=str, help="Application fund_id"
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
    query_params_parser.add_argument(
        "datetime_start",
        type=str,
        help=(
            "Only include results after this datetime"
        ),
    )
    query_params_parser.add_argument(
        "datetime_end",
        type=str,
        help=(
            "Only include results before this datetime"
        ),
    )

    @applications_ns.doc("get_applications", parser=query_params_parser)
    @applications_ns.marshal_with(applications_result, as_list=True, code=200)
    def get(self):
        args = self.query_params_parser.parse_args()
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        }
        return APPLICATIONS.search_applications(args), 200, response_headers
