"""enumerations.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 11:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from enum import Enum, EnumMeta
from typing import Any
from django.db.models import TextChoices

log = logging.getLogger(__name__)


class Fireplace2020(Enum):
    NONE = "No fireplace"
    FE_LTE_49 = "<=49FE"
    FE_50_59 = "50-59FE"
    FE_60_69 = "60-69FE"
    FE_GTE_70 = ">=70FE"


class PrimaryHeatingEquipment2020(Enum):
    GAS_FIREPLACE = "Gas Fireplace"
    GAS_UNIT_HEATER = "Gas Unit Heater"
    GAS_FURNACE = "Gas Furnace"
    GAS_BOILER = "Gas Boiler"
    DUCTED_ASHP = "Electric Heat Pump \u2013 Air Source Ducted"
    MINI_SPLIT_NON_DUCTED = "Electric Heat Pump \u2013 Mini Split Non-Ducted"
    MINI_SPLIT_DUCTED = "Electric Heat Pump \u2013 Mini Split Ducted"
    MINI_SPLIT_MIXED = "Electric Heat Pump \u2013 Mini Split Mixed Ducted and Non-Ducted"
    GSHP = "Electric Heat Pump \u2013 Ground Source"
    ELECTRIC_RESISTANCE = "Electric Resistance"
    OTHER_GAS = "Other Gas"
    OTHER_ELECTRIC = "Other Electric"
    DFHP = "Dual Fuel Heat Pump"


ETO_2020_PRIMARY_HEATING_EQUIPMENT_TYPE_CHOICES = tuple(
    [("", "--")] + [(x.value, x.value) for x in PrimaryHeatingEquipment2020]
)


class GridHarmonization2020(Enum):
    NONE = "None"
    BASE = "Energy smart homes – Base package"
    STORAGE = "Energy smart homes – Base package + storage ready"
    WIRING = "Energy smart homes – Base package + advanced wiring"
    ALL = "Energy smart homes – Base package + storage ready + advanced wiring"


ETO_2020_GRID_HARMONIZATION_ELEMENT_CHOICES = tuple(
    [("", "No")] + [(x.value, x.value) for x in GridHarmonization2020]
)


# This is needed b/c our db contains ecobee4 already.
# Make sure you use _missing method in the actual Enun definition


class CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(self, name: str):
        try:
            _member_map = {x.lower(): y for x, y in self._member_map_.items()}
            if len(_member_map) == len(self._member_map_):
                return _member_map[name.lower()]
            else:
                raise KeyError("Duplicate values found unable to be case-insensitive")
        except KeyError:
            pass
        return super(CaseInsensitiveEnumMeta, self).__getitem__(name)


class CaseInsensitiveEnum(Enum, metaclass=CaseInsensitiveEnumMeta):
    @classmethod
    def _missing_(cls, value: object) -> Any:
        all_strings = all([isinstance(x.value, str) for x in cls])
        if all_strings and isinstance(value, str):
            # Make sure we can do this. No duplicate values
            if len([x for x in cls]) == len(list(set([x.value.lower() for x in cls]))):
                for member in cls:
                    if member.value.lower() == value.lower():
                        return member
            else:
                raise KeyError("Duplicate values found unable to be case-insensitive")


class SmartThermostatBrands2020(CaseInsensitiveEnum):
    NONE = "N/A"
    BRYANT = "Bryant Housewise WiFi model T6-WEM01-A"
    CARRIER = "Carrier Cor WiFi model T6-WEM01-A"
    ECOBEE3 = "Ecobee3 (not 'lite')"
    ECOBEE4 = "Ecobee4"
    ECOBEE_VOICE = "Ecobee w/ Voice Control"
    NEST_LEARNING = "NEST Learning Thermostat"
    NEST_E = "NEST Thermostat E"
    OTHER = "Other, add comment"


ETO_2020_SMART_THERMOSTAT_BRAND_CHOICES = tuple(
    [("", "N/A")] + [(x.value, x.value) for x in SmartThermostatBrands2020]
)


class AdditionalIncentives2020(Enum):
    NO = "No"
    AFFORDABLE_HOUSING = "Affordable housing (upload 610L to documents tab)"
    SOLAR_ELEMENTS = "Solar elements"
    ENERGY_SMART = "Energy smart homes (upload solar exemption to documents tab)"
    AFFORDABLE_HOUSING_AND_SOLAR = "Affordable housing and solar elements"
    AFFORDABLE_HOUSING_AND_ENERGY_SMART = (
        "Affordable housing and energy smart homes (upload solar exemption to documents tab)"
    )
    SOLAR_ELEMENTS_AND_ENERGY_SMART = "Solar elements and energy smart homes"
    ALL = "Affordable housing, energy smart homes and solar elements"


ETO_2020_ADDITIONAL_INCENTIVE_CHOICES = tuple(
    [("", "No")] + [(x.value, x.value) for x in AdditionalIncentives2020]
)


class SolarElements2020(Enum):
    SOLAR_READY = "Solar Ready"
    SOLAR_PV = "Solar PV"
    NON_ETO_SOLAR = "Non-Energy Trust Solar PV"
    NONE = "No"


ETO_2020_SOLAR_ELEMENTS_CHOICES = tuple(
    [("", "No")] + [(x.value, x.value) for x in SolarElements2020]
)


class BuilderChoices2020(Enum):
    DR_HORTON = "DR Horton"
    OTHER = "Other/None"


ETO_2020_BUILDER_CHOICES = tuple(
    [
        ("dr-horton-portland", BuilderChoices2020.DR_HORTON.value),
        ("other/none", BuilderChoices2020.OTHER.value),
    ]
)


class ClimateLocation(Enum):
    ASTORIA = "Astoria"
    BURNS = "Burns"
    EUGENE = "Eugene"
    MEDFORD = "Medford"
    NORTH_BEND = "NorthBend"
    PENDLETON = "Pendleton"
    PORTLAND = "Portland"
    REDMOND = "Redmond"
    SALEM = "Salem"


class HeatType(Enum):
    GAS = "Gas Heat"
    ELECTRIC = "Electric Heat"


class ElectricUtility(Enum):
    PACIFIC_POWER = "Pacific Power"
    PORTLAND_GENERAL = "Portland General"
    NONE = "Other/None"


class GasUtility(Enum):
    NW_NATURAL = "NW Natural"
    CASCADE = "Cascade"
    AVISTA = "Avista"
    NONE = "Other/None"


class QualifyingThermostat(Enum):
    NONE = "No Qualifying Smart Thermostat"
    DUCTED_FURNACE = "Yes-Ducted Gas Furnace"
    DUCTED_ASHP = "Yes-Ducted Air Source Heat Pump"


class PNWUSStates(Enum):
    ID = "ID"
    MT = "MT"
    OR = "OR"
    WA = "WA"


class YesNo(Enum):
    YES = "Yes"
    NO = "No"


class ProjectTrackerSubmissionStatus(TextChoices):
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
