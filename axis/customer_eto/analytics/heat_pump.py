"""heat_pump: Django """

import logging

from simulation.enumerations import (
    HeatingEfficiencyUnit,
    CoolingEfficiencyUnit,
    HeatingCoolingCapacityUnit,
)
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "08/30/2019 10:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def eto_simulation_heat_pump_model_characteristics(
    simulation_id, equipment_heat_pump, primary_heating_equipment_type
):
    """Heat Pump data.  This will be a very pessimistic approach"""
    data = {
        "model_heat_pump_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        },
        "model_heat_pump_cooling_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        },
    }
    warning_msg = (
        "Heat pump mismatch: The characteristics for the heat pump selected in the "
        "checklist do not match the modeled values."
    )

    warnings = []

    cooling_warning_msg = (
        "Heat pump cooling mismatch: The characteristics for the heat pump "
        "selected in the checklist do not match the modeled values."
    )

    cooling_warnings = []

    if simulation_id is None or equipment_heat_pump.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    sim_heat_pump = None
    try:
        sim_equip = sim.mechanical_equipment.filter(air_source_heat_pump__isnull=False).order_by(
            "-heating_percent_served"
        )[0]
        sim_heat_pump = sim_equip.equipment
        heater_type = "ASHP"
    except IndexError:
        try:
            sim_equip = sim.mechanical_equipment.filter(
                ground_source_heat_pump__isnull=False
            ).order_by("-heating_percent_served")[0]
            sim_heat_pump = sim_equip.equipment
            heater_type = "GSHP"
        except IndexError:
            msg = "Simulation data does not contain any heat pump"
            data["model_heat_pump_characteristics"]["warnings"].append(msg)

    if equipment_heat_pump.get("is_custom"):
        warnings.append("Custom heat pump identified on checklist")
        warning_msg += " +"

    primary_heating_equipment_type = primary_heating_equipment_type["input"]
    equipment_heat_pump = equipment_heat_pump["input"]
    checklist_cooling = "cooling_capacity_kbtuh" in equipment_heat_pump

    _ckl = "[%s] %s Heat Pump %s 47f kBtu/h %s HSPF" % (
        primary_heating_equipment_type,
        equipment_heat_pump["brand_name"] or "-",
        equipment_heat_pump["capacity_47f_kbtuh"] or "-",
        equipment_heat_pump["hspf"] or "-",
    )
    data["model_heat_pump_characteristics"]["checklist"] = _ckl

    _cckl = (
        "%s %s kBtu/h %s SEER"
        % (
            equipment_heat_pump["brand_name"] or "-",
            equipment_heat_pump["cooling_capacity_kbtuh"] or "-",
            equipment_heat_pump["seer"] or "-",
        )
        if checklist_cooling
        else "-"
    )

    data["model_heat_pump_cooling_characteristics"]["checklist"] = _cckl

    if sim_heat_pump:
        # Heating
        _sim = "%s %.2f %s %.2f %s" % (
            heater_type,
            sim_heat_pump.heating_capacity,
            sim_heat_pump.get_capacity_unit_display(),
            sim_heat_pump.heating_efficiency,
            sim_heat_pump.get_heating_efficiency_unit_display(),
        )
        data["model_heat_pump_characteristics"]["simulation"] = _sim

        value = equipment_heat_pump.get("capacity_47f_kbtuh")
        if not value or round(sim_heat_pump.heating_capacity) != round(float(value)):
            _msg = "%s heating capacity %.2f does not match checklist answer %s" % (
                heater_type,
                sim_heat_pump.heating_capacity,
                "%.2f" % float(value) if value else 'is a custom selection"',
            )
            warnings.append(_msg)

        if sim_heat_pump.heating_efficiency_unit != HeatingEfficiencyUnit.HSPF:
            _msg = "Simulation data heater efficiency unit is not HSPF (%s)" % (
                sim_heat_pump.get_heating_efficiency_unit_display()
            )
            warnings.append(_msg)
        elif equipment_heat_pump.get("hspf"):
            value = equipment_heat_pump.get("hspf") or 0.0
            if value and round(sim_heat_pump.heating_efficiency) != round(float(value)):
                _msg = "%s efficiency %.2f does does not match checklist answer %.2f" % (
                    heater_type,
                    sim_heat_pump.heating_efficiency,
                    float(equipment_heat_pump.get("hspf")),
                )
                warnings.append(_msg)

        if heater_type != "GSHP":
            value = equipment_heat_pump.get("capacity_17f_kbtuh") or 0.0
            sim_value = sim_heat_pump.heating_capacity_17f
            if sim_value is not None and value and round(sim_value) != round(float(value)):
                _msg = "%s heating capacity at 17f %.2f does does not match " % (
                    heater_type,
                    sim_value,
                )
                _msg += "checklist answer %.2f" % (
                    float(equipment_heat_pump.get("capacity_17f_kbtuh"))
                )
                warnings.append(_msg)

        # Cooling
        _sim = "%.2f %s %.2f %s" % (
            sim_heat_pump.cooling_capacity,
            sim_heat_pump.get_capacity_unit_display(),
            sim_heat_pump.cooling_efficiency,
            sim_heat_pump.get_cooling_efficiency_unit_display(),
        )
        data["model_heat_pump_cooling_characteristics"]["simulation"] = _sim
        if sim_heat_pump and not checklist_cooling:
            _msg = "Cooling Brand not specified for ASHP"
            cooling_warnings.append(_msg)

        if sim_heat_pump.capacity_unit != HeatingCoolingCapacityUnit.KBTUH:
            cooling_warnings.append(
                f"{heater_type} Cooling capacity is not kBtu/h "
                f"({sim_heat_pump.get_capacity_unit_display()})"
            )

        value = equipment_heat_pump.get("cooling_capacity_kbtuh")
        if not value or round(sim_heat_pump.cooling_capacity) != round(float(value)):
            value = f"{float(value):.2f}" if value else "None"
            cooling_warnings.append(
                f"{heater_type} cooling capacity {sim_heat_pump.cooling_capacity:.2f}"
                f" kBtu/h does does not match checklist answer {value}"
            )

        if sim_heat_pump.cooling_efficiency_unit != CoolingEfficiencyUnit.SEER:
            cooling_warnings.append(
                "%s Cooling units are not SEER (%s)"
                % (heater_type, sim_heat_pump.get_cooling_efficiency_unit_display())
            )
        value = equipment_heat_pump.get("seer") or 0.0
        if not value or round(sim_heat_pump.cooling_efficiency) != round(float(value)):
            value = f"{float(value):.2f}" if value else "None"
            cooling_warnings.append(
                f"{heater_type} cooling efficiency of {sim_heat_pump.cooling_efficiency:.2f} "
                f"SEER does not match checklist value of {value}"
            )

    if warnings:
        data["model_heat_pump_characteristics"]["warnings"] = warnings
        data["model_heat_pump_characteristics"]["warning"] = warning_msg

    if cooling_warnings:
        data["model_heat_pump_cooling_characteristics"]["warnings"] = cooling_warnings
        data["model_heat_pump_cooling_characteristics"]["warning"] = cooling_warning_msg

    return data
