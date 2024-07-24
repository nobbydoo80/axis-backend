from django.conf import settings

from infrastructure.utils import symbol_by_name

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "RESNET", {})


class RESNETConfig(technology.TechnologyAppConfig):
    """RESNET technology configuration."""

    name = "axis.resnet"

    @property
    def eep_programs(self):
        """Supported programs for program builder"""
        return [
            symbol_by_name(f"{self.name}.eep_programs:ResnetRegistryData"),
        ]
