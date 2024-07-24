"""consumption_output_analytics.py: Django Output Analytics"""

import logging
from collections import OrderedDict

from django.apps import apps
from simulation.analytics import SimulationAnalytics

__author__ = "Steven K"
__date__ = "08/30/2019 10:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


def get_output_analytics(
    simulation_id,
    similar_total_simulation_ids,
    similar_total_simulation_last_18mo_ids,
    analysis_type,
):
    """Get the output Analytics"""
    data = OrderedDict()
    similar = similar_total_simulation_ids
    expanded_source_data = True
    if len(similar_total_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_total_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)

    data["heating_consumption_kwh"] = analytics.get_heating_consumption_kwh()
    data["heating_consumption_therms"] = analytics.get_heating_consumption_therms()
    data["cooling_consumption_kwh"] = analytics.get_cooling_consumption_kwh()
    data["hot_water_consumption_kwh"] = analytics.get_hot_water_consumption_kwh()
    data["hot_water_consumption_therms"] = analytics.get_hot_water_consumption_therms()
    _lna_cons = analytics.get_lights_and_appliances_consumption_kwh()
    data["lights_and_appliances_consumption_kwh"] = _lna_cons

    # data['design_load_heating'] = analytics.get_design_load_heating()
    # data['design_load_cooling'] = analytics.get_design_load_cooling()
    data["total_consumption"] = analytics.get_total_consumption()
    data["total_consumption_no_pv"] = analytics.get_total_consumption_no_pv()
    return data
