__author__ = "Steven K"
__date__ = "09/11/2021 09:28 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from collections import namedtuple
from enum import Enum

round_value = 2

SimData = namedtuple(
    "SimData",
    [
        "heating_therms",
        "heating_kwh",
        "cooling_kwh",
        "hot_water_therms",
        "hot_water_kwh",
        "solar_hot_water_therms",
        "solar_hot_water_kwh",
        "lights_and_appliance_therms",
        "lights_and_appliance_kwh",
        "pv_kwh",
        "total_therms",
        "total_kwh",
        "electric_cost",
        "gas_cost",
    ],
)

CodeData = namedtuple(
    "CodeData",
    [
        "heating_therms",
        "heating_kwh",
        "cooling_kwh",
        "hot_water_therms",
        "hot_water_kwh",
        "lights_and_appliance_therms",
        "lights_and_appliance_kwh",
        "fireplace_therms",
    ],
)

EPSCalculationData = namedtuple(
    "EPSCalculationData",
    [
        "total_therms",
        "total_kwh",
        "total_mbtu",
    ],
)

CarbonCalculationData = namedtuple(
    "CarbonCalculationData",
    [
        "total_therms",
        "total_kwh",
        "carbon_score",
    ],
)

ConsumptionCalculationData = namedtuple(
    "ConsumptionCalculationData",
    ["total_therms", "total_kwh", "total_mbtu"],
)


ImprovedData = namedtuple(
    "ImprovedData",
    [
        "heating_therms",
        "gas_thermostat_savings",
        "heating_kwh",
        "electric_thermostat_savings",
        "cooling_kwh",
        "cooling_thermostat_savings",
        "hot_water_therms",
        "hot_water_kwh",
        "lights_and_appliance_therms",
        "lights_and_appliance_kwh",
        "fireplace_therms",
        "solar_hot_water_therms",
        "solar_hot_water_kwh",
        "pv_kwh",
    ],
)

ImprovementData = namedtuple("ImprovementData", ["therms", "kwh", "mbtu"])

ImprovementSummmaryData = namedtuple(
    "ImprovementData",
    [
        "code",
        "improved",
        "savings",
        "percent_improvement_breakout",
        "floored_improvement_breakout",
        "percent_improvement",
    ],
)

FuelAllocationIncentive = namedtuple(
    "FuelAllocationIncentive",
    ["allocation", "incentive", "fuel", "utility", "load_profile", "waml"],
)

AllocationIncentive = namedtuple(
    "AllocationIncentive",
    ["electric", "gas", "allocation", "incentive", "waml"],
)


LoadProfile = namedtuple(
    "LoadProfile",
    [
        "electric_load_profile",
        "gas_load_profile",
        "weighted_avg_measure_life",
        "electric_allocation",
        "gas_allocation",
    ],
)

Projected = namedtuple(
    "Projected", ["location", "electric_home_kwh", "gas_home_kwh", "gas_home_therms"]
)

CarbonData = namedtuple(
    "CarbonData", ["location", "electric_utility", "electric_score", "gas_utility", "gas_score"]
)


class HomePath(Enum):
    PATH_1 = "Path 1"
    PATH_2 = "Path 2"
    PATH_3 = "Path 3"
    PATH_4 = "Path 4"
    UNDEFINED = "-"


class HomeSubType(Enum):
    GHEW = "GH+EW"
    GHGW = "GH+GW"
    EHEW = "EH+EW"
    EHGW = "EH+GW"
    OTHER = "Other"


class ElectricLoadProfile(Enum):
    RESIDENTIAL_LIGHTING = "Res Lighting"
    RESIDENTIAL_ASHP = "Res Air Source HP"
    RESIDENTIAL_SPACE_CONDITIONING = "Res Space Conditioning"
    RESIDENTIAL_CENTRAL_AC = "Res Central AC"
    RESIDENTIAL_WATER_HEAT = "Res Water Heat"
    NONE = "None"


class GasLoadProfile(Enum):
    RESIDENTIAL_HEATING = "Res Heating"
    HOT_WATER = "DHW"
    NONE = "None"
