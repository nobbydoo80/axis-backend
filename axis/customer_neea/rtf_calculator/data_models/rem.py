"""rem.py - Axis"""

__author__ = "Steven K"
__date__ = "6/26/21 11:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import FuelType

from axis.customer_neea.rtf_calculator.data_models.base import SimulatedInputBase
from axis.remrate_data.strings import UTILITY_UNITS

log = logging.getLogger(__name__)


class RemModeledInputBase(SimulatedInputBase):
    """Simulation input for the calculator"""

    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        self.is_improved = kwargs.get("is_improved", False)
        self.simulation = kwargs.get("simulation")
        self._fuel_summary_values = None

    @property
    def _fuel_summary_values_base(self):
        if not getattr(self, "_fuel_summary_values"):
            self._fuel_summary_values = self.simulation.fuelsummary_set.values()
        return self._fuel_summary_values

    def _fuel_summary_values_by_unit(self, unit="kwh"):
        unit_no = next((x[0] for x in UTILITY_UNITS if unit.lower() == x[1].lower()))
        return [x for x in self._fuel_summary_values_base if x["fuel_units"] == unit_no]

    @property
    def heating_therms(self):
        """Return the total heating therms"""
        vals = self._fuel_summary_values_by_unit("therms")
        return float(sum([x["heating_consumption"] for x in vals if x["heating_consumption"] > 0]))

    @property
    def heating_kwh(self):
        """Return the total heating kwh"""
        vals = self._fuel_summary_values_by_unit("kwh")
        return float(sum([x["heating_consumption"] for x in vals if x["heating_consumption"] > 0]))

    @property
    def cooling_kwh(self):
        """Return the total cooling kwh"""
        vals = self._fuel_summary_values_by_unit("kwh")
        return float(sum([x["cooling_consumption"] for x in vals if x["cooling_consumption"] > 0]))

    @property
    def total_consumption_kwh(self):
        """Return the total consumption kwh"""
        vals = self._fuel_summary_values_by_unit("kwh")
        data = float(
            sum(
                [
                    x["total_consumption"]
                    for x in vals
                    if x["total_consumption"] and x["total_consumption"] > 0
                ]
            )
        )
        keys = [
            "heating_consumption",
            "cooling_consumption",
            "hot_water_consumption",
            "lights_and_appliances_consumption",
        ]
        if data == 0.0:
            for key in keys:
                data += float(sum([x[key] for x in vals if x[key] > 0]))
        return data

    @property
    def total_consumption_therms(self):
        """Return the total consumption therms"""
        vals = self._fuel_summary_values_by_unit("therms")
        data = float(
            sum(
                [
                    x["total_consumption"]
                    for x in vals
                    if x["total_consumption"] and x["total_consumption"] > 0
                ]
            )
        )
        keys = [
            "heating_consumption",
            "cooling_consumption",
            "hot_water_consumption",
            "lights_and_appliances_consumption",
        ]
        if data == 0.0:
            for key in keys:
                data += float(sum([x[key] for x in vals if x[key] > 0]))
        return data

    @property
    def qty_heat_pump_water_heaters(self):
        """Return the total number of heat pump water heaters"""
        return self.simulation.hotwaterheater_set.filter(type__in=[4, 5]).count()

    @property
    def dominant_equipment(self):
        """Return the dominant equipment"""
        if hasattr(self, "_dominant_equipment"):
            return self._dominant_equipment  # pylint: disable=access-member-before-definition
        self._dominant_equipment = self.simulation.installedequipment_set.get_dominant_values(
            self.simulation.id
        )[self.simulation.id]
        return self._dominant_equipment

    @property
    def primary_heating_type(self):
        """Return the dominant heating fuel"""
        return self.dominant_equipment["dominant_heating"]["type"]

    @property
    def primary_cooling_type(self):
        """Return the dominant cooling type"""
        return self.dominant_equipment["dominant_cooling"]["type"]

    @property
    def primary_cooling_fuel(self):
        """Return the dominant cooling fuel"""
        return self.dominant_equipment["dominant_cooling"]["fuel"]

    @property
    def is_primary_heating_is_heat_pump(self):
        """Is the dominant heating type a heat pump"""

        if self.primary_heating_type and "heat pump" in self.primary_heating_type.lower():
            return True
        return False

    @property
    def primary_water_heating_type(self):
        """Return the dominant hot water heating type"""

        hot_water = self.dominant_equipment["dominant_hot_water"]
        if "gas" in hot_water["fuel"].lower():
            return "gas"
        elif "heat pump" in hot_water["fuel"]["type"].lower():
            return "hpwh"
        return "electric resistance"

    @property
    def primary_water_heating_fuel(self):
        hot_water = self.dominant_equipment["dominant_hot_water"]
        if "gas" in hot_water["fuel"].lower():
            return FuelType.NATURAL_GAS
        if "electric" in hot_water["fuel"].lower():
            return FuelType.ELECTRIC
        return hot_water["fuel"]

    @property
    def clothes_dryer_fuel(self):
        """Return the dominant heating fuel"""
        base = self.simulation.lightsandappliance.get_clothes_dryer_fuel_display()
        if base.lower() == "electric":
            return FuelType.ELECTRIC
        elif base.lower() == "propane":
            return FuelType.PROPANE
        elif base.lower() == "natural gas":
            return FuelType.NATURAL_GAS

    @property
    def square_footage(self):
        """Return the conditioned area"""

        return self.simulation.building.building_info.conditioned_area

    def get_udrh_percent_improvement(self):
        assert self.is_improved, "Only allowed on as designed"
        return self.simulation.results.udrh_percent_improvement


class RTFRemModeledInput(RemModeledInputBase):
    """Simulation input for the RTF Calculator"""

    pass


class NEEARemModeledInput(RemModeledInputBase):
    """Simulation input for the NEEA Calculator"""

    pass
