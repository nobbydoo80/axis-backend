"""eto_2020.py: Django """


__author__ = "Steven K"
__date__ = "12/17/2019 13:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from simulation.enumerations import SourceType

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.home.models import EEPProgramHomeStatus, Home
from axis.customer_eto.calculator.eps.constants.eto_2020 import (
    ETO_2020_FUEL_RATES,
    ETO_2020_FUEL_RATES_WA_OVERRIDE,
)
from axis.floorplan.tests.factories import (
    floorplan_with_simulation_factory,
)


log = logging.getLogger(__name__)


class EEPProgramETO2020ProgramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for ETO 2020 eep_program"""

    client_class = AxisClient

    # NOTE PROGRAM CHECKS VERIFIED IN THE eto/tests/program_checks FOLDER

    def test_get_eto_approved_utility_gas_utility_failing_status(self):
        """
        Test get_eto_approved_utility_gas_utility for eto-2020, since utility.slug is not in ETO_2020_FUEL_RATES,
         we expect FailingStatusTuple
        """
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        self.assertNotIn(utility_company.slug, fuel_rates)
        result = eep_program.get_eto_approved_utility_gas_utility(home_status, "home_url")
        self.assertFalse(result.status)

    def test_get_eto_approved_utility_gas_utility_wa_state_failing_status(self):
        """
        Test get_eto_approved_utility_gas_utility for eto-2020, since utility.slug is in ETO_2020_FUEL_RATES or
        ETO_2020_FUEL_RATES_WA_OVERRIDE, we expect FailingStatusTuple
        """
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        self.assertNotIn(utility_company.slug, fuel_rates)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program.get_eto_approved_utility_gas_utility(home_status, "home_url")
        self.assertFalse(result.status)

    def test_get_eto_approved_utility_gas_utility_passing_status(self):
        """
        Test get_eto_approved_utility_gas_utility for eto-2020, since utility.slug is in ETO_2020_FUEL_RATES,
         we expect FailingStatusTuple
        """
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        utility_slug = random.choice(list(fuel_rates.keys()))
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        result = eep_program.get_eto_approved_utility_gas_utility(home_status, "home_url")
        self.assertTrue(result.status)

    def test_get_eto_approved_utility_gas_utility_wa_state_passing_status(self):
        """
        Test get_eto_approved_utility_gas_utility for eto-2020,  home_status.home.state = 'WA',
        since utility.slug is in ETO_2020_FUEL_RATES_WA_OVERRIDE, we expect PassingStatusTuple
        """
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))
        utility_slug = random.choice(list(fuel_rates.keys()))
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program.get_eto_approved_utility_gas_utility(home_status, "home_url")
        self.assertTrue(result.status)

    def test_get_eto_approved_utility_electric_utility_failing_status(self):
        """Test get_eto_approved_utility_electric_utility"""
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        self.assertNotIn(utility_company.slug, fuel_rates)
        result = eep_program.get_eto_approved_utility_electric_utility(home_status, "home_url")
        self.assertFalse(result.status)

    def test_get_eto_approved_utility_electric_utility_passing_status(self):
        """
        Test get_eto_approved_utility_electric_utility for eto-2020, since utility.slug is in ETO_2020_FUEL_RATES,
         we expect FailingStatusTuple
        """
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        utility_slug = ETO_2020_FUEL_RATES[random.randint(0, len(ETO_2020_FUEL_RATES) - 1)][0]
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_electric_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        result = eep_program.get_eto_approved_utility_electric_utility(home_status, "home_url")
        self.assertTrue(result.status)

    def test_get_eto_approved_utility_electric_utility_wa_state_passing_status(self):
        """
        Test get_eto_approved_utility_electric_utility for eto-2020,  home_status.home.state = 'WA',
        since utility.slug is in ETO_2020_FUEL_RATES_WA_OVERRIDE, we expect PassingStatusTuple
        """
        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_slug = ETO_2020_FUEL_RATES_WA_OVERRIDE[
            random.randint(0, len(ETO_2020_FUEL_RATES_WA_OVERRIDE) - 1)
        ][0]
        utility_company = home_status.get_electric_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program.get_eto_approved_utility_electric_utility(home_status, "home_url")
        self.assertTrue(result.status)

    def test_get_eto_electric_heated_utility_check_(self):
        """Test get_eto_electric_heated_utility_check, primary_heat_type is None, expected result None"""
        input_values = {
            "us_state": "WA",
            "electric_utility": "sno-pud",
            "gas_utility": "puget-sound-energy",
        }
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        result = eep_program.get_eto_electric_heated_utility_check(
            home_status, input_values, "edit_url"
        )
        self.assertIsNone(result)

    def test_get_eto_electric_heated_utility_check_failing(self):
        """
        Test get_eto_electric_heated_utility_check, 'primary-heating-equipment-type' contains the word electric,
        but the electric_utility.slug not in ['pacific-power', 'portland-electric']
        """
        input_values = {"primary-heating-equipment-type": "electric-something"}
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_electric_company()
        self.assertNotIn(utility_company.slug, ["pacific-power", "portland-electric"])
        result = eep_program.get_eto_electric_heated_utility_check(
            home_status, input_values, "edit_url"
        )
        self.assertFalse(result.status)

    def test_get_eto_electric_heated_utility_check_passing_status(self):
        """
        Test get_eto_electric_heated_utility_check, 'primary-heating-equipment-type' does NOT contains the word
        electric, expected result passing status
        """
        input_values = {"primary-heating-equipment-type": "Gas Furnace"}
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        result = eep_program.get_eto_electric_heated_utility_check(
            home_status, input_values, "edit_url"
        )
        self.assertIsNone(result)

    def test_get_eto_electric_heated_utility_check_electric_equipment_passing_status(self):
        """
        Test get_eto_electric_heated_utility_check, 'primary-heating-equipment-type' contains the word electric,
        but the electric_utility.slug in ['pacific-power', 'portland-electric'], expected result passing status
        """
        input_values = {"primary-heating-equipment-type": "electric-something"}
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_electric_company()
        utility_company.slug = "portland-electric"
        utility_company.save()
        result = eep_program.get_eto_electric_heated_utility_check(
            home_status, input_values, "edit_url"
        )
        self.assertTrue(result.status)

    def test_get_eto_2020_no_multifamily_failing_status_for_multifamily_home(self):
        """Test for get_eto_no_multifamily. home is multifamily. expected Failing Status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        Home.objects.filter(id=home_status.home.id).update(is_multi_family=True)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.home.is_multi_family)
        kwargs = {"home_edit_url": "home_edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertFalse(result.status)
        self.assertEqual("Home must not be designated as multifamily.", result.message)

    def test_get_eto_2020_no_multifamily_no_floorplan(self):
        """
        Test for get_eto_no_multifamily. passed home_status argument has NO floorplan.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        self.assertFalse(home_status.home.is_multi_family)
        kwargs = {"home_edit_url": "home_edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertIsNone(result)

    def test_get_eto_2020_no_multifamily_rem_not_multifamily(self):
        """
        Test for get_eto_no_multifamily. passed home_status argument has floorplan & remrate,
        but building type is NOT "Multi-family, whole building" or building_type != 6
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.home.is_multi_family)
        kwargs = {"home_edit_url": "home_edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertIsNone(result)

    def test_get_eto_2020_no_multifamily_rem_multifamily(self):
        """
        Test for get_eto_no_multifamily. passed home_status argument has floorplan & remrate,
        but building type is "Multi-family, whole building" or building_type == 6
        expected back Failing Status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__building_info__type": 6}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.home.is_multi_family)
        kwargs = {"edit_url": "edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertIsNotNone(result)
        self.assertEqual("REM building type must not be designated as multifamily.", result.message)

    def test_get_remrate_udhr_check_invalid_simulation_udrh_file(self):
        """
        Test for get_remrate_udhr_check. Unable to get simulation udrh_checksum from floorplan
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        eep_program.slug = "eto-2020"
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
            "Incorrect UDRH associated with as built home. Repeat the UDRH "
            "export from REM and attach to home"
        )
        self.assertEqual(msg, result.message)

    def test_get_remrate_udhr_check_passing_status(self):
        """
        Test for get_remrate_udhr_check. Unable to get simulation udrh_checksum from floorplan
        Expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        eep_program.slug = "eto-2020"
        eep_program.save()
        kwargs = {
            "remrate_target__version": "15.7.1",
            "remrate_target__udrh_checksum": "7EFE1FE0",
            "remrate_target__udrh_filename": "OR Perf Path Zonal 2020-Final.udr",
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))
        self.assertIsNotNone(floorplan.remrate_target.udrh_checksum)
        result = eep_program.get_remrate_udhr_check(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_min_simulation_version(self):
        """Tests that our minimum verision for Eko and REM work"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        eep_program.slug = "eto-2020"
        eep_program.save()
        kwargs = {
            "simulation__source_type": random.choice([SourceType.REMRATE_SQL, SourceType.EKOTROPE]),
            "simulation__flavor": "Rate",
            "simulation__version": "99.99.99",
            "simulation__all_electric": True,
        }
        floorplan = floorplan_with_simulation_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIn(
            floorplan.simulation.source_type, [SourceType.REMRATE_SQL, SourceType.EKOTROPE]
        )

        result = eep_program.get_min_max_simulation_version(home_status, edit_url="foo")
        self.assertTrue(result.status)

        floorplan.simulation.version = "0.0.0"
        floorplan.simulation.save()

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_min_max_simulation_version(home_status, edit_url="foo")
        self.assertFalse(result.status)
        self.assertIn("Simulation data must be REM >=", result.message)
