"""Flask configuration."""
from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):

    # Add any dev specific config here

    pass
