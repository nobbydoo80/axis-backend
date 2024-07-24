"""test_managers.py: Django eep_program managers tests"""


import logging

from django.contrib.auth import get_user_model

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import general_super_user_factory
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram

from axis.eep_program.tests.mixins import EEPProgramsTestMixin, EEPProgramManagerTestMixin
from axis.home.models import EEPProgramHomeStatus
from axis.subdivision.models import Subdivision, EEPProgramSubdivisionStatus

__author__ = "Johnny Fang"
__date__ = "14/6/19 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

User = get_user_model()

log = logging.getLogger(__name__)


class EEPProgramModelTests(EEPProgramsTestMixin, AxisTestCase):
    """Tests for EEPProgram model"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        super(EEPProgramModelTests, cls).setUpTestData()
        EEPProgramManagerTestMixin().setUpTestData()

    REQUIREMENTS_TESTS = [
        EEPProgram.get_program_certification_eligibility,
        EEPProgram.get_std_protocol_percent_improvement_status,
        EEPProgram.get_resnet_approved_provider_status,
        EEPProgram.get_aps_double_payment_status,
        EEPProgram.get_aps_calculator_status,
        EEPProgram.get_eps_calculator_status,
        EEPProgram.get_eto_builder_account_number_status,
        EEPProgram.get_eto_rater_account_number_status,
        EEPProgram.get_eto_2017_answer_sets,
        EEPProgram.get_eto_legacy_builder_incentive_status,
        EEPProgram.get_neea_utilities_satisfied_status,
        EEPProgram.get_neea_invalid_program_status,
        EEPProgram.get_hquito_accrediation_status,
        EEPProgram.get_nwesh_invalid_qa_program_status,
        EEPProgram.get_generic_singlefamily_support,
        EEPProgram.get_generic_us_state_eligibility,
        EEPProgram.get_min_max_simulation_version,
        EEPProgram.get_simulation_udrh_check,
        EEPProgram.get_simulation_flavor_status,
        EEPProgram.get_remrate_flavor_status,
        EEPProgram.get_remrate_version_status,
        EEPProgram.get_built_green_annotations_status,
        EEPProgram.get_pnw_utility_required_status,
        EEPProgram.get_water_heater_status,
        EEPProgram.get_duct_system_test_status,
        EEPProgram.get_ventilation_type_status,
        EEPProgram.get_neea_checklist_type_matches_remrate_status,
        EEPProgram.get_neea_checklist_water_heater_matches_remrate_status,
        EEPProgram.get_neea_bpa_refrigerator_installed_status,
        EEPProgram.get_neea_bpa_clothes_washer_installed_status,
        EEPProgram.get_neea_bpa_clothes_dryer_installed_status,
        EEPProgram.get_neea_bpa_dishwasher_installed_status,
        EEPProgram.get_neea_bpa_checklist_smart_thermostat_installed_status,
        EEPProgram.get_neea_bpa_remrate_version_status,
        EEPProgram.get_program_end_warning_status,
        EEPProgram.get_eto_no_multifamily,
        EEPProgram.get_eto_2018_oven_fuel_type,
        EEPProgram.get_eto_2018_dryer_attributes,
        EEPProgram.get_eto_heat_pump_water_heater_status,
        EEPProgram.get_eto_percent_improvement_oregon,
        EEPProgram.get_eto_percent_improvement_washington,
        EEPProgram.get_eto_primary_heating_fuel_type,
        EEPProgram.get_eto_min_program_version,
        EEPProgram.get_remrate_udhr_check,
        EEPProgram.get_eto_2019_approved_utility_electric_utility,
        EEPProgram.get_eto_2019_approved_utility_gas_utility,
        EEPProgram.get_aps_2019_estar_check,
        EEPProgram.get_built_green_wa_electric_utility_required_status,
        EEPProgram.get_built_green_wa_gas_utility_required_status,
        EEPProgram.get_wa_code_annotation_dwelling_status,
        EEPProgram.get_wa_code_opt_1_status,
        EEPProgram.get_wa_code_opt_2_status,
        EEPProgram.get_wa_code_opt_3_status,
        EEPProgram.get_wa_code_opt_4_status,
        EEPProgram.get_wa_code_opt_5a_status,
        EEPProgram.get_wa_code_opt_5bc_status,
        EEPProgram.get_wa_code_opt_5d_status,
        EEPProgram.get_wa_code_opt_6_status,
        EEPProgram.get_wa_code_bathroom_status,
        EEPProgram.get_wa_code_warning_status,
        EEPProgram.get_wa_code_damper_status,
        EEPProgram.get_eto_approved_utility_gas_utility,
        EEPProgram.get_eto_approved_utility_electric_utility,
        EEPProgram.get_eto_gas_heated_utility_check,
        EEPProgram.get_eto_electric_heated_utility_check,
        EEPProgram.get_eto_revised_primary_heating_fuel_type,
        EEPProgram.get_neea_v3_availability_check,
        EEPProgram.get_neea_v3_refrigerator_installed_status,
        EEPProgram.get_neea_v3_clothes_washer_installed_status,
        EEPProgram.get_wcc_builder_incentive_status,
        EEPProgram.get_eto_builder_incentive_status,
        EEPProgram.get_eto_fire_rebuild_checks,
    ]

    def test_save_no_slug_given(self):
        """Test a slug is assigned even when one was not provided"""

        program = EEPProgram.objects.first()
        program_name = "Test Program"
        eep_program = EEPProgram(name=program_name, owner=program.owner)

        self.assertEqual("", eep_program.slug)
        eep_program.save()
        self.assertIsNotNone(eep_program.slug)

    def test_save_sets_viewable_by_company_type_to_none(self):
        """Test to verify that viewable_by_company_type is set to none if empty string was given"""
        program = EEPProgram.objects.first()
        program_name = "Test Program"
        eep_program = EEPProgram(
            name=program_name, owner=program.owner, viewable_by_company_type=""
        )

        self.assertEqual("", eep_program.viewable_by_company_type)
        eep_program.save()
        self.assertIsNone(eep_program.viewable_by_company_type)

    def test_get_absolute_url(self):
        """Test absolute url generated is correct"""
        from django.urls import reverse

        program = EEPProgram.objects.first()
        absolute_url = program.get_absolute_url()
        self.assertIsNotNone(absolute_url)
        expected_url = reverse("eep_program:view", kwargs={"pk": program.pk})
        self.assertEqual(expected_url, absolute_url)

    def test_natural_key(self):
        """Test natural key is returned. natural key is formed by a tuple (name, owner.slug)"""
        program = EEPProgram.objects.first()
        key = program.natural_key()
        expected_key = (program.name, program.owner.slug)
        self.assertEqual(expected_key, key)

    def test_get_checklist_question_set(self):
        """Test get_checklist_question_set()"""
        program = EEPProgram.objects.first()
        questions = program.get_checklist_question_set()
        self.assertIsNotNone(questions)

    def test_requires_flooorplan(self):
        """Test requires_floorplan() should return true if program will require Floorplan data"""
        program = EEPProgram.objects.first()
        requires_floorplan = (
            program.require_input_data
            or program.require_rem_data
            or program.require_model_file
            or program.require_ekotrope_data
        )

        result = program.requires_floorplan()

        self.assertEqual(requires_floorplan, result)

        new_value = False if result else True
        program.require_input_data = new_value
        program.save()
        result = program.requires_floorplan()
        self.assertEqual(new_value, result)

    def test_is_claimable(self):
        """
        Test for is_claimable(User), a program is claimable if the user's company is eep_sponsor
        or if the user's company owns the  program AND the company is a non-customer that have no
        associated sponsor
        """
        program = EEPProgram.objects.first()
        user = User.objects.get(company__name="EEP1")
        result = program.is_claimable(user)

        self.assertTrue(result)

    def test_is_claimable_false(self):
        """
        Test for is_claimable(User), a program is claimable if the user's company is eep_sponsor
        or if the user's company owns the  program AND the company is a non-customer that have no
        associated sponsor
        """
        program = EEPProgram.objects.first()

        # rater's company is does not meet the criteria
        rater = User.objects.get(company__name="Rater1")
        result = program.is_claimable(rater)
        self.assertFalse(result)

    def test_is_claimable__by_claimable_companies(self):  # TODO fix
        """
        Test for is_claimable(User), a program is claimable if the user's company is eep_sponsor
        or if the user's company owns the  program AND the company is a non-customer that have no
        associated sponsor
        """
        program = EEPProgram.objects.first()
        general_user = User.objects.get(company__name="General1")
        company = general_user.company

        # making company non-customer
        company.is_customer = False
        company.save()
        # we want to make sure the user's company is not an eep_sponsor
        self.assertFalse(general_user.company.is_eep_sponsor)
        program.owner = general_user.company
        program.save()
        result = program.is_claimable(general_user)
        # make sure is claimable
        self.assertTrue(result)

    def test_requires_manual_floorplan_approval(self):
        """
        Test requires_manual_floorplan_approval which indicates that the given company mut have
        floorplans activated vy the program owner
        """
        program = EEPProgram.objects.first()
        expected = program.require_floorplan_approval
        result = program.requires_manual_floorplan_approval(program.owner)

        self.assertEqual(expected, result)

    def test_requires_manual_floorplan_approval_with_superuser(self):
        """Test requires_manual_floorplan_approval()"""
        program = EEPProgram.objects.first()
        program.require_floorplan_approval = True
        program.save()
        user = general_super_user_factory()
        expected = program.require_floorplan_approval
        result = program.requires_manual_floorplan_approval(program.owner, user)

        self.assertEqual(
            expected,
            result,
            "approval-required flag is True, superuser might not "
            "have any owned relationships and should be put through "
            "directly.",
        )

        program.require_floorplan_approval = False
        program.save()
        expected = program.require_floorplan_approval
        result = program.requires_manual_floorplan_approval(program.owner, user)

        self.assertEqual(expected, result)

    def test_requires_manual_floorplan_approval_with_regular_user(self):
        """
        First scenario we test for the case where manual approval is not required. Then,
        we test for the case when approval is required
        """
        from axis.relationship.models import Relationship

        eep_user = User.objects.get(company__name="EEP1")
        unrelated_eep = EEPProgram.objects.filter(owner__name="unrelated_eep").first()
        unrelated_eep.require_floorplan_approval = True
        unrelated_eep.save()
        result = unrelated_eep.requires_manual_floorplan_approval(user=eep_user)

        rl = Relationship.objects.get_reversed_companies(eep_user.company).filter(
            id=unrelated_eep.owner.id
        )
        expected = rl.exists()

        self.assertEqual(expected, result)

        provider_user = User.objects.get(company__name="Provider1")
        eep = EEPProgram.objects.filter(owner__name="EEP1").first()
        eep.require_floorplan_approval = True
        eep.save()
        rl = Relationship.objects.get_reversed_companies(provider_user.company).filter(
            id=eep.owner_id
        )
        expected = rl.exists()
        result = eep.requires_manual_floorplan_approval(user=provider_user)

        self.assertEqual(expected, result)

    def test_can_be_added(self):
        """
        Test for can_be_added() it should return True in the following casess:
        1) user's company is_eep_sponsor or is_superuser or comapy is type eep
        2) user's company type is either [ rater, provider, hvac] AND
        is company admin and is_customer
        """
        from axis.core.tests.factories import hvac_admin_factory, general_user_factory

        eep_user = User.objects.get(company__name="EEP1")
        self.assertTrue(eep_user.company.is_eep_sponsor)
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        result = eep_program.can_be_added(eep_user)
        self.assertTrue(result)

        general_user = general_super_user_factory()
        company = general_user.company
        self.assertTrue(general_user.is_superuser)
        self.assertFalse(company.is_eep_sponsor)
        result = eep_program.can_be_added(general_user)
        self.assertTrue(result)
        company = general_user.company
        self.assertFalse(company.company_type == "eep")
        company.company_type = "eep"
        company.save()
        self.assertTrue(company.company_type == "eep")

        company_types = ["rater", "provider", "hvac"]
        provider_user = User.objects.filter(company__name="Provider1").first()
        self.assertIn(provider_user.company.company_type, company_types)
        result = eep_program.can_be_added(provider_user)
        self.assertTrue(result)

        rater_user = User.objects.filter(company__name="Rater1").first()
        self.assertIn(rater_user.company.company_type, company_types)
        result = eep_program.can_be_added(rater_user)
        self.assertTrue(result)

        hvac_user = hvac_admin_factory(company__name="Hvac1")
        self.assertIn(hvac_user.company.company_type, company_types)
        result = eep_program.can_be_added(hvac_user)
        self.assertTrue(result)

        plain_user = general_user_factory()
        result = eep_program.can_be_added(plain_user)
        company = plain_user.company
        self.assertNotIn(company.company_type, company_types)
        self.assertFalse(plain_user.is_superuser)
        self.assertFalse(company.is_eep_sponsor)
        self.assertFalse(result)
        company.company_type = "rater"
        company.save()
        self.assertIn(company.company_type, company_types)
        self.assertFalse(plain_user.is_company_admin)
        result = eep_program.can_be_added(plain_user)
        self.assertFalse(result)

    def test_can_be_edited_with_superuser(self):
        """Test for can_be_edited(user) for the case where user is_superuser=True"""
        general_user = general_super_user_factory()
        eep_program = EEPProgram.objects.first()
        result = eep_program.can_be_edited(general_user)
        self.assertTrue(result)

    def test_can_be_edited_case_1(self):
        """
        Test for can_be_edited(user) for scenario where user is NOT a superuser AND his
        company is_eep_sponsor .Also, given eep_program does NOT belong to either a Subdivision and
        a EEPProgramHomeStatus
        """
        eep_user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        result = eep_program.can_be_edited(eep_user)
        self.assertTrue(result)

    def test_can_be_edited_fails_case_1(self):
        """
        Test for can_be_edited(user) when it should returns false.
        user is not superuser and his company is not eep_sponsor
        """
        provider_user = User.objects.filter(company__name="Provider1").first()
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        result = eep_program.can_be_edited(provider_user)
        self.assertFalse(result)

    def test_can_be_edited_fails_case_2(self):
        """
        Test for can_be_edited(user) when it should returns false.
        user is not superuser and program DOES belong to a Subdivision
        """
        from axis.subdivision.tests.factories import subdivision_factory

        eep_user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        subdivision = subdivision_factory()
        eep_program_sub_status = EEPProgramSubdivisionStatus(
            subdivision=subdivision, eep_program=eep_program, company=eep_user.company
        )
        eep_program_sub_status.save()
        self.assertTrue(Subdivision.objects.filter(eep_programs=eep_program).count())
        result = eep_program.can_be_edited(eep_user)
        self.assertFalse(result)

    def test_can_be_edited_fails_case_3(self):
        """
        Test for can_be_edited(user) when it should returns false.
        user is not superuser and program DOES belong to a EEPProgramHomeStatus
        """
        from axis.home.tests.factories import home_factory

        eep_user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        home = home_factory()
        eep_program_home_status = EEPProgramHomeStatus(
            eep_program=eep_program, home=home, company=eep_user.company
        )
        eep_program_home_status.save()
        self.assertTrue(EEPProgramHomeStatus.objects.filter(eep_program=eep_program).count())
        result = eep_program.can_be_edited(eep_user)
        self.assertFalse(result)

    def test_can_be_deleted_passing_user_is_super_user(self):
        """Test for can_be_deleted(user) for the case where user is_superuser=True"""
        general_user = general_super_user_factory()
        eep_program = EEPProgram.objects.first()
        result = eep_program.can_be_deleted(general_user)
        self.assertTrue(result)

    def test_can_be_deleted_case_1(self):
        """
        Test for can_be_deleted(user) for scenario where user is NOT a superuser AND his
        company is_eep_sponsor .Also, given eep_program does NOT belong to either a Subdivision and
        a EEPProgramHomeStatus
        """
        eep_user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        result = eep_program.can_be_deleted(eep_user)
        self.assertTrue(result)

    def test_can_be_deleted_fails_case_1(self):
        """
        Test for can_be_deleted(user) when it should returns false.
        user is not superuser and his company is not eep_sponsor
        """
        provider_user = User.objects.filter(company__name="Provider1").first()
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        result = eep_program.can_be_deleted(provider_user)
        self.assertFalse(result)

    def test_can_be_deleted_fails_case_2(self):
        """
        Test for can_be_deleted(user) when it should returns false.
        user is not superuser and program DOES belong to a Subdivision
        """
        from axis.subdivision.tests.factories import subdivision_factory

        eep_user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        subdivision = subdivision_factory()
        eep_program_sub_status = EEPProgramSubdivisionStatus(
            subdivision=subdivision, eep_program=eep_program, company=eep_user.company
        )
        eep_program_sub_status.save()
        self.assertTrue(Subdivision.objects.filter(eep_programs=eep_program).count())
        result = eep_program.can_be_deleted(eep_user)
        self.assertFalse(result)

    def test_can_be_deleted_fails_case_3(self):
        """
        Test for can_be_deleted(user) when it should returns false.
        user is not superuser and program DOES belong to a EEPProgramHomeStatus
        """

        from axis.home.tests.factories import home_factory

        eep_user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.filter(owner__name="EEP1").first()
        home = home_factory()
        eep_program_home_status = EEPProgramHomeStatus(
            eep_program=eep_program, home=home, company=eep_user.company
        )
        eep_program_home_status.save()
        self.assertTrue(EEPProgramHomeStatus.objects.filter(eep_program=eep_program).count())
        result = eep_program.can_be_deleted(eep_user)
        self.assertFalse(result)

    def test_user_can_certify(self):
        """Test for user_can_certify()"""
        user = User.objects.get(company__name="Provider1")
        eep_program = EEPProgram.objects.first()
        can_certify = eep_program.user_can_certify(user)
        self.assertTrue(can_certify)

    def test_user_can_certify_false(self):
        """Test for user_can_certify()"""
        user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.first()
        can_certify = eep_program.user_can_certify(user)
        self.assertFalse(can_certify)

    def test_user_can_certify_certifiable_by(self):
        """Test for user_can_certify()"""
        user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.first()
        eep_program.certifiable_by.add(user.company)
        eep_program.save()
        self.assertTrue(eep_program.certifiable_by.count())
        can_certify = eep_program.user_can_certify(user)
        self.assertTrue(can_certify)

    def test_user_can_certify_certifiable_by_false(self):
        """Test for user_can_certify()"""
        user = User.objects.get(company__name="EEP1")
        eep_program = EEPProgram.objects.first()
        rater = User.objects.get(company__name="Rater1")
        eep_program.certifiable_by.add(rater.company)
        eep_program.save()
        self.assertTrue(eep_program.certifiable_by.count())
        can_certify = eep_program.user_can_certify(user)
        self.assertFalse(can_certify)

    def test_get_rater_program_itself_not_qa(self):
        """Test for get_rater_program()"""
        eep_program = EEPProgram.objects.get(name="Regular Program 3")
        result = eep_program.get_rater_program()
        self.assertEqual(eep_program, result)

    def test_get_rater_program(self):
        """Test for get_rater_program()"""
        eep_program = EEPProgram.objects.get(name="Regular Program 3")
        qa_eep_program = EEPProgram.objects.get(name="QA Program 3")
        self.assertTrue(qa_eep_program.is_qa_program)
        result = qa_eep_program.get_rater_program()
        self.assertEqual(eep_program, result)

    def test_get_qa_program_self_is_qa(self):
        """Test for get_qa_program(). the program itself is qa"""
        qa_eep_program = EEPProgram.objects.get(name="QA Program 3")
        self.assertTrue(qa_eep_program.is_qa_program)
        result = qa_eep_program.get_qa_program()
        self.assertEqual(qa_eep_program, result)  # more on this can be found in the Atom file

    def test_get_qa_program_self_is_not_qa(self):
        """Test case when program has a program that is qa"""
        eep_program = EEPProgram.objects.get(name="Regular Program 3")
        qa_eep_program = EEPProgram.objects.get(name="QA Program 3")
        result = eep_program.get_qa_program()
        self.assertEqual(qa_eep_program, result)

    def test_get_qa_program_no_qa_found(self):
        """Test case when program has no qa"""
        eep_program = EEPProgram.objects.get(name="Regular Program 1")
        result = eep_program.get_qa_program()
        self.assertIsNone(result)

    def test_alter_certification_requirements_references_none(self):
        """Test for alter_certification_requirements(requirement_tests, references=None)"""
        eep_program = EEPProgram.objects.first()
        result = eep_program.alter_certification_requirements([])

        self.assertEqual(len(result), len(self.REQUIREMENTS_TESTS))

    def test_alter_certification_requirements_no_references(self):
        """Test for alter_certification_requirements()"""
        requirement_tests = []
        eep_program = EEPProgram.objects.first()
        result = eep_program.alter_certification_requirements(requirement_tests)

        self.assertEqual(len(result), len(self.REQUIREMENTS_TESTS))

    def test_alter_certification_requirements_no_references_add(self):
        """Test for alter_certification_requirements()"""
        requirement_tests = [
            EEPProgramHomeStatus.get_rater_of_record_status,
        ]
        eep_program = EEPProgram.objects.first()
        result = eep_program.alter_certification_requirements(requirement_tests)

        self.assertGreater(len(result), len(self.REQUIREMENTS_TESTS))

    def test_alter_certification_requirements_remove_test(self):
        """So for this tests I want to keep only references to annotations_edit_url"""
        import inspect

        requirement_tests = []
        eep_program = EEPProgram.objects.first()
        references = ["annotations_edit_url"]
        result = eep_program.alter_certification_requirements(
            requirement_tests, references=references
        )
        self.assertTrue(len(result) > 0)
        reference = references[0]
        for test in result:
            required_args = inspect.getfullargspec(test).args
            self.assertTrue(reference in required_args)

    def test_alter_certification_requirements_add_test(self):
        """Test for alter_certification_requirements()"""
        requirement_tests = [
            EEPProgramHomeStatus.get_rater_of_record_status,
        ]
        eep_program = EEPProgram.objects.first()
        references = {"edit_url", "user", "home_status"}
        result = eep_program.alter_certification_requirements(
            requirement_tests, references=references
        )

        self.assertGreater(len(result), len(self.REQUIREMENTS_TESTS))
