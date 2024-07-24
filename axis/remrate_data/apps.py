from django.apps import apps
from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

settings = getattr(settings, "REMRATE_DATA", {})


class REMRateDataConfig(technology.TechnologyAppConfig):
    """REMRate Data technology configuration."""

    name = "axis.remrate_data"

    # Imports
    @property
    def rater_organization_factory(self):
        return apps.get_app_config("company").rater_organization_factory

    # Exports
    @property
    def simulation_factory(self):
        dotted_path = ".tests.factories.simulation_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def udrh_simulation_factory(self):
        dotted_path = ".tests.factories.udrh_simulation_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def building_factory(self):
        dotted_path = ".tests.factories.building_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def composite_factory(self):
        dotted_path = ".tests.factories.composite_type_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def above_grade_wall_factory(self):
        dotted_path = ".tests.factories.above_grade_wall_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def foundation_wall_factory(self):
        dotted_path = ".tests.factories.foundation_wall_factory"
        return self._get_dotted_path_function(dotted_path)
