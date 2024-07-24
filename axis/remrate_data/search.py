"""search.py: Django remrate_data"""


import logging
from appsearch.registry import ModelSearch, search
from .models import Simulation

__author__ = "Steven Klass"
__date__ = "3/8/13 2:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuildingSearch(ModelSearch):
    verbose_name = "REM/Rate® Data"
    verbose_name_plural = "REM/Rate® Entries"

    display_fields = (
        ("Name", "building__project__name"),
        ("Address", "building__project__property_address"),
        ("Plan/Model", "building__project__builder_model"),
        ("Community/Develop", "building__project__builder_development"),
        ("Rating Number", "rating_number"),
        ("HERS Score", "hers__score"),
        ("Upload", "simulation_date"),
    )

    search_fields = (
        "rating_number",
        "version",
        {
            "building": (
                ("Filename", "filename"),
                ("Conditioned Area", "building_info__conditioned_area"),
                ("Volume", "building_info__volume"),
                ("Year Built", "building_info__year_built"),
                ("Number Stories", "building_info__number_stories"),
                ("Number Bedrooms", "building_info__number_bedrooms"),
                ("Property Address", "project__property_address"),
                ("Property City", "project__property_city"),
                ("Rater Name", "project__rater_name"),
                ("RESNET Registry ID", "project__resnet_registry_id"),
            )
        },
        {
            "site": (
                ("Site Label", "site_label"),
                ("Elevation", "elevation"),
            )
        },
        {"hers": (("HERS Score", "score"),)},
        {
            "energystar": (
                (
                    'ENERGY STAR v2.5 photo voltaic adjusted HERS score"',
                    "energy_star_v2p5_pv_score",
                ),
                # ('ENERGY STAR v2.5 Reference Design HERS score', 'energy_star_v2p5_hers_score'),
                ('ENERGY STAR v3 photo voltaic adjusted HERS score"', "energy_star_v3_pv_score"),
                # ('ENERGY STAR v3 Reference Design HERS score', 'energy_star_v3_hers_score'),
                (
                    'ENERGY STAR v3.1 photo voltaic adjusted HERS score"',
                    "energy_star_v3p1_pv_score",
                ),
                # ('ENERGY STAR v3.1 Reference Design HERS score', 'energy_star_v3p1_hers_score'),
            )
        },
        {
            "results": (
                ("Total An. Cost", "total_cost"),
                ("Cooling An. Cost", "cooling_cost"),
                ("Heating An. Cost", "heating_cost"),
                ("Cooling An. Consumption", "cooling_consumption"),
                ("Heating An. Consumption", "heating_consumption"),
            )
        },
        {"windowtype": (("Window SHGC", "shgc"),)},
        {"door": (("Door U-Value", "u_value"),)},
        {"compositetype": (("Wall/Roof U-Value", "u_value"),)},
    )


search.register(Simulation, BuildingSearch)
