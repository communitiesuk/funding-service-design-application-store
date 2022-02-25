from api import api
from flask import Flask


def create_app() -> Flask:
    flask_app = Flask(__name__)
    api.init_app(flask_app)
    return flask_app


app = create_app()
