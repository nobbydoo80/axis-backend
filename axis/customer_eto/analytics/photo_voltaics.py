"""photo_voltaics.py - Axis"""

__author__ = "Steven K"
__date__ = "3/17/22 14:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import PvCapacity
from simulation.models import Simulation

log = logging.getLogger(__name__)


def eto_simulation_pv_characteristics(
    simulation_id: int | None, non_ets_dc_capacity_installed: dict | None
) -> dict:
    """This will be a very pessimistic approach"""
    data = {
        "model_pv_characteristics": {
            "warning": None,
            "warnings": [],
            "simulation": None,
            "checklist": None,
        }
    }
    warnings = []
    warning_msg = (
        "PV mismatch: The PV characteristics selected in the "
        "checklist do not match the modeled values."
    )

    if simulation_id is None and non_ets_dc_capacity_installed is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    try:
        checklist_kw = non_ets_dc_capacity_installed.get("input")
    except AttributeError:
        return data

    if checklist_kw and "kw" in checklist_kw.lower():
        checklist_kw = checklist_kw.split(" ")[0]
    try:
        checklist_kw_value = float(checklist_kw)
    except ValueError:
        data["model_pv_characteristics"]["warnings"] = [f"Invalid PV Watt value {checklist_kw}"]
        data["model_pv_characteristics"]["warning"] = f"Invalid PV Watt value {checklist_kw}"
        return data
    except TypeError:
        return data

    label = f"PV Total Capacity: {checklist_kw_value:,.1f} kW"
    data["model_pv_characteristics"]["checklist"] = label

    total_capacities = sim.photovoltaics.values_list("capacity", "capacity_units")
    simulation_kw_value = 0.0
    for cap, unit in total_capacities:
        if unit == PvCapacity.WATT:
            cap /= 1000.00
        simulation_kw_value += cap

    label = f"PV Total Capacity: {simulation_kw_value:,.1f} kW"
    data["model_pv_characteristics"]["simulation"] = label

    if round(checklist_kw_value, 1) != round(simulation_kw_value, 1):
        warnings.append(
            f"Total capacity in simulation {simulation_kw_value:,.1f} kW does "
            f"not match checklist answer {checklist_kw_value:,.1f} kW"
        )
    if warnings:
        data["model_pv_characteristics"]["warnings"] = warnings
        data["model_pv_characteristics"]["warning"] = warning_msg
    return data
