"""calc_testing.py: Django """


import logging
import datetime

__author__ = "Autumn Valenta"
__date__ = "11/10/15 1:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


from .original import *

ETO_MININUM_RATER_INCENTIVE = 0

ALLOWED_GAS_UTILITY_NAMES = "nw natural"
EPS_VALID_LOCATIONS = ["portland"]

EPS_FULL_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.000,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 300.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 25,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 400.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 31,
    },
    {
        "performance_target": 0.30,
        "pathway": "path 3",
        "base_incentive": 500.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 35,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 4",
        "base_incentive": 700.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 38,
    },
    {
        "performance_target": 0.45,
        "pathway": "path 5",
        "base_incentive": 900.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 39,
    },
]

EPS_FULL_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.000,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.15,
        "pathway": "path 2",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.30,
        "pathway": "path 4",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 5",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
]

EPS_GAS_ONLY_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.000,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 300.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 25,
    },
    {
        "performance_target": 0.20,
        "pathway": "path 2",
        "base_incentive": 400.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 31,
    },
    {
        "performance_target": 0.30,
        "pathway": "path 3",
        "base_incentive": 500.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 35,
    },
    {
        "performance_target": 0.40,
        "pathway": "path 4",
        "base_incentive": 700.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 38,
    },
    {
        "performance_target": 0.45,
        "pathway": "path 5",
        "base_incentive": 900.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 39,
    },
]

EPS_GAS_ONLY_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.000,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.15,
        "pathway": "path 2",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.30,
        "pathway": "path 4",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 5",
        "base_incentive": 150.0,
        "electric_pct": 0.0,
        "gas_pct": 1.0,
        "electric_waml": 0,
        "gas_waml": 15,
    },
]

EPS_ELECTRIC_ONLY_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.15,
        "pathway": "path 2",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.30,
        "pathway": "path 4",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 5",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
]

EPS_ELECTRIC_ONLY_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS = [
    {
        "performance_target": 0.00,
        "pathway": "code",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": None,
        "gas_waml": None,
    },
    {
        "performance_target": 0.10,
        "pathway": "path 1",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.15,
        "pathway": "path 2",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.25,
        "pathway": "path 3",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.30,
        "pathway": "path 4",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
    {
        "performance_target": 0.35,
        "pathway": "path 5",
        "base_incentive": 0.0,
        "electric_pct": 0.0,
        "gas_pct": 0.0,
        "electric_waml": 0,
        "gas_waml": 0,
    },
]
