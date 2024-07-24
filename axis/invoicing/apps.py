"""apps.py: """

__author__ = "Artem Hruzd"
__date__ = "03/03/2021 17:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.core import platform


class InvoicingConfig(platform.PlatformAppConfig):
    """Invoicing platform configuration."""

    name = "axis.invoicing"
