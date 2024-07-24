"""eto_2018.py: Django eps"""


import logging

__author__ = "Steven Klass"
__date__ = "12/6/17 4:08 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

from .eto_2017 import *

EPS_VALID_LOCATIONS = [
    "astoria",
    "burns",
    "eugene",
    "medford",
    "northbend",
    "pendleton",
    "portland",
    "redmond",
    "salem",
]
LOCATION_TRANSLATION = {
    "astoria": "portland",
    "burns": "redmond",
    "eugene": "portland",
    "northbend": "portland",
    "pendleton": "redmond",
    "salem": "portland",
}

EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR = {
    "natural gas": 11.7,
    "pacific power": 1.356,
    "portland general": 0.926,
    "bpa": 0.04837,
}
EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA = EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR

EPS_OR_SAVINGS_PCT = {
    "gas_smart_tstat_savings_pct": 0.06,
    "electric_smart_tstat_savings_pct": 0.12,
    "gas_showerhead_savings_pct": 0.0,
    "electric_showerhead_savings_pct": 0.0,
}
EPS_WA_SAVINGS_PCT = {
    "gas_smart_tstat_savings_pct": 0.06,
    "electric_smart_tstat_savings_pct": 0.12,
    "gas_showerhead_savings_pct": 0.05,
    "electric_showerhead_savings_pct": 0.075,
}

EPS_OR_POLY = {"second_order": 36354.0, "first_order": -4510.2, "scaler": 710.5, "min": 4723.0}
EPS_WA_POLY = {"second_order": 0.0, "first_order": 2000.0, "scaler": 50, "min": 850.0}


WEIGHTED_UTILITY_ALLOCATIONS = [
    ("GH+EW", [("electric", 0.45), ("gas", 0.55)]),
    ("GH+GW", [("electric", 0.08), ("gas", 0.92)]),
    ("EH+EW", [("electric", 1.00), ("gas", 0.00)]),
    ("EH+GW", [("electric", 0.83), ("gas", 0.17)]),
]

EPS_WAML_LOAD_PROFILES = [
    (
        "N/A",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
        ],
    ),
    (
        "Path 1",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 40.40),
                    ("electric_benefit_ratio", 0.12),
                    ("gas_benefit_ratio", 0.88),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 39.60),
                    ("electric_benefit_ratio", 0.10),
                    ("gas_benefit_ratio", 0.90),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "None - Gas"),
                    ("measure_life", 35.60),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 35.00),
                    ("electric_benefit_ratio", 0.95),
                    ("gas_benefit_ratio", 0.05),
                ],
            ),
        ],
    ),
    (
        "Path 2",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res HP Water Heat"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 30.30),
                    ("electric_benefit_ratio", 0.62),
                    ("gas_benefit_ratio", 0.38),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 37.10),
                    ("electric_benefit_ratio", 0.06),
                    ("gas_benefit_ratio", 0.94),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "None - Gas"),
                    ("measure_life", 28.20),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 34.50),
                    ("electric_benefit_ratio", 0.75),
                    ("gas_benefit_ratio", 0.25),
                ],
            ),
        ],
    ),
    (
        "Path 3",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res HP Water Heat"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.00),
                    ("electric_benefit_ratio", 0.54),
                    ("gas_benefit_ratio", 0.46),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.70),
                    ("electric_benefit_ratio", 0.11),
                    ("gas_benefit_ratio", 0.89),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "None - Gas"),
                    ("measure_life", 37.80),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 41.30),
                    ("electric_benefit_ratio", 0.84),
                    ("gas_benefit_ratio", 0.16),
                ],
            ),
        ],
    ),
    (
        "Path 4",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res HP Water Heat"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.50),
                    ("electric_benefit_ratio", 0.42),
                    ("gas_benefit_ratio", 0.58),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.20),
                    ("electric_benefit_ratio", 0.07),
                    ("gas_benefit_ratio", 0.93),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "None - Gas"),
                    ("measure_life", 40.20),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 42.60),
                    ("electric_benefit_ratio", 0.91),
                    ("gas_benefit_ratio", 0.09),
                ],
            ),
        ],
    ),
]

EPS_WA_WAML_LOAD_PROFILES = [
    (
        "N/A",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "N/A"),
                    ("gas_load_profile", "N/A"),
                    ("measure_life", 0.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
        ],
    ),
    (
        "Path 1",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.4),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.4),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.4),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.4),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
        ],
    ),
    (
        "Path 2",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.5),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.5),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.5),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.5),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
        ],
    ),
    (
        "Path 3",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
        ],
    ),
    (
        "Path 4",
        [
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.6),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.6),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.6),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 42.6),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
        ],
    ),
]
