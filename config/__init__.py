from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

match FLASK_ENV:
    case "development":
        from config.envs.development import DevelopmentConfig as Config  # noqa
    case "dev":
        from config.envs.dev import DevConfig as Config  # noqa
    case "test":
        from config.envs.test import TestConfig as Config  # noqa
    case "production":
        from config.envs.production import ProductionConfig as Config  # noqa
    case _:
        from config.envs.default import DefaultConfig as Config  # noqa

try:
    Config.pretty_print()
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = [Config]
