"""Flask configuration."""
from config.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):

    # Add any development specific config here

    pass
