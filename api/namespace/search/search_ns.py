from flask_restx import fields
from flask_restx import Namespace


"""
Namespace acts as part of an api (with the same methods as api)
"""


search_ns = Namespace("search", description="application search operations")