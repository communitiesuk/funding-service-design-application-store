from api import api
from flask import Flask


def create_app() -> Flask:
    flask_app = Flask(__name__)

    flask_app.config.from_object("config.Config")

    api.init_app(flask_app)
    return flask_app


app = create_app()
