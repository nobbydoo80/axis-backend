"""eto_2019.py: Django """

__author__ = "Steven K"
__date__ = "12/17/2019 13:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from unittest import mock

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.home.models import EEPProgramHomeStatus, Home

log = logging.getLogger(__name__)


class EEPProgramETO2019ProgramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for ETO 2019 eep_program"""

    client_class = AxisClient

    @mock.patch("axis.home.utils.get_eps_data")
    def test_get_eto_builder_incentive_status_passing_status(self, get_eps_data):
        """Test for get_eto_builder_incentive_status"""
        data = {"builder_incentive": 11.0}
        get_eps_data.return_value = data
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_legacy_builder_incentive_status(home_status, "edit_utl")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_eto_min_program_version_no_floorplan(self):
        """Test for get_eto_min_program_version. home_status has NO floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_eto_min_program_version(home_status.home, home_status)
        self.assertIsNone(result)

    def test_get_eto_min_program_version_no_remrate_target(self):
        """Test for get_eto_min_program_version"""
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_min_program_version(home_status.home, home_status)
        self.assertIsNone(result)

    def test_get_eto_min_program_version_wrong_simulation_version(self):
        """
        Test for get_eto_min_program_version. simulation version != (15, 7, 1)
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__version": "15.3.0"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        kwargs = {"edit_url": "edit_url"}
        self.assertNotEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        result = eep_program.get_eto_min_program_version(home_status.home, home_status, **kwargs)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn(
            'REM data must be version 15.7.1 and flavor "rate" (national).', result.message
        )

    def test_get_eto_min_program_version_wrong_flavor(self):
        """
        Test for get_eto_min_program_version. simulation  flavor != 'rate'
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__version": "15.7.1", "remrate_target__flavor": ""}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        kwargs = {"edit_url": "edit_url"}
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        result = eep_program.get_eto_min_program_version(home_status.home, home_status, **kwargs)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn(
            'REM data must be version 15.7.1 and flavor "rate" (national).', result.message
        )

    def test_get_eto_min_program_version_passing_status(self):
        """Test for get_eto_min_program_version."""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__version": "15.7.1"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        kwargs = {"edit_url": "edit_url"}
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        self.assertEqual(floorplan.remrate_target.flavor, "rate")
        result = eep_program.get_eto_min_program_version(home_status.home, home_status, **kwargs)
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertEqual(floorplan.remrate_target.numerical_version, result.data)

    def test_get_remrate_udhr_check_no_floorplan(self):
        """Test for get_remrate_udhr_check. home_status has NO floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_remrate_udhr_check(home_status, "")
        self.assertIsNone(result)

    def test_get_remrate_udhr_check_no_remrate_target(self):
        """Test get_remrate_udhr_check. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_udhr_check(home_status, "")
        self.assertIsNone(result)

    def test_get_remrate_udhr_check_wrong_simulation_version(self):
        """
        Test for get_remrate_udhr_check. simulation version != (15, 7, 1)
        Expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__version": "15.3.0"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertNotEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        result = eep_program.get_remrate_udhr_check(home_status, "")
        self.assertIsNone(result)

    def test_get_remrate_udhr_check_simulation_udrh_checksum_none(self):
        """
        Test for get_remrate_udhr_check. Unable to get simulation udrh_checksum from floorplan
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__version": "15.7.1"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        self.assertIsNone(floorplan.remrate_target.udrh_checksum)
        result = eep_program.get_remrate_udhr_check(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)

    def test_get_remrate_udhr_check_invalid_simulation_udrh_checksum(self):
        """
        Test for get_remrate_udhr_check. Unable to get simulation udrh_checksum from floorplan
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__version": "15.7.1",
            "remrate_target__udrh_checksum": "sBRChk3453",
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        self.assertIsNotNone(floorplan.remrate_target.udrh_checksum)
        result = eep_program.get_remrate_udhr_check(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Incorrect UDRH associated with as built home. Repeat the UDRH export from REM "
            "and attach to home"
        )
        self.assertEqual(msg, result.message)

    def test_get_remrate_udhr_check_invalid_simulation_udrh_file(self):
        """
        Test for get_remrate_udhr_check. Unable to get simulation udrh_checksum from floorplan
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        eep_program.slug = "eto-2019"
        eep_program.save()
        kwargs = {
            "remrate_target__version": "15.7.1",
            "remrate_target__udrh_checksum": "5FA1D9E5",
            "remrate_target__udrh_filename": "2019-SWWA EPS-REMv15.7-Final.udr",
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        self.assertIsNotNone(floorplan.remrate_target.udrh_checksum)
        result = eep_program.get_remrate_udhr_check(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Incorrect UDRH File used - expected OR Central 2019-Final.udr. "
            "This is verified via checksum"
        )
        self.assertEqual(msg, result.message)

    def test_get_remrate_udhr_check_passing_status(self):
        """
        Test for get_remrate_udhr_check. Unable to get simulation udrh_checksum from floorplan
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        eep_program.slug = "eto-2019"
        eep_program.save()
        kwargs = {
            "remrate_target__version": "15.7.1",
            "remrate_target__udrh_checksum": "5FA1D9E5",
            "remrate_target__udrh_filename": "OR Central 2019-Final.udr",
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        self.assertIsNotNone(floorplan.remrate_target.udrh_checksum)
        result = eep_program.get_remrate_udhr_check(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_verify_approved_utility_company_not_allowed(self):
        """
        Test for _verify_approved_utility. utility company's slug is NOT in the ETO_2019_FUEL_RATES
        expected Failing Status
        """
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        utility = Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE).get(
            name="Utility1"
        )
        fuel_rates = dict(ETO_2019_FUEL_RATES)
        self.assertIsNone(fuel_rates.get(utility.slug))
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        label = "test_label"
        result = eep_program._verify_approved_utility(home_status, utility, label, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "{company} is not an allowed {type} company".format(company=utility, type=label)
        self.assertEqual(msg, result.message)

    def test_verify_approved_utility_passing_status(self):
        """
        Test for _verify_approved_utility. utility company's slug is in the ETO_2019_FUEL_RATES
        expected Passing Status
        """
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE, name="Utility1").update(
            slug=ETO_2019_FUEL_RATES[0][0]
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        utility = Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE).get(
            name="Utility1"
        )
        fuel_rates = dict(ETO_2019_FUEL_RATES)
        self.assertIsNotNone(fuel_rates.get(utility.slug))
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        label = "test_label"
        result = eep_program._verify_approved_utility(home_status, utility, label, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_verify_approved_utility_company_not_allowed_wa_state(self):
        """
        Test for _verify_approved_utility. home_status' home state is 'WA'
        utility company's slug is NOT in the ETO_2019_FUEL_RATES_WA_OVERRIDE
        expected Failing Status
        """
        from axis.customer_eto.calculator.eps import (
            ETO_2019_FUEL_RATES,
            ETO_2019_FUEL_RATES_WA_OVERRIDE,
        )

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("WA", home_status.home.state)
        utility = Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE).get(
            name="Utility1"
        )
        fuel_rates = dict(ETO_2019_FUEL_RATES)
        fuel_rates.update(dict(ETO_2019_FUEL_RATES_WA_OVERRIDE))
        self.assertIsNone(fuel_rates.get(utility.slug))
        label = "test_label"
        result = eep_program._verify_approved_utility(home_status, utility, label, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "{company} is not an allowed {type} company".format(company=utility, type=label)
        self.assertEqual(msg, result.message)

    def test_verify_approved_utility_passing_status_wa_state(self):
        """
        Test for _verify_approved_utility. home_status' home state is 'WA'
        utility company's slug is in the ETO_2019_FUEL_RATES_WA_OVERRIDE
        expected Failing Status
        """
        from axis.customer_eto.calculator.eps import (
            ETO_2019_FUEL_RATES,
            ETO_2019_FUEL_RATES_WA_OVERRIDE,
        )

        Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE, name="Utility1").update(
            slug="nw-natural-gas"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("WA", home_status.home.state)
        utility = Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE).get(
            name="Utility1"
        )
        fuel_rates = dict(ETO_2019_FUEL_RATES)
        fuel_rates.update(dict(ETO_2019_FUEL_RATES_WA_OVERRIDE))
        self.assertIsNotNone(fuel_rates.get(utility.slug))
        label = "test_label"
        result = eep_program._verify_approved_utility(home_status, utility, label, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_eto_2019_approved_utility_gas_utility_no_utility(self):
        """Test for get_eto_2019_approved_utility_gas_utility"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        utility = home_status.get_gas_company()
        self.assertIsNone(utility)
        result = eep_program.get_eto_2019_approved_utility_gas_utility(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_eto_2019_approved_utility_gas_utility_failing_status(self):
        """Test for get_eto_2019_approved_utility_gas_utility"""
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        utility = home_status.get_gas_company()
        self.assertIsNotNone(utility)
        fuel_rates = dict(ETO_2019_FUEL_RATES)
        self.assertIsNone(fuel_rates.get(utility.slug))
        result = eep_program.get_eto_2019_approved_utility_gas_utility(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)

    def test_get_eto_2019_approved_utility_gas_utility_passing_status(self):
        """Test for get_eto_2019_approved_utility_gas_utility"""
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        utility = home_status.get_gas_company()
        self.assertIsNotNone(utility)
        Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE, name=utility.name).update(
            slug=ETO_2019_FUEL_RATES[0][0]
        )
        result = eep_program.get_eto_2019_approved_utility_gas_utility(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_eto_2019_approved_utility_electric_utility_no_utility(self):
        """Test for get_eto_2019_approved_utility_electric_utility"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        utility = home_status.get_electric_company()
        self.assertIsNone(utility)
        result = eep_program.get_eto_2019_approved_utility_electric_utility(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_eto_2019_approved_utility_electric_utility_failing_status(self):
        """Test for get_eto_2019_approved_utility_gas_utility"""
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        utility = home_status.get_electric_company()
        self.assertIsNotNone(utility)
        fuel_rates = dict(ETO_2019_FUEL_RATES)
        self.assertIsNone(fuel_rates.get(utility.slug))
        result = eep_program.get_eto_2019_approved_utility_electric_utility(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)

    def test_get_eto_2019_approved_utility_electric_utility_passing_status(self):
        """Test for get_eto_2019_approved_utility_gas_utility"""
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        utility = home_status.get_electric_company()
        self.assertIsNotNone(utility)
        Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE, name=utility.name).update(
            slug=ETO_2019_FUEL_RATES[0][0]
        )
        result = eep_program.get_eto_2019_approved_utility_electric_utility(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
