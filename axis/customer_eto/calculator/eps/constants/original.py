"""calc_testing.py: Django """


import logging
import datetime

from django.conf import settings

__author__ = "Steven Klass"
__date__ = "10/3/13 4:24 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


EPS_CALCULATOR_VERSION = datetime.date(2015, 12, 1)

ETO_MININUM_RATER_INCENTIVE = 300

DEFAULT_UTILITY_NAME = "other/none"

ETO_2019_FUEL_RATES = [
    ("portland-electric", "PGE-Dec2018"),
    ("pacific-power", "PAC-Dec2018"),
    ("central-electric", "CEC-Dec2018"),
    ("utility-city-of-ashland", "Ashland-Dec2018"),
    ("clark-pud", "ClarkPUD-Dec2018"),
    ("utility-umatilla-electric-co-op", "Umatilla-Dec2018"),
    ("utility-cowlitz-county-pud", "CowlitzPUD-Dec2018"),
    ("utility-columbia-basin-electric-co-op", "ColBasinCoop-Dec 2018"),
    ("utility-columbia-river-pud", "ColRiverPUD-Dec2018"),
    ("utility-forest-grove-light-department", "ForestGrove-Dec2018"),
    ("utility-hermiston-energy-services", "Hermiston-Dec2018"),
    ("utility-eugene-water-electric-board", "EWEB-Dec2018"),
    ("avista", "Avista-Dec2018"),
    ("nw-natural-gas", "NWN_OR-Dec2018"),
    ("cascade-gas", "Cascade-Dec2018"),
]
ETO_2019_FUEL_RATES_WA_OVERRIDE = [
    ("nw-natural-gas", "NWN_WA-Dec2018"),
]

ALLOWED_ELECTRIC_UTILITY_NAMES = ("pacific power", "portland general", DEFAULT_UTILITY_NAME)
ALLOWED_GAS_UTILITY_NAMES = ("nw natural", "cascade", DEFAULT_UTILITY_NAME)
ALLOWED_HEAT_TYPES = ("gas heat", "heat pump")

EPS_VALID_LOCATIONS = ["portland", "medford", "redmond"]
LOCATION_TRANSLATION = {}
EPS_VALID_PATHWAYS = ["path 1", "path 2", "path 3", "path 4", "path 5", "pct"]
EPS_VALID_HEAT_TYPES = ALLOWED_HEAT_TYPES
EPS_VALID_ELECTRIC_UTILITY_COMPANIES = ALLOWED_ELECTRIC_UTILITY_NAMES
EPS_VALID_GAS_UTILITY_COMPANIES = ALLOWED_GAS_UTILITY_NAMES

EPS_ELECTRIC_SPACE_HEAT_FUEL_WEIGHT = {"portland": 1, "medford": 1, "redmond": 1}
EPS_ELECTRIC_HOT_WATER_FUEL_WEIGHT = {"portland": 1, "medford": 1, "redmond": 1}
if settings.ETO_VARIABLE_RATES:
    EPS_ELECTRIC_SPACE_HEAT_FUEL_WEIGHT = {"portland": 2.38, "medford": 1.89, "redmond": 1.59}
    EPS_ELECTRIC_HOT_WATER_FUEL_WEIGHT = {"portland": 1.30, "medford": 1.30, "redmond": 1.30}

EPS_CODE_HEATING_AJUSTMENT_FACTORS = {"portland": 1.54, "medford": 1.82, "redmond": 2.06}
EPS_CODE_COOLING_AJUSTMENT_FACTORS = {"portland": 0.35, "medford": 0.63, "redmond": 0.34}
EPS_IMPROVED_HEATING_AJUSTMENT_FACTORS = {"portland": 1.32, "medford": 1.63, "redmond": 1.91}
EPS_IMPROVED_COOLING_AJUSTMENT_FACTORS = {"portland": 0.39, "medford": 0.59, "redmond": 0.44}
EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR = {
    "natural gas": 11.7,
    "pacific power": 2.08,
    "portland general": 1.06,
    "bpa": 0.12,
}
EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_WA = EPS_POUNDS_OF_CARBON_PER_KWH_BY_COMPANY_OR

EPS_FULL_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.0000,
        "electric_pct": 0,
        "gas_pct": 0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 600.00,
        "electric_pct": 0.44,
        "gas_pct": 0.56,
        "electric_waml": 23,
        "gas_waml": 40,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 1200.0,
        "electric_pct": 0.33,
        "gas_pct": 0.67,
        "electric_waml": 23,
        "gas_waml": 34,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 2000.0,
        "electric_pct": 0.40,
        "gas_pct": 0.60,
        "electric_waml": 33,
        "gas_waml": 37,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 4",
        "base_incentive": 4000.0,
        "electric_pct": 0.39,
        "gas_pct": 0.61,
        "electric_waml": 27,
        "gas_waml": 38,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 5",
        "base_incentive": 5000.0,
        "electric_pct": 0.22,
        "gas_pct": 0.78,
        "electric_waml": 14,
        "gas_waml": 38,
    },
]

EPS_FULL_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.0000,
        "electric_pct": 0,
        "gas_pct": 0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 600.00,
        "electric_pct": 0.88,
        "gas_pct": 0.12,
        "electric_waml": 32,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 1200.0,
        "electric_pct": 0.55,
        "gas_pct": 0.45,
        "electric_waml": 29,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 2000.0,
        "electric_pct": 0.65,
        "gas_pct": 0.35,
        "electric_waml": 33,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 4",
        "base_incentive": 4000.0,
        "electric_pct": 0.68,
        "gas_pct": 0.32,
        "electric_waml": 35,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 5",
        "base_incentive": 5000.0,
        "electric_pct": 0.74,
        "gas_pct": 0.26,
        "electric_waml": 37,
        "gas_waml": 12,
    },
]

EPS_GAS_ONLY_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.0000,
        "electric_pct": 0,
        "gas_pct": 0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 400.00,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 40,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 800.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 34,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 1300.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 37,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 4",
        "base_incentive": 2600.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 38,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 5",
        "base_incentive": 3250.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 38,
    },
]

EPS_GAS_ONLY_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.00,
        "electric_pct": 0,
        "gas_pct": 0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 100.00,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 0.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 0.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 4",
        "base_incentive": 0.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 12,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 5",
        "base_incentive": 0.0,
        "electric_pct": 0,
        "gas_pct": 1,
        "electric_waml": 0,
        "gas_waml": 12,
    },
]

EPS_ELECTRIC_ONLY_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.0000,
        "electric_pct": 0,
        "gas_pct": 0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 200.00,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 23,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 400.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 23,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 700.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 33,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 4",
        "base_incentive": 1400.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 27,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 5",
        "base_incentive": 1750.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 14,
        "gas_waml": 0,
    },
]

EPS_ELECTRIC_ONLY_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.00,
        "electric_pct": 0,
        "gas_pct": 0,
        "electric_waml": None,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 600.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 32,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 1200.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 29,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 2000.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 33,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 4",
        "base_incentive": 4000.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 35,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 5",
        "base_incentive": 5000.0,
        "electric_pct": 1,
        "gas_pct": 0,
        "electric_waml": 37,
        "gas_waml": 0,
    },
]

EPS_SIMILAR_SIZE_REGRESSIVE_VALUES = [
    {
        "location": "portland",
        "regression_values": {
            "electric_home_kwh": {"constant": 23520, "slope": 5.54},
            "gas_home_kwh": {"constant": 4700, "slope": 2.39},
            "gas_home_therms": {"constant": 271, "slope": 0.23},
        },
    },
    {
        "location": "medford",
        "regression_values": {
            "electric_home_kwh": {"constant": 20806, "slope": 7.74},
            "gas_home_kwh": {"constant": 4700, "slope": 2.39},
            "gas_home_therms": {"constant": 271, "slope": 0.23},
        },
    },
    {
        "location": "redmond",
        "regression_values": {
            "electric_home_kwh": {"constant": 19320, "slope": 9.96},
            "gas_home_kwh": {"constant": 2397, "slope": 3.29},
            "gas_home_therms": {"constant": 192, "slope": 0.3},
        },
    },
]

EPS_SIMILAR_SIZE_CARBON_REGRESSIVE_VALUES = [
    {
        "location": "portland",
        "regression_values": {
            "electric_home_kwh": {"constant": 11874, "slope": 3.52},
            "gas_home_kwh": {"constant": 4700, "slope": 2.39},
            "gas_home_therms": {"constant": 271, "slope": 0.23},
        },
    },
    {
        "location": "medford",
        "regression_values": {
            "electric_home_kwh": {"constant": 11141, "slope": 5.08},
            "gas_home_kwh": {"constant": 4700, "slope": 2.39},
            "gas_home_therms": {"constant": 271, "slope": 0.23},
        },
    },
    {
        "location": "redmond",
        "regression_values": {
            "electric_home_kwh": {"constant": 9978, "slope": 5.45},
            "gas_home_kwh": {"constant": 2397, "slope": 3.29},
            "gas_home_therms": {"constant": 192, "slope": 0.3},
        },
    },
]

EPS_INCREMENTAL_INCENTIVE_VALUE = 25
EPS_VERIFIER_MULTIPLIER = 0.20

EPS_VALID_SMART_THERMOMETER_CHOICES = {
    "no qualifying smart thermostat": (False, None),
    "yes-ducted gas furnace": (False, None),
    "yes-ducted air source heat pump": (False, None),
}

EPS_OR_SAVINGS_PCT = {
    "gas_smart_tstat_savings_pct": 0.0,
    "electric_smart_tstat_savings_pct": 0.0,
    "gas_showerhead_savings_pct": 0.0,
    "electric_showerhead_savings_pct": 0.0,
}
EPS_WA_SAVINGS_PCT = EPS_OR_SAVINGS_PCT
