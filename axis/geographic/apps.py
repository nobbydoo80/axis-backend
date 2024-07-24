from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "GEOGRAPHIC", {})


class GeographicConfig(technology.TechnologyAppConfig):
    """Geographic technology configuration."""

    name = "axis.geographic"

    @property
    def climate_zone_factory(self):
        dotted_path = ".tests.factories.climate_zone_factory"
        return self._get_dotted_path_function(dotted_path)
