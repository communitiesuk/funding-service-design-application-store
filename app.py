import connexion
from apscheduler.schedulers.background import BackgroundScheduler
from connexion.resolver import MethodViewResolver
from flask import Flask
from fsd_utils import init_sentry
from fsd_utils.healthchecks.checkers import DbChecker
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from openapi.utils import get_bundled_specs
from scripts.send_application_reminder import application_deadline_reminder


def create_app() -> Flask:
    init_sentry()

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
    migrate.init_app(flask_app, db, directory="db/migrations", render_as_batch=True)

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())
    health.add_check(DbChecker(db))

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=application_deadline_reminder,
        trigger="interval",
        seconds=12,
        args=(flask_app,),
    )
    scheduler.start()

    try:
        return flask_app
    except Exception:
        return scheduler.shutdown()


app = create_app()
