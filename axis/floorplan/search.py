"""search.py: Floorplan"""


from appsearch.registry import ModelSearch, search
from .models import Floorplan

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class FloorplanSearch(ModelSearch):
    display_fields = (
        "name",
        "number",
        ("Plan Name", "name"),
        ("RemRate Project", "remrate_target__building__project__name"),
        ("HERs Index", "remrate_target__hers__score"),
        (
            "ENERGY STAR v2.5 photo voltaic adjusted HERS score",
            "remrate_target__energystar__energy_star_v2p5_pv_score",
        ),
        (
            "ENERGY STAR v3 photo voltaic adjusted HERS score",
            "remrate_target__energystar__energy_star_v3_pv_score",
        ),
        (
            "ENERGY STAR v3.1 photo voltaic adjusted HERS score",
            "remrate_target__energystar__energy_star_v3p1_pv_score",
        ),
    )

    search_fields = (
        ("Plan Name", "name"),
        "number",
        ("RemRate BLG", "remrate_data_file"),
        # {'subdivision': (
        #     ('Subdivision', 'name'),
        #     {'builder_org': (
        #         ('Builder', 'name'),
        #     )},
        # )},
        {
            "remrate_target": (
                {
                    "compliance": (
                        ("HERs Index", "hers_index"),
                        ("HERs Index (w/o) PV", "hers_photo_voltaic_adjusted_score"),
                        ("Pass Energy Star V2", "passes_energy_star_v2"),
                        ("Pass Energy Star V2.5", "passes_energy_star_v2p5"),
                        ("Pass Energy Star V3", "passes_energy_star_v3"),
                    )
                },
                {"building": (("RemRate data BLG Filename", "filename"),)},
            )
        },
    )


search.register(Floorplan, FloorplanSearch)
