"""App configs."""


import logging

from axis.core.technology import TechnologyAppConfig
from axis.core.technology.register_signals import RegisterSignalsConfig

__author__ = "Autumn Valenta"
__date__ = "2019-50-15 02:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class PlatformAppConfig(TechnologyAppConfig):
    """Base AppConfig settings system for customer apps.

    Inherit from this AppConfig base to enable standard customer features.  Capture basic settings
    by assigning constants or flags from from settings.
    """

    name = None  # `axis.APPNAME`

    # Tuple of `ExtensionConfig` classes that contribute to this appconfig.
    extensions = (
        # Avoid taking TechnologyAppConfig's extensions, but include signal registration
        RegisterSignalsConfig,
    )
