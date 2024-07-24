"""building.py: Django factories"""


import datetime

from .utils import random_digits, random_sequence
from ...models import Building

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def building_factory(**kwargs):
    """A building factory.  get_or_create based on the field '_source_building_number'"""
    last_update = datetime.datetime.now(datetime.timezone.utc)
    created_on = last_update - datetime.timedelta(
        hours=int(random_digits(2)), minutes=int(random_digits(3))
    )
    kwrgs = {
        "_result_number": int(random_digits(6)),
        "_source_building_number": int(random_digits(6)),
        "created_on": created_on,
        "last_update": last_update,
        "user_host": "me@home.com",
        "filename": f"Simulation {random_sequence(4)}.blg",
        "above_ground_wall_buffer_to_outdoor_area": 0.0,
        "above_ground_wall_buffer_to_outdoor_ro": 0.0,
        "above_ground_wall_conditioned_to_outdoor_area": 1681.0,
        "above_ground_wall_conditioned_to_outdoor_ro": 23.288803,
        "added_mass_drywall_thickness": 0.5,
        "building_input_type": 2,
        "ceiling_attic_area": 1728.0,
        "ceiling_attic_ro": 38.493618,
        "ceiling_cathedral_area": 0.0,
        "ceiling_cathedral_ro": 0.0,
        "door_conditioned_to_outdoor_area": 45.0,
        "door_conditioned_to_outdoor_ro": 4.420522,
        "foundation_walls_buffer_to_outdoor_area": 0.0,
        "foundation_walls_buffer_to_outdoor_ro": 0.0,
        "foundation_walls_conditioned_to_outdoor_area": 0.0,
        "foundation_walls_conditioned_to_outdoor_ro": 0.0,
        "frame_floor_conditioned_to_outdoor_area": 0.0,
        "frame_floor_conditioned_to_outdoor_ro": 0.0,
        "joist_buffer_to_outdoor_area": 0.0,
        "joist_buffer_to_outdoor_ro": 0.0,
        "joist_conditioned_to_outdoor_area": 0.0,
        "joist_conditioned_to_outdoor_ro": 0.0,
        "skylight_conditioned_to_outdoor_area": 0.0,
        "skylight_conditioned_to_outdoor_ro": 0.0,
        "sync_status": 1,
        "window_conditioned_to_outdoor_area": 244.0,
        "window_conditioned_to_outdoor_ro": 2.941176,
        "window_floor_ratio": None,
        "window_wall_ratio": None,
    }

    if not kwargs.get("simulation"):
        raise NotImplemented("Circular not supported - Start with Simulation")
    if not kwargs.get("company"):
        raise NotImplemented("Circular not supported - Start with Simulation")

    kwrgs.update(kwargs)
    _source_building_number = kwrgs.pop("_source_building_number")
    return Building.objects.get_or_create(
        _source_building_number=_source_building_number, defaults=kwrgs
    )[0]
