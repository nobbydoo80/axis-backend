"""heater.py: Django Heater Analytics"""

import logging

from simulation.enumerations import HeatingEfficiencyUnit, HeatingCoolingCapacityUnit, AuxEnergyUnit
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "08/30/2019 10:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def eto_simulation_heater_model_characteristics(
    simulation_id, equipment_furnace, primary_heating_equipment_type
):
    """Heater data.  This will be a very pessimistic approach"""
    data = {
        "model_heater_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warning_msg = (
        "Furnace mismatch: The characteristics for the furnace selected in the "
        "checklist do not match the modeled values."
    )

    warnings = []

    if simulation_id is None or equipment_furnace.get("input") is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    try:
        equipment = sim.mechanical_equipment.filter(heater__isnull=False).order_by(
            "-heating_percent_served"
        )[0]
        heater = equipment.equipment
        distribution_system = equipment.heating_distribution_systems.first()
    except IndexError:
        msg = "Simulation data does not contain a heater"
        data["model_heater_characteristics"]["warnings"].append(msg)
        data["model_heater_characteristics"]["warning"] = warning_msg
        return data

    if equipment_furnace.get("is_custom"):
        warnings.append("Custom heat pump identified on checklist")
        warning_msg += " +"

    primary_heating_equipment_type = primary_heating_equipment_type["input"]
    equipment_furnace = equipment_furnace["input"]

    if distribution_system is not None:
        dist_sys_string = distribution_system.get_system_type_display()
    else:
        dist_sys_string = "Undistributed"
    data["model_heater_characteristics"]["simulation"] = "%s %.2f %s %.2f %s" % (
        dist_sys_string,
        heater.capacity,
        heater.get_capacity_unit_display(),
        heater.efficiency,
        heater.get_efficiency_unit_display(),
    )

    data["model_heater_characteristics"]["checklist"] = "[%s] %s %s mBtuh %s AFUE" % (
        primary_heating_equipment_type,
        equipment_furnace.get("brand_name", "-") or "-",
        equipment_furnace.get("capacity_mbtuh", "-") or "-",
        equipment_furnace.get("afue", "-") or "-",
    )

    # Yes I know this is wrong it should be kbtuh but this is how AHRI does it.
    value = equipment_furnace.get("capacity_mbtuh", 0.0) or 0.0
    sim_value = heater.capacity if heater.capacity else 0.0

    if heater.capacity_unit != HeatingCoolingCapacityUnit.KBTUH:
        warnings.append(
            "Heater simulation output capacity unit is not kBtuh (%s)"
            % (heater.get_capacity_unit_display())
        )
    elif round(sim_value) != round(float(value)):
        warnings.append(
            "Heater output capacity %.2f does not match checklist answer %s"
            % (heater.capacity, equipment_furnace.get("capacity_mbtuh", "-") or "-")
        )

    aux_sim_capacity = None
    if heater.auxiliary_electric_capacity:
        # Ekotrope has NO IDEA that EAE is different KWH_YEAR
        if heater.auxiliary_electric_unit not in [AuxEnergyUnit.EAE, AuxEnergyUnit.KWH_YEAR]:
            _msg = "Simulation data aux heater efficiency unit is not EAE (%s)" % (
                heater.get_auxiliary_electric_unit_display()
            )
            warnings.append(_msg)
        aux_sim_capacity = heater.auxiliary_electric_capacity
        data["model_heater_characteristics"]["simulation"] += " %s %s" % (
            heater.auxiliary_electric_capacity,
            heater.get_auxiliary_electric_unit_display(),
        )

    aux_ckl_capacity = equipment_furnace.get("eae_kwh_yr")
    if aux_ckl_capacity:
        data["model_heater_characteristics"]["checklist"] += " %s Eae" % equipment_furnace.get(
            "eae_kwh_yr"
        )

    if (
        aux_sim_capacity
        and aux_ckl_capacity
        and round(aux_sim_capacity) != round(float(aux_ckl_capacity))
    ):
        warnings.append(
            "Heater auxiliary electric use %.2f %s does not match checklist answer %.2f Eae"
            % (
                float(heater.auxiliary_electric_capacity),
                heater.get_auxiliary_electric_unit_display(),
                float(equipment_furnace.get("eae_kwh_yr")),
            )
        )

    if heater.efficiency_unit != HeatingEfficiencyUnit.AFUE:
        _msg = "Simulation data heater efficiency unit is not AFUE (%s)" % (
            heater.get_efficiency_unit_display()
        )
        warnings.append(_msg)
    else:
        value = equipment_furnace.get("afue")
        if value and round(heater.efficiency) != round(float(value)):
            warnings.append(
                "Heater efficiency %.2f does does not match checklist answer %.2f"
                % (heater.efficiency, float(equipment_furnace.get("afue")))
            )

    if warnings:
        data["model_heater_characteristics"]["warnings"] = warnings
        data["model_heater_characteristics"]["warning"] = warning_msg
    return data
