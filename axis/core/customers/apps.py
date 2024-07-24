"""App configs."""

import logging

from axis.core import platform
from .company_utils import CompanyUtils

__author__ = "Autumn Valenta"
__date__ = "2019-50-15 02:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class CustomerAppConfig(platform.PlatformAppConfig):
    """Base AppConfig settings system for customer apps.

    Inherit from this AppConfig base to enable standard customer features.  Capture basic settings
    by assigning constants or flags from from settings.
    """

    name = None  # `axis.customer_FOO`

    # Tuple of `ExtensionConfig` classes that contribute to this appconfig.
    extensions = platform.PlatformAppConfig.extensions + (CompanyUtils,)
