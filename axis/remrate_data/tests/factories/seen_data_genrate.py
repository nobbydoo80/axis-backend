"""seen_data_genrate.py - simulation"""

import logging

from ...models import CompositeType

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/22/20 16:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


# This is how we will generate some values based off of real stuff


def collect_quick_fill_values(type="wall"):
    data = {}

    composite = CompositeType.objects.all()
    if type == "floor":
        composites = CompositeType.objects.filter(floortype__isnull=False, quick_fill=True)
        attr_name = "floortype_set"
        type_name = "get_construction_type_display"
    elif type == "wall":
        composites = CompositeType.objects.filter(walltype__isnull=False, quick_fill=True)
        attr_name = "walltype_set"
    elif type == "ceiling":
        composites = CompositeType.objects.filter(ceilingtype__isnull=False, quick_fill=True)
        attr_name = "ceilingtype_set"
    else:
        raise TypeError("Need a valid type")

    for composite_type in composites:
        object_type = getattr(composite, attr_name).get()
        label = getattr(object_type, type_name)()


def collect_heat_paths(type="wall"):
    data = {
        "heat_path_1": {
            "quick_fill": {
                "air_gap": {
                    "r_values": [],
                }
            },
            "custom": {
                "air_gap": {
                    "r_values": [],
                }
            },
        }
    }

    import json

    data = {}

    composite = CompositeType.objects.all()
    if type == "floor":
        composites = CompositeType.objects.filter(floortype__isnull=False)
    elif type == "wall":
        composites = CompositeType.objects.filter(walltype__isnull=False)
    elif type == "ceiling":
        composites = CompositeType.objects.filter(ceilingtype__isnull=False)
    else:
        raise TypeError("Need a valid type")

    for composite_type in composites:
        quick_fill = bool(composite_type.quick_fill)
        for idx, heat_path in enumerate(composite_type.heatpath_set.all(), start=1):
            if heat_path.r_value == 0.0:
                continue
            for layer_idx in range(1, 9):
                name = (
                    "air_gap"
                    if layer_idx in [1, 8]
                    else getattr(composite_type, "layer_%s" % (layer_idx - 1))
                )

                heat_path_layer = "heat_path_%s" % layer_idx
                if heat_path_layer not in data:
                    data[heat_path_layer] = {"quick_fill": {}, "custom": {}}

                heat_path_type = "quick_fill" if quick_fill else "custom"

                if name not in data[heat_path_layer][heat_path_type]:
                    data[heat_path_layer][heat_path_type][name] = {"r_values": []}

                r_value = getattr(heat_path, "layer_%s_r_value" % layer_idx)
                data[heat_path_layer][heat_path_type][name]["r_values"].append(r_value)

    with open("%s_analysis.json", "w") as anal_obj:
        anal_obj.write(json.dumps(data))
