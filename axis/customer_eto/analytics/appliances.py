"""appliances.py: Django Appliance Analytics"""

import logging

from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "08/30/2019 10:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def eto_simulation_clothes_dryer_model_characteristics(simulation_id, equipment_clothes_dryer):
    """This will be a very pessimistic approach"""
    data = {
        "model_clothes_dryer_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Clothes dryer mismatch: The clothes dryer characteristics selected in the "
        "checklist do not match the modeled values."
    )

    if simulation_id is None and equipment_clothes_dryer.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    is_custom = equipment_clothes_dryer.get("is_custom") or equipment_clothes_dryer.get(
        "hints", {}
    ).get("is_custom")
    if is_custom:
        warnings.append("Custom Clothes Dryer identified on checklist")
        warning_msg += " +"

    equipment = equipment_clothes_dryer.get("input")
    if equipment is None:
        return data

    data["model_clothes_dryer_characteristics"]["checklist"] = "%s %s CEF" % (
        equipment.get("brand_name", "-"),
        equipment.get("combined_energy_factor", "-"),
    )

    data["model_clothes_dryer_characteristics"][
        "simulation"
    ] = sim.appliances.get_clothes_dryer_display()

    value = equipment.get("combined_energy_factor") or 0.0
    _ef = round(sim.appliances.clothes_dryer_efficiency, 2)
    if value and _ef != round(float(value), 2):
        warnings.append(
            "Clothes Dryer combined energy factor %.2f does not match checklist answer %s"
            % (sim.appliances.clothes_dryer_efficiency, value)
        )

    if warnings:
        data["model_clothes_dryer_characteristics"]["warnings"] = warnings
        data["model_clothes_dryer_characteristics"]["warning"] = warning_msg
    return data


def eto_simulation_clothes_washer_model_characteristics(simulation_id, equipment_clothes_washer):
    """This will be a very pessimistic approach"""
    data = {
        "model_clothes_washer_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Clothes washer mismatch: The clothes washer characteristics selected in the "
        "checklist do not match the modeled values."
    )

    if simulation_id is None and equipment_clothes_washer.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    is_custom = equipment_clothes_washer.get("is_custom") or equipment_clothes_washer.get(
        "hints", {}
    ).get("is_custom")
    if is_custom:
        warnings.append("Custom Clothes Washer identified on checklist")
        warning_msg += " +"

    equipment = equipment_clothes_washer.get("input")
    if equipment is None:
        return data

    # Nothing to compare..

    data["model_clothes_washer_characteristics"]["checklist"] = "%s %s KW/yr" % (
        equipment.get("brand_name", "-"),
        equipment.get("annual_energy_use_kwh_yr", "-"),
    )

    data["model_clothes_washer_characteristics"][
        "simulation"
    ] = sim.appliances.get_clothes_washer_display()

    value = equipment.get("annual_energy_use_kwh_yr") or 0.0
    if value and round(sim.appliances.clothes_washer_label_electric_consumption) != round(
        float(value)
    ):
        warnings.append(
            "Clothes Washer power of %.2f does not match checklist answer %s"
            % (sim.appliances.clothes_washer_label_electric_consumption, value)
        )

    # Add IMEF
    data["model_clothes_washer_characteristics"]["checklist"] += " %s IMEF" % equipment.get(
        "integrated_modified_energy_factor", "-"
    )

    value = equipment.get("integrated_modified_energy_factor")
    sim_value = sim.appliances.clothes_washer_efficiency
    if value and round(sim_value) != round(float(value)):
        warnings.append(
            "Modified energy factor %.2f does not match checklist answer %.2f IMEF"
            % (round(sim_value), round(float(value)))
        )

    # Add Washer volume
    data["model_clothes_washer_characteristics"]["checklist"] += " %s CUFT" % equipment.get(
        "volume_cu_ft", "-"
    )

    value = equipment.get("volume_cu_ft")
    sim_value = sim.appliances.clothes_washer_capacity
    if value and round(sim_value) != round(float(value)):
        warnings.append(
            "Volume %.2f does not match checklist value %.2f"
            % (round(sim_value), round(float(value)))
        )

    if warnings:
        data["model_clothes_washer_characteristics"]["warnings"] = warnings
        data["model_clothes_washer_characteristics"]["warning"] = warning_msg
    return data


def eto_simulation_refrigerator_model_characteristics(simulation_id, equipment_refrigerator):
    """This will be a very pessimistic approach"""
    data = {
        "model_refrigerator_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Refrigerator mismatch: The refrigerator characteristics selected in the "
        "checklist do not match the modeled values."
    )

    if simulation_id is None and equipment_refrigerator.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    is_custom = equipment_refrigerator.get("is_custom") or equipment_refrigerator.get(
        "hints", {}
    ).get("is_custom")

    if is_custom:
        warnings.append("Custom Refrigerator identified on checklist")
        warning_msg += " +"

    equipment = equipment_refrigerator.get("input")
    if equipment is None:
        return data

    data["model_refrigerator_characteristics"]["checklist"] = "%s %s KW/yr" % (
        equipment.get("brand_name", "-"),
        equipment.get("annual_energy_use_kwh_yr", "-"),
    )

    data["model_refrigerator_characteristics"][
        "simulation"
    ] = sim.appliances.get_refrigerator_display()

    value = equipment.get("annual_energy_use_kwh_yr") or 0.0
    if value and round(sim.appliances.refrigerator_consumption) != round(float(value)):
        warnings.append(
            "Refrigerator energy use of %.2f does not match checklist answer %s"
            % (sim.appliances.refrigerator_consumption, value)
        )

    if warnings:
        data["model_refrigerator_characteristics"]["warnings"] = warnings
        data["model_refrigerator_characteristics"]["warning"] = warning_msg
    return data


def eto_simulation_diswasher_model_characteristics(simulation_id, equipment_dishwasher):
    """This will be a very pessimistic approach"""
    data = {
        "model_dishwasher_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Dish washer mismatch: The dishwasher characteristics selected in the "
        "checklist do not match the modeled values."
    )

    if simulation_id is None and equipment_dishwasher.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    is_custom = equipment_dishwasher.get("is_custom") or equipment_dishwasher.get("hints", {}).get(
        "is_custom"
    )

    if is_custom:
        warnings.append("Custom Dishwasher identified on checklist")
        warning_msg += " +"

    equipment = equipment_dishwasher.get("input")
    if equipment is None:
        return data

    data["model_dishwasher_characteristics"]["checklist"] = "%s %s KW/yr" % (
        equipment.get("brand_name", "-"),
        equipment.get("annual_energy_use_kwh_yr", "-"),
    )

    data["model_dishwasher_characteristics"]["simulation"] = sim.appliances.get_dishwasher_display()

    value = equipment.get("annual_energy_use_kwh_yr") or 0.0
    if value and round(sim.appliances.dishwasher_consumption) != round(float(value)):
        warnings.append(
            "Dishwasher energy use of %.2f does not match checklist answer %s"
            % (sim.appliances.dishwasher_consumption, value)
        )

    if warnings:
        data["model_dishwasher_characteristics"]["warnings"] = warnings
        data["model_dishwasher_characteristics"]["warning"] = warning_msg
    return data
