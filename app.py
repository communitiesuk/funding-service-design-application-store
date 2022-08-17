from api import api
from flask import Flask
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging


def create_app() -> Flask:
    flask_app = Flask(__name__)

    flask_app.config.from_object("config.Config")

    api.init_app(flask_app)
    logging.init_app(flask_app)

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    return flask_app


app = create_app()
