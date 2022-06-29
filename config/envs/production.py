"""Flask configuration."""
from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class ProductionConfig(DefaultConfig):

    # Add any development specific config here

    pass
