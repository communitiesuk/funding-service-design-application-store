"""
Namespace for bulk operations on applications
"""

from flask_restx import Namespace


applications_ns = Namespace("applications", description="bulk application operations")
