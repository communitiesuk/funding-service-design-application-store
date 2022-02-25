"""The entry point for app.py to start our app
"""
from application_store_api import application_store_api
from flask import Flask


def create_app() -> Flask:
    flask_app = Flask(__name__)
    application_store_api.init_app(flask_app)
    return flask_app


app = create_app()
