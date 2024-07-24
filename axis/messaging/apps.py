from django.conf import settings

from axis.core import platform

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "MESSAGING", {})


class MessagingConfig(platform.PlatformAppConfig):
    """Messaging platform configuration."""

    name = "axis.messaging"
