# from api import api
# from db import db
# from db import migrate
# from flask import Flask
# from fsd_utils.healthchecks.checkers import FlaskRunningChecker
# from fsd_utils.healthchecks.healthcheck import Healthcheck
# from fsd_utils.logging import logging


# def create_app() -> Flask:
#     flask_app = Flask(__name__)

#     flask_app.config.from_object("config.Config")

#     api.init_app(flask_app)
#     logging.init_app(flask_app)

#     # Bind SQLAlchemy ORM to Flask app
#     db.init_app(flask_app)
#     # Bind Flask-Migrate db utilities to Flask app
#     migrate.init_app(
#         flask_app, db, directory="db/migrations", render_as_batch=True
#     )

#     health = Healthcheck(flask_app)
#     health.add_check(FlaskRunningChecker())
#     # TODO Add the following once PR 22 is merged (and we have a real DB)
#     # health.add_check(DbChecker(db))
#     return flask_app


# app = create_app()


import connexion
from connexion.resolver import MethodViewResolver
from flask import Flask
from fsd_utils.healthchecks.checkers import DbChecker
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from openapi.utils import get_bundled_specs


def create_app() -> Flask:

    connexion_options = {
        "swagger_url": "/",
    }
    connexion_app = connexion.FlaskApp(
        __name__, specification_dir="openapi/", options=connexion_options
    )
    connexion_app.add_api(
        get_bundled_specs("/openapi/api.yml"),
        validate_responses=True,
        resolver=MethodViewResolver("api"),
    )

    flask_app = connexion_app.app
    flask_app.config.from_object("config.Config")

    # Initialise logging
    logging.init_app(flask_app)

    from db import db, migrate

    # Bind SQLAlchemy ORM to Flask app
    db.init_app(flask_app)
    # Bind Flask-Migrate db utilities to Flask app
    migrate.init_app(
        flask_app, db, directory="db/migrations", render_as_batch=True
    )

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    health.add_check(DbChecker(db))

    return flask_app


app = create_app()
