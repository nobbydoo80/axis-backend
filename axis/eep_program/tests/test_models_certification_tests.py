"""test_models_certifications.py: Django eep_program models tests"""


import logging

from django.contrib.auth import get_user_model

from axis.company.models import ProviderOrganization, Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram

from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin, EEPProgramManagerTestMixin
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.home import strings as home_strings
from axis.home.models import EEPProgramHomeStatus, Home

__author__ = "Johnny Fang"
__date__ = "14/6/19 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

from axis.relationship.models import Relationship

log = logging.getLogger(__name__)
User = get_user_model()


class EEPProgramModelCertificationTests(EEPProgramManagerTestMixin, AxisTestCase):
    """Tests for EEPProgram model certification tests"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        super(EEPProgramModelCertificationTests, cls).setUpTestData()
        EEPProgramHomeStatusTestMixin().setUpTestData()

    def test_get_program_certification_eligibility_certification_date(self):
        """
        Test for get_program_certification_eligibility() if home_status (EEPProgramHomeStatus) has
        a certification date, then there is already a certification, so no eligibility for you.
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        url = "edit_url"

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        home_status.certification_date = datetime.datetime.now()
        self.assertIsNotNone(home_status.certification_date)
        result = eep_program.get_program_certification_eligibility(home_status, url)
        self.assertIsNone(result)

    def test_get_program_certification_eligibility_program_start_end_date_equal(self):
        """Now  program_start_date <= today <= end_date: i.e. a program that has expired!!!!"""
        url = "edit_url"
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        # now we don't have a certification date so we MIGHT be eligible for one. if the program
        # start_date is at most today, and its end_date is at least today.
        result = eep_program.get_program_certification_eligibility(home_status, url)
        self.assertIsNone(result)

    def test_get_program_certification_eligibility_program_too_early(self):
        """Now program_start_date > today i.e. program too early!!"""
        import datetime
        from django.utils import formats

        url = "edit_url"
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        eep_program = home_status.eep_program
        eep_program.program_start_date = datetime.date.today() + datetime.timedelta(days=5)
        eep_program.program_end_date = datetime.date.today() + datetime.timedelta(days=10)
        eep_program.save()
        result = eep_program.get_program_certification_eligibility(home_status, url)
        self.assertIsNotNone(result)
        msg = home_strings.PROGRAM_TOO_EARLY.format(
            program=eep_program,
            date=formats.date_format(eep_program.program_start_date, "SHORT_DATE_FORMAT"),
        )
        status, data, message, _url, weight, total_weight, show_data = result
        self.assertFalse(status)
        self.assertFalse(show_data)
        self.assertIsNone(data)
        self.assertEqual(url, _url)
        self.assertEqual(msg, message)
        self.assertEqual(total_weight, 1)
        self.assertEqual(weight, 0)
        self.assertFalse(show_data)

    def test_get_program_certification_eligibility_program_too_late(self):
        """Now program_end_date < today i.e. program too late!!"""
        import datetime
        from django.utils import formats

        url = "edit_url"
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        # let's make program late
        eep_program = home_status.eep_program
        eep_program.program_start_date = datetime.date.today() - datetime.timedelta(days=10)
        eep_program.program_end_date = datetime.date.today() - datetime.timedelta(days=5)
        eep_program.save()
        result = eep_program.get_program_certification_eligibility(home_status, url)
        self.assertIsNotNone(result)
        msg = home_strings.PROGRAM_TOO_LATE.format(
            program=eep_program,
            date=formats.date_format(eep_program.program_end_date, "SHORT_DATE_FORMAT"),
        )
        status, data, message, _url, weight, total_weight, show_data = result
        self.assertFalse(status)
        self.assertFalse(show_data)
        self.assertIsNone(data)
        self.assertEqual(url, _url)
        self.assertEqual(weight, 0)
        self.assertEqual(total_weight, 1)
        self.assertEqual(msg, message)

    def test_get_std_protocol_percent_improvement_status(self):
        """
        Test certifications are blocked if % improvement < 10%
        Test proper message is included with the returned status (Passing/Failing)
        """
        from axis.customer_neea.models import StandardProtocolCalculator

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        url = "edit_url"
        result = eep_program.get_std_protocol_percent_improvement_status(home_status, url)
        self.assertIsNone(result)

        calc_kwargs = {"home_status": home_status}
        calculations = StandardProtocolCalculator(**calc_kwargs)
        calculations.save()
        result = eep_program.get_std_protocol_percent_improvement_status(home_status, url)
        msg = home_strings.PERCENT_IMPROVEMENT_TOO_LOW
        self.assertIsNotNone(result)
        status, data, message, _url, weight, total_weight, show_data = result
        self.assertFalse(status)
        self.assertFalse(show_data)
        self.assertEqual(msg, message)
        self.assertEqual(data, 0)
        self.assertEqual(weight, 0)
        self.assertEqual(total_weight, 1)
        self.assertEqual(url, _url)

        calculations.revised_percent_improvement = 0.101
        calculations.save()
        result = eep_program.get_std_protocol_percent_improvement_status(home_status, url)
        self.assertIsNotNone(result)
        status, data, message, _url, weight, total_weight, show_data = result
        self.assertTrue(status)
        self.assertIsNone(message)

    def test_get_resnet_approved_provider_status_failing(self):
        """Test for get_resnet_approved_provider_status()"""
        from axis.sampleset.tests.factories import empty_sampleset_factory
        from axis.sampleset.models import SampleSetHomeStatus

        rater_co = User.objects.get(company__name="Rater1").company
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(company=rater_co)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        provider = Company.objects.filter_by_company(
            rater_co, company_type=Company.PROVIDER_COMPANY_TYPE
        ).get()
        Relationship.objects.validate_or_create_relations_to_entity(home_status.home, provider)

        url = "edit_url"
        result = eep_program.get_resnet_approved_provider_status(home_status, url)
        self.assertIsNone(result)

        sampleset_kwargs = {"owner": rater_co}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        sampleset_home_status = SampleSetHomeStatus(
            sampleset=sample_set, revision=1, is_active=True, home_status=home_status
        )
        sampleset_home_status.save()

        eep_program.require_resnet_sampling_provider = True
        eep_program.save()

        result = eep_program.get_resnet_approved_provider_status(home_status, url)
        self.assertIsNotNone(result)
        status, data, message, _url, weight, total_weight, show_data = result
        self.assertFalse(status)
        self.assertTrue("not approved" in message)
        self.assertIsNone(data)
        self.assertEqual(total_weight, 1)
        self.assertEqual(weight, 0)
        self.assertEqual(url, _url)
        self.assertFalse(show_data)

    def test_get_resnet_approved_provider_status_passing(self):
        """
        Test for get_resnet_approved_provider_status() In order to get back a passing status
        we need to make sure that:
        EEPProgramHomeStatus and Sampleset are related (through SampleSetHomeStatus)
        RESNETCompany is_sampling_provider and related to our provider company
        last but not least, we MUST create mutual relationship for our actors' companies
        eep_program_home_status, provider, rater
        """

        from axis.resnet.tests.factories import resnet_company_factory
        from axis.sampleset.tests.factories import empty_sampleset_factory
        from axis.sampleset.models import SampleSetHomeStatus
        from axis.relationship.models import Relationship
        from axis.home.tests.factories import home_factory

        url = "edit_url"
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        provider = User.objects.get(company__name="Provider1")
        rater_user = User.objects.get(company__name="Rater1")
        home = home_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company, home=home
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        resnet_kwargs = {"company": provider.company, "is_sampling_provider": True}
        resnet_company_factory(**resnet_kwargs)

        Relationship.objects.create_mutual_relationships(
            home_status.company, provider.company, rater_user.company
        )

        sampleset_kwargs = {"owner": provider.company}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        sampleset_home_status = SampleSetHomeStatus(
            sampleset=sample_set, revision=1, is_active=True, home_status=home_status
        )
        sampleset_home_status.save()

        eep_program.require_resnet_sampling_provider = True
        eep_program.save()

        result = eep_program.get_resnet_approved_provider_status(home_status, url)
        self.assertIsNotNone(result)
        status, data, message, _url, weight, total_weight, show_data = result
        self.assertTrue(status)
        self.assertIsNone(message)
        self.assertIsNone(data)
        self.assertIsNone(_url)
        self.assertEqual(total_weight, 1)
        self.assertEqual(weight, 1)
        self.assertFalse(show_data)

    def test_get_eps_calculator_status_no_utilities(self):
        """
        Test for get_eps_calculator_status home_status has no electric and
        gas utilities
        """
        edit_url = "edit_url"
        co_url = "companies_edit_url"
        checklist_url = "checklist_url"
        provider = User.objects.get(company__name="Provider1")
        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        self.assertIn(eep_program.slug, ["eto-2017", "eto-2018"])

        result = eep_program.get_eps_calculator_status(
            home_status, checklist_url, edit_url, co_url, "input_values"
        )

        self.assertIsNone(result)

    def test_get_eps_calculator_status_no_remrate_target(self):
        """
        Test for get_eps_calculator_status(). home_status's floorplan has no remrate. expected
        result: None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        edit_url = "edit_url"
        co_url = "companies_edit_url"
        checklist_url = "checklist_url"
        provider = User.objects.get(company__name="Provider1")
        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company, floorplan=floorplan
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        result = eep_program.get_eps_calculator_status(
            home_status, checklist_url, edit_url, co_url, "input_values"
        )
        self.assertIsNone(result)

    def test_get_eps_calculator_status_eto_bad_remrate_type(self):
        """
        Test for get_eps_calculator_status() home_status' remrate_target.export_type is not the
        correct type (expected type is 4)
        """
        edit_url = "edit_url"
        co_url = "companies_edit_url"
        checklist_url = "checklist_url"
        provider = User.objects.get(company__name="Provider1")

        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        # bad REM/Rate type
        kwargs = {"remrate_target__export_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertNotEqual(floorplan.remrate_target.export_type, 4)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company, floorplan=floorplan
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        result = eep_program.get_eps_calculator_status(
            home_status, checklist_url, edit_url, co_url, "input_values"
        )

        self.assertIsNotNone(result)
        msg = home_strings.ETO_BAD_REMRATE_TYPE
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(msg, result.message)
        self.assertFalse(result.show_data)
        self.assertIsNone(result.data)
        self.assertEqual(edit_url, result.url)
        self.assertEqual(result.weight, 0)
        self.assertEqual(result.total_weight, 1)

    def test_get_eps_calculator_status_non_eto_gen2_home_status(self):
        """Test for get_eps_calculator_status() home_status.slug is not in ETO_GEN2"""
        edit_url = "edit_url"
        co_url = "companies_edit_url"
        checklist_url = "checklist_url"
        provider = User.objects.get(company__name="Provider1")
        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="eto-2018")
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="non-eto")
        eep_program4 = EEPProgram.objects.get(owner__name="EEP4")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        # create a floorplan with REM Rate (export_type 4) and then update home_status
        kwargs = {"use_udrh_simulation": True}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.export_type, 4)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company, floorplan=floorplan
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        input_values = {"primary-heating-equipment-type": "ETO_HEAT_TYPE_QUESTION_SLUG"}
        result = eep_program4.get_eps_calculator_status(
            home_status, checklist_url, edit_url, co_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        missing_checklist_data_points = (
            "Primary Heating Equipment, Primary Water Heater EF, " "Water Heater Type, Pathway"
        )
        self.assertIn(missing_checklist_data_points, result.message)
        self.assertIsNone(result.data)

    def test_get_eps_calculator_status_passing_status(self):
        """
        Test for get_eps_calculator_status() Allow separate utility requirement to report
        an issue.
        For this test case we need to modify our eep_program's slug and add a floor plan with
        rem rate target type 4 to our home_status.
        Expected result: passing status
        input values is a dictionary containing info related to the eto program.
        for more info check QUESTION_SLUG_DATA in eps/utils.py
        required argument companies_edit_url is not being used but still required.
        """
        edit_url = "edit_url"
        co_url = "companies_edit_url"
        checklist_url = "checklist_url"
        provider = User.objects.get(company__name="Provider1")
        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        # create a floorplan with REM Rate (export_type 4) and then update home_status
        kwargs = {"use_udrh_simulation": True}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.export_type, 4)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company, floorplan=floorplan
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        input_values = {"primary-heating-equipment-type": "ETO_HEAT_TYPE_QUESTION_SLUG"}
        result = eep_program.get_eps_calculator_status(
            home_status, checklist_url, edit_url, co_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        self.assertTrue(result.status)

    def test_get_eps_calculator_status_missing_input_values(self):
        """
        Test for get_eps_calculator_status() passed attr input_values (dict_ empty.
        Expected result: failing status
        """
        edit_url = "edit_url"
        co_url = "companies_edit_url"
        checklist_url = "checklist_url"
        provider = User.objects.get(company__name="Provider1")
        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        # create a floorplan with REM Rate and then update home_status
        kwargs = {"use_udrh_simulation": True}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.export_type, 4)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            company=provider.company, floorplan=floorplan
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        input_values = {}
        result = eep_program.get_eps_calculator_status(
            home_status, checklist_url, edit_url, co_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.message)
        self.assertIn("Primary Heating Equipment", result.message)
        self.assertIsNone(result.data)
        self.assertFalse(result.status)

    def test_get_nwesh_invalid_qa_program_status_passing_status_legacy_qa(self):
        """Test for get_nwesh_invalid_qa_program_status() for legacy_qa."""
        legacy_qa = [
            "northwest-energy-star-version-3-2014-qa",
            "northwest-energy-star-version-3-2014-full-qa",
            "neea-energy-star-v3-qa",
        ]
        for qa in legacy_qa:
            EEPProgram.objects.filter(owner__name="EEP4").update(slug=qa)
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            result = eep_program.get_nwesh_invalid_qa_program_status(home_status, "home_edit_url")
            self.assertIsNotNone(result)
            self.assertTrue(result.status)

    def test_get_nwesh_invalid_qa_program_status_bad_nwesh_qa_legacy_qa(self):
        """Test for get_nwesh_invalid_qa_program_status() for legacy_qa."""
        legacy_qa = [
            "northwest-energy-star-version-3-2014-qa",
            "northwest-energy-star-version-3-2014-full-qa",
            "neea-energy-star-v3-qa",
        ]
        ep = EEPProgram.objects.get(owner__name="EEP3")
        ep4 = EEPProgram.objects.get(owner__name="EEP4")
        home = EEPProgramHomeStatus.objects.get(eep_program=ep4).home
        EEPProgramHomeStatus.objects.filter(eep_program=ep).update(home=home)
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-performance-2015")
        for qa in legacy_qa:
            EEPProgram.objects.filter(owner__name="EEP4").update(slug=qa)
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            result = eep_program.get_nwesh_invalid_qa_program_status(home_status, "home_edit_url")
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            self.assertIn("The QA Program you are using should be one", result.message)

    def test_get_nwesh_invalid_qa_program_status_passing_status_current_qa(self):
        """Test for get_nwesh_invalid_qa_program_status() for current_qa."""
        current_qa = ["northwest-energy-star-v3-r8-qa-short", "northwest-energy-star-v3-r8-qa-long"]
        for qa in current_qa:
            EEPProgram.objects.filter(owner__name="EEP4").update(slug=qa)
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            result = eep_program.get_nwesh_invalid_qa_program_status(home_status, "home_edit_url")
            self.assertIsNotNone(result)
            self.assertTrue(result.status)

    def test_get_nwesh_invalid_qa_program_status_bad_nwesh_qa_current_qa(self):
        """Test for get_nwesh_invalid_qa_program_status() for legacy_qa."""
        current_qa = ["northwest-energy-star-v3-r8-qa-short", "northwest-energy-star-v3-r8-qa-long"]
        ep = EEPProgram.objects.get(owner__name="EEP3")
        ep4 = EEPProgram.objects.get(owner__name="EEP4")
        home = EEPProgramHomeStatus.objects.get(eep_program=ep4).home
        EEPProgramHomeStatus.objects.filter(eep_program=ep).update(home=home)
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-energy-star-v3")
        for qa in current_qa:
            EEPProgram.objects.filter(owner__name="EEP4").update(slug=qa)
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            result = eep_program.get_nwesh_invalid_qa_program_status(home_status, "home_edit_url")
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            self.assertIn("The QA Program you are using should be one", result.message)

    def test_get_generic_singlefamily_support_failing_status(self):
        """
        Test for get_generic_singlefamily_support where slug is 'neea-efficient-homes' and
        home_status home is_multi_family
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-efficient-homes")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        home_slug = EEPProgramHomeStatus.objects.get(eep_program=eep_program).home.slug
        Home.objects.filter(slug=home_slug).update(is_multi_family=True)

        self.assertEqual(eep_program.slug, "neea-efficient-homes")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_generic_singlefamily_support(home_status, "home_edit_url", "")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Only single family projects are allowed", result.message)

    def test_get_generic_singlefamily_support_passing_status(self):
        """
        Test for get_generic_singlefamily_support where slug is 'neea-efficient-homes' and
        home_status home is_multi_family == False
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-efficient-homes")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        self.assertEqual(eep_program.slug, "neea-efficient-homes")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_generic_singlefamily_support(home_status, "home_edit_url", "")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_remrate_flavor_status_no_floorplan(self):
        """Test for get_remrate_flavor_status(). home_status has no floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_remrate_flavor_status(home_status, "edit_url", "")
        self.assertIsNone(result)

    def test_get_remrate_flavor_status_no_remrate_target(self):
        """Test for get_remrate_flavor_status(). home_status floorplan has no remrate"""
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_flavor_status(home_status, "edit_url", "")
        self.assertIsNone(result)

    def test_get_remrate_flavor_status_remrate_wrong_flavor(self):
        """
        Test for get_remrate_flavor_status. eep_program's slug in northwest_only_programs:
        'utility-incentive-v1-single-family', 'eto-2016', 'eto-2017'
        but floorplan's remrate flavor not in ['Northwest', 'Washington']
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-single-family"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        floorplan = floorplan_with_remrate_factory()
        self.assertIsNotNone(floorplan.remrate_target)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        flavors = ["Northwest", "Washington"]
        self.assertNotIn(home_status.floorplan.remrate_target.flavor.strip(), flavors)
        result = eep_program.get_remrate_flavor_status(home_status, "edit_url", "")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Program {program} only allows rating data from the {accepted_flavor} version of "
            "REM/Rate".format(program=home_status.eep_program, accepted_flavor="Northwest")
        )
        self.assertIn(msg, result.message)
        self.assertEqual("edit_url", result.url)

    def test_get_remrate_flavor_status_national_program_wrong_flavor(self):
        """
        Test for get_remrate_flavor_status. eep_program's slug == 'neea-bpa'
        remrate_target flavor is NOT in ['', 'None', 'Rate']
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        kwargs = {"remrate_target__flavor": "some_other_flavor"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.flavor, "some_other_flavor")

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_flavor_status(home_status, "edit_url", "")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Program {program} only allows rating data from the {accepted_flavor} version of "
            "REM/Rate".format(
                program="{}".format(home_status.eep_program), accepted_flavor="National"
            )
        )
        self.assertIn(msg, result.message)
        self.assertEqual("edit_url", result.url)

    def test_get_remrate_flavor_status_northwest_program_passing_status(self):
        """
        Test for get_remrate_flavor_status. eep_program's slug in northwest_only_programs:
        'utility-incentive-v1-single-family', 'eto-2016', 'eto-2017'
        and floorplan's remrate flavor in ['Northwest', 'Washington']
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-single-family"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        kwargs = {"remrate_target__flavor": "Northwest"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.flavor, "Northwest")

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        result = eep_program.get_remrate_flavor_status(home_status, "edit_url", "")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_get_remrate_flavor_status_passing_status_national_program(self):
        """
        Test for get_remrate_flavor_status. eep_program's slug == 'neea-bpa'
        remrate_target flavor is in ['', 'None', 'Rate']
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        kwargs = {"remrate_target__flavor": ""}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.flavor, "")

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_flavor_status(home_status, "edit_url", "")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_get_remrate_version_status_not_applicable_program(self):
        """
        Test for get_remrate_version_status. eep_program's slug
        NOT 'utility-incentive-v1-single-family'
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        self.assertNotEqual(eep_program.slug, "utility-incentive-v1-single-family")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_version_status(home_status, "edit_url", "")
        self.assertIsNone(result)

    def test_get_remrate_version_status_no_floorplan(self):
        """Test for get_remrate_version_status. home_Sattus has no floorplan"""
        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-single-family"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)

        result = eep_program.get_remrate_version_status(home_status, "edit_url", "")
        self.assertIsNone(result)

    def test_get_remrate_version_status_no_remrate_target(self):
        """Test for get_remrate_version_status. home_status' floorplan has no remrate target"""
        from axis.floorplan.tests.factories import floorplan_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-single-family"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_version_status(home_status, "edit_url", "")
        self.assertIsNone(result)

    def test_get_remrate_version_status_not_allowed_remrate_numerical_version(self):
        """
        Test for get_remrate_version_status. not allowed numerical version. This program allows
        versions 14.0 - 14.6.4
        remrate_target.numerical_version not in that range
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-single-family"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        kwargs = {"remrate_target__version": "14.7.0"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (14, 7, 0))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_version_status(home_status, "edit_url", "")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Program {program} only allows rating data from REM/Rate™ versions {versions}.".format(
                program=home_status.eep_program, versions="14.6 - 14.6.4"
            )
        )
        self.assertIn(msg, result.message)
        self.assertEqual("edit_url", result.url)

    def test_get_remrate_version_status_passing_status(self):
        """
        Test for get_remrate_version_status. This program allows versions 14.0 - 14.6.4
        remrate_target.numerical_version in that range
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-single-family"
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        kwargs = {"remrate_target__version": "14.6.4"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (14, 6, 4))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_remrate_version_status(home_status, "edit_url", "")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_get_built_green_annotations_status_no_annotations(self):
        """
        Test for get_built_green_annotations_status. home_status eep_program slug is not part of
        the applicable programs
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="built-green-tri-cities")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_built_green_annotations_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)

    def test_get_pnw_utility_required_status_passing_non_eto(self):
        """Test for get_pnw_utility_required_status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_pnw_utility_required_status(
            "home", home_status, "companies_edit_url", "input_values"
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_pnw_utility_required_status_(self):
        """
        Test for get_pnw_utility_required_status. meets both program requirements., since
        home has utilities associated
        """
        for slug in ["eto-2017", "eto-2018"]:
            EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
            eep_program = EEPProgram.objects.get(owner__name="EEP3")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            input_values = {"primary-heating-equipment-type": "Gas Furnace"}
            result = eep_program.get_pnw_utility_required_status(
                "home", home_status, "companies_edit_url", input_values
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)

    def test_get_pnw_utility_required_status_failed_electric_requirement(self):
        """
        Test for get_pnw_utility_required_status. eto-2017 checks only for electirc utility.
        for this case it fail since home does not have electric utility associated
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="eto-2017")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Gas Furnace"}
        result = eep_program.get_pnw_utility_required_status(
            "home", home_status, "companies_edit_url", input_values
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("An electric utility must be assigned.", result.message)

    def test_get_pnw_utility_required_status_failed_utilities_requirement(self):
        """
        Test for get_pnw_utility_required_status. eto-2018 checks for both utilities. for this
        case it fails on both check since it does NOT have any utilities associated to home
        """

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Gas Furnace"}
        result = eep_program.get_pnw_utility_required_status(
            "home", home_status, "companies_edit_url", input_values
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertTrue(result.show_data)
        self.assertIn("An electric utility must be assigned.", result.data)
        self.assertIn("requires a gas utility be assigned.", result.data)

    def test_get_pnw_utility_required_status_failed_electric_requirement_only_eto_2018(self):
        """
        Test for get_pnw_utility_required_status. eto-2018 checks only  for both utilities. for this
        case it fails on the electric check since it does NOT have heating equipment in the
        input values
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="eto-2018")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Heat pump"}
        result = eep_program.get_pnw_utility_required_status(
            "home", home_status, "companies_edit_url", input_values
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertFalse(result.show_data)
        self.assertIn("An electric utility must be assigned.", result.message)
        self.assertNotIn("requires a gas utility be assigned.", result.message)

    def test_get_water_heater_status_non_neea_bpa(self):
        """Test for get_water_heater_status. eep_program slug not 'neea-bpa' expected result None"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertNotEqual("neea-bpa", eep_program.slug)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_water_heater_status_no_floorplan(self):
        """Test for get_water_heater_status. home_status has no floorplan expected result None"""
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_water_heater_status_no_remrate_target(self):
        """
        Test for get_water_heater_status. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_water_heater_status_ground_heat_pump(self):
        """
        Test for get_water_heater_status. simulation's (remrate_target) HotWaterHeater type is
        5 ('Ground source heat pump')
        """
        from axis.remrate_data.tests.factories.hot_water_heater import hot_water_heater_factory

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        simulation = floorplan.remrate_target
        kwargs = {"blg_data": {"system_type": 5}}
        hot_water_heater_factory(simulation, 33, **kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertTrue(simulation.hotwaterheater_set.filter(type__in=[5, 21]).count())
        self.assertFalse(simulation.integratedspacewaterheater_set.count())

        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = (
            "Ground Source Heat Pump Water Heaters OR Integrated Space Water Heaters "
            "are not allowed"
        )
        self.assertEqual(msg, result.message)

    def test_get_water_heater_status_integrated_water_heater(self):
        """
        Test for get_water_heater_status. simulation's (remrate_target) HotWaterHeater type is
        21 ('Integrated')
        """
        from axis.remrate_data.tests.factories.hot_water_heater import hot_water_heater_factory

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        simulation = floorplan.remrate_target
        kwargs = {"blg_data": {"system_type": 21}}
        hot_water_heater_factory(simulation, 33, **kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertTrue(simulation.hotwaterheater_set.filter(type__in=[5, 21]).count())
        self.assertFalse(simulation.integratedspacewaterheater_set.count())

        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = (
            "Ground Source Heat Pump Water Heaters OR Integrated Space Water Heaters "
            "are not allowed"
        )
        self.assertEqual(msg, result.message)

    def test_get_water_heater_status_integrated_space_water_heater(self):
        """
        Test for get_water_heater_status. simulation's (remrate_target) HotWaterHeater type is
        21 ('Integrated')
        """
        from axis.remrate_data.models import IntegratedSpaceWaterHeater

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        simulation = floorplan.remrate_target
        IntegratedSpaceWaterHeater.objects.create(
            simulation=simulation,
            _result_number=33,
            _source_integrated_space_water_heater_number=1,
            name="sHTDType",
            fuel_type=4,
            type=4,
        )
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertFalse(simulation.hotwaterheater_set.filter(type__in=[5, 21]).count())
        self.assertTrue(simulation.integratedspacewaterheater_set.count())

        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = (
            "Ground Source Heat Pump Water Heaters OR Integrated Space Water Heaters "
            "are not allowed"
        )
        self.assertEqual(msg, result.message)

    def test_get_water_heater_status_passing(self):
        """
        Test for get_water_heater_status. simulation's (remrate_target) HotWaterHeater type is
        NOT 5 ('Ground source heat pump') or 21 ('Integrated')
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        simulation = floorplan.remrate_target
        self.assertFalse(simulation.hotwaterheater_set.filter(type__in=[5, 21]).count())
        self.assertFalse(simulation.integratedspacewaterheater_set.count())
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_water_heater_status(home_status, "edit_url")
        self.assertIsNotNone(result)

    def test_get_duct_system_test_status_non_neea_bpa(self):
        """Test get_duct_system_test_status. eep_program slug is NOT 'neea-bpa'"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_duct_system_test_status_no_floorplan(self):
        """Test get_duct_system_test_status. home_status has no floorplan expected result None"""
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_duct_system_test_status_no_remrate_target(self):
        """Test get_duct_system_test_status. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_duct_system_test_status_duct_system_required_duct_leakage_exempt(self):
        """
        Test for get_duct_system_test_status. simulation's (remrate_target) DuctSystem
        leakage_tightness_test is 4 ("Duct Leakage Exemption") AND leakage_test_exemption = False
        """

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory(
            remrate_target__duct_system__leakage_tightness_test=4,
            remrate_target__duct_system__leakage_test_exemption=False,
        )

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertTrue(simulation.ductsystem_set.filter(leakage_tightness_test=4).count())
        self.assertFalse(simulation.ductsystem_set.filter(leakage_test_exemption=True).count())

        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = "Duct System Testing is Required - No exemptions allowed"
        self.assertEqual(msg, result.message)
        self.assertFalse(result.status)

    def test_get_duct_system_test_status_leakage_test_exemption(self):
        """
        Test for get_duct_system_test_status. simulation's (remrate_target) DuctSystem
        leakage_tightness_test is NOT 4 ("Duct Leakage Exemption") AND leakage_test_exemption = True
        """

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory(
            remrate_target__duct_system__leakage_tightness_test=1,
            remrate_target__duct_system__leakage_test_exemption=True,
        )
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertFalse(simulation.ductsystem_set.filter(leakage_tightness_test=4).count())
        self.assertTrue(simulation.ductsystem_set.filter(leakage_test_exemption=True).count())

        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = "Duct System Testing is Required - No exemptions allowed"
        self.assertEqual(msg, result.message)
        self.assertFalse(result.status)

    def test_get_duct_system_test_status_duct_system_required(self):
        """
        Test for get_duct_system_test_status. simulation's (remrate_target) DuctSystem
        leakage_tightness_test is 4 ("Duct Leakage Exemption") AND leakage_test_exemption = True
        """

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory(
            remrate_target__duct_system__leakage_tightness_test=4,
            remrate_target__duct_system__leakage_test_exemption=True,
        )
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertTrue(simulation.ductsystem_set.filter(leakage_tightness_test=4).count())
        self.assertTrue(simulation.ductsystem_set.filter(leakage_test_exemption=True).count())

        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = "Duct System Testing is Required - No exemptions allowed"
        self.assertEqual(msg, result.message)
        self.assertFalse(result.status)

    def test_get_duct_system_test_status_passing(self):
        """
        Test for get_duct_system_test_status. simulation's (remrate_target) DuctSystem
        leakage_tightness_test is NOT 4 ("Duct Leakage Exemption") AND leakage_test_exemption=False
        """

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory(
            remrate_target__duct_system__leakage_tightness_test=2,
            remrate_target__duct_system__leakage_test_exemption=False,
        )
        simulation = floorplan.remrate_target
        self.assertEqual(simulation.ductsystem_set.count(), 1)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertFalse(simulation.ductsystem_set.filter(leakage_tightness_test=4).count())
        self.assertFalse(simulation.ductsystem_set.filter(leakage_test_exemption=True).count())

        result = eep_program.get_duct_system_test_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        self.assertTrue(result.status)

    def test_get_ventilation_type_status_non_neea_bpa(self):
        """Test get_ventilation_type_status.eep_program slug is NOT 'neea-bpa'"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_ventilation_type_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_ventilation_type_status_no_floorplan(self):
        """Test get_ventilation_type_status. home_status has no floorplan expected result None"""
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_ventilation_type_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_ventilation_type_status_no_remrate_target(self):
        """Test get_duct_system_test_status. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_ventilation_type_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_ventilation_type_status_mechanical_vent_type(self):
        """
        Test for get_ventilation_type_status. for this check, simulation's (remrate_target)
        infiltration mechanical_vent_type can NOT be 4 ('Air Cycler') otherwise status will FAIL
        mechanical_vent_type != 4  expected status FAILING
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__infiltration__mechanical_vent_type": 4,
            "remrate_target__version": "15.8",
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertTrue(simulation.infiltration.mechanical_vent_type == 4)

        result = eep_program.get_ventilation_type_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        msg = "Mechanical Ventilation System for IAQ cannot be Air Cycler"
        self.assertEqual(msg, result.message)
        self.assertFalse(result.status)

    def test_get_ventilation_type_status_passing(self):
        """
        Test for get_ventilation_type_status. for this check, simulation's (remrate_target)
        infiltration mechanical_vent_type can NOT be 4 ('Air Cycler') otherwise status will FAIL.
        mechanical_vent_type != 4  expected status PASSING
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__infiltration__mechanical_vent_type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        simulation = home_status.floorplan.remrate_target
        self.assertFalse(simulation.infiltration.mechanical_vent_type == 4)

        result = eep_program.get_ventilation_type_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        self.assertIsNone(result.message)
        self.assertTrue(result.status)

    def test_get_program_end_warning_program_submit_date_approaching(self):
        """
        Test for get_program_end_warning_status. eep_program.program_submit_warning_date <= today
        AND eep_program.program_end_date is NOT None.
        expected back Warning Status
        """
        import datetime
        from ..strings import PROGRAM_SUBMIT_DATE_APPROACHING as MESSAGE

        program_end_date = datetime.date.today() + datetime.timedelta(days=5)
        lt_warning_date = datetime.date.today() - datetime.timedelta(days=5)
        eq_warning_date = datetime.date.today()
        program_submit_warning_dates = [lt_warning_date, eq_warning_date]
        for program_submit_warning_date in program_submit_warning_dates:
            EEPProgram.objects.filter(owner__name="EEP4").update(
                program_end_date=program_end_date,
                program_submit_date=program_end_date,
                program_submit_warning_date=program_submit_warning_date,
            )
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            result = eep_program.get_program_end_warning_status(home_status.home, home_status)
            self.assertIsNotNone(result)
            self.assertIsNone(result.status)
            msg = MESSAGE.format(
                program_name=eep_program.name,
                date=eep_program.program_submit_date.strftime("%B %d, %Y"),
            )
            self.assertIn(msg, result.message)

    def test_get_program_end_warning_program_end_date_approaching(self):
        """
        Test for get_program_end_warning_status. eep_program.program_close_warning_date <= today
        eep_program.program_end_date is NOT None
        eep_program.program_submit_date is None
        expected back Warning Status
        """
        import datetime
        from ..strings import PROGRAM_END_DATE_APPROACHING as MESSAGE

        program_end_date = datetime.date.today() + datetime.timedelta(days=5)
        lt_warning_date = datetime.date.today() - datetime.timedelta(days=5)
        eq_warning_date = datetime.date.today()
        program_close_warning_dates = [lt_warning_date, eq_warning_date]
        for program_close_warning_date in program_close_warning_dates:
            EEPProgram.objects.filter(owner__name="EEP4").update(
                program_end_date=program_end_date,
                program_submit_date=None,
                program_close_warning_date=program_close_warning_date,
            )
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            result = eep_program.get_program_end_warning_status(home_status.home, home_status)
            self.assertIsNotNone(result)
            self.assertIsNone(result.status)
            msg = MESSAGE.format(
                program_name=eep_program.name,
                date=eep_program.program_end_date.strftime("%B %d, %Y"),
            )
            self.assertIn(msg, result.message)

    def test_get_program_end_warning_status_no_warn_dates(self):
        """
        Test get_program_end_warning_status. eep_program has no program_close_warning_date or
        program_submit_warning_date
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(
            program_submit_warning_date=None, program_close_warning_date=None
        )
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_program_end_warning_status(home_status.home, home_status)
        self.assertIsNone(result)
