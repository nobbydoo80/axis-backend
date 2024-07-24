"""eto_2020: Django """

from .eto_2019 import *

__author__ = "Steven K"
__date__ = "12/15/2019 20:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)

FIREPLACE_ADJUSTMENTS = {
    "baseline": 88.5,
    "No fireplace": 0.0,
    "<=49FE": 88.5,
    "50-59FE": 88.5,
    "60-69FE": 88.5,
    ">=70FE": 70.2,
}

EPS_OR_SAVINGS_PCT = {
    "gas_smart_tstat_heating_savings_pct": 0.06,
    "electric_smart_tstat_heating_savings_pct": 0.12,
    "electric_smart_tstat_cooling_savings_pct": 0.06,
}

EPS_OR_POLY = {
    "second_order": 36354.0,
    "first_order": -4510.2,
    "scaler": 1210.5,
    "min": 5223.0,
}

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
                "EH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 43.0),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 43.00),
                    ("electric_benefit_ratio", 0.9744819195559840000),
                    ("gas_benefit_ratio", 0.0255180804440162000),
                ],
            ),
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 35.0),
                    ("electric_benefit_ratio", 0.3790606181956560000),
                    ("gas_benefit_ratio", 0.6209393818043440000),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.0),
                    ("electric_benefit_ratio", 0.3453554216774470000),
                    ("gas_benefit_ratio", 0.6546445783225530000),
                ],
            ),
        ],
    ),
    (
        "Path 2",
        [
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 38.0),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 41.00),
                    ("electric_benefit_ratio", 0.8689876634365060000),
                    ("gas_benefit_ratio", 0.1310123365634940000),
                ],
            ),
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 29.00),
                    ("electric_benefit_ratio", 0.7560419843980000000),
                    ("gas_benefit_ratio", 0.2439580156020000000),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 34.00),
                    ("electric_benefit_ratio", 0.1883061089346960000),
                    ("gas_benefit_ratio", 0.8116938910653040000),
                ],
            ),
        ],
    ),
    (
        "Path 3",
        [
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 36.0),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 39.0),
                    ("electric_benefit_ratio", 0.8458957826709290000),
                    ("gas_benefit_ratio", 0.1541042173290710000),
                ],
            ),
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 33.00),
                    ("electric_benefit_ratio", 0.7547094636691920000),
                    ("gas_benefit_ratio", 0.2452905363308080000),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 38.00),
                    ("electric_benefit_ratio", 0.2263699182253570000),
                    ("gas_benefit_ratio", 0.7736300817746430000),
                ],
            ),
        ],
    ),
    (
        "Path 4",
        [
            (
                "EH+EW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "None"),
                    ("measure_life", 37.0),
                    ("electric_benefit_ratio", 1.00),
                    ("gas_benefit_ratio", 0.0),
                ],
            ),
            (
                "EH+GW",
                [
                    ("electric_load_profile", "Res Air Source HP"),
                    ("gas_load_profile", "DHW"),
                    ("measure_life", 40.0),
                    ("electric_benefit_ratio", 0.8855852584722720000),
                    ("gas_benefit_ratio", 0.1144147415277280000),
                ],
            ),
            (
                "GH+EW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 36.0),
                    ("electric_benefit_ratio", 0.6532115667028290000),
                    ("gas_benefit_ratio", 0.3467884332971710000),
                ],
            ),
            (
                "GH+GW",
                [
                    ("electric_load_profile", "Res Space Conditioning"),
                    ("gas_load_profile", "Res Heating"),
                    ("measure_life", 40.0),
                    ("electric_benefit_ratio", 0.1661286423177830000),
                    ("gas_benefit_ratio", 0.8338713576822170000),
                ],
            ),
        ],
    ),
]

ETO_RATER_MAX_INCENTIVE_MUTIPLIER = 300.00
ETO_RATER_MIN_INCENTIVE_PCT_MUTIPLIER = 0.4

EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR = {
    "natural gas": 11.7,
    "pacific power": 1.09,
    "portland general": 1.09,
    "bpa": 0.067,
}

EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA = {
    "natural gas": 11.7,
    "pacific power": 1.356,
    "portland general": 0.926,
    "bpa": 0.04837,
}


EPS_WA_SAVINGS_PCT = {
    "gas_smart_tstat_heating_savings_pct": 0.06,
    "electric_smart_tstat_heating_savings_pct": 0.12,
    "electric_smart_tstat_cooling_savings_pct": 0.06,
}

ALTERNATE_METHOD_ELECTRIC_SAVINGS_ALLOCATION = 0.253930
ALTERNATE_METHOD_GAS_SAVINGS_ALLOCATION = 0.741819
ALTERNATE_METHOD_ELECTRIC_INCENTIVE_ALLOCATION = 0.668181
ALTERNATE_METHOD_GAS_INCENTIVE_ALLOCATION = 0.331819

ETO_2020_FUEL_RATES = [
    ("portland-electric", "PGE-Jan2021"),
    ("pacific-power", "PAC-Jan2021"),
    ("central-electric", "CEC-Jan2021"),
    ("utility-city-of-ashland", "Ashland-Jan2021"),
    ("clark-pud", "ClarkPUD-Jan2021"),
    ("utility-umatilla-electric-co-op", "Umatilla-Jan2021"),
    ("utility-cowlitz-county-pud", "CowlitzPUD-Jan2021"),
    ("utility-columbia-basin-electric-co-op", "ColBasinCoop-Jan2021"),
    ("utility-columbia-river-pud", "ColRiverPUD-Jan2021"),
    ("utility-forest-grove-light-department", "ForestGrove-Jan2021"),
    ("utility-eugene-water-electric-board", "EWEB-Jan2021"),
    ("avista", "Avista-Jan2021"),
    ("nw-natural-gas", "NWN_OR-Jan2021"),
    ("cascade-gas", "Cascade-Jan2021"),
    ("utility-clatskanie-pud", "ClatskPUD-Jan2021"),
    ("utility-canby-utility-board", "CanbyPUD-Jan2021"),
    ("utility-columbia-power-co-op", "ColPowerCoop-Jan2021"),
    ("utility-oregon-trail-electric-co-op", "OTEC-Jan2021"),
    ("utility-mcminnville-water-light", "MW&L-Jan2021"),
    ("utility-springfield-utility-board", "SUB-Jan2021"),
    ("utility-klickitat-pud", "KlickitatPUD-Jan2021"),
]
ETO_2020_FUEL_RATES_WA_OVERRIDE = [
    ("nw-natural-gas", "NWN_WA-Jan2021"),
]

NET_ZERO_INCENTIVE = 750.0

ENERGY_SMART_HOMES_INCENTIVES = {
    "base_package": 200.0,
    "storage_ready": 150.0,
    "advanced_wiring": 150.0,
}


NET_ZERO_PROGRAM_MAX_INCENTIVE = (
    ("Path 1", {"base_price": 1586.0, "b": 255.0}),
    ("Path 2", {"base_price": 2917.0, "b": 1733.0}),
    ("Path 3", {"base_price": 3509.0, "b": -3397.0}),
    ("Path 4", {"base_price": 5811.0, "b": 5811.0}),
)
