"""building_info.py: Django factories"""


import random

from .utils import random_digits
from ...models import BuildingInfo

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def building_info_factory(simulation, **kwargs):
    kwrgs = {
        "_result_number": int(random_digits(6)),
        "_building_number": int(random_digits(6)),
        "volume": random.randrange(10000, 50000),
        "conditioned_area": random.randrange(1000, 5000),
        "type": 3,
        "house_level_type": None,
        "number_stories": random.randrange(1, 3),
        "foundation_type": random.randint(1, 8),
        "number_bedrooms": random.randrange(2, 4),
        "num_units": random.randrange(1, 2),
        "crawl_space_type": random.randrange(1, 3),
        "year_built": random.randrange(2010, 2023),
        "thermal_boundary": random.randint(0, 3),
        "number_stories_including_conditioned_basement": random.randrange(1, 4),
    }
    kwrgs.update(kwargs)
    result_number = kwrgs.pop("_result_number")

    return BuildingInfo.objects.get_or_create(
        simulation=simulation, _result_number=result_number, **kwrgs
    )[0]
