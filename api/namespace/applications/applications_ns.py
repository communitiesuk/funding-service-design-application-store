from flask_restx import Namespace


"""
Namespace acts as part of an api (with the same methods as api)
"""


applications_ns = Namespace("applications", description="bulk application operations")