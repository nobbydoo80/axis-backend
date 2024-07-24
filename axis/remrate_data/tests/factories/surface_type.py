import random
from typing import Type
from .above_grade_wall import composite_type_factory
from .utils import get_factory_from_fields
from ...models.simulation import Simulation as RemSimulation
from ...models.composite_type import CompositeType

__author__ = "Benjamin Stürmer"
__date__ = "10/07/22 13:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin Stürmer",
]


def surface_type_factory(surface_type_class: Type, simulation: RemSimulation, **kwargs):
    """Generic implementation of a type factory for roof and frame floor types. Returns
    an instance of surface_type_class."""
    layer_count: int = random.randint(3, 5)
    composite_type: CompositeType = composite_type_factory(
        simulation=simulation, layer_count=layer_count, **kwargs
    )

    surface_type_kwargs: dict = get_factory_from_fields(surface_type_class)
    surface_type_kwargs["framing_factor"] = random.random()
    surface_type_kwargs.update(kwargs)

    return surface_type_class.objects.get_or_create(
        simulation=simulation, composite_type=composite_type, **surface_type_kwargs
    )[0]
