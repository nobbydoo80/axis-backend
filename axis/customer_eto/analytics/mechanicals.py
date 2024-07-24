"""mechanicals.py: Django Mecahnical Analytics"""

import logging
from collections import OrderedDict

from django.apps import apps
from simulation.analytics import SimulationAnalytics
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "08/30/2019 10:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


def get_mechanical_analytics(
    simulation_id,
    similar_heating_simulation_ids,
    similar_heating_simulation_last_18mo_ids,
    analysis_type,
):
    """Mechanical Analytics"""
    data = OrderedDict()
    similar = similar_heating_simulation_ids
    expanded_source_data = True
    if len(similar_heating_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_heating_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)
    data["heater_heating_capacity"] = analytics.get_heater_heating_capacity()
    data["heater_heating_efficiency"] = analytics.get_heater_heating_efficiency()

    data["air_conditioner_cooling_capacity"] = analytics.get_air_conditioner_cooling_capacity()
    data["air_conditioner_cooling_efficiency"] = analytics.get_air_conditioner_cooling_efficiency()

    _label = "ground_source_heat_pump_heating_capacity"
    data[_label] = analytics.get_ground_source_heat_pump_heating_capacity()
    _label = "ground_source_heat_pump_heating_efficiency"
    data[_label] = analytics.get_ground_source_heat_pump_heating_efficiency()
    _label = "ground_source_heat_pump_cooling_capacity"
    data[_label] = analytics.get_ground_source_heat_pump_cooling_capacity()
    _label = "ground_source_heat_pump_cooling_efficiency"
    data[_label] = analytics.get_ground_source_heat_pump_cooling_efficiency()

    _label = "air_source_heat_pump_heating_capacity"
    data[_label] = analytics.get_air_source_heat_pump_heating_capacity()
    _label = "air_source_heat_pump_heating_efficiency"
    data[_label] = analytics.get_air_source_heat_pump_heating_efficiency()
    _label = "air_source_heat_pump_cooling_capacity"
    data[_label] = analytics.get_air_source_heat_pump_cooling_capacity()
    _label = "air_source_heat_pump_cooling_efficiency"
    data[_label] = analytics.get_air_source_heat_pump_cooling_efficiency()

    return data


def get_mechanical_water_analytics(
    simulation_id,
    similar_hot_water_simulation_ids,
    similar_hot_water_simulation_last_18mo_ids,
    analysis_type,
):
    """Hot Water Analytics"""
    data = OrderedDict()
    similar = similar_hot_water_simulation_ids
    expanded_source_data = True
    if len(similar_hot_water_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_hot_water_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)

    data["water_heater_tank_size"] = analytics.get_water_heater_tank_size()
    data["water_heater_energy_factor"] = analytics.get_water_heater_energy_factor()

    return data


def eto_heating_load_allocations(simulation_id):
    """This will be a very pessimistic approach"""
    data = {
        "heating_load_allocations": {"warning": None, "values": []},
        "cooling_load_allocations": {"warning": None, "values": []},
    }

    if simulation_id is None:
        return data

    try:
        sim = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return data

    heat_total = 0
    found_ids = []
    for item in sim.mechanical_equipment.filter(heating_percent_served__gt=0):
        heat_total += item.heating_percent_served
        if item.cooling_percent_served:
            found_ids.append(item.id)
        data["heating_load_allocations"]["values"].append(str(item))

    if round(heat_total, 0) != 100:
        data["heating_load_allocations"]["warning"] = "Only %s %% is being served" % heat_total

    for item in sim.mechanical_equipment.filter(cooling_percent_served__gt=0):
        if item.id in found_ids:
            continue
        data["cooling_load_allocations"]["values"].append(str(item))

    return data
