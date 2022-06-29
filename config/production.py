"""Flask configuration."""
from config.default import DefaultConfig
from fsd_utils import configclass


@configclass
class ProductionConfig(DefaultConfig):

    # Add any development specific config here

    pass
