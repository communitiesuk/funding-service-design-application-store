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

if FLASK_ENV in ["development", "dev"]:
    Config.pretty_print()

__all__ = [Config]
