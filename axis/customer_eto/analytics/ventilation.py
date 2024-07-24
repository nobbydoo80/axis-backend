"""ventilation.py - Axis"""

__author__ = "Steven K"
__date__ = "3/18/22 08:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.apps import apps

from axis.customer_eto.eep_programs.eto_2022 import MechanicalVentilationSystemTypes
from simulation.enumerations import MechanicalVentilationType, VentilationRateUnit, AuxEnergyUnit
from simulation.models import Simulation


log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


def eto_simulation_exhaust_ventilation_model_characteristics(
    simulation_id: int | None,
    equipment_ventilation_exhaust: dict | None,
    equipment_ventilation_system_type: dict | None = None,
) -> dict:
    """Ventilation data.  This will be a very pessimistic approach"""
    data = {
        "model_exhaust_ventilation_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Ventilation mismatch: The ventilation characteristics selected in "
        "the checklist do not match the modeled values."
    )

    if equipment_ventilation_exhaust is None and simulation_id is None:
        return data

    equipment_type = (
        equipment_ventilation_system_type.get("input")
        if equipment_ventilation_system_type
        else None
    )
    # According to Anna (9/20/22) this only applies to WA Exhaust
    if equipment_type and "exhaust only" not in equipment_type.lower():
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    vents = sim.mechanical_ventilation_systems.filter(
        type__in=[MechanicalVentilationType.EXHAUST_ONLY, MechanicalVentilationType.AIR_CYCLER]
    )
    if not vents.count():
        return data

    if vents.exclude(consumption_unit=AuxEnergyUnit.WATT).count():
        _msg = "Simulation data ventilation must use consumption units of Watts"
        data["model_exhaust_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_exhaust_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.exclude(ventilation_rate_unit=VentilationRateUnit.CFM).count():
        _msg = "Simulation data ventilation must use ventilation rate units of CFM"
        data["model_exhaust_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_exhaust_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.filter(type=MechanicalVentilationType.AIR_CYCLER).count():
        warning_msg = "Air Cycler ventilation must be individually verified."
        data["model_exhaust_ventilation_characteristics"]["warnings"].append(warning_msg)

    checklist = equipment_ventilation_exhaust.get("input")

    if checklist is None:
        msg = (
            f"Simulation contains {vents.first().get_type_display()} ventilation but "
            f"checklist does not contain a exhaust checklist answer"
        )
        warnings.append(msg)
        checklist = dict()

    vent = vents.first()
    label = (
        f"{vent.get_type_display()} - Hours/day: {vent.hour_per_day:.1f}, "
        f"Rate ({vent.get_ventilation_rate_unit_display()}): {vent.ventilation_rate:.2f},  "
        f"Fan ({vent.get_consumption_unit_display()}s): {vent.consumption:.2f}"
    )
    data["model_exhaust_ventilation_characteristics"]["simulation"] = label

    if "is_custom" in f"{equipment_ventilation_exhaust}":
        warnings.append("Custom equipment identified on checklist")
        warning_msg += " +"

    label = (
        f"Exhaust Only - Rate (CFM): {checklist.get('speed_cfm') or '-'}, "
        f"Fan (Watts): {checklist.get('input_power_watts') or '-'}"
    )
    if checklist.get("asre"):
        label += f" ASRE: {checklist.get('asre')}"
    data["model_exhaust_ventilation_characteristics"]["checklist"] = label

    if warnings:
        data["model_exhaust_ventilation_characteristics"]["warnings"] = warnings
        data["model_exhaust_ventilation_characteristics"]["warning"] = warning_msg
        return data

    try:
        value = float(checklist.get("input_power_watts") or 0.0)
    except ValueError:
        value = 0.0

    if round(vent.consumption, 1) != round(value, 1):
        warnings.append(
            f"Exhaust ventilation power of {vent.consumption:.2f} does not match "
            f"checklist response of {float(value):.2f}"
        )

    try:
        value = float(checklist.get("speed_cfm") or 0.0)
    except ValueError:
        value = 0.0
    if round(vent.ventilation_rate, 1) != round(value, 1):
        warnings.append(
            f"Exhaust ventilation rate of {vent.ventilation_rate:.2f} does not match "
            f"checklist response of {float(value):.2f}"
        )

    if warnings:
        data["model_exhaust_ventilation_characteristics"]["warnings"] = warnings
        data["model_exhaust_ventilation_characteristics"]["warning"] = warning_msg

    return data


def eto_simulation_supply_ventilation_model_characteristics(
    simulation_id: int | None,
    equipment_furnace: dict | None,
    equipment_heat_pump: dict | None,
    primary_heating_equipment_type: dict | None,
) -> dict:
    """Ventilation data.  This will be a very pessimistic approach"""
    data = {
        "model_supply_ventilation_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Ventilation mismatch: The ventilation characteristics selected in "
        "the checklist do not match the modeled values."
    )

    if simulation_id is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    vents = sim.mechanical_ventilation_systems.filter(type=MechanicalVentilationType.SUPPLY_ONLY)
    if not vents.count():
        return data

    if vents.exclude(consumption_unit=AuxEnergyUnit.WATT).count():
        _msg = "Simulation data ventilation must use consumption units of Watts"
        data["model_supply_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_supply_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.exclude(ventilation_rate_unit=VentilationRateUnit.CFM).count():
        _msg = "Simulation data ventilation must use ventilation rate units of CFM"
        data["model_supply_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_supply_ventilation_characteristics"]["warning"] = warning_msg
        return data

    vents = sim.mechanical_ventilation_systems.filter(type=MechanicalVentilationType.SUPPLY_ONLY)

    checklist = equipment_furnace
    secondary = equipment_heat_pump
    msg = "Simulation contains supply ventilation but checklist does not contain a furnace"
    primary_heating = primary_heating_equipment_type if primary_heating_equipment_type else {}
    primary_heating = primary_heating if primary_heating is not None else {}
    primary_heating = primary_heating.get("input", "") or ""
    if "heat pump" in primary_heating.lower():
        checklist = equipment_heat_pump
        secondary = equipment_furnace
        msg = "Simulation contains supply ventilation but checklist does not contain an ASHP"
    if checklist is None or checklist.get("input") is None:
        checklist = secondary

    if checklist is None or checklist.get("input") is None:
        warnings.append(msg)
        checklist = {}

    if "is_custom" in f"{checklist}":
        warnings.append("Custom equipment identified on checklist")
        warning_msg += " +"

    checklist = checklist.get("input", {})
    vent = vents.first()
    label = (
        f"{vent.get_type_display()} - Hours/day: {vent.hour_per_day:.1f}, "
        f"Rate ({vent.get_ventilation_rate_unit_display()}): {vent.ventilation_rate:.2f}, "
        f"Fan ({vent.get_consumption_unit_display()}s): {vent.consumption:.2f}"
    )
    data["model_supply_ventilation_characteristics"]["simulation"] = label

    label = (
        f"Supply Only ({primary_heating or '-'}) - "
        f"Fan (Watts): {checklist.get('ventilation_fan_watts') or '-'}"
    )
    data["model_supply_ventilation_characteristics"]["checklist"] = label

    if warnings:
        data["model_supply_ventilation_characteristics"]["warnings"] = warnings
        data["model_supply_ventilation_characteristics"]["warning"] = warning_msg
        return data

    try:
        value = float(checklist.get("ventilation_fan_watts") or 0.0)
    except ValueError:
        value = 0.0
    if round(vent.consumption, 1) != round(value, 1):
        warnings.append(
            f"Supply ventilation power of {vent.consumption:.2f} does not match "
            f"checklist response of {float(value):.2f}"
        )

    if warnings:
        data["model_supply_ventilation_characteristics"]["warnings"] = warnings
        data["model_supply_ventilation_characteristics"]["warning"] = warning_msg

    return data


def eto_simulation_balanced_ventilation_model_characteristics(
    simulation_id: int | None,
    # Heat Recovery
    equipment_ventilation_hrv_erv: dict | None = None,
    equipment_ventilation_spot_erv_count: dict | None = None,
    # No heat Recovery
    primary_heating_equipment_type: dict | None = None,
    equipment_furnace: dict | None = None,
    equipment_heat_pump: dict | None = None,
    equipment_ventilation_supply_brand: dict | None = None,
    equipment_ventilation_supply_model: dict | None = None,
    equipment_ventilation_exhaust: dict | None = None,
    equipment_ventilation_system_type: dict | None = None,
) -> dict:
    """This gets us
    Balanced no HR - BALANCED_NO_HR
    Balanced with HR (Indirect) - STAND_ALONE INTEGRATED_HRV_ERV SPOT

    equipment_ventilation_balanced

    equipment_ventilation_system_type
        BALANCED_NO_HR - Balanced No HR
            equipment_balanced_ventilation_no_hr
                INTERMITTENT CONTINUOUS SECONDARY
                    equipment_ventilation_exhaust
                STAND_ALONE
                    equipment_ventilation_supply_brand
                    equipment_ventilation_supply_model
        STAND_ALONE INTEGRATED_HRV_ERV SPOT - Balanced?
            equipment_ventilation_spot_erv_count
            equipment_ventilation_hrv_erv

    So as I interpret this backwards..
    If we have equipment_ventilation_hrv_erv - We can assume that this is no HR

    If we have equipment_ventilation_exhaust


    equipment_balanced_ventilation_no_hr
    """

    if equipment_ventilation_hrv_erv is None:
        equipment_ventilation_hrv_erv = {"input": {}}
    if equipment_ventilation_spot_erv_count is None:
        equipment_ventilation_spot_erv_count = {"input": None}
    if primary_heating_equipment_type is None:
        primary_heating_equipment_type = {"input": {}}
    if equipment_furnace is None:
        equipment_furnace = {"input": {}}
    if equipment_heat_pump is None:
        equipment_heat_pump = {"input": {}}
    if equipment_ventilation_supply_brand is None:
        equipment_ventilation_supply_brand = {"input": None}
    if equipment_ventilation_supply_model is None:
        equipment_ventilation_supply_model = {"input": None}
    if equipment_ventilation_exhaust is None:
        equipment_ventilation_exhaust = {"input": {}}
    if equipment_ventilation_system_type is None:
        equipment_ventilation_system_type = {"input": {}}

    data = {
        "model_balanced_ventilation_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "Ventilation mismatch: The ventilation characteristics selected in "
        "the checklist do not match the modeled values."
    )

    if simulation_id is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    vents = sim.mechanical_ventilation_systems.filter(
        type__in=[
            MechanicalVentilationType.BALANCED,
            MechanicalVentilationType.HRV,
            MechanicalVentilationType.ERV,
            MechanicalVentilationType.EXHAUST_ONLY,
            MechanicalVentilationType.AIR_CYCLER,
        ]
    )
    if not vents.count():
        return data

    # According to Anna (9/20/22) everything should flow through here except WA Exhaust
    equipment_type = (
        equipment_ventilation_system_type.get("input")
        if equipment_ventilation_system_type
        else None
    )
    if equipment_type and "exhaust only" in equipment_type.lower():
        return data

    if vents.exclude(consumption_unit=AuxEnergyUnit.WATT).count():
        _msg = "Simulation data ventilation must use consumption units of Watts"
        data["model_balanced_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_balanced_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.exclude(ventilation_rate_unit=VentilationRateUnit.CFM).count():
        _msg = "Simulation data ventilation must use ventilation rate units of CFM"
        data["model_balanced_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_balanced_ventilation_characteristics"]["warning"] = warning_msg
        return data

    vent = vents.first()
    label = (
        f"{vent.get_type_display()} - ECM: {'Yes' if vent.ecm_motor else 'No'}, "
        f"ASRE: {vent.adjusted_sensible_recovery_efficiency:.2f}, "
        f"ATRE: {vent.adjusted_total_recovery_efficiency if vent.adjusted_total_recovery_efficiency is not None else 0}, "
        f"Hours/day: {vent.hour_per_day:.1f}, "
        f"Rate ({vent.get_ventilation_rate_unit_display()}): {vent.ventilation_rate:.2f}, "
        f"Fan ({vent.get_consumption_unit_display()}s): {vent.consumption:.2f}"
    )
    data["model_balanced_ventilation_characteristics"]["simulation"] = label

    source_checklist = None

    heating_equip = None
    primary_heating = primary_heating_equipment_type.get("input", "") or ""
    if equipment_furnace or equipment_heat_pump:
        heating_equip = {}
        if equipment_furnace.get("input"):
            heating_equip = equipment_furnace.get("input")
        if "heat pump" in primary_heating.lower():
            heating_equip = equipment_heat_pump.get("input")

    label = None
    # Balanced with HR
    if equipment_ventilation_hrv_erv.get("input"):
        source_checklist = equipment_ventilation_hrv_erv
        checklist = equipment_ventilation_hrv_erv.get("input")
        label = (
            f"Balanced w/HR: "
            f"ASRE: {checklist.get('asre', '-') or '-'}, "
            f"Rate (CFM): {checklist.get('net_airflow_cfm', '-') or '-'}, "
            f"Fan (Watts): {checklist.get('power_consumption_watts', '-') or '-'}"
        )
        if equipment_ventilation_spot_erv_count.get("input"):
            label += f", Units: {equipment_ventilation_spot_erv_count.get('input')}"
    else:
        # Balanced without HR
        if equipment_ventilation_exhaust.get("input"):
            source_checklist = equipment_ventilation_exhaust
            checklist = equipment_ventilation_exhaust.get("input")
            label = (
                f"Balanced without/HR (Exhaust): - Rate (CFM):{checklist.get('speed_cfm') or '-'}, "
                f"Fan (Watts): {checklist.get('input_power_watts') or '-'}"
            )
        elif equipment_ventilation_supply_model.get(
            "input"
        ) and equipment_ventilation_supply_brand.get("input"):
            model = equipment_ventilation_supply_model.get("input")
            brand = equipment_ventilation_supply_brand.get("input")
            label = f"Balanced without/HR (Stand alone Supply): {model} {brand}"
    if heating_equip:
        if label is None:
            label = (
                f"Balanced without/HR (Heating Supply) ({primary_heating or '-'}) - "
                f"Fan (Watts): {heating_equip.get('ventilation_fan_watts') or '-'}"
            )
        else:
            label += (
                f" (Supply) Rate: (CFM) Fan (Watts):"
                f" {heating_equip.get('ventilation_fan_watts') or '-'}"
            )

    data["model_balanced_ventilation_characteristics"]["checklist"] = label

    warning_msg = "Balanced ventilation must be individually verified"
    if "'is_custom': True" in f"{source_checklist}":
        warnings.append("Custom equipment identified on checklist")
        warning_msg += " +"

    # We always present a warning
    _warning_message = warning_msg + "\n".join(
        data["model_balanced_ventilation_characteristics"]["warnings"]
    )
    data["model_balanced_ventilation_characteristics"]["warnings"].append(warning_msg)
    data["model_balanced_ventilation_characteristics"]["warning"] = _warning_message
    return data
