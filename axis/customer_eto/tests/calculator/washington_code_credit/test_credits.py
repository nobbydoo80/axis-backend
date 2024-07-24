"""credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 12:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.test import TestCase

from ....calculator.washington_code_credit.credits import Credits
from ....calculator.washington_code_credit.constants.defaults import (
    BUILDING_ENVELOPE_OPTIONS,
    AIR_LEAKAGE,
    HVAC,
    HVAC_DISTRIBUTION,
    DRAIN_WATER_HEAT_RECOVER,
    HOT_WATER,
    RENEWABLES,
    APPLIANCES,
)
from ....eep_programs.washington_code_credit import (
    BuildingEnvelope,
    AirLeakageControl,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DWHR,
    EfficientWaterHeating,
    RenewableEnergy,
    Appliances,
)

log = logging.getLogger(__name__)


class CreditTests(TestCase):
    @property
    def input_options(self):
        class DummySpec:
            meet_requirements = True
            meets_dwhr_requirements = True
            meets_water_heater_requirements = True

        return {
            "envelope_option": BuildingEnvelope.OPTION_1p6b,
            "air_leakage_option": AirLeakageControl.OPTION_2p4,
            "hvac_option": HighEfficiencyHVAC.OPTION_3p1,
            "hvac_distribution_option": HighEfficiencyHVACDistribution.OPTION_4p2,
            "dwhr_option": DWHR.OPTION_5p1,
            "water_heating_option": EfficientWaterHeating.OPTION_5p3,
            "renewable_electric_option": RenewableEnergy.OPTION_6p1c,
            "appliance_option": Appliances.OPTION_7p1,
            "specifications": {
                "building_envelope": DummySpec(),
                "air_leakage": DummySpec(),
                "hvac": DummySpec(),
                "hvac_distribution": DummySpec(),
                "water": DummySpec(),
            },
        }

    def test_building_envelope_option_credits(self):
        data = self.input_options
        for label, option in BuildingEnvelope.__members__.items():
            data["envelope_option"] = option
            credit = Credits(**data)
            with self.subTest(f"Envelope Option - {label}"):
                target_value = BUILDING_ENVELOPE_OPTIONS[option]["eligible_credits"]
                self.assertEqual(credit.eligible_building_envelope_credits, target_value)
                self.assertEqual(credit.achieved_building_envelope_credits, target_value)
                self.assertNotEqual(credit.achieved_total_credits, 0.0)
                self.assertNotEqual(credit.eligible_total_credits, 0.0)
                self.assertNotIn("DNQ", credit.credit_report)

    def test_air_leakage_option_credits(self):
        data = self.input_options
        for label, option in AirLeakageControl.__members__.items():
            data["air_leakage_option"] = option
            credit = Credits(**data)
            with self.subTest(f"Air Leakage Option eligible_credits - {label}"):
                target_value = AIR_LEAKAGE[option]["eligible_credits"]
                self.assertEqual(credit.eligible_air_leakage_credits, target_value)
                self.assertEqual(credit.achieved_air_leakage_credits, target_value)
                self.assertNotEqual(credit.eligible_total_credits, 0.0)
                self.assertNotEqual(credit.achieved_total_credits, 0.0)
                self.assertNotIn("DNQ", credit.credit_report)

    def test_hvac_option_credits(self):
        data = self.input_options
        for label, option in HighEfficiencyHVAC.__members__.items():
            data["hvac_option"] = option
            credit = Credits(**data)
            with self.subTest(f"HVAC Option eligible_credits - {label}"):
                target_value = HVAC[option]["eligible_credits"]
                self.assertEqual(credit.eligible_hvac_credits, target_value)
                self.assertEqual(credit.achieved_hvac_credits, target_value)
                if str(label) == "OPTION_3p1":
                    self.assertNotEqual(credit.eligible_total_credits, 0.0)
                    self.assertNotEqual(credit.achieved_total_credits, 0.0)
                    self.assertNotIn("DNQ", credit.credit_report)
                else:
                    self.assertEqual(credit.eligible_total_credits, 0.0)
                    self.assertEqual(credit.achieved_total_credits, 0.0)
                    self.assertIn("DNQ", credit.credit_report)

    def test_hvac_distribution_option_credits(self):
        data = self.input_options
        for label, option in HighEfficiencyHVACDistribution.__members__.items():
            data["hvac_distribution_option"] = option
            credit = Credits(**data)
            with self.subTest(f"HVAC Distribution Option eligible_credits - {label}"):
                target_value = HVAC_DISTRIBUTION[option]["eligible_credits"]
                self.assertEqual(credit.eligible_hvac_distribution_credits, target_value)
                self.assertEqual(credit.achieved_hvac_distribution_credits, target_value)
                self.assertNotEqual(credit.eligible_total_credits, 0.0)
                self.assertNotEqual(credit.achieved_total_credits, 0.0)
                self.assertNotIn("DNQ", credit.credit_report)

    def test_dwhr_credits(self):
        data = self.input_options
        for label, option in DWHR.__members__.items():
            data["dwhr_option"] = option
            credit = Credits(**data)
            with self.subTest(f"DWHR Option eligible_credits - {label}"):
                target_value = DRAIN_WATER_HEAT_RECOVER[option]["eligible_credits"]
                self.assertEqual(credit.eligible_dwhr_credits, target_value)
                self.assertEqual(credit.achieved_dwhr_credits, target_value)
                self.assertNotEqual(credit.achieved_total_credits, 0.0)
                self.assertNotEqual(credit.eligible_total_credits, 0.0)
                self.assertNotIn("DNQ", credit.credit_report)

    def test_water_heating_credits(self):
        data = self.input_options
        for label, option in EfficientWaterHeating.__members__.items():
            data["water_heating_option"] = option
            credit = Credits(**data)
            with self.subTest(f"Hot Water Option eligible_credits - {label}"):
                target_value = HOT_WATER[option]["eligible_credits"]
                self.assertEqual(credit.eligible_water_heating_credits, target_value)
                self.assertEqual(credit.achieved_water_heating_credits, target_value)
                if str(label) in ["OPTION_5p2"]:
                    self.assertEqual(credit.eligible_total_credits, 0.0)
                    self.assertEqual(credit.achieved_total_credits, 0.0)
                    self.assertIn("DNQ", credit.credit_report)
                else:
                    self.assertNotEqual(credit.eligible_total_credits, 0.0)
                    self.assertNotEqual(credit.achieved_total_credits, 0.0)
                    self.assertNotIn("DNQ", credit.credit_report)

    def test_renewable_electric_credits(self):
        data = self.input_options
        for label, option in RenewableEnergy.__members__.items():
            data["renewable_electric_option"] = option
            credit = Credits(**data)
            with self.subTest(f"Renewable Option eligible_credits - {label}"):
                target_value = RENEWABLES[option]["eligible_credits"]
                self.assertEqual(credit.eligible_renewable_electric_credits, target_value)
                self.assertEqual(credit.achieved_renewable_electric_credits, target_value)
                self.assertNotEqual(credit.achieved_total_credits, 0.0)
                self.assertNotEqual(credit.eligible_total_credits, 0.0)
                self.assertNotIn("DNQ", credit.credit_report)

    def test_appliance_credits(self):
        data = self.input_options
        for label, option in Appliances.__members__.items():
            data["appliance_option"] = option
            credit = Credits(**data)
            with self.subTest(f"Appliance Option eligible_credits - {label}"):
                target_value = APPLIANCES[option]["eligible_credits"]
                self.assertEqual(credit.eligible_appliances_credits, target_value)
                self.assertEqual(credit.achieved_appliances_credits, target_value)
                self.assertNotEqual(credit.eligible_total_credits, 0.0)
                self.assertNotEqual(credit.achieved_total_credits, 0.0)
                self.assertNotIn("DNQ", credit.credit_report)
