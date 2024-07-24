"""data_models.py: Django eps"""


import logging

from collections import OrderedDict


try:
    from .base import EPSBase
    from .calculations import Calculations2020
    from .calculations import Calculations2019
    from .calculations import Calculations2018
    from .calculations import Calculations2017
    from .calculations import Calculations
except (ValueError, ImportError):
    from axis.customer_eto.calculator.eps import EPSBase
    from axis.customer_eto.calculator.eps.calculations import (
        Calculations,
        Calculations2017,
        Calculations2018,
        Calculations2019,
        Calculations2020,
    )

__author__ = "Steven Klass"
__date__ = "10/26/16 16:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SimulatedInput(EPSBase):
    """A container for a fake simulation"""

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

        self.hot_water_therms = 0.0
        try:
            _h2o_therms = kwargs.get("hot_water_therms", simulation.get("hot_water_therms", 0.0))
            self.hot_water_therms = float(_h2o_therms)
        except TypeError:
            pass

        self.hot_water_kwh = 0.0
        try:
            _h2o_kwh = kwargs.get("hot_water_kwh", simulation.get("hot_water_kwh", 0.0))
            self.hot_water_kwh = float(_h2o_kwh)
        except TypeError:
            pass

        self.lights_and_appliances_therms = 0.0
        try:
            _lna_therms = kwargs.get(
                "lights_and_appliances_therms", simulation.get("lights_and_appliances_therms", 0.0)
            )
            self.lights_and_appliances_therms = float(_lna_therms)
        except TypeError:
            pass

        self.lights_and_appliances_kwh = 0.0
        try:
            _lna_kwh = kwargs.get(
                "lights_and_appliances_kwh", simulation.get("lights_and_appliances_kwh", 0.0)
            )
            self.lights_and_appliances_kwh = float(_lna_kwh)
        except TypeError:
            pass

        self.pv_kwh = 0.0
        try:
            self.pv_kwh = float(kwargs.get("pv_kwh", simulation.get("pv_kwh", 0.0)))
        except TypeError:
            pass
        try:
            _pv_kwh = kwargs.get(
                "generated_solar_pv_kwh", simulation.get("generated_solar_pv_kwh", 0.0)
            )
            self.generated_solar_pv_kwh = float(_pv_kwh)
        except TypeError:
            self.generated_solar_pv_kwh = None

        # These need to align legacy purposes they wouldn't
        if self.pv_kwh == 0.0 and self.generated_solar_pv_kwh:
            self.pv_kwh = self.generated_solar_pv_kwh
        if self.generated_solar_pv_kwh == 0.0 and self.pv_kwh:
            self.generated_solar_pv_kwh = self.pv_kwh

        self.electric_cost = 0.0
        try:
            _ele_cost = kwargs.get("electric_cost", simulation.get("electric_cost", 0.0))
            self.electric_cost = float(_ele_cost)
        except TypeError:
            pass

        self.gas_cost = 0.0
        try:
            _gas_cost = kwargs.get("gas_cost", simulation.get("gas_cost", 0.0))
            self.gas_cost = float(_gas_cost)
        except TypeError:
            pass

        _solar_therms = kwargs.get(
            "solar_hot_water_therms", simulation.get("solar_hot_water_therms", 0.0)
        )
        self.solar_hot_water_therms = float(_solar_therms)
        solar_kwh = kwargs.get("solar_hot_water_kwh", simulation.get("solar_hot_water_kwh", 0.0))
        self.solar_hot_water_kwh = float(solar_kwh)

        # These are NOT used and only used for testing to make sure that our values add correctly
        self._reference_non_solar_hot_water_therms = (
            self.hot_water_therms + self.solar_hot_water_therms
        )
        self._reference_non_solar_hot_water_kwh = self.hot_water_kwh + self.solar_hot_water_kwh

        self.has_solar_hot_water = self.solar_hot_water_kwh > 0 or self.solar_hot_water_kwh > 0
        self.has_gas_hot_water = self.hot_water_therms > 0

        self.has_ashp = kwargs.get("has_ashp", False)
        self.has_gas_heater = self.heating_therms > 0

        self.gas_furnace_afue = None
        if self.has_gas_heater:
            self.gas_furnace_afue = kwargs.get("gas_furnace_afue", None)

    @property
    def total_therms(self):
        """Total Therms"""
        value = self.heating_therms + self.hot_water_therms + self.lights_and_appliances_therms
        if self.is_improved:
            value -= self.solar_hot_water_therms
        return value

    @property
    def total_kwh(self):
        """Total kWh"""
        value = (
            self.heating_kwh
            + self.hot_water_kwh
            + self.lights_and_appliances_kwh
            + self.cooling_kwh
        )
        if self.is_improved and self.solar_hot_water_kwh > 0:
            value += self.solar_hot_water_kwh
            value -= self.hot_water_kwh
        return value

    def report(self, show_header=True):
        """Pretty print this"""
        data = []
        msg = "{:>12}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}"
        if show_header:
            data.append("\n--- Energy Usage ---")
            data.append(
                msg.format(
                    "",
                    "Heating",
                    "Heating",
                    "Cooling",
                    "H20 Heater",
                    "H20 Heater",
                    "Lights & App",
                    "Lights & App",
                    "PV",
                    "Total",
                    "Total",
                    "Cost",
                    "Cost",
                )
            )
            data.append(
                msg.format(
                    "",
                    "Therms",
                    "kWh",
                    "kWh",
                    "Therms",
                    "kWh",
                    "Therms",
                    "kWh",
                    "kWh",
                    "Therms",
                    "kWh",
                    "Elec",
                    "Gas",
                )
            )
            data.append(
                msg.format(
                    "----------",
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                    "-" * 10,
                )
            )
        data.append(
            msg.format(
                "Improved" if self.is_improved else "Code",
                self.round4__heating_therms,
                self.round4__heating_kwh,
                self.round4__cooling_kwh,
                self.round4__hot_water_therms,
                self.round4__hot_water_kwh,
                self.round4__lights_and_appliances_therms,
                self.round4__lights_and_appliances_kwh,
                self.round4__pv_kwh,
                self.round4__total_therms,
                self.round4__total_kwh,
                self.round4__electric_cost,
                self.round4__gas_cost,
            )
        )

        if self.is_improved:
            data.append(
                msg.format(
                    "",
                    "",
                    "",
                    "Solar Hot H20",
                    self.round__solar_hot_water_therms,
                    self.round4__solar_hot_water_kwh,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                )
            )
        return "\n".join(data)

    @property
    def report_data(self):
        """Reportable data"""
        data = [
            ("is_improved", self.is_improved),
            ("type", "Improved" if self.is_improved else "Code"),
            ("axis_simulation_model", False),
            ("heating_therms", self.heating_therms),
            ("heating_kwh", self.heating_kwh),
            ("cooling_kwh", self.cooling_kwh),
            ("hot_water_therms", self.hot_water_therms),
            ("hot_water_kwh", self.hot_water_kwh),
            ("lights_and_appliances_therms", self.lights_and_appliances_therms),
            ("lights_and_appliances_kwh", self.lights_and_appliances_kwh),
        ]
        if self.is_improved:
            data += [
                ("pv_kwh", self.pv_kwh),
                ("solar_hot_water_therms", self.solar_hot_water_therms),
                ("solar_hot_water_kwh", self.solar_hot_water_kwh),
            ]
        data += [
            ("total_therms", self.total_therms),
            ("total_kwh", self.total_kwh),
            ("electric_cost", self.electric_cost),
            ("gas_cost", self.gas_cost),
        ]
        return OrderedDict(data)

    def get_calculations(self, **kwargs):
        """Return the calculation methods based on the program"""
        if kwargs.get("program") == "eto-2020":
            return Calculations2020(self, is_improved=self.is_improved, **kwargs)
        elif kwargs.get("program") == "eto-2019":
            return Calculations2019(self, is_improved=self.is_improved, **kwargs)
        elif kwargs.get("program") == "eto-2018":
            return Calculations2018(self, is_improved=self.is_improved, **kwargs)
        elif kwargs.get("program") == "eto-2017":
            return Calculations2017(self, is_improved=self.is_improved, **kwargs)
        return Calculations(self, is_improved=self.is_improved, **kwargs)


class ModeledInput(SimulatedInput):
    """Simulation input for the EPS Calculator"""

    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        self.is_improved = kwargs.get("is_improved", False)
        self.simulation = kwargs.get("simulation")

        self.non_solar_hot_water_therms = float(kwargs.get("non_solar_hot_water_therms", 0.0))
        self.non_solar_hot_water_kwh = float(kwargs.get("non_solar_hot_water_kwh", 0.0))
        self.solar_hot_water_therms = float(kwargs.get("solar_hot_water_therms", 0.0))
        self.solar_hot_water_kwh = float(kwargs.get("solar_hot_water_kwh", 0.0))

        # These are NOT used and only used for testing to make sure that our values add correctly
        self._reference_non_solar_hot_water_therms = float(
            kwargs.get("_reference_non_solar_hot_water_therms", 0.0)
        )
        self._reference_non_solar_hot_water_kwh = float(
            kwargs.get("_reference_non_solar_hot_water_kwh", 0.0)
        )

        self.has_solar_hot_water = self.solar_hot_water_kwh > 0 or self.solar_hot_water_therms > 0
        _has_tnkls = self.simulation.hotwaterheater_set.filter(type=3).exists()
        self.has_tankless_water_heater = _has_tnkls
        _has_gas = self.simulation.hotwaterheater_set.filter(fuel_type=1).exists()
        self.has_gas_hot_water = _has_gas
        _has_hpwh = self.simulation.hotwaterheater_set.filter(type__in=[4, 5]).exists()
        self.has_heat_pump_water_heater = _has_hpwh

        self.generated_solar_pv_kwh = kwargs.get("generated_solar_pv_kwh")

        # msg = 'Using %sSimulation [%r] - %r'
        # log.debug(msg, 'Improved ' if self.is_improved else '', self.simulation.id, self.simulation)
        from axis.remrate_data.models import Simulation

        assert isinstance(self.simulation, Simulation)

        self._fuel_summary_values = None

    @property
    def location(self):
        """Rem simulation site label"""
        return self.simulation.site.site_label

    @property
    def _fuel_summary_values_base(self):
        if not getattr(self, "_fuel_summary_values"):
            self._fuel_summary_values = self.simulation.fuelsummary_set.values()
        return self._fuel_summary_values

    def _fuel_summary_values_by_unit(self, unit="kwh"):
        from axis.remrate_data.strings import UTILITY_UNITS

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
    def hot_water_therms(self):
        """Return the total hot water therms"""
        vals = self._fuel_summary_values_by_unit("therms")
        vals = sum([x["hot_water_consumption"] for x in vals if x["hot_water_consumption"] > 0])
        data = float(vals)
        if self.is_improved and self.has_solar_hot_water:
            return self.non_solar_hot_water_therms
        return data

    @property
    def hot_water_kwh(self):
        """Return the total hot water kwh"""
        vals = self._fuel_summary_values_by_unit("kwh")
        vals = sum([x["hot_water_consumption"] for x in vals if x["hot_water_consumption"] > 0])
        data = float(vals)
        if self.is_improved and self.has_solar_hot_water:
            return self.non_solar_hot_water_kwh
        return data

    @property
    def lights_and_appliances_therms(self):
        """Return the total lights and appliance therms"""
        vals = self._fuel_summary_values_by_unit("therms")
        vals = sum(
            [
                x["lights_and_appliances_consumption"]
                for x in vals
                if x["lights_and_appliances_consumption"] > 0
            ]
        )
        return float(vals)

    @property
    def lights_and_appliances_kwh(self):
        """Return the total lights and appliance kwh"""
        vals = self._fuel_summary_values_by_unit("kwh")
        vals = sum(
            [
                x["lights_and_appliances_consumption"]
                for x in vals
                if x["lights_and_appliances_consumption"] > 0
            ]
        )
        return float(vals)

    @property
    def pv_kwh(self):
        """Return the total generated PV kwh"""
        if self.is_improved:
            if self.generated_solar_pv_kwh is not None:
                return float(abs(self.generated_solar_pv_kwh))
            vals = [
                x["photo_voltaics_consumption"]
                for x in self._fuel_summary_values_base
                if x["fuel_units"] == 1 and x["photo_voltaics_consumption"] < 0
            ]
            return float(abs(sum(vals)))
        return 0.0

    @property
    def electric_cost(self):
        """Return the total electric cost"""
        vals = [
            x["total_cost"]
            for x in self._fuel_summary_values_base
            if x["fuel_type"] == 4 and x["fuel_units"] in range(7)
        ]
        return float(sum(vals))

    @property
    def gas_cost(self):
        """Return the total gas cost"""
        vals = [
            x["total_cost"]
            for x in self._fuel_summary_values_base
            if x["fuel_type"] == 1 and x["fuel_units"] in range(7)
        ]
        return float(sum(vals))

    @property
    def conditioned_area(self):
        """Return the total conditioned area"""
        return self.simulation.buildinginfo.conditioned_area

    @property
    def hot_water_ef(self):
        """Return the hot water efficiency value"""
        vals = list(set(self.simulation.hotwaterheater_set.values_list("energy_factor", flat=True)))
        if len(vals) == 1:
            return vals[0]
        if not vals:
            return 0.0
        msg = "Multiple differing water heaters exist you must provide value externally"
        raise AttributeError(msg)

    @property
    def has_ashp(self):
        """Does this have an ASHP?"""
        # A Change was made to allow for Duel Fuel Heat Pumps
        # https://pivotalenergysolutions.zendesk.com/agent/tickets/6920
        return (
            self.simulation.airsourceheatpump_set.count()
            or self.simulation.heater_set.filter(type=6).count()
            or self.simulation.installedequipment_set.filter(system_type__in=[4, 6]).count()
        )

    @property
    def has_gas_heater(self):
        """Does this have a gas heater?"""
        return self.simulation.heater_set.filter(fuel_type=1).count()

    @property
    def gas_furnace_afue(self):
        """Do we have a gas furnace with an AFUE < 94"""
        value = self.simulation.heater_set.filter(
            fuel_type=1, efficiency_unit=1, type=1, efficiency__lt=94
        ).first()
        return value.efficiency if value else None


class SimulationInput(SimulatedInput):
    """A container for a Axis native simulation"""

    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        """This usess the new Axis model"""
        self.is_improved = kwargs.get("is_improved", False)
        self.simulation = kwargs.get("simulation")

        self.non_solar_hot_water_therms = float(kwargs.get("non_solar_hot_water_therms", 0.0))
        self.non_solar_hot_water_kwh = float(kwargs.get("non_solar_hot_water_kwh", 0.0))
        self.solar_hot_water_therms = float(kwargs.get("solar_hot_water_therms", 0.0))
        self.solar_hot_water_kwh = float(kwargs.get("solar_hot_water_kwh", 0.0))
        self.generated_solar_pv_kwh = kwargs.get("generated_solar_pv_kwh")

        self.has_solar_hot_water = self.solar_hot_water_kwh > 0 or self.solar_hot_water_therms > 0

        msg = "Using %sSimulation [%r] - %r"
        log.debug(msg, "Improved " if self.is_improved else "", self.simulation.id, self.simulation)

        from simulation.models import Simulation
        from simulation.enumerations import AnalysisType, EtoReferenceType

        assert isinstance(self.simulation, Simulation)

        design, reference = AnalysisType.UDRH_DESIGN, AnalysisType.UDRH_REFERENCE
        ref_types_available = list(self.simulation.analyses.values_list("type", flat=True))
        if AnalysisType.OR_2019_CENTRAL_DESIGN in ref_types_available:
            design, reference = (
                AnalysisType.OR_2019_CENTRAL_DESIGN,
                AnalysisType.OR_2019_CENTRAL_REFERENCE,
            )

        self.reference_type = self.simulation.project.eto_reference_home_type
        if self.reference_type == EtoReferenceType.CENTRAL:
            if AnalysisType.OR_2020_CENTRAL_DESIGN in ref_types_available:
                design, reference = (
                    AnalysisType.OR_2020_CENTRAL_DESIGN,
                    AnalysisType.OR_2020_CENTRAL_REFERENCE,
                )
        elif self.reference_type == EtoReferenceType.ZONAL:
            if AnalysisType.OR_2020_ZONAL_DESIGN in ref_types_available:
                design, reference = (
                    AnalysisType.OR_2020_ZONAL_DESIGN,
                    AnalysisType.OR_2020_ZONAL_REFERENCE,
                )
        elif self.reference_type == EtoReferenceType.SWWA:
            if AnalysisType.SWWA_2020_DESIGN in ref_types_available:
                design, reference = AnalysisType.SWWA_2020_DESIGN, AnalysisType.SWWA_2020_REFERENCE

        self.improved_analysis = self.simulation.analyses.filter(type=design).first()
        self.reference_analysis = self.simulation.analyses.filter(type=reference).first()
        # print(self.improved_analysis.pk)
        # print(self.reference_analysis.pk)

        self.analysis = self.improved_analysis if self.is_improved else self.reference_analysis

    @property
    def has_tankless_water_heater(self):
        from simulation.enumerations import WaterHeaterStyle

        return self.simulation.water_heaters.filter(style=WaterHeaterStyle.TANKLESS).exists()

    @property
    def has_gas_hot_water(self):
        from simulation.enumerations import FuelType

        return self.simulation.water_heaters.filter(fuel=FuelType.NATURAL_GAS).exists()

    @property
    def has_heat_pump_water_heater(self):
        return self.simulation.water_heaters.heat_pumps().exists()

    @property
    def location(self):
        # Location - TODO - We need to map these back for Ekotrope
        return self.simulation.location.weather_station

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
    def hot_water_therms(self):
        """Return the total hot water therms"""
        return self.analysis.fuel_usages.all().gas_water_heating_consumption_therms

    @property
    def hot_water_kwh(self):
        """Return the total hot water kwh"""
        return self.analysis.fuel_usages.all().electric_water_heating_consumption_kwh

    @property
    def lights_and_appliances_therms(self):
        """Return the total lights and appliance therms"""
        return self.analysis.fuel_usages.all().gas_lighting_and_appliances_consumption_therms

    @property
    def lights_and_appliances_kwh(self):
        """Return the total lights and appliance kwh"""
        return self.analysis.fuel_usages.all().electric_lighting_and_appliances_consumption_kwh

    @property
    def pv_kwh(self):
        """Return the total generated PV kwh"""
        if self.is_improved:
            if self.generated_solar_pv_kwh is not None:
                return float(abs(self.generated_solar_pv_kwh))
            return self.analysis.summary.solar_generation_kwh
        return 0.0

    @property
    def electric_cost(self):
        """Return the total electric cost"""
        return self.analysis.fuel_usages.all().electric_cost

    @property
    def gas_cost(self):
        """Return the total gas cost"""
        return self.analysis.fuel_usages.all().gas_cost

    @property
    def conditioned_area(self):
        """Return the total conditioned area"""
        return self.simulation.conditioned_area

    @property
    def hot_water_ef(self):
        """Return the hot water efficiency value"""
        from simulation.enumerations import HotWaterEfficiencyUnit

        vals = list(
            set(
                self.simulation.water_heaters.filter(
                    efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR
                ).values_list("efficiency", flat=True)
            )
        )
        if len(vals) == 1:
            return vals[0]
        if not vals:
            return 0.0
        msg = "Multiple differing water heaters exist you must provide value externally"
        raise AttributeError(msg)

    @property
    def has_ashp(self):
        """Does this have an ASHP?"""
        return self.simulation.air_source_heat_pumps.exists()

    @property
    def has_gas_heater(self):
        """Does this have a gas heater?"""
        from simulation.enumerations import FuelType

        return self.simulation.heaters.filter(fuel=FuelType.NATURAL_GAS).exists()

    @property
    def gas_furnace_afue(self):
        """Do we have a gas furnace with an AFUE < 94"""
        from simulation.enumerations import FuelType, HeatingEfficiencyUnit

        value = self.simulation.heaters.filter(
            fuel=FuelType.NATURAL_GAS, efficiency_unit=HeatingEfficiencyUnit.AFUE, efficiency__lt=94
        ).first()
        return value.efficiency if value else None

    @property
    def report_data(self):
        data = super(SimulationInput, self).report_data
        data["axis_simulation_model"] = True
        data["reference_type"] = self.reference_type
        return data
