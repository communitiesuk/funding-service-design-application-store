from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

match FLASK_ENV:
    case "development":
        from config.envs.development import DevelopmentConfig as Config  # noqa
    case "dev":
        pass
    case "test":
        from config.envs.test import TestConfig as Config  # noqa
    case "production":
        pass
    case _:
        from config.envs.default import DefaultConfig as Config  # noqa

try:
    Config.pretty_print()
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = [Config]
