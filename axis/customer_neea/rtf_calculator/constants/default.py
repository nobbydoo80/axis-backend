"""default.py: Django rtf_calculator"""


import logging

__author__ = "Steven Klass"
__date__ = "1/11/17 11:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

ALLOWED_HEATING_FUELS = ("gas", "electric")
ALLOWED_HEATING_SYSTEM_TYPES = ("central", "zonal", "all")
ALLOWED_HOME_SIZE = ("small", "medium", "large", "all")
ALLOWED_HEATING_ZONE = ("hz1", "hz2", "hz3")

ELECTRICITY_ADJUSTMENT_FACTOR = 1.0
GAS_ADJUSTMENT_FACTOR = 1.0

HEAT_PUMP_WATER_HEATER_TIERS = ("tier1", "tier2", "tier3")

ELECTRIC_RESISTANCE = "Electric Resistance"
HPWH_TIER_1 = "HPWH Tier 1"
HPWH_TIER_2 = "HPWH Tier 2"
HPWH_TIER_3 = "HPWH Tier 3"
GAS_CONV_EF_LT_0p67 = "Gas Conventional EF < 0.67"
GAS_CONV_EF_GTE_0p67 = "Gas Conventional EF ≥ 0.67"
GAS_CONV_EF_GTE_0p7 = "Gas Conventional EF ≥ 0.70"
GAS_TANKLESS_EF_GTE_0p82 = "Gas Tankless EF ≥ 0.82"
GAS_TANKLESS_EF_GTE_0p90 = "Gas Tankless EF ≥ 0.90"
PROPANE_TANK = "Propane Tank"
PROPANE_TANKLESS = "Propane Tankless"

NEEA_WATER_HEATER_TIERS = [
    ELECTRIC_RESISTANCE,
    HPWH_TIER_1,
    HPWH_TIER_2,
    HPWH_TIER_3,
    GAS_CONV_EF_LT_0p67,
    GAS_CONV_EF_GTE_0p67,
    GAS_CONV_EF_GTE_0p7,
    GAS_TANKLESS_EF_GTE_0p82,
    GAS_TANKLESS_EF_GTE_0p90,
    PROPANE_TANK,
    PROPANE_TANKLESS,
]

NEEA_WATER_HEATER_TIER_MAP = (
    ("electric resistance", ELECTRIC_RESISTANCE),
    ("tier1", HPWH_TIER_1),
    ("tier2", HPWH_TIER_2),
    ("tier3", HPWH_TIER_3),
    ("gas_ef_lt_0p67", GAS_CONV_EF_LT_0p67),
    ("gas_ef_gte_0p67", GAS_CONV_EF_GTE_0p67),
    ("gas_ef_gte_0p7", GAS_CONV_EF_GTE_0p7),
    ("gas_tankless_ef_gte_0p82", GAS_TANKLESS_EF_GTE_0p82),
    ("gas_tankless_ef_gte_0p9", GAS_TANKLESS_EF_GTE_0p90),
    ("propane_tank", PROPANE_TANK),
    ("propane_tankless", PROPANE_TANKLESS),
)

HEAT_PUMP_WATER_HEATER_BASELINE_CONSUMPTION_RATES = [
    (("OR", "zonal", "all", "hz1"), 2238.0),
    (("OR", "zonal", "all", "hz2"), 2340.0),
    (("OR", "zonal", "all", "hz3"), 2457.0),
    (("OR", "central", "all", "hz1"), 2791.0),
    (("OR", "central", "all", "hz2"), 2909.0),
    (("OR", "central", "all", "hz3"), 3024.0),
    (("WA", "zonal", "small", "hz1"), 2791.0),
    (("WA", "zonal", "small", "hz2"), 2909.0),
    (("WA", "zonal", "small", "hz3"), 3024.0),
    (("WA", "zonal", "medium", "hz1"), 2791.0),
    (("WA", "zonal", "medium", "hz2"), 2909.0),
    (("WA", "zonal", "medium", "hz3"), 3024.0),
    (("WA", "zonal", "large", "hz1"), 1609.0),
    (("WA", "zonal", "large", "hz2"), 1693.0),
    (("WA", "zonal", "large", "hz3"), 1812.0),
    (("WA", "central", "small", "hz1"), 2791.0),
    (("WA", "central", "small", "hz2"), 2909.0),
    (("WA", "central", "small", "hz3"), 3024.0),
    (("WA", "central", "medium", "hz1"), 2791.0),
    (("WA", "central", "medium", "hz2"), 2909.0),
    (("WA", "central", "medium", "hz3"), 3024.0),
    (("WA", "central", "large", "hz1"), 1609.0),
    (("WA", "central", "large", "hz2"), 1693.0),
    (("WA", "central", "large", "hz3"), 1812.0),
    (("ID", "zonal", "all", "hz1"), 2791.0),
    (("ID", "zonal", "all", "hz2"), 2909.0),
    (("ID", "zonal", "all", "hz3"), 3024.0),
    (("MT", "zonal", "all", "hz1"), 2791.0),
    (("MT", "zonal", "all", "hz2"), 2909.0),
    (("MT", "zonal", "all", "hz3"), 3024.0),
    (("ID", "central", "all", "hz1"), 2791.0),
    (("ID", "central", "all", "hz2"), 2909.0),
    (("ID", "central", "all", "hz3"), 3024.0),
    (("MT", "central", "all", "hz1"), 2791.0),
    (("MT", "central", "all", "hz2"), 2909.0),
    (("MT", "central", "all", "hz3"), 3024.0),
]

NEEA_WATER_HEATER_BASELINE_SAVINGS_RATES = [
    (
        ("OR", "zonal", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 628.4474897003200,
            "tier2": 1018.0439922297700,
            "tier3": 1118.2073045809000,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("OR", "zonal", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 646.7248485580310,
            "tier2": 1064.4572368825800,
            "tier3": 1166.4441002319900,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("OR", "zonal", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 644.8027133462390,
            "tier2": 1137.7569327414100,
            "tier3": 1236.4574192320600,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("OR", "central", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("OR", "central", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("OR", "central", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "small", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "small", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "small", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "medium", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "medium", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "medium", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "large", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0000000000000,
            "tier2": 389.5965025294530,
            "tier3": 489.7598148805830,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "large", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0000000000000,
            "tier2": 417.7323883245460,
            "tier3": 519.7192516739560,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "zonal", "large", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0000000000000,
            "tier2": 492.9542193951740,
            "tier3": 591.6547058858190,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "small", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "small", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "small", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "medium", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "medium", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "medium", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "large", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0000000000000,
            "tier2": 389.5965025294530,
            "tier3": 489.7598148805830,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "large", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0000000000000,
            "tier2": 417.7323883245460,
            "tier3": 519.7192516739560,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("WA", "central", "large", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 0.0000000000000,
            "tier2": 492.9542193951740,
            "tier3": 591.6547058858190,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("ID", "zonal", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("ID", "zonal", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("ID", "zonal", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("MT", "zonal", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("MT", "zonal", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("MT", "zonal", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("ID", "central", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("ID", "central", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("ID", "central", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("MT", "central", "all", "hz1"),
        {
            "electric resistance": 0.0,
            "tier1": 1181.4812806366000,
            "tier2": 1571.0777831660500,
            "tier3": 1671.2410955171800,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("MT", "central", "all", "hz2"),
        {
            "electric resistance": 0.0,
            "tier1": 1215.8427152891000,
            "tier2": 1633.5751036136400,
            "tier3": 1735.5619669630500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
    (
        ("MT", "central", "all", "hz3"),
        {
            "electric resistance": 0.0,
            "tier1": 1212.2291010909300,
            "tier2": 1705.1833204861000,
            "tier3": 1803.8838069767500,
            "gas_ef_lt_0p67": 0.0,
            "gas_ef_gte_0p67": 25.3,
            "gas_ef_gte_0p7": 31.5,
            "gas_tankless_ef_gte_0p82": 62.0,
            "gas_tankless_ef_gte_0p9": 71.0,
        },
    ),
]

HEAT_PUMP_WATER_HEATER_KWH = [
    (("tier1", "hz1"), 1609.0),
    (("tier1", "hz2"), 1693.0),
    (("tier1", "hz3"), 1812.0),
    (("tier2", "hz1"), 1220.0),
    (("tier2", "hz2"), 1275.0),
    (("tier2", "hz3"), 1319.0),
    (("tier3", "hz1"), 1119.0),
    (("tier3", "hz2"), 1173.0),
    (("tier3", "hz3"), 1221.0),
    ((None, "hz1"), 2866.0),
    ((None, "hz2"), 2986.0),
    ((None, "hz3"), 3102.0),
]

BASELINE_PCT_LIGHTING_EFFICACY = [
    (("OR", "zonal", "all"), 1.0),
    (("OR", "central", "all"), 1.0),
    (("WA", "zonal", "small"), 0.75),
    (("WA", "zonal", "medium"), 0.75),
    (("WA", "zonal", "large"), 0.75),
    (("WA", "central", "small"), 0.75),
    (("WA", "central", "medium"), 0.75),
    (("WA", "central", "large"), 0.75),
    (("ID", "zonal", "all"), 0.50),
    (("ID", "central", "all"), 0.50),
    (("MT", "zonal", "all"), 0.75),
    (("MT", "central", "all"), 0.75),
]

WEIGHTED_AVERAGE_HOU = 1.9339232560560600
WEIGHTED_AVERAGE_INEFFICIENT_WATTAGE = 30.92792464685660
WEIGHTED_AVERAGE_CFL_WATTAGE = 14.66922099937440
WEIGHTED_AVERAGE_LED_WATTAGE = 11.45098278344010

STANDARD_REFRIGERATOR_ENERGY_SAVINGS_EUL = 39.0
COMPACT_REFRIGERATOR_ENERGY_SAVINGS_EUL = 9.0

CLOTHES_DRYER_TYPES = ("ventless", "vented")

CLOTHES_DRYER_ANNUAL_SAVINGS = [
    (
        (3.0, 3.4, "vented"),
        {"annual_savings": 93.0, "measure_life": 12.0, "label": "3.0 to 3.39"},
    ),
    (
        (3.4, 4.0, "vented"),
        {"annual_savings": 183.0, "measure_life": 12.0, "label": "3.4 to 3.99"},
    ),
    (
        (4.0, 5.0, "vented"),
        {"annual_savings": 286.0, "measure_life": 12.0, "label": "4.0 to 4.99"},
    ),
    (
        (5.0, 6.0, "vented"),
        {"annual_savings": 376.0, "measure_life": 12.0, "label": "5.0 to 5.99"},
    ),
    (
        (6.0, 7.0, "vented"),
        {"annual_savings": 438.0, "measure_life": 12.0, "label": "6.0 to 6.99"},
    ),
    (
        (7.0, 8.0, "vented"),
        {"annual_savings": 484.0, "measure_life": 12.0, "label": "7.0 to 7.99"},
    ),
    (
        (3.0, 3.4, "ventless"),
        {"annual_savings": 141.0, "measure_life": 12.0, "label": "3.0 to 3.39"},
    ),
    (
        (3.4, 4.0, "ventless"),
        {"annual_savings": 228.0, "measure_life": 12.0, "label": "3.4 to 3.99"},
    ),
    (
        (4.0, 5.0, "ventless"),
        {"annual_savings": 325.0, "measure_life": 12.0, "label": "4.0 to 4.99"},
    ),
    (
        (5.0, 6.0, "ventless"),
        {"annual_savings": 411.0, "measure_life": 12.0, "label": "5.0 to 5.99"},
    ),
    (
        (6.0, 7.0, "ventless"),
        {"annual_savings": 470.0, "measure_life": 12.0, "label": "6.0 to 6.99"},
    ),
    (
        (7.0, 8.0, "ventless"),
        {"annual_savings": 513.0, "measure_life": 12.0, "label": "7.0 to 7.99"},
    ),
]

SMART_TSTAT_SAVINGS = [
    (
        ("electric", "central", False),
        {"type": "eFAF", "heating_pct": 0.06, "cooling_pct": 0.06},
    ),
    (
        ("electric", "central", True),
        {"type": "ASHP", "heating_pct": 0.14, "cooling_pct": 0.06},
    ),
    (
        ("electric", "zonal", True),
        {"type": "DHP", "heating_pct": 0.0, "cooling_pct": 0.0},
    ),
    (
        ("electric", "zonal", False),
        {"type": "eZonal", "heating_pct": 0.0, "cooling_pct": 0.0},
    ),
    (
        ("gas", "central", False),
        {"type": "GasFAF", "heating_pct": 0.06, "cooling_pct": 0.06},
    ),
    (
        ("gas", "central", True),
        {"type": "GasFAF", "heating_pct": 0.06, "cooling_pct": 0.06},
    ),
    (
        ("gas", "zonal", False),
        {"type": "Other", "heating_pct": 0.0, "cooling_pct": 0.0},
    ),
    (("gas", "zonal", True), {"type": "Other", "heating_pct": 0.0, "cooling_pct": 0.0}),
    (
        ("all", "central", False),
        {"type": "GasFAF", "heating_pct": 0.06, "cooling_pct": 0.06},
    ),
    (
        ("all", "central", True),
        {"type": "GasFAF", "heating_pct": 0.06, "cooling_pct": 0.06},
    ),
    (
        ("all", "zonal", False),
        {"type": "Other", "heating_pct": 0.0, "cooling_pct": 0.0},
    ),
    (("all", "zonal", True), {"type": "Other", "heating_pct": 0.0, "cooling_pct": 0.0}),
]

LOWFLOW_CONSUMPTION = [
    (
        ("electric resistance", 1.75),
        {"kwh_consumption": 580.331853759892000, "therms_consumption": 0.0},
    ),
    (
        ("electric resistance", 1.5),
        {"kwh_consumption": 526.849123062258000, "therms_consumption": 0.0},
    ),
    (
        ("hpwh", 1.75),
        {"kwh_consumption": 290.165926879946000, "therms_consumption": 0.0},
    ),
    (
        ("hpwh", 1.5),
        {"kwh_consumption": 263.424561531129000, "therms_consumption": 0.0},
    ),
    (("gas", 1.75), {"kwh_consumption": 0.0, "therms_consumption": 26.402326389925900}),
    (("gas", 1.5), {"kwh_consumption": 0.0, "therms_consumption": 23.969117695702400}),
]

LOWFLOW_UEC = [
    (
        ("OR", "electric", "zonal", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("OR", "electric", "central", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("OR", "gas", "central", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("OR", "gas", "zonal", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("WA", "electric", "zonal", "small", "electric resistance"),
        {"consumption": 580.331853759892, "units": "kWh"},
    ),
    (
        ("WA", "electric", "zonal", "medium", "electric resistance"),
        {"consumption": 610.165486093215, "units": "kWh"},
    ),
    (
        ("WA", "electric", "zonal", "large", "electric resistance"),
        {"consumption": 610.165486093215, "units": "kWh"},
    ),
    (
        ("WA", "electric", "central", "small", "electric resistance"),
        {"consumption": 580.331853759892, "units": "kWh"},
    ),
    (
        ("WA", "electric", "central", "medium", "electric resistance"),
        {"consumption": 620.110030204323, "units": "kWh"},
    ),
    (
        ("WA", "electric", "central", "large", "electric resistance"),
        {"consumption": 620.110030204323, "units": "kWh"},
    ),
    (
        ("WA", "gas", "central", "small", "electric resistance"),
        {"consumption": 580.331853759892, "units": "kWh"},
    ),
    (
        ("WA", "gas", "central", "medium", "electric resistance"),
        {"consumption": 620.110030204323, "units": "kWh"},
    ),
    (
        ("WA", "gas", "central", "large", "electric resistance"),
        {"consumption": 620.110030204323, "units": "kWh"},
    ),
    (
        ("WA", "gas", "zonal", "small", "electric resistance"),
        {"consumption": 580.331853759892, "units": "kWh"},
    ),
    (
        ("WA", "gas", "zonal", "medium", "electric resistance"),
        {"consumption": 610.165486093215, "units": "kWh"},
    ),
    (
        ("WA", "gas", "zonal", "large", "electric resistance"),
        {"consumption": 610.165486093215, "units": "kWh"},
    ),
    (
        ("ID", "electric", "zonal", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("ID", "electric", "central", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("ID", "gas", "central", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("ID", "gas", "zonal", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("MT", "electric", "zonal", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("MT", "electric", "central", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("MT", "gas", "central", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("MT", "gas", "zonal", "all", "electric resistance"),
        {"consumption": 679.777294870969, "units": "kWh"},
    ),
    (
        ("OR", "electric", "zonal", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("OR", "electric", "central", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("OR", "gas", "central", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("OR", "gas", "zonal", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("WA", "electric", "zonal", "small", "hpwh"),
        {"consumption": 290.165926879946, "units": "kWh"},
    ),
    (
        ("WA", "electric", "zonal", "medium", "hpwh"),
        {"consumption": 305.082743046608, "units": "kWh"},
    ),
    (
        ("WA", "electric", "zonal", "large", "hpwh"),
        {"consumption": 305.082743046608, "units": "kWh"},
    ),
    (
        ("WA", "electric", "central", "small", "hpwh"),
        {"consumption": 290.165926879946, "units": "kWh"},
    ),
    (
        ("WA", "electric", "central", "medium", "hpwh"),
        {"consumption": 310.055015102161, "units": "kWh"},
    ),
    (
        ("WA", "electric", "central", "large", "hpwh"),
        {"consumption": 310.055015102161, "units": "kWh"},
    ),
    (
        ("WA", "gas", "central", "small", "hpwh"),
        {"consumption": 290.165926879946, "units": "kWh"},
    ),
    (
        ("WA", "gas", "central", "medium", "hpwh"),
        {"consumption": 310.055015102161, "units": "kWh"},
    ),
    (
        ("WA", "gas", "central", "large", "hpwh"),
        {"consumption": 310.055015102161, "units": "kWh"},
    ),
    (
        ("WA", "gas", "zonal", "small", "hpwh"),
        {"consumption": 290.165926879946, "units": "kWh"},
    ),
    (
        ("WA", "gas", "zonal", "medium", "hpwh"),
        {"consumption": 305.082743046608, "units": "kWh"},
    ),
    (
        ("WA", "gas", "zonal", "large", "hpwh"),
        {"consumption": 305.082743046608, "units": "kWh"},
    ),
    (
        ("ID", "electric", "zonal", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("ID", "electric", "central", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("ID", "gas", "central", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("ID", "gas", "zonal", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("MT", "electric", "zonal", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("MT", "electric", "central", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("MT", "gas", "central", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("MT", "gas", "zonal", "all", "hpwh"),
        {"consumption": 339.888647435484, "units": "kWh"},
    ),
    (
        ("OR", "electric", "zonal", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("OR", "electric", "central", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("OR", "gas", "central", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("OR", "gas", "zonal", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("WA", "electric", "zonal", "small", "gas"),
        {"consumption": 26.402326389926, "units": "therms"},
    ),
    (
        ("WA", "electric", "zonal", "medium", "gas"),
        {"consumption": 27.759614109285, "units": "therms"},
    ),
    (
        ("WA", "electric", "zonal", "large", "gas"),
        {"consumption": 27.759614109285, "units": "therms"},
    ),
    (
        ("WA", "electric", "central", "small", "gas"),
        {"consumption": 26.402326389926, "units": "therms"},
    ),
    (
        ("WA", "electric", "central", "medium", "gas"),
        {"consumption": 28.212043349072, "units": "therms"},
    ),
    (
        ("WA", "electric", "central", "large", "gas"),
        {"consumption": 28.212043349072, "units": "therms"},
    ),
    (
        ("WA", "gas", "central", "small", "gas"),
        {"consumption": 26.402326389926, "units": "therms"},
    ),
    (
        ("WA", "gas", "central", "medium", "gas"),
        {"consumption": 28.212043349072, "units": "therms"},
    ),
    (
        ("WA", "gas", "central", "large", "gas"),
        {"consumption": 28.212043349072, "units": "therms"},
    ),
    (
        ("WA", "gas", "zonal", "small", "gas"),
        {"consumption": 26.402326389926, "units": "therms"},
    ),
    (
        ("WA", "gas", "zonal", "medium", "gas"),
        {"consumption": 27.759614109285, "units": "therms"},
    ),
    (
        ("WA", "gas", "zonal", "large", "gas"),
        {"consumption": 27.759614109285, "units": "therms"},
    ),
    (
        ("ID", "electric", "zonal", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("ID", "electric", "central", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("ID", "gas", "central", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("ID", "gas", "zonal", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("MT", "electric", "zonal", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("MT", "electric", "central", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("MT", "gas", "central", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
    (
        ("MT", "gas", "zonal", "all", "gas"),
        {"consumption": 30.926618787791, "units": "therms"},
    ),
]

NEEA_REFRIGERATOR_SAVINGS_PER_UNIT = 39.0
NEEA_DISHWASHER_SAVINGS_PER_UNIT = 58.67200000000000000000000
NEEA_CLOTHES_WASTER_SAVINGS_PER_UNIT = 114.35686359218700000000000

DRYER_TIER_2 = "tier2"
DRYER_TIER_2_LABEL = "Tier 2"
DRYER_TIER_3 = "tier3"
DRYER_TIER_3_LABEL = "Tier 3"

ESTAR = "estar"
ESTAR_LABEL = "ENERGY STAR®"
NONE_LABEL = "None"

NEEA_CLOTHES_DRYER_TIERS = (ESTAR_LABEL, DRYER_TIER_2_LABEL, DRYER_TIER_3_LABEL, NONE_LABEL)
NEEA_CLOTHES_DRYER_TIER_MAP = (
    (DRYER_TIER_2, DRYER_TIER_2_LABEL),
    (DRYER_TIER_3, DRYER_TIER_3_LABEL),
    (ESTAR, ESTAR_LABEL),
    (None, NONE_LABEL),
)

NEEA_CLOTHES_DRYER_TIER_SAVINGS_MAP = ((DRYER_TIER_2, 175.0), (DRYER_TIER_3, 350.0), (ESTAR, 125.0))

NEEA_MEDIUM_MEASURE_LIFE_PCT = 0.10
NEEA_COOLING_INTERNAL_GAINS_PCT = 0.75

BPA_KWH_PAYMENT_TIERS = (("short", 0.10), ("medium", 0.27), ("long", 0.45))
BPA_REFERENCE_HOME_CONSUMPTIONS = (
    ("WA", 17000.0),
    ("OR", 16000.0),
    ("ID", 18000.0),
    ("MT", 19000.0),
)

CLARK_REQUIREMENTS = {
    "title": "Clark PUD will only pay incentives for homes meeting ANY of the following criteria:",
    "requirements": [
        "Electrically heated homes with a percent improvement of 10% or greater.",
        "Gas heated homes with a percent improvement of 10% or greater and the "
        "gas utility is NW Natural",
    ],
}


PUGET_REQUIREMENTS = {
    "title": "Puget Sound Energy will only pay incentives for homes meeting "
    "ANY of the following criteria:",
    "requirements": [
        "Electrically heated homes in which PSE is the electric utility "
        "(gas utility – if applicable – may be a utility other than PSE).",
        "Gas heated homes in which Puget Sound Energy is both the electric and gas utility.",
    ],
}


CENTRAL_REQUIREMENTS = {
    "title": "Central Electric Cooperative will only pay incentives for homes meeting "
    "ALL of the following criteria:",
    "requirements": [
        "Electrically heated homes and a percent improvement of 10% or greater.",
    ],
}

PACIFIC_REQUIREMENTS = {
    "title": "Pacific Power will only pay incentives for homes in Washington state meeting "
    "ANY of the following criteria:",
    "requirements": [
        "Electrically heated homes with any percent improvement.",
        "Gas heated homes with electric cooling, a percent improvement of 10% or greater, "
        "and Cascade Natural Gas is the gas utility. Gas heating system must be gas furnace.",
    ],
}

IDAHO_REQUIREMENTS = {
    "title": "Idaho Power will only pay incentives for homes meeting "
    "ALL of the following criteria:",
    "requirements": [
        "Electrically heated homes with a percent improvement of 10% or greater. Heating "
        "system must be heat pump technology.",
    ],
}

BENTON_REQUIREMENTS = {
    "title": "Benton PUD will only pay incentives for homes meeting ALL of the following criteria:",
    "requirements": [
        "Electrically heated homes with a percent improvement of 10% or greater.",
    ],
}

BENTON_REA_REQUIREMENTS = {
    "title": "Benton REA will only pay incentives for homes meeting ALL of the following criteria:",
    "requirements": [
        "Electrically heated homes with a percent improvement of 10% or greater.",
    ],
}

INLAND_REQUIREMENTS = {
    "title": "Inland Power and Light will only pay incentives for homes meeting "
    "ALL of the following criteria:",
    "requirements": [
        "Electrically heated homes with an electric water heater and a percent "
        "improvement of 10% or greater.",
    ],
}

UTILITY_CITY_OF_RICHLAND_REQUIREMENTS = {
    "title": "City of Richland will only pay incentives "
    "for homes meeting ALL of the following criteria:",
    "requirements": [
        "Electrically heated homes with a percent improvement of 10% or greater.",
    ],
}

EWEB_REQUIREMENTS = {
    "title": " Eugene Water & Electric Board:",
    "requirements": [
        "Electrically heated homes with an electric water heater and a percent "
        "improvement of 10% or greater.",
        "Must be an Earth Advantage Certified Home. "
        "(Select certification level in the Annotations section below.)",
    ],
}

TACOMA_REQUIREMENTS = {
    "title": "Tacoma Public Utilities will pay incentives for homes meeting ALL of the following "
    "criteria:",
    "requirements": [
        "Electrically heated homes with an electric water heater and a percent "
        "improvement of 10% or greater.",
    ],
}

PENINSULA_POWER_REQUIREMENTS = {
    "title": "Peninsula Power & Light will pay incentives for homes meeting ALL of the following "
    "criteria:",
    "requirements": [
        "Electrically heated homes with a percent improvement of 10% or greater "
        "and the Electric Meter number is provided.",
    ],
}
