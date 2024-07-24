"""calculator.py - Axis"""

__author__ = "Steven K"
__date__ = "8/11/21 12:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from tabulate import tabulate


from axis.customer_eto.eep_programs.washington_code_credit import (
    FireplaceType,
    Appliances,
    RenewableEnergy,
    EfficientWaterHeating,
    DWHR,
    HighEfficiencyHVACDistribution,
    HighEfficiencyHVAC,
    BuildingEnvelope,
    AirLeakageControl,
    WACCFuelType,
)
from .incentives import Incentives
from .savings import Savings

from .specifications import EnvelopeSpecification, HVACSpecification, AirLeakageSpecification
from axis.customer_eto.calculator.washington_code_credit.credits import Credits
from .specifications.hvac import HVACDistributionSpecification
from .specifications.water import WaterSpecification

log = logging.getLogger(__name__)


class WashingtonCodeCreditCalculator:
    def __init__(self, **kwargs):
        self.envelope_option = kwargs.get("envelope_option", BuildingEnvelope.NONE)
        self.air_leakage_option = kwargs.get("air_leakage_option", AirLeakageControl.NONE)
        self.hvac_option = kwargs.get("hvac_option", HighEfficiencyHVAC.NONE)
        self.hvac_distribution_option = kwargs.get(
            "hvac_distribution_option", HighEfficiencyHVACDistribution.NONE
        )
        self.dwhr_option = kwargs.get("dwhr_option", DWHR.NONE)
        self.water_heating_option = kwargs.get("water_heating_option", EfficientWaterHeating.NONE)
        self.renewable_electric_option = kwargs.get(
            "renewable_electric_option", RenewableEnergy.NONE
        )
        self.appliance_option = kwargs.get("appliance_option", Appliances.NONE)
        self.conditioned_floor_area = kwargs.get("conditioned_floor_area", 0.0)
        self.water_heating_fuel = kwargs.get("water_heating_fuel", None)
        self.thermostat_type = kwargs.get("thermostat_type", None)
        self.fireplace_efficiency = kwargs.get("fireplace_efficiency", FireplaceType.NONE)
        self.envelope_measures = {
            "wall_cavity_r_value": kwargs.get("wall_cavity_r_value", 0),
            "wall_continuous_r_value": kwargs.get("wall_continuous_r_value", 0),
            "framing_type": kwargs.get("framing_type", None),
            "window_u_value": kwargs.get("window_u_value", 0.0),
            "window_shgc": kwargs.get("window_shgc", 0.0),
            "floor_cavity_r_value": kwargs.get("floor_cavity_r_value", 0),
            "slab_perimeter_r_value": kwargs.get("slab_perimeter_r_value", 0),
            "under_slab_r_value": kwargs.get("under_slab_r_value", 0),
            "ceiling_r_value": kwargs.get("ceiling_r_value", 0),
            "raised_heel": kwargs.get("raised_heel", None),
            "total_ua_alternative": kwargs.get("total_ua_alternative", None),
        }
        self.air_leakage_measures = {
            "air_leakage_ach": kwargs.get("air_leakage_ach", 0.0),
            "ventilation_type": kwargs.get("ventilation_type", None),
            "ventilation_brand": kwargs.get("ventilation_brand", None),
            "ventilation_model": kwargs.get("ventilation_model", None),
            "hrv_asre": kwargs.get("hrv_asre", 0.0),
        }
        self.hvac_measures = {
            "furnace_brand": kwargs.get("furnace_brand", None),
            "furnace_model": kwargs.get("furnace_model", None),
            "furnace_afue": kwargs.get("furnace_afue", 0),
        }
        self.hvac_distribution_measures = {
            "furnace_location": kwargs.get("furnace_location", None),
            "duct_location": kwargs.get("duct_location", None),
            "duct_leakage": kwargs.get("duct_leakage", 0),
        }
        self.water_heating_measures = {
            "dwhr_installed": kwargs.get("dwhr_installed", None),
            "water_heater_brand": kwargs.get("water_heater_brand", None),
            "water_heater_model": kwargs.get("water_heater_model", None),
            "gas_water_heater_uef": kwargs.get("gas_water_heater_uef", 0.0),
            "electric_water_heater_uef": kwargs.get("electric_water_heater_uef", 0.0),
        }

        self._specifications = None

        self.input_data = {
            "envelope_option": self.envelope_option,
            "air_leakage_option": self.air_leakage_option,
            "hvac_option": self.hvac_option,
            "hvac_distribution_option": self.hvac_distribution_option,
            "dwhr_option": self.dwhr_option,
            "water_heating_option": self.water_heating_option,
            "renewable_electric_option": self.renewable_electric_option,
            "appliance_option": self.appliance_option,
            "conditioned_floor_area": self.conditioned_floor_area,
            "water_heating_fuel": self.water_heating_fuel,
            "thermostat_type": self.thermostat_type,
            "fireplace_efficiency": self.fireplace_efficiency,
            "wall_cavity_r_value": self.envelope_measures["wall_cavity_r_value"],
            "wall_continuous_r_value": self.envelope_measures["wall_continuous_r_value"],
            "framing_type": self.envelope_measures["framing_type"],
            "window_u_value": self.envelope_measures["window_u_value"],
            "window_shgc": self.envelope_measures["window_shgc"],
            "floor_cavity_r_value": self.envelope_measures["floor_cavity_r_value"],
            "slab_perimeter_r_value": self.envelope_measures["slab_perimeter_r_value"],
            "under_slab_r_value": self.envelope_measures["under_slab_r_value"],
            "ceiling_r_value": self.envelope_measures["ceiling_r_value"],
            "raised_heel": self.envelope_measures["raised_heel"],
            "air_leakage_ach": self.air_leakage_measures["air_leakage_ach"],
            "ventilation_type": self.air_leakage_measures["ventilation_type"],
            "ventilation_brand": self.air_leakage_measures["ventilation_brand"],
            "ventilation_model": self.air_leakage_measures["ventilation_model"],
            "hrv_asre": self.air_leakage_measures["hrv_asre"],
            "furnace_brand": self.hvac_measures["furnace_brand"],
            "furnace_model": self.hvac_measures["furnace_model"],
            "furnace_afue": self.hvac_measures["furnace_afue"],
            "furnace_location": self.hvac_distribution_measures["furnace_location"],
            "duct_location": self.hvac_distribution_measures["duct_location"],
            "duct_leakage": self.hvac_distribution_measures["duct_leakage"],
            "dwhr_installed": self.water_heating_measures["dwhr_installed"],
            "water_heater_brand": self.water_heating_measures["water_heater_brand"],
            "water_heater_model": self.water_heating_measures["water_heater_model"],
            "gas_water_heater_uef": self.water_heating_measures["gas_water_heater_uef"],
            "electric_water_heater_uef": self.water_heating_measures["electric_water_heater_uef"],
        }

    def get_input_data_string(
        self,
    ):
        data = self.input_data
        input_data_str = "input_data = {"
        input_data_str += f"""
        "envelope_option": {data.get('envelope_option')},
        "air_leakage_option": {data.get('air_leakage_option')},
        "hvac_option": {data.get('hvac_option')},
        "hvac_distribution_option": {data.get('hvac_distribution_option')},
        "dwhr_option": {data.get('dwhr_option')},
        "water_heating_option": {data.get('water_heating_option')},
        "renewable_electric_option": {data.get('renewable_electric_option')},
        "appliance_option": {data.get('appliance_option')},
        "conditioned_floor_area": {data.get('conditioned_floor_area')!r},
        "water_heating_fuel": {data.get('water_heating_fuel')},
        "thermostat_type": {data.get('thermostat_type')},
        "fireplace_efficiency": {data.get('fireplace_efficiency')},
        "wall_cavity_r_value": {data.get('wall_cavity_r_value')!r},
        "wall_continuous_r_value": {data.get('wall_continuous_r_value')!r},
        "framing_type": {data.get('framing_type')},
        "window_u_value": {data.get('window_u_value')!r},
        "window_shgc": {data.get('window_shgc')!r},
        "floor_cavity_r_value": {data.get('floor_cavity_r_value')!r},
        "slab_perimeter_r_value": {data.get('slab_perimeter_r_value')!r},
        "under_slab_r_value": {data.get('under_slab_r_value')!r},
        "ceiling_r_value": {data.get('ceiling_r_value')!r},
        "raised_heel": {data.get('raised_heel')},
        "air_leakage_ach": {data.get('air_leakage_ach')!r},
        "ventilation_type": {data.get('ventilation_type')},
        "ventilation_brand": {data.get('ventilation_brand')!r},
        "ventilation_model": {data.get('ventilation_model')!r},
        "hrv_asre": {data.get('hrv_asre')!r},
        "furnace_brand": {data.get('furnace_brand')!r},
        "furnace_model": {data.get('furnace_model')!r},
        "furnace_afue": {data.get('furnace_afue')!r},
        "furnace_location": {data.get('furnace_location')},
        "duct_location": {data.get('duct_location')},
        "duct_leakage": {data.get('duct_leakage')!r},
        "dwhr_installed": {data.get('dwhr_installed')}
        "water_heater_brand": {data.get('water_heater_brand')!r},
        "water_heater_model": {data.get('water_heater_model')!r},
        "gas_water_heater_uef": {data.get('gas_water_heater_uef')!r},
        "electric_water_heater_uef": {data.get('electric_water_heater_uef')!r},\n"""
        input_data_str += "}\n"
        input_data_str += "calculator = WashingtonCodeCreditCalculator(**input_data)"
        return input_data_str

    def get_value(self, obj):
        if obj is None:
            return None
        try:
            return obj.value
        except AttributeError:
            return obj

    @property
    def input_report(self):
        table = [
            (label.replace("_", " ").capitalize(), self.get_value(item))
            for label, item in self.input_data.items()
        ]
        return tabulate(table, headers=["Input", "Value"])

    @property
    def required_credits_to_meet_code(self):
        if self.conditioned_floor_area < 1500:
            return 3
        elif self.conditioned_floor_area < 5000:
            return 6
        return 7

    @cached_property
    def specifications(self):
        if self._specifications is not None:
            return self._specifications

        envelope_spec = EnvelopeSpecification(self.envelope_option, **self.envelope_measures)
        air_leakage_spec = AirLeakageSpecification(
            self.air_leakage_option, **self.air_leakage_measures
        )
        hvac_spec = HVACSpecification(self.hvac_option, **self.hvac_measures)
        hvac_distribution_spec = HVACDistributionSpecification(
            self.hvac_distribution_option, **self.hvac_distribution_measures
        )
        water_spec = WaterSpecification(
            self.dwhr_option,
            self.water_heating_option,
            self.water_heating_fuel,
            **self.water_heating_measures,
        )
        self._specifications = {
            "building_envelope": envelope_spec,
            "air_leakage": air_leakage_spec,
            "hvac": hvac_spec,
            "hvac_distribution": hvac_distribution_spec,
            "water": water_spec,
        }
        return self._specifications

    @cached_property
    def specification_data(self):
        return {k: v.data for k, v in self.specifications.items()}

    @cached_property
    def spec_report(self):
        data = ""
        for key in ["building_envelope", "air_leakage", "hvac", "hvac_distribution", "water"]:
            data += self.specifications[key].report + "\n\n"
        return data

    @cached_property
    def credits(self):
        return Credits(
            envelope_option=self.envelope_option,
            air_leakage_option=self.air_leakage_option,
            hvac_option=self.hvac_option,
            hvac_distribution_option=self.hvac_distribution_option,
            dwhr_option=self.dwhr_option,
            water_heating_option=self.water_heating_option,
            renewable_electric_option=self.renewable_electric_option,
            appliance_option=self.appliance_option,
            specifications=self.specifications,
        )

    @cached_property
    def credit_data(self):
        return self.credits.credit_data

    @cached_property
    def credit_report(self):
        return self.credits.credit_report

    @cached_property
    def eligible_gas_points(self):
        """
            =IFERROR(
                MIN(1.5,
                    IF(D11>=C11,
                        MIN(
                            D11-SUM(
                                D10,
                                D9,
                                D5,
                                IF($C$6=$I$6,
                                    SUM(D8,D7),
                                    D8)
                                ),
                            D11-C11)
                        )
                    ),
                    0)


        :return:
        """
        if self.credits.achieved_total_credits < self.required_credits_to_meet_code:
            return 0.0
        value = self.credits.achieved_total_credits
        if self.credits.achieved_appliances_credits:
            value -= self.credits.achieved_appliances_credits
        if self.credits.achieved_renewable_electric_credits:
            value -= self.credits.achieved_renewable_electric_credits
        if self.credits.achieved_hvac_credits:
            value -= self.credits.achieved_hvac_credits
        if self.credits.achieved_water_heating_credits:
            value -= self.credits.achieved_water_heating_credits
        if self.water_heating_fuel == WACCFuelType.ELECTRIC and self.credits.achieved_dwhr_credits:
            value -= self.credits.achieved_dwhr_credits

        basic = self.credits.achieved_total_credits - self.required_credits_to_meet_code
        return min([1.5, min([value, basic])])

    @cached_property
    def incentive(self):
        return Incentives(
            eligible_gas_points=self.eligible_gas_points,
            thermostat_type=self.thermostat_type,
            fireplace_efficiency=self.fireplace_efficiency,
        )

    @cached_property
    def incentive_data(self):
        return self.incentive.incentive_data

    @cached_property
    def incentive_report(self):
        return self.incentive.incentive_report

    @cached_property
    def savings(self):
        return Savings(
            eligible_gas_points=self.eligible_gas_points,
            thermostat_incentive=self.incentive.thermostat_incentive,
            fireplace_incentive=self.incentive.fireplace_incentive,
        )

    @cached_property
    def savings_data(self):
        return self.savings.savings_data

    @cached_property
    def savings_report(self):
        return self.savings.savings_report

    @cached_property
    def summary_data(self):
        water_fuel = self.water_heating_fuel.value.capitalize() if self.water_heating_fuel else None
        fireplace = self.fireplace_efficiency.value if self.fireplace_efficiency else None
        return {
            # Home
            "conditioned_floor_area": self.conditioned_floor_area,
            "water_heating_fuel": water_fuel,
            "thermostat_type": self.thermostat_type.value if self.thermostat_type else None,
            "fireplace_efficiency": fireplace,
            # Code Credits
            "required_credits_to_meet_code": self.required_credits_to_meet_code,
            "achieved_total_credits": self.credits.achieved_total_credits,
            "eligible_gas_points": self.eligible_gas_points,
            "total_therm_savings": round(self.savings.total_therm_savings, 2),  # Rounded for model
            "code_credit_incentive": self.incentive.code_credit_incentive,
            "thermostat_incentive": self.incentive.thermostat_incentive,
            "fireplace_incentive": self.incentive.fireplace_incentive,
            "total_builder_incentive": self.incentive.total_builder_incentive,
            "verifier_incentive": self.incentive.verifier_incentive,
        }

    @cached_property
    def summary_report(self):
        data = self.summary_data

        result = "Home Summary\n "
        table = [
            ("Conditioned Floor Area", f"{data['conditioned_floor_area']} Sq Ft"),
            ("Water Heating Fuel", f"{data['water_heating_fuel']}"),
            ("Thermostat Type", f"{data['thermostat_type']}"),
            ("Fireplace Efficiency", f"{data['fireplace_efficiency']}"),
        ]
        result += tabulate(table)
        result += "\n\nCode Credits\n "
        table = [
            ("Required Credits to Meet Code", f"{data['required_credits_to_meet_code']}"),
            ("Total Credit Selected", f"{data['achieved_total_credits']}"),
            ("Eligible Above Code Credits", f"{data['eligible_gas_points']}"),
            ("Total Therm Savings", f"{data['total_therm_savings']}"),
        ]
        result += tabulate(table)
        result += "\n\nIncentives\n "
        table = [
            ("Code Credit Incentive", f"${data['code_credit_incentive']:.2f}"),
            ("Smart Thermostat Incentive", f"${data['thermostat_incentive']:.2f}"),
            ("Fireplace Incentive", f"${data['fireplace_incentive']:.2f}"),
            ("Total Builder Incentive", f"${data['total_builder_incentive']:.2f}"),
            ("Total Verifier Incentive", f"${data['verifier_incentive']:.2f}"),
        ]
        result += tabulate(table)
        return result
