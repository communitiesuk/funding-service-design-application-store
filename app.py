from api import api
from flask import Flask
from db import db, migrate
from fsd_utils.logging import logging


def create_app() -> Flask:
    flask_app = Flask(__name__)

    flask_app.config.from_object("config.Config")

    api.init_app(flask_app)
    logging.init_app(flask_app)

    # Bind SQLAlchemy ORM to Flask app
    db.init_app(flask_app)
    # Bind Flask-Migrate db utilities to Flask app
    migrate.init_app(
    flask_app, db, directory="db/migrations", render_as_batch=True
    )

    return flask_app


app = create_app()
