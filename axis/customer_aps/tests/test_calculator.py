"""calculator.py: Django aps"""


import logging

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_aps.aps_calculator.base import APSInputException
from axis.customer_aps.aps_calculator.calculator import APSCalculator
from axis.customer_aps.tests.mixins import (
    CustomerAPS2019ModelTestMixin,
    CustomerAPSModelTestMixin,
)
from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven Klass"
__date__ = "4/6/18 12:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CustomerAPSCalculatorBaseTests(CustomerAPSModelTestMixin, AxisTestCase):
    """APS Incentive Calculator Base tests"""

    client_class = AxisClient

    def test_home_status_only_no_issues(self):
        """Test home status without any issues"""
        stat = EEPProgramHomeStatus.objects.get()
        calculator = APSCalculator(home_status_id=stat.id)
        self.assertEqual(calculator.errors, [])

    def test_fp_only_no_issues(self):
        """Test Calculator Via FP"""
        stat = EEPProgramHomeStatus.objects.get()
        calculator = APSCalculator(floorplan=stat.floorplan, electric_utility="aps", us_state="AZ")
        self.assertEqual(calculator.errors, [])

    def test_home_status_only_no_utility(self):
        """Test Calculator missing utility"""
        stat = EEPProgramHomeStatus.objects.get()
        stat.home.relationships.filter(company__slug="aps").delete()
        self.assertRaises(APSInputException, APSCalculator, home_status_id=stat.id)

        calculator = APSCalculator(home_status_id=stat.id, raise_issues=False)
        self.assertEqual(len(calculator.errors), 1)
        self.assertIn("APS is not the utility", calculator.errors[0])

    def test_fp_no_state(self):
        """Test Calculator missing state"""
        stat = EEPProgramHomeStatus.objects.get()
        self.assertRaises(
            APSInputException, APSCalculator, floorplan=stat.floorplan, electric_utility="aps"
        )

        calculator = APSCalculator(
            floorplan=stat.floorplan, electric_utility="aps", raise_issues=False
        )
        self.assertEqual(len(calculator.errors), 1)
        self.assertIn("State was not", calculator.errors[0])

    def test_program_swap(self):
        """Test Calculator swapping state"""
        kwargs = {
            "gas_utility": None,
            "simulation": {"hers_score": 30, "non_pv_hers_score": 65, "climate_zone": 2},
            "electric_utility": "aps",
            "program": "aps-energy-star-v3-hers-60-2018",
            "us_state": "AZ",
            "climate_zone": 2,
        }

        calculator = APSCalculator(**kwargs.copy())

        self.assertEqual(calculator.climate_zone, 2)
        self.assertEqual(calculator.simulation.hers_score, 30)
        self.assertEqual(calculator.simulation.non_pv_hers_score, 65)
        self.assertEqual(calculator.program, "aps-energy-star-v3-2018")
        self.assertNotEqual(calculator.program, kwargs.get("program"))
        self.assertEqual(calculator.incentives.builder_incentive, 500.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 500.00)
        self.assertEqual(calculator.incentives.has_incentive, True)

    def test_program_allow_80_hers(self):
        """Test Calculator failing on hers of 80+"""
        kwargs = {
            "gas_utility": None,
            "simulation": {"hers_score": 80, "non_pv_hers_score": 81, "climate_zone": 2},
            "electric_utility": "aps",
            "program": "aps-energy-star-v3-2018",
            "us_state": "AZ",
            "climate_zone": 2,
        }

        calculator = APSCalculator(**kwargs.copy())
        self.assertEqual(calculator.errors, [])
        self.assertEqual(calculator.climate_zone, 2)
        self.assertEqual(calculator.simulation.hers_score, 80)
        self.assertEqual(calculator.simulation.non_pv_hers_score, 81)
        self.assertEqual(calculator.program, "aps-energy-star-v3-2018")
        self.assertEqual(calculator.incentives.builder_incentive, 500.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 500.00)
        self.assertEqual(calculator.incentives.has_incentive, True)


class CustomerAPS2019CalculatorBaseTests(CustomerAPS2019ModelTestMixin, AxisTestCase):
    """APS 2019 program options"""

    def test_program_2019_low_hers(self):
        """Test Calculator failing on low hers"""
        # This was reported on home Home Status ID: 90472
        kwargs = {
            "gas_utility": "southwest-gas",
            "simulation": {"hers_score": 55.0, "non_pv_hers_score": 54.0, "climate_zone": 4},
            "electric_utility": "aps",
            "program": "aps-energy-star-v3-2019",
            "us_state": "AZ",
            "climate_zone": None,
        }

        calculator = APSCalculator(**kwargs.copy())

        self.assertEqual(calculator.climate_zone, 4)
        self.assertEqual(calculator.simulation.hers_score, 55.0)
        self.assertEqual(calculator.simulation.non_pv_hers_score, 54.0)
        self.assertEqual(calculator.program, "aps-energy-star-v3-2019")
        self.assertEqual(calculator.incentives.builder_incentive, 200.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 200.00)
        self.assertEqual(calculator.incentives.has_incentive, True)

    def test_program_2019_high_hers(self):
        """Test Calculator failing on high hers"""
        kwargs = {
            "gas_utility": "southwest-gas",
            "simulation": {"hers_score": 120.0, "non_pv_hers_score": 125.0, "climate_zone": 4},
            "electric_utility": "aps",
            "program": "aps-energy-star-v3-2019",
            "us_state": "AZ",
            "climate_zone": None,
        }

        calculator = APSCalculator(**kwargs.copy())

        self.assertEqual(calculator.climate_zone, 4)
        self.assertEqual(calculator.simulation.hers_score, 120.0)
        self.assertEqual(calculator.simulation.non_pv_hers_score, 125.0)
        self.assertEqual(calculator.program, "aps-energy-star-v3-2019")
        self.assertEqual(calculator.incentives.builder_incentive, 200.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 200.00)
        self.assertEqual(calculator.incentives.has_incentive, True)


class CustomerAPS2019TstatCalculatorBaseTests(CustomerAPS2019ModelTestMixin, AxisTestCase):
    """APS 2019 Thermostat program options"""

    def test_program_2019_with_thermostat_complete_option(self):
        """Test Calculator with thermostat option $30 kicker"""
        kwargs = {
            "gas_utility": "southwest-gas",
            "thermostat_option": "complete",
            "thermostat_qty": 2,
            "simulation": {"hers_score": 120.0, "non_pv_hers_score": 125.0, "climate_zone": 4},
            "electric_utility": "aps",
            "program": "aps-energy-star-2019-tstat",
            "us_state": "AZ",
            "climate_zone": None,
        }

        calculator = APSCalculator(**kwargs.copy())
        self.assertEqual(calculator.program, "aps-energy-star-2019-tstat")
        self.assertEqual(calculator.incentives.builder_incentive, 260.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 260.00)
        self.assertEqual(calculator.incentives.has_incentive, True)

    def test_program_2019_with_thermostat_partial_option(self):
        """Test Calculator with thermostat option $30 kicker missing when only partial"""
        kwargs = {
            "gas_utility": "southwest-gas",
            "thermostat_option": "partial",
            "thermostat_qty": 1,
            "simulation": {"hers_score": 120.0, "non_pv_hers_score": 125.0, "climate_zone": 4},
            "electric_utility": "aps",
            "program": "aps-energy-star-2019-tstat",
            "us_state": "AZ",
            "climate_zone": None,
        }

        calculator = APSCalculator(**kwargs.copy())
        self.assertFalse(calculator.errors)
        self.assertEqual(calculator.climate_zone, 4)
        self.assertEqual(calculator.simulation.hers_score, 120.0)
        self.assertEqual(calculator.simulation.non_pv_hers_score, 125.0)
        self.assertEqual(calculator.program, "aps-energy-star-2019-tstat")
        self.assertEqual(calculator.incentives.builder_incentive, 200.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 200.00)
        self.assertEqual(calculator.incentives.has_incentive, True)


class CustomerAPS2019TstatAddonCalculatorBaseTests(CustomerAPS2019ModelTestMixin, AxisTestCase):
    """APS 2019 Thermostat Addon program options"""

    def test_program_2019_with_thermostat_option(self):
        """Test the functionality of the 2019 Thermostat Check"""

        kwargs = {
            "gas_utility": "FOO",
            "thermostat_option": "complete",
            "electric_utility": "aps",
            "program": "aps-energy-star-2019-tstat-addon",
            "us_state": "AZ",
            "simulation": {"hers_score": 120.0, "non_pv_hers_score": 125.0, "climate_zone": 4},
        }

        calculator = APSCalculator(**kwargs.copy())
        self.assertFalse(calculator.errors)
        self.assertEqual(calculator.program, "aps-energy-star-2019-tstat-addon")
        self.assertEqual(calculator.incentives.builder_incentive, 0.00)
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 0.00)
        self.assertEqual(calculator.incentives.has_incentive, False)

        kwargs["thermostat_qty"] = 3
        kwargs["thermostat_option"] = "partial"
        calculator = APSCalculator(**kwargs.copy())
        self.assertFalse(calculator.errors)
        self.assertEqual(calculator.program, "aps-energy-star-2019-tstat-addon")
        self.assertEqual(calculator.incentives.builder_incentive, 30.00 * kwargs["thermostat_qty"])
        self.assertEqual(calculator.incentives.rater_incentive, 0.00)
        self.assertEqual(calculator.incentives.total_incentive, 30.00 * kwargs["thermostat_qty"])
        self.assertEqual(calculator.incentives.has_incentive, True)
