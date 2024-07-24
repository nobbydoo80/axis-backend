"""Built-in extensions for platform apps."""

import logging

__author__ = "Autumn Valenta"
__date__ = "2019-50-15 02:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class ExtensionConfig(object):
    """Base extension for classes contributing to a PlatformAppConfig."""

    def ready(self):
        super(ExtensionConfig, self).ready()
