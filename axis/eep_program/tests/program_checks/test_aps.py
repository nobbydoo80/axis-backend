"""aps.py: Django eep_program program checks tests"""


__author__ = "Johnny Fang"
__date__ = "16/7/19 3:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]


import logging
import random
from unittest import mock

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_aps.strings import APS_PROGRAM_SLUGS
from axis.eep_program import strings
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import eep_program_custom_home_status_factory

log = logging.getLogger(__name__)


class EEPProgramAPSProgramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for APS eep_program"""

    client_class = AxisClient

    def test_get_aps_double_payment_status_for_abandoned_program(self):
        """
        Test for get_aps_double_payment_status(). Scenario where
        home_status.state == 'abandoned'
        """
        slug = APS_PROGRAM_SLUGS[random.randint(0, len(APS_PROGRAM_SLUGS) - 1)]
        eep_program = EEPProgram.objects.get(owner__name="EEP3", is_qa_program=False)
        eep_program.slug = slug
        eep_program.save()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(state="abandoned")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        result = eep_program.get_aps_double_payment_status(home_status)

        self.assertIsNone(result)

    def test_get_aps_double_payment_status_duplicate_aps_program(self):
        """
        Test for get_aps_double_payment_status().
        Scenario where home_status attributes home and eep_program__owner are duplicate. Keep in
        mind that home_status has the requirement of  unique_together = ('home', 'eep_program').
        """
        slug = APS_PROGRAM_SLUGS[random.randint(0, len(APS_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        home = home_status.home
        kwargs = {"owner": home_status.eep_program.owner}
        basic_eep_program = basic_eep_program_factory(**kwargs)
        kwargs = {"home": home, "eep_program": basic_eep_program, "company": eep_program.owner}
        eep_program_custom_home_status_factory(**kwargs)
        result = eep_program.get_aps_double_payment_status(home_status)

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("has already been assigned", result.message)

    def test_get_aps_double_payment_status_passing(self):
        """
        Test for get_aps_double_payment_status().
        Scenario where  we have programs with same home but different eep_program__owner.
        Keep in mind that home_status has the requirement of
        unique_together = ('home', 'eep_program').
        """
        slug = APS_PROGRAM_SLUGS[random.randint(0, len(APS_PROGRAM_SLUGS) - 1)]
        eep_program = EEPProgram.objects.get(owner__name="EEP3", is_qa_program=False)
        eep_program.slug = slug
        eep_program.save()

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        home = home_status.home
        basic_eep_program = basic_eep_program_factory()
        kwargs = {"home": home, "eep_program": basic_eep_program, "company": eep_program.owner}
        eep_program_custom_home_status_factory(**kwargs)
        result = eep_program.get_aps_double_payment_status(home_status)

        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_aps_double_payment_status_legacy_aps_home(self):
        """
        Test for get_aps_double_payment_status().
        Scenario for home has APSHome  AND LegacyAPSHome has APSHome and eep_program
        """
        from axis.customer_aps.models import APSHome, LegacyAPSHome

        slug = APS_PROGRAM_SLUGS[random.randint(0, len(APS_PROGRAM_SLUGS) - 1)]
        eep_program = EEPProgram.objects.get(owner__name="EEP3", is_qa_program=False)
        eep_program.slug = slug
        eep_program.save()

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        home = home_status.home

        aps_home = APSHome(home=home)
        aps_home.save()
        legacy_aps_home = LegacyAPSHome(aps_home=aps_home, eep_program=eep_program)
        legacy_aps_home.save()

        result = eep_program.get_aps_double_payment_status(home_status)

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("This project already has a legacy payment on it", result.message)

    def test_get_aps_calculator_home_status_state_complete(self):
        """Test for get_aps_calculator_status(). eep_program state is 'complete'"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3", is_qa_program=False)
        eep_program.slug = APS_PROGRAM_SLUGS[5]
        eep_program.save()

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(state="complete")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_aps_calculator_status(home_status, "edit_url")

        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_aps_calculator_status_aps_input_exception(self):
        """Test for get_aps_calculator_status(). eep_program state is 'complete'"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3", is_qa_program=False)
        eep_program.slug = APS_PROGRAM_SLUGS[5]
        eep_program.save()

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.state == "complete")
        result = eep_program.get_aps_calculator_status(home_status, "edit_url")

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("APS is not the utility defined on home", result.message)

    @mock.patch("axis.customer_aps.aps_calculator.calculator.APSCalculator")
    def test_get_aps_calculator_status_calc_warning(self, aps_alculator):
        """Test for get_aps_calculator_status()."""

        aps_alculator.warnings = "something"
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=APS_PROGRAM_SLUGS[5])
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_aps_calculator_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)

    def test_get_aps_2019_estar_check_no_floorplan(self):
        """Test for get_aps_2019_estar_check. home_status has no floorplan. expected back None"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4", is_qa_program=False)
        eep_program.slug = APS_PROGRAM_SLUGS[5]
        eep_program.save()

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_aps_2019_estar_check(home_status, "")
        self.assertIsNone(result)

    def test_get_aps_2019_estar_check_no_remrate_or_ekotrope_houseplan(self):
        """
        Test for get_aps_2019_estar_check.
        home_status' floorplan has NO remrate or ekotrope_houseplan
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4", is_qa_program=False)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan.remrate_target)
        self.assertFalse(home_status.floorplan.ekotrope_houseplan)
        result = eep_program.get_aps_2019_estar_check(home_status, "")
        self.assertIsNone(result)

    def test_get_aps_2019_estar_check_simulation_fails_energy_start_v3(self):
        """
        Test for get_aps_2019_estar_check.
        home_status' floorplan remrate passes_energy_star_v3 is False or None
        expected back Warning Status, status = False
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4", is_qa_program=False)
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan.simulation_passes_energy_star_v3)
        result = eep_program.get_aps_2019_estar_check(home_status, "")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(strings.APS_2019_FAILING_REM_ESTAR, result.message)

    def test_get_aps_2019_estar_check_simulation_passes_energy_start_v3(self):
        """
        Test for get_aps_2019_estar_check.
        home_status' floorplan remrate passes_energy_star_v3 is True
        expected back Passing status
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4", is_qa_program=False)
        kwargs = {"remrate_target__energystar__passes_energy_star_v3": True}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan.remrate_target)
        result = eep_program.get_aps_2019_estar_check(home_status, "")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_get_aps_2019_estar_check_simulation_fails_ekotrope(self, import_project_tree):
        """
        Test for get_aps_2019_estar_check.
        home_status' floorplan ekotrope_houseplan has no analysis
        expected back Warning Status, status False
        """
        from axis.ekotrope.tests.factories import (
            house_plan_factory,
            project_factory,
            ekotrope_auth_details_factory,
        )
        from axis.floorplan.tests.factories import floorplan_factory
        from axis.core.tests.factories import rater_user_factory

        # prepare data for handling signals when we have ekotrope
        user = rater_user_factory()
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)

        floorplan = floorplan_factory()
        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        eep_program = EEPProgram.objects.get(owner__name="EEP4", is_qa_program=False)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNone(home_status.floorplan.remrate_target)
        self.assertFalse(home_status.floorplan.simulation_passes_energy_star_v3)
        result = eep_program.get_aps_2019_estar_check(home_status, "")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(strings.APS_2019_FAILING_EKOTROPE_ESTAR, result.message)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_get_aps_2019_estar_check_simulation_passing_ekotrope(self, import_project_tree):
        """Test for get_aps_2019_estar_check.        expected back Passing Status"""
        from axis.ekotrope.tests.factories import (
            house_plan_factory,
            project_factory,
            analysis_factory,
            ekotrope_auth_details_factory,
        )
        from axis.floorplan.tests.factories import floorplan_factory
        from axis.core.tests.factories import rater_user_factory

        # prepare data for handling signals when we have ekotrope
        user = rater_user_factory()
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)
        analysis_factory(houseplan=house_plan)

        floorplan = floorplan_factory()
        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        eep_program = EEPProgram.objects.get(owner__name="EEP4", is_qa_program=False)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNone(home_status.floorplan.remrate_target)
        self.assertTrue(home_status.floorplan.simulation_passes_energy_star_v3)
        result = eep_program.get_aps_2019_estar_check(home_status, "")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
