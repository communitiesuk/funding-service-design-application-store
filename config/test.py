"""Flask configuration."""
from os import environ
from os import path
from fsd_tech import configclass

from config.default import DefaultConfig


@configclass
class TestConfig(DefaultConfig):

    # Add any development specific config here

    pass
