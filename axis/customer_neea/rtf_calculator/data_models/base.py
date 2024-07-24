"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "6/26/21 11:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import FuelType

from axis.customer_neea.rtf_calculator.base import RTFBase
from axis.remrate_data.strings import FUEL_TYPES

log = logging.getLogger(__name__)


class SimulatedInputBase(RTFBase):
    """Base class for Simulated data"""

    def __init__(self, **kwargs):  # pylint: disable=too-many-statements  # noqa: MC0001
        self.is_improved = kwargs.get("is_improved", False)

        simulation = kwargs.get("simulation", {})

        self.heating_therms = 0.0
        try:
            _heating_therms = kwargs.get("heating_therms", simulation.get("heating_therms", 0.0))
            self.heating_therms = float(_heating_therms)
        except TypeError:
            pass

        self.heating_kwh = 0.0
        try:
            _heating_kwh = kwargs.get("heating_kwh", simulation.get("heating_kwh", 0.0))
            self.heating_kwh = float(_heating_kwh)
        except TypeError:
            pass

        self.cooling_kwh = 0.0
        try:
            _cooling_kwh = kwargs.get("cooling_kwh", simulation.get("cooling_kwh", 0.0))
            self.cooling_kwh = float(_cooling_kwh)
        except TypeError:
            pass

        self.primary_heating_type = None
        try:
            _pri_heat = kwargs.get("primary_heating_type", simulation.get("primary_heating_type"))
            self.primary_heating_type = _pri_heat
        except TypeError:
            pass

        self.primary_cooling_type = None
        try:
            _pri_cool = kwargs.get("primary_cooling_type", simulation.get("primary_cooling_type"))
            self.primary_cooling_type = _pri_cool
        except TypeError:
            pass

        self.primary_cooling_fuel = None
        if self.primary_cooling_type:
            try:
                _c_fuel = kwargs.get("primary_cooling_fuel", simulation.get("primary_cooling_fuel"))
                self.primary_cooling_fuel = _c_fuel
            except TypeError:
                pass
        assert self.primary_cooling_fuel is None or self.primary_cooling_fuel.lower() in [
            y.lower() for y in dict(FUEL_TYPES).values()
        ]

        is_hp = kwargs.get(
            "is_primary_heating_is_heat_pump", simulation.get("is_primary_heating_is_heat_pump")
        )
        if is_hp is not None:
            raise KeyError("This has changed - Please specify heating type instead")

        self.is_primary_heating_is_heat_pump = False
        if self.primary_heating_type:
            if (
                "heat pump" in self.primary_heating_type.lower()
                or "ashp" in self.primary_heating_type.lower()
                or "gshp" in self.primary_heating_type.lower()
            ):
                self.is_primary_heating_is_heat_pump = True

        self.total_consumption_therms = 0.0
        self.total_consumption_kwh = 0.0

        try:
            val = kwargs.get(
                "total_consumption_kwh",
                simulation.get("total_consumption_kwh", self.cooling_kwh + self.heating_kwh),
            )
            self.total_consumption_kwh = float(val)
        except TypeError:
            pass

        try:
            val = kwargs.get(
                "total_consumption_therms",
                simulation.get("total_consumption_therms", self.heating_therms),
            )
            self.total_consumption_therms = float(val)
        except TypeError:
            pass

    @property
    def square_footage(self):
        """Returns the square footage"""

        return None

    def _get_total_consumption_mbtu(self):
        """Get total consumption mbtue"""
        return self.kwh_to_mbtu(self.total_consumption_kwh) + self.therms_to_mbtu(
            self.total_consumption_therms
        )

    def get_udrh_percent_improvement(self, code_data):
        """Will progmatically get the percent improvement"""
        assert self.is_improved
        assert code_data.is_improved is False
        as_built = self._get_total_consumption_mbtu()
        code = code_data._get_total_consumption_mbtu()  # pylint: disable=protected-access
        try:
            return (code - as_built) / code
        except ZeroDivisionError:
            return 0.0


class RTFSimulatedInput(SimulatedInputBase):
    """RTF Simulated Data"""

    def __init__(self, **kwargs):
        super(RTFSimulatedInput, self).__init__(**kwargs)

        simulation = kwargs.get("simulation", {})

        # FOR NEEA THIS IS DTERMINED VIA WATER_HEATER_TIER!!
        self.primary_water_heating_type = None
        try:
            val = kwargs.get(
                "primary_water_heating_type", simulation.get("primary_water_heating_type")
            )
            self.primary_water_heating_type = val
        except TypeError:
            pass
        assert self.primary_water_heating_type in [None, "gas", "hpwh", "electric resistance"]

        self.qty_heat_pump_water_heaters = 0
        try:
            val = kwargs.get(
                "qty_heat_pump_water_heaters", simulation.get("qty_heat_pump_water_heaters", 0)
            )
            self.qty_heat_pump_water_heaters = int(val)
        except TypeError:
            pass
        assert self.qty_heat_pump_water_heaters >= 0, "You can't have negative water heaters"


class NEEASimulatedInput(SimulatedInputBase):
    """NEEA Simulated data"""

    def __init__(self, **kwargs):
        super(NEEASimulatedInput, self).__init__(**kwargs)

        simulation = kwargs.get("simulation", {})

        self.primary_water_heating_efficiency = 0.0
        try:
            val = kwargs.get(
                "primary_water_heating_efficiency",
                simulation.get("primary_water_heating_efficiency", 0.0),
            )
            self.primary_water_heating_efficiency = val
        except TypeError:
            pass

        self.clothes_dryer_fuel = None
        try:
            val = kwargs.get("clothes_dryer_fuel", simulation.get("clothes_dryer_fuel"))
            self.clothes_dryer_fuel = val
        except TypeError:
            pass
        assert self.clothes_dryer_fuel in [None, FuelType.NATURAL_GAS, FuelType.ELECTRIC]
