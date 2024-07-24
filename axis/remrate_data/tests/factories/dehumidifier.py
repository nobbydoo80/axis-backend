"""dehumidifier.py - Axis"""

__author__ = "Steven K"
__date__ = "7/26/21 10:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from ...models import Dehumidifier

log = logging.getLogger(__name__)


def dehumidifier_factory(simulation, _result_number, **kwargs):
    if tuple(simulation.numerical_version) < (16, 1, 0):
        return

    kwrgs = {
        "_source_humidifier_number": _result_number,
        "name": f"Humidifier {_result_number}",
        "type": random.choice([1, 2]),
        "fuel_type": random.choice([4, 4, 4, 4, 1, 2, 3]),
        "capacity": random.randint(10, 50) + random.random(),
        "efficiency": random.randint(10, 50) + random.random(),
        "note": random.choice([None, "Some dehumidifier comment"]),
    }

    kwrgs.update(kwargs)

    _source_humidifier_number = kwargs.pop("_source_humidifier_number")
    return Dehumidifier.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        _source_humidifier_number=_source_humidifier_number,
        defaults=kwrgs,
    )[0]
