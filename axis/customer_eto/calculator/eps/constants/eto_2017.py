"""eto_2017.py: Django eps"""


import logging

__author__ = "Steven Klass"
__date__ = "11/4/16 16:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

from .original import *

EPS_VALID_SMART_THERMOMETER_CHOICES = {
    "no qualifying smart thermostat": (False, None),
    "yes-ducted gas furnace": (True, "GAS"),
    "yes-ducted air source heat pump": (True, "ASHP"),
}

ALLOWED_GAS_UTILITY_NAMES = ("nw natural", "cascade", "avista", DEFAULT_UTILITY_NAME)

EPS_ELECTRIC_SPACE_HEAT_FUEL_WEIGHT = {"portland": 3.29, "medford": 3.29, "redmond": 3.29}
EPS_ELECTRIC_HOT_WATER_FUEL_WEIGHT = {"portland": 1.43, "medford": 1.43, "redmond": 1.43}

EPS_CODE_HEATING_AJUSTMENT_FACTORS = {"portland": 1.00, "medford": 1.00, "redmond": 1.00}
EPS_CODE_COOLING_AJUSTMENT_FACTORS = {"portland": 1.00, "medford": 1.00, "redmond": 1.00}
EPS_IMPROVED_HEATING_AJUSTMENT_FACTORS = {"portland": 1.00, "medford": 1.00, "redmond": 1.00}
EPS_IMPROVED_COOLING_AJUSTMENT_FACTORS = {"portland": 1.00, "medford": 1.00, "redmond": 1.00}

EPS_OR_SAVINGS_PCT = {
    "gas_smart_tstat_savings_pct": 0.06,
    "electric_smart_tstat_savings_pct": 0.06,
    "gas_showerhead_savings_pct": 0.05,
    "electric_showerhead_savings_pct": 0.075,
}
EPS_WA_SAVINGS_PCT = EPS_OR_SAVINGS_PCT

EPS_INCENTIVE_ALLOCATION_DATA = [
    {"min": 0.0, "incentive_increment": 60, "incentive": 600.00},
    {"min": 0.11, "incentive_increment": 60, "incentive": 1140.0},
    {"min": 0.20, "incentive_increment": 100, "incentive": 1340.0},
    {"min": 0.22, "incentive_increment": 115, "incentive": 1570.0},
    {"min": 0.24, "incentive_increment": 125, "incentive": 1820.0},
    {"min": 0.26, "incentive_increment": 150, "incentive": 2270.0},
    {"min": 0.29, "incentive_increment": 175, "incentive": 2620.0},
    {"min": 0.31, "incentive_increment": 200, "incentive": 2820.0},
    {"min": 0.32, "incentive_increment": 205, "incentive": 4050.0},
    {"min": 0.38, "incentive_increment": 210, "incentive": 4680.0},
]

EPS_WA_INCENTIVE_ALLOCATION_DATA = [
    {"min": 0.0, "incentive_increment": 0.0, "incentive": 250.00},
    {"min": 0.10, "incentive_increment": 20, "incentive": 430.0},
    {"min": 0.20, "incentive_increment": 20, "incentive": 630.0},
    {"min": 0.30, "incentive_increment": 20, "incentive": 830.0},
    {"min": 0.40, "incentive_increment": 0.0, "incentive": 850.0},
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
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 30.2256634009944),
                    ("electric_benefit_ratio", 0.71795716336194800),
                    ("gas_benefit_ratio", 0.28204283663805200),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 31.58871668185350),
                    ("electric_benefit_ratio", 0.62396627700981900),
                    ("gas_benefit_ratio", 0.37603372299018100),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 32.27651597450190),
                    ("electric_benefit_ratio", 1.00000000000000000),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 33.55967518846630),
                    ("electric_benefit_ratio", 0.93873166798060900),
                    ("gas_benefit_ratio", 0.06126833201939140),
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
                    ("measure_life", 25.00806430678370),
                    ("electric_benefit_ratio", 0.79269239096973100),
                    ("gas_benefit_ratio", 0.20730760903026900),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 29.13323009005290),
                    ("electric_benefit_ratio", 0.50846668624601100),
                    ("gas_benefit_ratio", 0.49153331375398900),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 27.03871423885270),
                    ("electric_benefit_ratio", 1.00000000000000000),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 30.52475403181400),
                    ("electric_benefit_ratio", 0.81917892007505500),
                    ("gas_benefit_ratio", 0.18082107992494500),
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
                    ("measure_life", 26.67439095191240),
                    ("electric_benefit_ratio", 0.76273407044585100),
                    ("gas_benefit_ratio", 0.23726592955414900),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 32.04921908630750),
                    ("electric_benefit_ratio", 0.46793299840894600),
                    ("gas_benefit_ratio", 0.53206700159105400),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res HP Water Heat"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 28.10596676075550),
                    ("electric_benefit_ratio", 1.00000000000000000),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 31.86366613351470),
                    ("electric_benefit_ratio", 0.88841398321234600),
                    ("gas_benefit_ratio", 0.11158601678765400),
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
                    ("measure_life", 31.52459138366460),
                    ("electric_benefit_ratio", 0.65433167278375900),
                    ("gas_benefit_ratio", 0.34566832721624100),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 36.94309142546350),
                    ("electric_benefit_ratio", 0.33519731334178800),
                    ("gas_benefit_ratio", 0.66480268665821200),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 31.95376102600250),
                    ("electric_benefit_ratio", 1.00000000000000000),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Ductless HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 35.60111305561320),
                    ("electric_benefit_ratio", 0.90029811812749200),
                    ("gas_benefit_ratio", 0.09970188187250790),
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
                    ("measure_life", 34.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.0),
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
                    ("measure_life", 39.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 39.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 39.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 39.0),
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
                    ("measure_life", 41.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 41.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 1.0),
                ],
            ),
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 41.0),
                    ("electric_benefit_ratio", 0.0),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Lighting"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 41.0),
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
]

WEIGHTED_UTILITY_ALLOCATIONS = [
    ("GH+EW", [("electric", 0.75), ("gas", 0.25)]),
    ("GH+GW", [("electric", 0.54), ("gas", 0.46)]),
    ("EH+EW", [("electric", 1.00), ("gas", 0.00)]),
    ("EH+GW", [("electric", 0.89), ("gas", 0.11)]),
]

NET_ZERO_INCENTIVE = 0.0

ENERGY_SMART_HOMES_INCENTIVES = {"base_package": 0.0, "storage_ready": 0.0, "advanced_wiring": 0.0}
