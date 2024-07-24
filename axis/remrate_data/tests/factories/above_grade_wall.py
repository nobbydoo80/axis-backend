import logging
import random

from .utils import get_factory_from_fields, pop_kwargs, random_sequence
from ...models import WallType, HeatPath, CompositeType, AboveGradeWall
from simulation.tests.factories.surface import get_surface_heat_path_definitions

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/8/20 15:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

MIN_COMPOSITE_R_VALUE = 8.0
MAX_COMPOSITE_R_VALUE = 30.0
MIN_HEAT_PATH_RVALUE = 1.5


def path_layer_factory(
    simulation, composite_type, layer_count, area, r_value, type="wall", **kwargs
):
    """The heat path is built up of 8 layers.  1 and 8 are required (air gaps) everything else is
    used based on the name of the corresponding composite layer name.

    Note: there is NO requirement that a composite layer be named to be included here.

    This will build up (max 6) elements representing each wall
    """
    name = kwargs.get("name", f"path_{random_sequence(10)}")

    total_r_value = 0.0

    kw = get_factory_from_fields(HeatPath)
    kw.update(
        {
            "name": name,
            "area": area,
            "r_value": r_value,
            "layer_1_r_value": 0.0,
            "layer_2_r_value": 0.0,
            "layer_3_r_value": 0.0,
            "layer_4_r_value": 0.0,
            "layer_5_r_value": 0.0,
            "layer_6_r_value": 0.0,
            "layer_7_r_value": 0.0,
            "layer_8_r_value": 0.0,
        }
    )

    if type == "wall":
        kw["layer_1_r_value"] = kwargs.get("layer_1_r_value", random.uniform(0.68, 0.92))
        kw["layer_8_r_value"] = kwargs.get("layer_8_r_value", random.uniform(0.15, 0.19))
        total_r_value += kw["layer_1_r_value"]
        total_r_value += kw["layer_8_r_value"]
    else:
        raise TypeError("Unknown path 'type' %s" % type)

    target_layer_r_value = (r_value - total_r_value) / layer_count
    for layer_idx in range(layer_count - 1):
        if layer_idx + 3 > 8:
            break
        value = round(random.uniform(target_layer_r_value * 0.95, target_layer_r_value), 4)
        kw["layer_%s_r_value" % str(layer_idx + 3)] = value
        total_r_value += value

    # Now layer 2 makes up our difference
    kw["layer_2_r_value"] = r_value - total_r_value

    for idx in range(8):
        log.debug("     Layer: %s", kw["layer_%s_r_value" % str(idx + 1)])

    total_r_value = sum([kw["layer_%s_r_value" % str(idx + 1)] for idx in range(8)])
    if round(total_r_value, 4) != round(r_value, 4):
        raise ValueError("Unable to get total_r_value %s != %s" % (total_r_value, r_value))

    log.debug("  Heat path Total: %s Area: %s", total_r_value, area)
    kw.update(**kwargs)
    return HeatPath.objects.create(simulation=simulation, composite_type=composite_type, **kw)


def composite_type_factory(simulation=None, **kwargs) -> CompositeType:
    """A composite type is the construction of 6 heat paths with a % area.  Each heat path has an
    R-value.  Based on the R-Value we can then determine the overall wall R-value
    """
    name = kwargs.pop("name", f"composite_{random_sequence(10)}")

    assembly_effective_r_value = kwargs.get(
        "assembly_effective_r_value", random.uniform(MIN_COMPOSITE_R_VALUE, MAX_COMPOSITE_R_VALUE)
    )
    log.debug("Assy Effective R-Value: %s", assembly_effective_r_value)

    # Layer count does not include interior and exterior air films, which are always present
    layer_count = kwargs.get("layer_count", random.choice([3] * 10 + [4] * 5 + [5] * 3 + [6] * 1))
    log.debug("Total Layers: %s", layer_count)

    heat_path_count = kwargs.get(
        "heat_path_count", random.choice([2] * 100 + [3] * 20 + [4] * 10 + [5] * 5 + [6] * 2)
    )
    log.debug("Total Heat Paths: %s", heat_path_count)

    kw = get_factory_from_fields(CompositeType)
    kw.update(
        dict(
            name=name,
            quick_fill=kwargs.get("quick_fill", random.choice([True, False])),
            layer_1="",
            layer_2="",
            layer_3="",
            layer_4="",
            layer_5="",
            layer_6="",
        )
    )

    for layer_no in range(1, layer_count + 1):
        kw[f"layer_{layer_no}"] = f"layer_{layer_no}_{random_sequence(10)}"
    kw["u_value"] = 1 / assembly_effective_r_value
    composite_type = CompositeType.objects.create(simulation=simulation, **kw)

    heat_path_definitions = get_surface_heat_path_definitions(
        assembly_r_value=assembly_effective_r_value,
        heat_path_count=heat_path_count,
        layer_count=layer_count,
    )
    for heat_path_definition in heat_path_definitions:
        r_value_total = sum(
            [
                heat_path_definition["interior_air_film_r_val"],
                *[heat_path_definition.get(f"layer_{i}_r_val", 0) for i in range(1, 7)],
                heat_path_definition["exterior_air_film_r_val"],
            ]
        )
        heat_path_layer_kwargs = {
            "layer_1_r_value": heat_path_definition["interior_air_film_r_val"],
            **{
                f"layer_{i + 1}_r_value": heat_path_definition.get(f"layer_{i}_r_val", 0)
                for i in range(1, 7)
            },
            "layer_8_r_value": heat_path_definition["exterior_air_film_r_val"],
        }
        HeatPath.objects.create(
            _result_number=random.randint(100000, 999999),
            _composite_type_number=random.randint(100000, 999999),
            simulation=simulation,
            composite_type=composite_type,
            name=f"path_{random_sequence(10)}",
            area=heat_path_definition["area_fraction"],
            r_value=r_value_total,
            **heat_path_layer_kwargs,
        )

    # Add the zero value heat paths.
    log.debug("Adding %s empty heat paths", 6 - heat_path_count)
    for _hp in range(6 - heat_path_count):
        kw = get_factory_from_fields(HeatPath)
        kw.update(
            {
                "name": "",
                "area": 0.0,
                "r_value": 0.0,
                "layer_1_r_value": 0.0,
                "layer_2_r_value": 0.0,
                "layer_3_r_value": 0.0,
                "layer_4_r_value": 0.0,
                "layer_5_r_value": 0.0,
                "layer_6_r_value": 0.0,
                "layer_7_r_value": 0.0,
                "layer_8_r_value": 0.0,
            }
        )
        HeatPath.objects.create(simulation=simulation, composite_type=composite_type, **kw)
    return composite_type


def wall_type_factory(simulation, **kwargs):
    """Wall types can be defined as quick fill or not.
    Case 1 (Quick Fill = True):
        Composite is automatically generated - which effectively generates the layers based on
        the Wall Construction.  From the values on the Wall Type the Heat Paths are dynamically
        generated.
    Case 2 (Quick Fill= False):
        Composite is built based on the user inputs.  Here the heat paths are obtained via the
        UI and the quick-fill values are effectively negated.

    In either case the Effective R-Values are Driven from the Heat Path values.
    They always exist.  We will defer to these values
    """
    quick_fill = kwargs.pop("quick_fill", None)
    if quick_fill is None:
        quick_fill = random.choice([True] + [False] * 5)
    kwargs["quick_fill"] = quick_fill

    construction_type = kwargs.pop("construction_type", None)
    if construction_type is None:
        construction_type = random.choice([1] * 20 + [2, 3, 4, 5, 6, 7] + [5, 8, 9] * 2)
    kwargs["construction_type"] = construction_type

    layer_count = 4  # Gyp, Cont, Cavity, Frame, Ext
    if construction_type in [4, 6]:
        layer_count = 3

    composite_type = composite_type_factory(
        simulation=simulation, layer_count=layer_count, **kwargs
    )

    kwrgs = get_factory_from_fields(WallType)
    kwrgs["framing_factor"] = random.random()
    kwrgs.update(kwargs)

    return WallType.objects.get_or_create(
        simulation=simulation, composite_type=composite_type, **kwrgs
    )[0]


def above_grade_wall_factory(simulation, **kwargs):
    wall_type = kwargs.pop("wall_type", None)

    if wall_type is None:
        wall_type = wall_type_factory(simulation, **pop_kwargs("wall_type__", kwargs))

    kwrgs = get_factory_from_fields(AboveGradeWall)
    kwrgs["u_value"] = wall_type.composite_type.u_value
    kwrgs["color"] = random.randint(1, 3)
    kwrgs["gross_area"] = random.randint(10, 5000) + random.random()
    location_choices = [201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213]
    if simulation.numerical_version >= (16, 1):
        location_choices = [
            217,
            218,
            219,
            220,
            221,
            222,
            201,
            202,
            223,
            204,
            225,
            205,
            206,
            203,
            224,
            213,
            226,
            227,
            228,
            229,
            230,
            231,
            232,
            233,
            234,
            235,
            236,
            237,
            238,
            214,
            215,
            216,
            239,
            240,
            241,
            242,
            243,
            244,
            207,
            208,
            209,
            245,
            246,
            247,
            248,
            210,
            211,
            212,
            249,
            250,
            251,
            252,
        ]

    kwrgs["location"] = random.choice(location_choices)
    kwrgs.update(kwargs)

    building = kwrgs.pop("building", simulation.building)
    return AboveGradeWall.objects.create(
        simulation=simulation, building=building, type=wall_type, **kwrgs
    )
