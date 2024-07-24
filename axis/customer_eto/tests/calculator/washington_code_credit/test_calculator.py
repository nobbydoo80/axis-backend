"""credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 12:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from ....api_v3.serializers.calculators.washington_code_credit import (
    WashingtonCodeCreditCalculatorBaseSerializer,
)
from ....calculator.washington_code_credit.calculator import WashingtonCodeCreditCalculator
from ....eep_programs.washington_code_credit import (
    BuildingEnvelope,
    AirLeakageControl,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DWHR,
    EfficientWaterHeating,
    RenewableEnergy,
    Appliances,
    WACCFuelType,
    ThermostatType,
    FireplaceType,
    FramingType,
    VentilationType,
    DuctLocation,
    FurnaceLocation,
)
from ....enumerations import YesNo

log = logging.getLogger(__name__)


class WashingtonCodeCreditCalculatorTests(TestCase):
    @property
    def input_options(self):
        return {
            "envelope_option": BuildingEnvelope.OPTION_1p6b,
            "air_leakage_option": AirLeakageControl.OPTION_2p4,
            "hvac_option": HighEfficiencyHVAC.OPTION_3p1,
            "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p2,
            "dwhr_option": DWHR.OPTION_5p1,
            "water_heating_option": EfficientWaterHeating.OPTION_5p3,
            "renewable_electric_option": RenewableEnergy.OPTION_6p1c,
            "appliance_option": Appliances.OPTION_7p1,
            "conditioned_floor_area": 1000,
            "water_heating_fuel": WACCFuelType.GAS,
            "thermostat_type": ThermostatType.PROGRAMABLE,
            "fireplace_efficiency": FireplaceType.FP_70_75,
        }

    def test_required_credits_to_meet_code(self):
        data = self.input_options
        with self.subTest(f"Small House"):
            data["conditioned_floor_area"] = 1499
            calculator = WashingtonCodeCreditCalculator(**data)
            self.assertEqual(calculator.required_credits_to_meet_code, 3)

        with self.subTest(f"Medium House"):
            data["conditioned_floor_area"] = 4999
            calculator = WashingtonCodeCreditCalculator(**data)
            self.assertEqual(calculator.required_credits_to_meet_code, 6)

        with self.subTest(f"Large House"):
            data["conditioned_floor_area"] = 5001
            calculator = WashingtonCodeCreditCalculator(**data)
            self.assertEqual(calculator.required_credits_to_meet_code, 7)

    def test_credit_data(self):
        """Verify we got credit data"""
        calculator = WashingtonCodeCreditCalculator(**self.input_options)
        self.assertEqual(type(calculator.credit_data), dict)
        self.assertEqual(len(calculator.credit_data.keys()), 9)

    def test_credit_report(self):
        """Verify we got credit data"""
        calculator = WashingtonCodeCreditCalculator(**self.input_options)
        self.assertEqual(type(calculator.credit_report), str)

    def test_summary_report(self):
        """Verify we got credit data"""
        calculator = WashingtonCodeCreditCalculator(**self.input_options)
        self.assertEqual(type(calculator.summary_data), dict)
        self.assertEqual(type(calculator.summary_report), str)

    def test_eligible_gas_points(self):
        calculator = WashingtonCodeCreditCalculator(**self.input_options)
        self.assertEqual(calculator.eligible_gas_points, 1.5)


class WashingtonCodeCreditCalculatorChecks(TestCase):
    serializer_class = WashingtonCodeCreditCalculatorBaseSerializer

    @property
    def default_kwargs(self):
        data = {
            "envelope_option": BuildingEnvelope.OPTION_1p1,
            "air_leakage_option": AirLeakageControl.OPTION_2p1.value,
            "hvac_option": HighEfficiencyHVAC.OPTION_3p1,
            "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p1,
            "dwhr_option": DWHR.NONE,
            "water_heating_option": EfficientWaterHeating.OPTION_5p3,
            "renewable_electric_option": RenewableEnergy.OPTION_6p1a,
            "appliance_option": Appliances.OPTION_7p1,
            "conditioned_floor_area": 500,
            "water_heating_fuel": WACCFuelType.GAS,
            "thermostat_type": ThermostatType.CARRIER,
            "fireplace_efficiency": FireplaceType.NONE,
            "wall_cavity_r_value": 0,
            "wall_continuous_r_value": 0,
            "framing_type": FramingType.INTERMEDIATE,
            "window_u_value": 0,
            "floor_cavity_r_value": 0,
            "slab_perimeter_r_value": 0,
            "under_slab_r_value": 0,
            "ceiling_r_value": 0,
            "raised_heel": YesNo.NO,
            "air_leakage_ach": 0,
            "ventilation_type": VentilationType.BALANCED,
            "ventilation_brand": "string",
            "furnace_brand": "string",
            "furnace_model": "string",
            "furnace_afue": 92,
            "furnace_location": FurnaceLocation.UNCONDITIONED_SPACE,
            "duct_leakage": 0,
            "duct_location": DuctLocation.UNCONDITIONED_SPACE,
            "dwhr_installed": YesNo.NO,
            "water_heater_brand": "string",
            "water_heater_model": "string",
            "gas_water_heater_uef": 0,
            "electric_water_heater_uef": 0,
        }
        return data.copy()

    def test_core_serializer(self):
        """Basic Serializer"""
        serializer = self.serializer_class(data=self.default_kwargs)
        serializer.is_valid(raise_exception=True)
        self.assertTrue(serializer.is_valid())
        # for k, v in serializer.validated_data.items():
        #     print(k, v)

    def dump_assertions(self, calculator, basic_only=False):
        for k, v in calculator.summary_data.items():
            print(f"self.assertEqual(calculator.summary_data['{k}'], {v!r})")

        for k, v in calculator.credit_data.items():
            for m, n in v.items():
                print(f"self.assertEqual(calculator.credit_data['{k}']['{m}'], {n!r})")

        for k, v in calculator.incentive_data.items():
            print(f"self.assertEqual(calculator.incentive_data['{k}'], {v!r})")

        for k, v in calculator.savings_data.items():
            print(f"self.assertEqual(calculator.savings_data['{k}'], {v!r})")

        if basic_only:
            return

        for k, v in calculator.specification_data.items():
            for m, n in v.items():
                if isinstance(n, dict):
                    for y, z in n.items():
                        print(
                            f"self.assertEqual(calculator.specification_data['{k}']['{m}']['{y}'], {z!r})"
                        )
                else:
                    print(f"self.assertEqual(calculator.specification_data['{k}']['{m}'], {n!r})")

    def test_max(self):
        data = {
            "envelope_option": BuildingEnvelope.OPTION_1p6a,
            "air_leakage_option": AirLeakageControl.OPTION_2p4,
            "hvac_option": HighEfficiencyHVAC.OPTION_3p1.value,
            "hvac_distribution_option": "4.2: HVAC & Ducts In Conditioned Space",
            "dwhr_option": "5.1: Drain Water Heat Recovery",
            "water_heating_option": "5.6: ELEC - Split HP w/ UEF 2.9",
            "renewable_electric_option": RenewableEnergy.OPTION_6p1c.value,
            "appliance_option": Appliances.OPTION_7p1.value,
            "conditioned_floor_area": 2500,
            "water_heating_fuel": "Electric",
            "thermostat_type": "ecobee4",
            "fireplace_efficiency": "70-75 FE",
            "wall_cavity_r_value": 22,
            "wall_continuous_r_value": 16,
            "framing_type": "Advanced",
            "window_u_value": 0.16,
            "window_shgc": 1.0,
            "floor_cavity_r_value": 49,
            "slab_perimeter_r_value": 21,
            "under_slab_r_value": 21,
            "ceiling_r_value": 61,
            "raised_heel": "Yes",
            "air_leakage_ach": 0.5,
            "ventilation_type": "HRV/ERV",
            "ventilation_brand": "Brand",
            "ventilation_model": "Model",
            "hrv_asre": 85.0,
            "furnace_brand": "Brand",
            "furnace_model": "Model",
            "furnace_afue": 97,
            "furnace_location": "Conditioned Space",
            "duct_location": "Conditioned Space",
            "duct_leakage": 4,
            "dwhr_installed": "Yes",
            "water_heater_brand": "Brand",
            "water_heater_model": "Model",
            "gas_water_heater_uef": 0.92,
            "electric_water_heater_uef": 2.95,
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        calculator = serializer.calculator

        # self.dump_assertions(calculator, basic_only=True)
        self.assertEqual(calculator.summary_data["conditioned_floor_area"], 2500)
        self.assertEqual(calculator.summary_data["water_heating_fuel"], "Electric")
        self.assertEqual(calculator.summary_data["thermostat_type"], "ecobee4")
        self.assertEqual(calculator.summary_data["fireplace_efficiency"], "70-75 FE")
        self.assertEqual(calculator.summary_data["required_credits_to_meet_code"], 6)
        self.assertEqual(calculator.summary_data["achieved_total_credits"], 13.5)
        self.assertEqual(calculator.summary_data["eligible_gas_points"], 1.5)
        self.assertEqual(calculator.summary_data["total_therm_savings"], 141.3)
        self.assertEqual(calculator.summary_data["code_credit_incentive"], 2400.0)
        self.assertEqual(calculator.summary_data["thermostat_incentive"], 125.0)
        self.assertEqual(calculator.summary_data["fireplace_incentive"], 200.0)
        self.assertEqual(calculator.summary_data["total_builder_incentive"], 2725.0)
        self.assertEqual(calculator.summary_data["verifier_incentive"], 100.0)
        self.assertEqual(calculator.credit_data["building_envelope"]["eligible"], 3.0)
        self.assertEqual(calculator.credit_data["building_envelope"]["achieved"], 3.0)
        self.assertEqual(calculator.credit_data["air_leakage"]["eligible"], 2.0)
        self.assertEqual(calculator.credit_data["air_leakage"]["achieved"], 2.0)
        self.assertEqual(calculator.credit_data["hvac"]["eligible"], 1.0)
        self.assertEqual(calculator.credit_data["hvac"]["achieved"], 1.0)
        self.assertEqual(calculator.credit_data["hvac_distribution"]["eligible"], 1.0)
        self.assertEqual(calculator.credit_data["hvac_distribution"]["achieved"], 1.0)
        self.assertEqual(calculator.credit_data["dwhr"]["eligible"], 0.5)
        self.assertEqual(calculator.credit_data["dwhr"]["achieved"], 0.5)
        self.assertEqual(calculator.credit_data["water_heater"]["eligible"], 2.5)
        self.assertEqual(calculator.credit_data["water_heater"]["achieved"], 2.5)
        self.assertEqual(calculator.credit_data["renewables"]["eligible"], 3.0)
        self.assertEqual(calculator.credit_data["renewables"]["achieved"], 3.0)
        self.assertEqual(calculator.credit_data["appliances"]["eligible"], 0.5)
        self.assertEqual(calculator.credit_data["appliances"]["achieved"], 0.5)
        self.assertEqual(calculator.credit_data["total"]["eligible"], 13.5)
        self.assertEqual(calculator.credit_data["total"]["achieved"], 13.5)
        self.assertEqual(calculator.incentive_data["code_credit_incentive"], 2400.0)
        self.assertEqual(calculator.incentive_data["thermostat_incentive"], 125.0)
        self.assertEqual(calculator.incentive_data["fireplace_incentive"], 200.0)
        self.assertEqual(calculator.incentive_data["total_builder_incentive"], 2725.0)
        self.assertEqual(calculator.incentive_data["verifier_incentive"], 100.0)
        self.assertEqual(calculator.savings_data["eligible_gas_points"], 1.5)
        self.assertEqual(calculator.savings_data["code_based_therm_savings"], 102.8351186628498)
        self.assertEqual(calculator.savings_data["thermostat_therm_savings"], 20.16)
        self.assertEqual(calculator.savings_data["fireplace_therm_savings"], 18.3)
        self.assertEqual(calculator.savings_data["total_therm_savings"], 141.2951186628498)

    def test_no_renewables(self):
        data = {
            "envelope_option": BuildingEnvelope.OPTION_1p6a,
            "air_leakage_option": AirLeakageControl.OPTION_2p4,
            "hvac_option": "3.1: REQUIRED - 95 AFUE",
            "hvac_distribution_option": "4.1: Deeply Buried Ducts",
            "dwhr_option": "5.1: Drain Water Heat Recovery",
            "water_heating_option": "5.6: ELEC - Split HP w/ UEF 2.9",
            "renewable_electric_option": "None",
            "appliance_option": Appliances.OPTION_7p1.value,
            "conditioned_floor_area": 2222,
            "water_heating_fuel": "Electric",
            "thermostat_type": "ecobee4",
            "fireplace_efficiency": "None",
            "wall_cavity_r_value": 40,
            "wall_continuous_r_value": 40,
            "framing_type": "Advanced",
            "window_u_value": 0.1,
            "window_shgc": 1.0,
            "floor_cavity_r_value": 60,
            "slab_perimeter_r_value": 40,
            "under_slab_r_value": 40,
            "ceiling_r_value": 60,
            "raised_heel": "Yes",
            "total_ua_alternative": 100.0,
            "air_leakage_ach": 0.1,
            "ventilation_type": "HRV/ERV",
            "ventilation_brand": "fsd",
            "ventilation_model": "sfd",
            "hrv_asre": 90.0,
            "furnace_brand": "fdas",
            "furnace_model": "sdf",
            "furnace_afue": 99,
            "furnace_location": "Unconditioned Space",
            "duct_location": "Deeply Buried",
            "duct_leakage": 1,
            "dwhr_installed": "Yes",
            "water_heater_brand": "asd",
            "water_heater_model": "fdsa",
            "electric_water_heater_uef": 5.0,
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        calculator = serializer.calculator
        # self.dump_assertions(calculator, basic_only=True)

        self.assertEqual(calculator.summary_data["conditioned_floor_area"], 2222)
        self.assertEqual(calculator.summary_data["water_heating_fuel"], "Electric")
        self.assertEqual(calculator.summary_data["thermostat_type"], "ecobee4")
        self.assertEqual(calculator.summary_data["fireplace_efficiency"], "None")
        self.assertEqual(calculator.summary_data["required_credits_to_meet_code"], 6)
        self.assertEqual(calculator.summary_data["achieved_total_credits"], 10.0)
        self.assertEqual(calculator.summary_data["eligible_gas_points"], 1.5)
        self.assertEqual(calculator.summary_data["total_therm_savings"], 123.0)
        self.assertEqual(calculator.summary_data["code_credit_incentive"], 2400.0)
        self.assertEqual(calculator.summary_data["thermostat_incentive"], 125.0)
        self.assertEqual(calculator.summary_data["fireplace_incentive"], 0.0)
        self.assertEqual(calculator.summary_data["total_builder_incentive"], 2525.0)
        self.assertEqual(calculator.summary_data["verifier_incentive"], 100.0)
        self.assertEqual(calculator.incentive_data["code_credit_incentive"], 2400.0)
        self.assertEqual(calculator.incentive_data["thermostat_incentive"], 125.0)
        self.assertEqual(calculator.incentive_data["fireplace_incentive"], 0.0)
        self.assertEqual(calculator.incentive_data["total_builder_incentive"], 2525.0)
        self.assertEqual(calculator.incentive_data["verifier_incentive"], 100.0)
        self.assertEqual(calculator.savings_data["eligible_gas_points"], 1.5)
        self.assertEqual(calculator.savings_data["code_based_therm_savings"], 102.8351186628498)
        self.assertEqual(calculator.savings_data["thermostat_therm_savings"], 20.16)
        self.assertEqual(calculator.savings_data["fireplace_therm_savings"], 0.0)
        self.assertEqual(calculator.savings_data["total_therm_savings"], 122.99511866284979)

    def test_gas_eligible_min(self):
        data = {
            "envelope_option": BuildingEnvelope.OPTION_1p7.value,
            "air_leakage_option": AirLeakageControl.OPTION_2p4.value,
            "hvac_option": "3.1: REQUIRED - 95 AFUE",
            "hvac_distribution_option": "4.2: HVAC & Ducts In Conditioned Space",
            "dwhr_option": "5.1: Drain Water Heat Recovery",
            "water_heating_option": "5.6: ELEC - Split HP w/ UEF 2.9",
            "renewable_electric_option": RenewableEnergy.OPTION_6p1c.value,
            "appliance_option": Appliances.OPTION_7p1.value,
            "conditioned_floor_area": 2000,
            "water_heating_fuel": "Electric",
            "thermostat_type": "Programmable",
            "fireplace_efficiency": "None",
            "wall_cavity_r_value": 20,
            "wall_continuous_r_value": 0,
            "framing_type": "Intermediate",
            "window_u_value": 0.3,
            "window_shgc": 0.0,
            "floor_cavity_r_value": 30,
            "slab_perimeter_r_value": 10,
            "under_slab_r_value": 0,
            "ceiling_r_value": 49,
            "raised_heel": "No",
            "air_leakage_ach": 5.0,
            "ventilation_type": "Exhaust Only",
            "ventilation_brand": "adfasd",
            "ventilation_model": "asdfds",
            "hrv_asre": 1.0,
            "furnace_brand": "asdfa",
            "furnace_model": "sadfdsf",
            "furnace_afue": 95,
            "furnace_location": "Unconditioned Space",
            "duct_location": "Unconditioned Space",
            "duct_leakage": 1,
            "dwhr_installed": "No",
            "water_heater_brand": "asdfas",
            "water_heater_model": "asddsa",
            "electric_water_heater_uef": 1.0,
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        calculator = serializer.calculator

        self.assertEqual(calculator.savings_data["eligible_gas_points"], 0.0)

    def test_site_111519(self):
        data = {
            "envelope_option": BuildingEnvelope.OPTION_1p3a.value,
            "air_leakage_option": AirLeakageControl.OPTION_2p4.value,
            "hvac_option": "3.1: REQUIRED - 95 AFUE",
            "hvac_distribution_option": "4.2: HVAC & Ducts In Conditioned Space",
            "dwhr_option": "None",
            "water_heating_option": "5.3: GAS - UEF 0.91 (REQUIRED FOR GAS DHW)",
            "renewable_electric_option": RenewableEnergy.OPTION_6p1a.value,
            "appliance_option": Appliances.OPTION_7p1.value,
            "conditioned_floor_area": 2200,
            "water_heating_fuel": "Gas",
            "thermostat_type": "Programmable + Wi-fi",
            "fireplace_efficiency": "<70 FE",
            "wall_cavity_r_value": 23,
            "wall_continuous_r_value": 0,
            "framing_type": "Advanced",
            "window_u_value": 0.25,
            "window_shgc": 0.3,
            "floor_cavity_r_value": 38,
            "slab_perimeter_r_value": 0,
            "under_slab_r_value": 0,
            "ceiling_r_value": 49,
            "raised_heel": "Yes",
            "air_leakage_ach": 0.6,
            "ventilation_type": "HRV/ERV",
            "ventilation_brand": "brand",
            "ventilation_model": "model",
            "hrv_asre": 84.0,
            "furnace_brand": "brand",
            "furnace_model": "model",
            "furnace_afue": 96,
            "furnace_location": "Conditioned Space",
            "duct_location": "Conditioned Space",
            "duct_leakage": 40,
            "dwhr_installed": "No",
            "water_heater_brand": "brand",
            "water_heater_model": "model",
            "gas_water_heater_uef": 0.99,
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        calculator = serializer.calculator

        # print(self.dump_assertions(calculator, basic_only=True))

        self.assertEqual(calculator.summary_data["conditioned_floor_area"], 2200)
        self.assertEqual(calculator.summary_data["water_heating_fuel"], "Gas")
        self.assertEqual(calculator.summary_data["thermostat_type"], "Programmable + Wi-fi")
        self.assertEqual(calculator.summary_data["fireplace_efficiency"], "<70 FE")
        self.assertEqual(calculator.summary_data["required_credits_to_meet_code"], 6)
        self.assertEqual(calculator.summary_data["achieved_total_credits"], 7.0)
        self.assertEqual(calculator.summary_data["eligible_gas_points"], 1.0)
        self.assertEqual(calculator.summary_data["total_therm_savings"], 68.56)
        self.assertEqual(calculator.summary_data["code_credit_incentive"], 1600.0)
        self.assertEqual(calculator.summary_data["thermostat_incentive"], 0.0)
        self.assertEqual(calculator.summary_data["fireplace_incentive"], 0.0)
        self.assertEqual(calculator.summary_data["total_builder_incentive"], 1600.0)
        self.assertEqual(calculator.summary_data["verifier_incentive"], 100.0)

    def test_gas_heat_electric_option_dnq(self):
        input_data = {
            "envelope_option": BuildingEnvelope.OPTION_1p7.value,
            "air_leakage_option": AirLeakageControl.OPTION_2p4.value,
            "hvac_option": HighEfficiencyHVAC.OPTION_3p1.value,
            "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p2.value,
            "dwhr_option": DWHR.OPTION_5p1.value,
            "water_heating_option": EfficientWaterHeating.OPTION_5p4.value,
            "renewable_electric_option": RenewableEnergy.OPTION_6p1c.value,
            "appliance_option": Appliances.OPTION_7p1.value,
            "conditioned_floor_area": 2000,
            "water_heating_fuel": WACCFuelType.GAS,
            "thermostat_type": ThermostatType.PROGRAMABLE.value,
            "fireplace_efficiency": FireplaceType.NONE.value,
            "wall_cavity_r_value": 20,
            "wall_continuous_r_value": 0,
            "framing_type": FramingType.INTERMEDIATE.value,
            "window_u_value": 0.3,
            "window_shgc": 0.0,
            "floor_cavity_r_value": 30,
            "slab_perimeter_r_value": 10,
            "under_slab_r_value": 0,
            "ceiling_r_value": 49,
            "raised_heel": YesNo.NO,
            "air_leakage_ach": 5.0,
            "ventilation_type": VentilationType.EXHAUST_ONLY.value,
            "ventilation_brand": "asfd",
            "ventilation_model": "sdaf",
            "hrv_asre": 1.0,
            "furnace_brand": "dfs",
            "furnace_model": "sfd",
            "furnace_afue": 95,
            "furnace_location": FurnaceLocation.UNCONDITIONED_SPACE.value,
            "duct_location": DuctLocation.UNCONDITIONED_SPACE.value,
            "duct_leakage": 1,
            "dwhr_installed": YesNo.NO.value,
            "water_heater_brand": "fdas",
            "water_heater_model": "afds",
            "gas_water_heater_uef": 1.0,
            "electric_water_heater_uef": 1.0,
        }
        serializer = self.serializer_class(data=input_data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        calculator = serializer.calculator
        self.assertEqual(calculator.incentive_data["code_credit_incentive"], 0.0)
        self.assertEqual(calculator.incentive_data["thermostat_incentive"], 0.0)
        self.assertEqual(calculator.incentive_data["fireplace_incentive"], 0.0)
        self.assertEqual(calculator.incentive_data["total_builder_incentive"], 0.0)
        self.assertEqual(calculator.incentive_data["verifier_incentive"], 0.0)
        self.assertEqual(calculator.savings_data["eligible_gas_points"], 0.0)
        self.assertEqual(calculator.savings_data["code_based_therm_savings"], 0.0)
        self.assertEqual(calculator.savings_data["thermostat_therm_savings"], 0.0)
        self.assertEqual(calculator.savings_data["fireplace_therm_savings"], 0.0)
        self.assertEqual(calculator.savings_data["total_therm_savings"], 0.0)
