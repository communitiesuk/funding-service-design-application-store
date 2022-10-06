# flake8: noqa
import os

FLASK_ENV = os.getenv("FLASK_ENV")

match FLASK_ENV:
    case "development":
        from config.envs.development import DevelopmentConfig as Config
    case "dev":
        from config.envs.dev import DevConfig as Config
    case "test":
        from config.envs.test import TestConfig as Config
    case "unit_test":
        from config.envs.unit_testing import UnitTestingConfig as Config
    case "uat" | "production":
        from config.envs.production import ProductionConfig as Config
    case _:
        from config.envs.default import DefaultConfig as Config

if FLASK_ENV in ["development", "dev"]:
    Config.pretty_print()

__all__ = [Config]
