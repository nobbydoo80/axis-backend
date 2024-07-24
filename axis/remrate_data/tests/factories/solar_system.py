"""solar_system.py: Django factories"""

from .utils import random_sequence
from ...models import SolarSystem

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def solar_system_factory(simulation, building, _result_number, _building_number, **kwargs):
    type = kwargs.pop("type", 0)
    return SolarSystem.objects.get_or_create(
        simulation=simulation,
        building=building,
        _result_number=_result_number,
        _building_number=_building_number,
        type=type,
        defaults=kwargs,
    )[0]
