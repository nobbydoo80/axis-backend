"""simulation.py - Axis"""

__author__ = "Steven K"
__date__ = "6/26/21 11:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import FuelType, HotWaterEfficiencyUnit
from simulation.models import Simulation

from .base import SimulatedInputBase
from ..base import RTFInputException

log = logging.getLogger(__name__)


class SimulationModeledInputBase(SimulatedInputBase):
    """Simulation input for the calculator"""

    def __init__(self, **kwargs):
        self.is_improved = kwargs.get("is_improved", False)
        self.simulation = kwargs.get("simulation")

        assert isinstance(self.simulation, Simulation)

        ref_types_available = list(self.simulation.analyses.values_list("type", flat=True))

        # This will need to get revisited when we get to ekotrope b/c there could conceivably
        # send us all of them..  Then we will need to figure out which one?  The way ETO handles
        # this is with a reference home type.  That could help us here too.
        if len(ref_types_available) != 2:
            raise RTFInputException(
                f"We expect at least two analyses.  We have {len(ref_types_available)}."
            )

        self.improved_analysis = self.simulation.analyses.filter(type__contains="_design").last()
        self.reference_analysis = self.simulation.analyses.filter(
            type__contains="_reference"
        ).last()

        self.analysis = self.improved_analysis if self.is_improved else self.reference_analysis

    @property
    def heating_therms(self):
        """Return the total heating therms"""
        return self.analysis.fuel_usages.all().gas_heating_consumption_therms

    @property
    def heating_kwh(self):
        """Return the total heating kwh"""
        return self.analysis.fuel_usages.all().electric_heating_consumption_kwh

    @property
    def cooling_kwh(self):
        """Return the total cooling kwh"""
        return self.analysis.fuel_usages.all().electric_cooling_consumption_kwh

    @property
    def total_consumption_therms(self):
        return self.analysis.fuel_usages.all().total_gas_consumption_therms

    @property
    def total_consumption_kwh(self):
        return self.analysis.fuel_usages.all().total_electric_consumption_kwh

    @property
    def qty_heat_pump_water_heaters(self):
        """Return the total number of heat pump water heaters"""
        return self.simulation.water_heaters.heat_pumps().count()

    @property
    def primary_heating_type(self):
        """Return the dominant heating fuel"""
        return self.simulation.dominant_heating_equipment.get_basic_type_display(False)

    @property
    def primary_heating_fuel(self):
        """Return the dominant heating fuel"""
        return self.simulation.dominant_heating_equipment.get_fuel_display()

    @property
    def is_primary_heating_is_heat_pump(self):
        """Is the dominant heating type a heat pump"""
        return "ASHP" in self.primary_heating_type or "GSHP" in self.primary_heating_type

    @property
    def primary_cooling_type(self):
        """Return the primary cooling type"""
        try:
            return self.simulation.dominant_cooling_equipment.get_basic_type_display(False)
        except AttributeError:
            return None

    @property
    def primary_cooling_fuel(self):
        """Return the dominant heating fuel"""
        try:
            return self.simulation.dominant_cooling_equipment.get_fuel_display()
        except AttributeError:
            return None

    @property
    def primary_water_heating_type(self):
        """Return the dominant heating fuel"""
        equipment = self.simulation.dominant_water_heating_equipment
        if equipment.fuel == FuelType.NATURAL_GAS:
            return "gas"
        if equipment.is_heat_pump:
            return "hpwh"
        return "electric resistance"

    @property
    def primary_water_heating_fuel(self):
        return self.simulation.dominant_water_heating_equipment.fuel

    @property
    def primary_water_heating_efficiency(self):
        """Return the dominant heating fuel"""
        equipment = self.simulation.dominant_water_heating_equipment.equipment
        if equipment.efficiency_unit == HotWaterEfficiencyUnit.ENERGY_FACTOR:
            return equipment.efficiency

    @property
    def clothes_dryer_fuel(self):
        """Return the dominant heating fuel"""
        return self.simulation.appliances.clothes_dryer_fuel

    @property
    def square_footage(self):
        """Return the conditioned area"""
        return self.simulation.conditioned_area

    def get_udrh_percent_improvement(self):
        assert self.is_improved, "Only allowed on as designed"
        return self.improved_analysis.get_percent_improvement_over(self.reference_analysis) / 100.0


class RTFSimModeledInput(SimulationModeledInputBase):
    """Simulation input for the RTF Calculator"""

    pass


class NEEASimModeledInput(SimulationModeledInputBase):
    """Simulation input for the NEEA Calculator"""

    pass
