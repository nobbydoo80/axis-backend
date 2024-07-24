"""ducts_infiltration.py: Django Ducts and Infiltration"""

import logging
from collections import OrderedDict

from django.apps import apps
from simulation.analytics import SimulationAnalytics

__author__ = "Steven K"
__date__ = "08/30/2019 10:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


def get_duct_analytics(
    simulation_id,
    similar_heating_simulation_ids,
    similar_heating_simulation_last_18mo_ids,
    analysis_type,
):
    """Get duct analysis"""
    data = OrderedDict()

    similar = similar_heating_simulation_ids
    expanded_source_data = True
    if len(similar_heating_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_heating_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)
    data["duct_system_total_leakage"] = analytics.get_duct_system_leakage_to_outside()
    data["duct_system_total_total_real_leakage"] = analytics.get_distribution_system_total_leakage()
    data.update(analytics.get_duct_breakout())
    return data


def get_infiltration_analytics(
    simulation_id,
    similar_insulation_simulation_ids,
    similar_insulation_simulation_last_18mo_ids,
    analysis_type,
):
    """Get Infiltration analysis"""
    data = OrderedDict()
    similar = similar_insulation_simulation_ids
    expanded_source_data = True
    if len(similar_insulation_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_insulation_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)
    data["annual_infiltration_value"] = analytics.get_annual_infiltration_values()
    return data
