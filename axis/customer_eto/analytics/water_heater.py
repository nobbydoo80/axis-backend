"""water_heater.py: Django Hot Water Analytics"""

import logging

from simulation.enumerations import WaterHeaterLiquidVolume, HotWaterEfficiencyUnit
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "08/30/2019 10:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def eto_simulation_water_heater_model_characteristics(simulation_id, equipment_water_heater):
    """This will be a very pessimistic approach"""
    data = {
        "model_water_heater_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Water heater mismatch: The characteristics for the water heater "
        "selected in the checklist do not match the modeled values."
    )

    if simulation_id is None or equipment_water_heater.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    try:
        equipment = sim.mechanical_equipment.filter(water_heater__isnull=False).order_by(
            "-water_heater_percent_served"
        )[0]
        water = equipment.equipment
    except IndexError:
        msg = "Simulation data does not contain a water heater"
        data["model_heater_characteristics"]["warnings"].append(msg)
        data["model_heater_characteristics"]["warning"] = warning_msg
        return data

    if equipment_water_heater.get("is_custom"):
        warnings.append("Custom water heater identified on checklist")
        warning_msg += " +"

    equipment = equipment_water_heater["input"]

    if water.tank_units != WaterHeaterLiquidVolume.GALLON:
        warnings.append(
            "Gallons are the expected tank units not %s" % water.get_tank_units_display()
        )

    if water.efficiency_unit != HotWaterEfficiencyUnit.ENERGY_FACTOR:
        warnings.append(
            "EF is the expected efficiency unit not %s" % water.get_efficiency_unit_display()
        )

    data["model_water_heater_characteristics"]["simulation"] = "%s" % water

    energy_factor = equipment.get("energy_factor", "-")
    if energy_factor == "-":
        energy_factor = equipment.get("converted_ef", "-")

    _msg = "%s %s Gal %s Eff" % (
        equipment.get("brand_name"),
        equipment.get("capacity", "-"),
        energy_factor,
    )
    if str(equipment.get("capacity", "0")) in ["0"]:
        _msg = "%s Tankless %s Eff" % (
            equipment.get("brand_name"),
            energy_factor,
        )
    data["model_water_heater_characteristics"]["checklist"] = _msg

    value = equipment["capacity"] or 0.0
    if value and round(water.tank_size) != round(float(value)):
        _msg = "Water heater capacity %.2f does not match checklist answer %.2f" % (
            water.tank_size,
            float(value),
        )
        warnings.append(_msg)

    if energy_factor == "-":
        energy_factor = None

    if energy_factor and round(water.efficiency, 2) != round(float(energy_factor), 2):
        _msg = "Water heater energy factor %.2f does not match checklist answer %.2f" % (
            water.efficiency,
            float(energy_factor),
        )
        warnings.append(_msg)

    if warnings:
        data["model_water_heater_characteristics"]["warning"] = warning_msg
        data["model_water_heater_characteristics"]["warnings"] = warnings
    return data
