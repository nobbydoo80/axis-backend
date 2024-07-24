"""ventillation.py: Django Ventillation Analytics"""

import logging
from collections import OrderedDict

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from simulation.analytics import SimulationAnalytics
from simulation.enumerations import MechanicalVentilationType, VentilationRateUnit, AuxEnergyUnit
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "08/30/2019 10:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


def eto_simulation_ventilation_model_characteristics(
    simulation_id,
    equipment_ventilation_exhaust,
    equipment_ventilation_balanced,
    equipment_furnace,
    equipment_heat_pump,
    primary_heating_equipment_type,
):
    """Ventilation data.  This will be a very pessimistic approach"""
    data = {
        "model_ventilation_characteristics": {
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

    if equipment_ventilation_exhaust is None and equipment_ventilation_balanced is None:
        return data
    if simulation_id is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    try:
        vents = sim.mechanical_ventilation_systems.all()
    except ObjectDoesNotExist:
        _msg = "Simulation data does not contain any mechanical ventilation"
        data["model_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.exclude(
        type__in=[
            MechanicalVentilationType.BALANCED,
            MechanicalVentilationType.HRV,
            MechanicalVentilationType.ERV,
            MechanicalVentilationType.EXHAUST_ONLY,
            MechanicalVentilationType.SUPPLY_ONLY,
        ]
    ).count():
        _msg = (
            "Simulation data ventilation is not balanced (hrv/erv), exhaust or supply ventilation"
        )
        data["model_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.exclude(consumption_unit=AuxEnergyUnit.WATT).count():
        _msg = "Simulation data ventilation must use consumption units of Watts"
        data["model_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.exclude(ventilation_rate_unit=VentilationRateUnit.CFM).count():
        _msg = "Simulation data ventilation must use ventilation rate units of CFM"
        data["model_ventilation_characteristics"]["warnings"].append(_msg)
        data["model_ventilation_characteristics"]["warning"] = warning_msg
        return data

    if vents.filter(
        type__in=[
            MechanicalVentilationType.BALANCED,
            MechanicalVentilationType.HRV,
            MechanicalVentilationType.ERV,
        ]
    ).count():
        does_not_exist = equipment_ventilation_balanced is None
        if does_not_exist or equipment_ventilation_balanced.get("input") is None:
            warnings.append(
                "Simulation contains balanced ventilation but checklist does not "
                "contain a balanced checklist answer"
            )
        else:
            vent = vents.filter(
                type__in=[
                    MechanicalVentilationType.BALANCED,
                    MechanicalVentilationType.HRV,
                    MechanicalVentilationType.ERV,
                ]
            ).first()
            _msg = "%s %.2f %s (%.2f ASRE) at %.2f %s" % (
                vent.get_type_display(),
                vent.consumption,
                vent.get_consumption_unit_display(),
                vent.adjusted_sensible_recovery_efficiency,
                vent.ventilation_rate,
                vent.get_ventilation_rate_unit_display(),
            )
            data["model_ventilation_characteristics"]["simulation"] = _msg

            if equipment_ventilation_balanced.get("is_custom"):
                warnings.append("Custom equipment identified on checklist")
                warning_msg += " +"

            compare = dict() if does_not_exist else equipment_ventilation_balanced.get("input", {})
            compare = dict() if compare is None else compare

            data["model_ventilation_characteristics"][
                "checklist"
            ] = "%s %s W (%s ASRE) at %s CFM" % (
                "Balanced",
                compare.get("power_consumption_watts"),
                compare.get("asre", "-"),
                compare.get("net_airflow_cfm"),
            )

            if warnings:
                data["model_ventilation_characteristics"]["warnings"] = warnings
                data["model_ventilation_characteristics"]["warning"] = warning_msg
                return data

            value = compare.get("power_consumption_watts") or 0.0
            if value and round(vent.consumption) != round(float(value)):
                warnings.append(
                    "%s ventilation power of %.2f does not match checklist answer %s"
                    % (vent.get_type_display(), vent.consumption, value)
                )

            value = compare.get("net_airflow_cfm") or 0.0
            if value and round(vent.ventilation_rate) != round(float(value)):
                warnings.append(
                    "%s ventilation CFM of %.2f does not match checklist answer %s"
                    % (vent.get_type_display(), vent.ventilation_rate, value)
                )

    elif vents.filter(type=MechanicalVentilationType.EXHAUST_ONLY).count():
        does_not_exist = equipment_ventilation_exhaust is None
        if does_not_exist or equipment_ventilation_exhaust.get("input") is None:
            warnings.append(
                "Simulation contains exhaust ventilation but checklist does not "
                "contain a balanced checklist answer"
            )
        else:
            vent = vents.filter(type=MechanicalVentilationType.EXHAUST_ONLY).first()
            _msg = "%s %.2f %s (%.2f ASRE) at %.2f %s" % (
                vent.get_type_display(),
                vent.consumption,
                vent.get_consumption_unit_display(),
                vent.adjusted_sensible_recovery_efficiency,
                vent.ventilation_rate,
                vent.get_ventilation_rate_unit_display(),
            )
            data["model_ventilation_characteristics"]["simulation"] = _msg

            if equipment_ventilation_balanced.get("is_custom"):
                warnings.append("Custom equipment identified on checklist")
                warning_msg += " +"

            compare = dict() if does_not_exist else equipment_ventilation_exhaust.get("input", {})
            compare = dict() if compare is None else compare

            data["model_ventilation_characteristics"][
                "checklist"
            ] = "%s %s W (%s ASRE) at %s CFM" % (
                "Exhaust",
                compare.get("input_power_watts"),
                compare.get("asre", "-"),
                compare.get("speed_cfm"),
            )

            if warnings:
                data["model_ventilation_characteristics"]["warnings"] = warnings
                data["model_ventilation_characteristics"]["warning"] = warning_msg
                return data

            value = compare.get("input_power_watts") or 0.0
            if value and round(vent.consumption) != round(float(value)):
                warnings.append(
                    "%s ventilation power of %.2f does not match checklist answer %s"
                    % (vent.get_type_display(), vent.consumption, value)
                )

            value = compare.get("speed_cfm") or 0.0
            if value and round(vent.ventilation_rate) != round(float(value)):
                warnings.append(
                    "%s ventilation CFM of %.2f does not match checklist answer %s"
                    % (vent.get_type_display(), vent.ventilation_rate, value)
                )

    elif vents.filter(type=MechanicalVentilationType.SUPPLY_ONLY).count():
        vent = vents.filter(type=MechanicalVentilationType.SUPPLY_ONLY).first()
        _msg = "%s %.2f %s (%.2f ASRE) at %.2f %s" % (
            vent.get_type_display(),
            vent.consumption,
            vent.get_consumption_unit_display(),
            vent.adjusted_sensible_recovery_efficiency,
            vent.ventilation_rate,
            vent.get_ventilation_rate_unit_display(),
        )
        data["model_ventilation_characteristics"]["simulation"] = _msg

        checklist_heating = equipment_furnace
        if equipment_furnace is None or equipment_furnace.get("input") is None:
            checklist_heating = equipment_heat_pump

        does_not_exist = checklist_heating is None
        if does_not_exist or checklist_heating.get("input") is None:
            msg = (
                "Simulation contains supply ventilation but checklist does "
                "not contain a furnace or ASHP"
            )
            warnings.append(msg)
        else:
            if checklist_heating.get("is_custom"):
                warnings.append("Custom equipment identified on checklist")
                warning_msg += " +"

        compare = dict() if does_not_exist else checklist_heating.get("input", {})
        compare = dict() if compare is None else compare

        check_list_str = "[%s] %s %s Watts" % (
            primary_heating_equipment_type.get("input", "-") or "-",
            "Supply Only",
            compare.get("ventilation_fan_watts", "-") or "-",
        )
        check_list_str = check_list_str.replace(" - Watts", "")
        check_list_str = check_list_str.replace("[-] ", "")
        check_list_str = check_list_str.replace("[-] ", "")
        data["model_ventilation_characteristics"]["checklist"] = check_list_str

        value = compare.get("ventilation_fan_watts") or 0.0
        if value and round(vent.consumption) != round(float(value)):
            warnings.append(
                "%s ventilation power of %.2f does not match checklist answer %s"
                % (vent.get_type_display(), vent.consumption, value)
            )

    if warnings:
        data["model_ventilation_characteristics"]["warnings"] = warnings
        data["model_ventilation_characteristics"]["warning"] = warning_msg

    return data


def get_ventilation_analytics(
    simulation_id,
    similar_insulation_simulation_ids,
    similar_insulation_simulation_last_18mo_ids,
    analysis_type,
):
    """Get Ventilation analysis"""
    data = OrderedDict()
    similar = similar_insulation_simulation_ids
    expanded_source_data = True
    if len(similar_insulation_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_insulation_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)
    data["ventilation_rate"] = analytics.get_ventilation_rates()
    data["ventilation_watts"] = analytics.get_ventilation_consumption()
    return data
