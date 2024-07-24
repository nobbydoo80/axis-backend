"""neea_v3.py - Axis"""

__author__ = "Steven K"
__date__ = "6/21/21 13:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from simulation.enumerations import FuelType

from .default import *

log = logging.getLogger(__name__)

NEEA_HEATING_SYSTEM_CONFIGS = ("Central", "Zonal", "All")

NEEA_V3_HEATING_TYPES = (
    "Heat Pump",
    "Heat Pump - Geothermal/Ground Source",
    "Heat Pump - w/ Gas Backup",
    "Heat Pump - Mini Split",
    "Gas with AC",
    "Gas No AC",
    "Zonal Electric",
    "Propane Oil or Wood",
    "Hydronic Radiant Electric Boiler",
    "Hydronic Radiant Gas Boiler",
    "Hydronic Radiant Heat Pump",
)

GAS_CONV_EF_GTE_0p77 = "Gas Conventional EF ≥ 0.77"
GAS_CONV_EF_GTE_0p67 = "Gas Conventional EF 0.67-0.76"

NEEA_WATER_HEATER_TIERS = (
    ELECTRIC_RESISTANCE,
    HPWH_TIER_1,
    HPWH_TIER_2,
    HPWH_TIER_3,
    GAS_CONV_EF_LT_0p67,
    GAS_CONV_EF_GTE_0p67,
    GAS_CONV_EF_GTE_0p77,
    GAS_TANKLESS_EF_GTE_0p82,
    GAS_TANKLESS_EF_GTE_0p90,
    PROPANE_TANK,
    PROPANE_TANKLESS,
)

NEEA_WATER_HEATER_TIER_MAP = (
    ("electric resistance", ELECTRIC_RESISTANCE),
    ("tier1", HPWH_TIER_1),
    ("tier2", HPWH_TIER_2),
    ("tier3", HPWH_TIER_3),
    ("gas_ef_lt_0p67", GAS_CONV_EF_LT_0p67),
    ("gas_ef_gte_0p67", GAS_CONV_EF_GTE_0p67),
    ("gas_ef_gte_0p7", GAS_CONV_EF_GTE_0p77),
    ("gas_tankless_ef_gte_0p82", GAS_TANKLESS_EF_GTE_0p82),
    ("gas_tankless_ef_gte_0p9", GAS_TANKLESS_EF_GTE_0p90),
    ("propane_tank", PROPANE_TANK),
    ("propane_tankless", PROPANE_TANKLESS),
)

NEEA_WATER_HEATER_BASELINE_SAVINGS_RATES = [
    (
        ("OR", "zonal", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 749.955156585345,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("OR", "zonal", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 729.89270095061,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("OR", "zonal", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 691.60561874321,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("OR", "central", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.91569438045,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("OR", "central", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("OR", "central", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "small", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "small", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "small", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "medium", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "medium", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "medium", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "large", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 0.0,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "large", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 0.0,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "zonal", "large", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 0.0,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "small", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "small", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "small", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "medium", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "medium", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "medium", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "large", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 0.0,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "large", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 0.0,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("WA", "central", "large", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 0.0,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("ID", "zonal", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("ID", "zonal", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("ID", "zonal", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("MT", "zonal", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("MT", "zonal", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("MT", "zonal", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("ID", "central", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("ID", "central", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("ID", "central", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("MT", "central", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1409.915694380450,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("MT", "central", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1372.198277787150,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
    (
        ("MT", "central", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0,
            "tier2": 0.0,
            "tier3": 1300.218563237230,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.180993218463,
            "gas_ef_gte_0p7": 55.448292198600,
            "gas_tankless_ef_gte_0p82": 46.072217626730,
            "gas_tankless_ef_gte_0p9": 60.692241774182,
        },
    ),
]


REFRIGERATOR_BOTTOM_FREEZER = "refrigerator_bottom_freezer"
REFRIGERATOR_BOTTOM_FREEZER_LABEL = "ENERGY STAR® with bottom-mounted freezer"
REFRIGERATOR_SIDE_FREEZER = "refrigerator_side_freezer"
REFRIGERATOR_SIDE_FREEZER_LABEL = "ENERGY STAR® with side-mounted freezer"
REFRIGERATOR_OTHER_FREEZER = "refrigerator_other_freezer"
REFRIGERATOR_OTHER_FREEZER_LABEL = "ENERGY STAR® with other freezer type"

NEEA_REFRIGERATOR_CHOICES = (
    REFRIGERATOR_BOTTOM_FREEZER_LABEL,
    REFRIGERATOR_SIDE_FREEZER_LABEL,
    REFRIGERATOR_OTHER_FREEZER_LABEL,
    NONE_LABEL,
)

NEEA_REFRIGERATOR_CHOICE_MAP = (
    (REFRIGERATOR_BOTTOM_FREEZER, REFRIGERATOR_BOTTOM_FREEZER_LABEL),
    (REFRIGERATOR_SIDE_FREEZER, REFRIGERATOR_SIDE_FREEZER_LABEL),
    (REFRIGERATOR_OTHER_FREEZER, REFRIGERATOR_OTHER_FREEZER_LABEL),
    (None, NONE_LABEL),
)

NEEA_REFRIGERATOR_SAVINGS_MAP = (
    (REFRIGERATOR_BOTTOM_FREEZER, 7.0),
    (REFRIGERATOR_SIDE_FREEZER, 45.0),
    (REFRIGERATOR_OTHER_FREEZER, 21.0),
    (None, 0.0),
)

CLOTHES_WASHER_TOP = "washer_top_load"
CLOTHES_WASHER_TOP_LABEL = "ENERGY STAR® with top load"
CLOTHES_WASHER_SIDE = "washer_side_load"
CLOTHES_WASHER_SIDE_LABEL = "ENERGY STAR® with front load"

NEEA_CLOTHES_WASHER_CHOICES = (
    CLOTHES_WASHER_TOP_LABEL,
    CLOTHES_WASHER_SIDE_LABEL,
    NONE_LABEL,
)
NEEA_CLOTHES_WASHER_CHOICE_MAP = (
    (CLOTHES_WASHER_TOP, CLOTHES_WASHER_TOP_LABEL),
    (CLOTHES_WASHER_SIDE, CLOTHES_WASHER_SIDE_LABEL),
    (None, NONE_LABEL),
)

# FYI Washer Type, Water heating, Dryer heating
NEEA_CLOTHES_WASHER_SAVINGS_MAP = (
    (
        (None, FuelType.NATURAL_GAS, FuelType.NATURAL_GAS),
        {"kwh_savings": 0, "therm_savings": 0},
    ),
    (
        (None, FuelType.NATURAL_GAS, FuelType.ELECTRIC),
        {"kwh_savings": 0, "therm_savings": 0},
    ),
    (
        (None, FuelType.ELECTRIC, FuelType.NATURAL_GAS),
        {"kwh_savings": 0, "therm_savings": 0},
    ),
    (
        (None, FuelType.ELECTRIC, FuelType.ELECTRIC),
        {"kwh_savings": 0, "therm_savings": 0},
    ),
    (
        (CLOTHES_WASHER_SIDE, FuelType.NATURAL_GAS, FuelType.NATURAL_GAS),
        {"kwh_savings": -11.910875907857200, "therm_savings": 8.498529892911450},
    ),
    (
        (CLOTHES_WASHER_SIDE, FuelType.NATURAL_GAS, FuelType.ELECTRIC),
        {"kwh_savings": 83.674357454009700, "therm_savings": 4.843200439551110},
    ),
    (
        (CLOTHES_WASHER_SIDE, FuelType.ELECTRIC, FuelType.NATURAL_GAS),
        {"kwh_savings": 30.642693954148800, "therm_savings": 3.655329453360340},
    ),
    (
        (CLOTHES_WASHER_SIDE, FuelType.ELECTRIC, FuelType.ELECTRIC),
        {"kwh_savings": 126.227927316016000, "therm_savings": 0.0},
    ),
    (
        (CLOTHES_WASHER_TOP, FuelType.NATURAL_GAS, FuelType.NATURAL_GAS),
        {"kwh_savings": 9.4623982277666000, "therm_savings": 1.6717271148991800},
    ),
    (
        (CLOTHES_WASHER_TOP, FuelType.NATURAL_GAS, FuelType.ELECTRIC),
        {"kwh_savings": -1.8914338809048400, "therm_savings": 2.1059154874715000},
    ),
    (
        (CLOTHES_WASHER_TOP, FuelType.ELECTRIC, FuelType.NATURAL_GAS),
        {"kwh_savings": 27.9654981795631000, "therm_savings": -0.4341883725723260},
    ),
    (
        (CLOTHES_WASHER_TOP, FuelType.ELECTRIC, FuelType.ELECTRIC),
        {"kwh_savings": 16.6116660708917000, "therm_savings": 0.0},
    ),
)

NEEA_CLOTHES_DRYER_TIER_SAVINGS_MAP = (
    (DRYER_TIER_2, 344.0),
    (DRYER_TIER_3, 485.0),
    (ESTAR, 68.0),
)
NEEA_CLOTHES_DRYER_FUELS_CHOICE_MAP = (
    (FuelType.ELECTRIC, "Electric"),
    (FuelType.NATURAL_GAS, "Gas"),
)
