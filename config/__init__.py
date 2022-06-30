# flake8: noqa
from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

match FLASK_ENV:
    case "development":
        from config.envs.development import DevelopmentConfig as Config
    case "dev":
        from config.envs.dev import DevConfig as Config
    case "test":
        from config.envs.test import TestConfig as Config
    case "production":
        from config.envs.production import ProductionConfig as Config
    case _:
        from config.envs.default import DefaultConfig as Config

if FLASK_ENV in ["development", "dev"]:
    Config.pretty_print()

__all__ = [Config]
