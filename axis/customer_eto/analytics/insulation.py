"""insulation.py: Django Insulation Analytics"""

import logging
from collections import OrderedDict

from django.apps import apps
from simulation.analytics import SimulationAnalytics

__author__ = "Steven K"
__date__ = "08/30/2019 10:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


def get_insulation_analytics(
    simulation_id,
    similar_insulation_simulation_ids,
    similar_insulation_simulation_last_18mo_ids,
    analysis_type,
):
    """Get the output Analytics"""

    data = OrderedDict()
    similar = similar_insulation_simulation_ids
    expanded_source_data = True
    if len(similar_insulation_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_insulation_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)
    data["total_frame_floor_area"] = analytics.get_total_frame_floor_area()
    data["dominant_floor_insulation_r_value"] = analytics.get_dominant_frame_floor_r_value()
    data["total_slab_floor_area"] = analytics.get_total_slab_area()
    data["dominant_slab_insulation_r_value"] = analytics.get_dominant_slab_r_value()

    data["total_above_grade_wall_area"] = analytics.get_total_above_grade_wall_area()
    data["dominant_above_grade_wall_r_value"] = analytics.get_dominant_above_grade_wall_r_value()

    data["total_ceiling_area"] = analytics.get_total_roof_area()
    data["dominant_ceiling_r_value"] = analytics.get_dominant_roof_r_value()

    data["dominant_window_u_value"] = analytics.get_dominant_window_u_value()
    data["dominant_window_shgc_value"] = analytics.get_dominant_window_shgc_value()
    data["total_window_area"] = analytics.get_total_window_area()
    return data


def get_insulation_analytics_2022(
    simulation_id,
    similar_insulation_simulation_ids,
    similar_insulation_simulation_last_18mo_ids,
    analysis_type,
):
    """Get the output Analytics"""

    data = OrderedDict()
    similar = similar_insulation_simulation_ids
    expanded_source_data = True
    if len(similar_insulation_simulation_last_18mo_ids) > app.ANALYTICS_MIN_THRESHOLD:
        similar = similar_insulation_simulation_last_18mo_ids
        expanded_source_data = False
    analytics = SimulationAnalytics(simulation_id, similar, analysis_type, expanded_source_data)
    data["total_frame_floor_area"] = analytics.get_total_frame_floor_area()
    data["dominant_floor_insulation_u_value"] = analytics.get_dominant_frame_floor_u_value()
    data["total_slab_floor_area"] = analytics.get_total_slab_area()
    data["dominant_slab_insulation_u_value"] = analytics.get_dominant_slab_u_value()
    data["total_above_grade_wall_area"] = analytics.get_total_above_grade_wall_area()
    data["dominant_above_grade_wall_u_value"] = analytics.get_dominant_above_grade_wall_u_value()
    data["total_ceiling_area"] = analytics.get_total_roof_area()
    data["dominant_ceiling_u_value"] = analytics.get_dominant_roof_u_value()
    data["dominant_window_u_value"] = analytics.get_dominant_window_u_value()
    data["dominant_window_shgc_value"] = analytics.get_dominant_window_shgc_value()
    data["total_window_area"] = analytics.get_total_window_area()
    return data
