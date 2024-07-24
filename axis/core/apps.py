"""config.py: Core app config"""


from .checks import ChecksConfig
from . import technology

__author__ = "Autumn Valenta"
__date__ = "7/20/15 1:57 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class CoreConfig(technology.TechnologyAppConfig):
    """Core AppConfig"""

    name = "axis.core"
    extensions = technology.TechnologyAppConfig.extensions + (ChecksConfig,)
