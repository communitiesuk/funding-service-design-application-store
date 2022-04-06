from flask_restx import Namespace

"""
Namespace acts as part of an api (with the same methods as api)
"""


application_ns = Namespace("application", path="", description="single application operations")




