from django.apps import apps
from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

settings = getattr(settings, "EKOTROPE", {})


class EkotropeConfig(technology.TechnologyAppConfig):
    """Ekotrope technology configuration."""

    name = "axis.ekotrope"

    @property
    def rater_organization_factory(self):
        return apps.get_app_config("company").rater_organization_factory

    @property
    def simulation_factory(self):
        dotted_path = ".tests.factories.simulation_factory"
        return self._get_dotted_path_function(dotted_path)
