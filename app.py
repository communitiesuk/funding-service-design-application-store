"""The entry point for app.py to start our app
"""
from apis import api
from flask import Flask


def create_app() -> Flask:
    flask_app = Flask(__name__)
    # if __name__ == "__main__":
    api.init_app(flask_app)

    return flask_app


app = create_app()
