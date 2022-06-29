"""Flask configuration."""
from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class TestConfig(DefaultConfig):

    # Add any development specific config here

    pass
