"""calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 15:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from .constants import FireConstants
from .incentives import Incentives2021Fire
from .net_zero import NetZeroFire2021
from ..eps_2021.calculator import EPS2021Calculator
from ...eep_programs.fire_rebuild_2021 import FireResilienceBonus
from ...enumerations import (
    PNWUSStates,
    ClimateLocation,
    ElectricUtility,
    GasUtility,
    PrimaryHeatingEquipment2020,
    SmartThermostatBrands2020,
    Fireplace2020,
    GridHarmonization2020,
    AdditionalIncentives2020,
    SolarElements2020,
    YesNo,
)

log = logging.getLogger(__name__)


class EPSFire2021Calculator(EPS2021Calculator):
    def __init__(
        self,
        us_state: PNWUSStates,
        climate_location: ClimateLocation,
        conditioned_area: float,
        electric_utility: ElectricUtility,
        gas_utility: GasUtility,
        primary_heating_class: PrimaryHeatingEquipment2020,
        thermostat_brand: SmartThermostatBrands2020,
        fireplace: Fireplace2020 = Fireplace2020.NONE,
        grid_harmonization_elements: GridHarmonization2020 = GridHarmonization2020.NONE,
        eps_additional_incentives: AdditionalIncentives2020 = AdditionalIncentives2020.NO,
        solar_elements: SolarElements2020 = SolarElements2020.NONE,
        fire_resilience_bonus: FireResilienceBonus = FireResilienceBonus.NO,
        fire_rebuild_qualification: YesNo = YesNo.NO,
        code_heating_therms: float = 0,
        code_heating_kwh: float = 0,
        code_cooling_kwh: float = 0,
        code_hot_water_therms: float = 0,
        code_hot_water_kwh: float = 0,
        code_lights_and_appliance_therms: float = 0,
        code_lights_and_appliance_kwh: float = 0,
        code_electric_cost: float = 0,
        code_gas_cost: float = 0,
        improved_heating_therms: float = 0,
        improved_heating_kwh: float = 0,
        improved_cooling_kwh: float = 0,
        improved_hot_water_therms: float = 0,
        improved_hot_water_kwh: float = 0,
        improved_lights_and_appliance_therms: float = 0,
        improved_lights_and_appliance_kwh: float = 0,
        improved_pv_kwh: float = 0,
        improved_solar_hot_water_therms: float = 0,
        improved_solar_hot_water_kwh: float = 0,
        improved_electric_cost: float = 0,
        improved_gas_cost: float = 0,
        has_heat_pump_water_heater: bool = False,
    ):
        self.fire_rebuild_qualification = fire_rebuild_qualification
        self.fire_resilience_bonus = fire_resilience_bonus

        super(EPSFire2021Calculator, self).__init__(
            us_state=us_state,
            climate_location=climate_location,
            conditioned_area=conditioned_area,
            electric_utility=electric_utility,
            gas_utility=gas_utility,
            primary_heating_class=primary_heating_class,
            thermostat_brand=thermostat_brand,
            fireplace=fireplace,
            grid_harmonization_elements=grid_harmonization_elements,
            eps_additional_incentives=eps_additional_incentives,
            solar_elements=solar_elements,
            code_heating_therms=code_heating_therms,
            code_heating_kwh=code_heating_kwh,
            code_cooling_kwh=code_cooling_kwh,
            code_hot_water_therms=code_hot_water_therms,
            code_hot_water_kwh=code_hot_water_kwh,
            code_lights_and_appliance_therms=code_lights_and_appliance_therms,
            code_lights_and_appliance_kwh=code_lights_and_appliance_kwh,
            code_electric_cost=code_electric_cost,
            code_gas_cost=code_gas_cost,
            improved_heating_therms=improved_heating_therms,
            improved_heating_kwh=improved_heating_kwh,
            improved_cooling_kwh=improved_cooling_kwh,
            improved_hot_water_therms=improved_hot_water_therms,
            improved_hot_water_kwh=improved_hot_water_kwh,
            improved_lights_and_appliance_therms=improved_lights_and_appliance_therms,
            improved_lights_and_appliance_kwh=improved_lights_and_appliance_kwh,
            improved_pv_kwh=improved_pv_kwh,
            improved_solar_hot_water_therms=improved_solar_hot_water_therms,
            improved_solar_hot_water_kwh=improved_solar_hot_water_kwh,
            improved_electric_cost=improved_electric_cost,
            improved_gas_cost=improved_gas_cost,
            has_heat_pump_water_heater=has_heat_pump_water_heater,
        )
        self.input_data["fire_rebuild_qualification"] = fire_rebuild_qualification
        self.input_data["fire_resilience_bonus"] = fire_resilience_bonus

    @cached_property
    def input_str(self) -> str:
        data = self.input_data
        input_data_str = "input_data = {"
        input_data_str += f"""
    "us_state": {data.get('us_state')},
    "climate_location": {data.get('climate_location')},
    "primary_heating_class": {data.get('primary_heating_class')},
    "conditioned_area": {data.get('conditioned_area')},
    "electric_utility": {data.get('electric_utility')},
    "gas_utility": {data.get('gas_utility')},
    "fireplace": {data.get('fireplace')},
    "thermostat_brand": {data.get('thermostat_brand')},
    "grid_harmonization_elements": {data.get('grid_harmonization_elements')},
    "eps_additional_incentives": {data.get('eps_additional_incentives')},
    "solar_elements": {data.get('solar_elements')},
    "fire_resilience_bonus": {data.get('fire_resilience_bonus')},
    "fire_rebuild_qualification": {data.get('fire_rebuild_qualification')},
    "code_heating_therms": {data.get('code_heating_therms')},
    "code_heating_kwh": {data.get('code_heating_kwh')},
    "code_cooling_kwh": {data.get('code_cooling_kwh')},
    "code_hot_water_therms": {data.get('code_hot_water_therms')},
    "code_hot_water_kwh": {data.get('code_hot_water_kwh')},
    "code_lights_and_appliance_therms": {data.get('code_lights_and_appliance_therms')},
    "code_lights_and_appliance_kwh": {data.get('code_lights_and_appliance_kwh')},
    "code_electric_cost": {data.get('code_electric_cost')},
    "code_gas_cost": {data.get('code_gas_cost')},
    "improved_heating_therms": {data.get('improved_heating_therms')},
    "improved_heating_kwh": {data.get('improved_heating_kwh')},
    "improved_cooling_kwh": {data.get('improved_cooling_kwh')},
    "improved_hot_water_therms": {data.get('improved_hot_water_therms')},
    "improved_hot_water_kwh": {data.get('improved_hot_water_kwh')},
    "improved_lights_and_appliance_therms": {data.get('improved_lights_and_appliance_therms')},
    "improved_lights_and_appliance_kwh": {data.get('improved_lights_and_appliance_kwh')},
    "improved_pv_kwh": {data.get('improved_pv_kwh')},
    "improved_solar_hot_water_therms": {data.get('improved_solar_hot_water_therms')},
    "improved_solar_hot_water_kwh": {data.get('improved_solar_hot_water_kwh')},
    "improved_electric_cost": {data.get('improved_electric_cost')},
    "improved_gas_cost": {data.get('improved_gas_cost')},\n"""
        input_data_str += "}\n"
        input_data_str += "calculator = EPSFire2021Calculator(**input_data)"
        return input_data_str

    @cached_property
    def constants(self):
        return FireConstants(self.electric_utility, self.us_state, self.thermostat, self.heat_type)

    @cached_property
    def net_zero(self):
        return NetZeroFire2021(
            self.improved.total_kwh,
            self.improved.total_therms,
            self.improved.cooling_kwh,
            self.improved.pv_kwh,
            self.improvement_data.percent_improvement,
            self.improvement_data.percent_improvement_breakout.therms,
            self.us_state,
            self.constants,
            self.electric_utility,
            self.primary_heating_class,
            self.thermostat_brand,
            self.grid_harmonization_elements,
            self.eps_additional_incentives,
            self.solar_elements,
            self.heat_type,
            self.fire_rebuild_qualification,
            self.fire_resilience_bonus,
        )

    @cached_property
    def incentives(self):
        return Incentives2021Fire(
            self.improvement_data.percent_improvement,
            self.electric_utility,
            self.gas_utility,
            self.improved.heating_therms,
            self.improved.hot_water_therms,
            self.improved.hot_water_kwh,
            self.constants,
            self.net_zero,
            self.has_heat_pump_water_heater,
        )
