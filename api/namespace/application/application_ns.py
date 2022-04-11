"""
Namespace for operations on single applications
"""

from flask_restx import Namespace


application_ns = Namespace("application", path="", description="single application operations")
