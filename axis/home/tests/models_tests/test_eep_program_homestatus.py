"""models.py: Django """

import datetime
import logging
import random
from unittest import mock  # pylint: disable=F0401

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone

from axis.company.tests.factories import (
    architect_organization_factory,
    developer_organization_factory,
    rater_organization_factory,
    communityowner_organization_factory,
    builder_organization_factory,
    provider_organization_factory,
)
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import rater_user_factory, provider_user_factory
from axis.core.tests.testcases import AxisTestCaseUserMixin
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import (
    hirl_project_factory,
    hirl_project_registration_factory,
    builder_agreement_factory,
    coi_document_factory,
)
from axis.eep_program.models import EEPProgram
from axis.home import strings
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.mixins import EEPProgramHomeStatusManagerTestMixin
from axis.incentive_payment.models import IncentivePaymentStatus, IncentiveDistribution
from axis.relationship.utils import get_mutual_company_ids_including_self
from axis.sampleset.models import SampleSetHomeStatus
from simulation.models import get_or_import_ekotrope_simulation, get_or_import_rem_simulation

__author__ = "Johnny Fang"
__date__ = "24/7/19 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")

User = get_user_model()


# pylint: disable=R0904
# pylint: disable=C0302
# pylint: disable=W0212


class EEPProgramHomeStatusModelTests(
    EEPProgramHomeStatusManagerTestMixin, TestCase, AxisTestCaseUserMixin
):
    """Test out homes app's EEPProgramHomeStatus model"""

    client_class = AxisClient

    def test__str__(self):
        """Test __str__"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.floorplan)
        floorplan = home_status.floorplan.__str__()

        self.assertTrue(home_status.home.get_home_address_display())
        addr = home_status.home.get_home_address_display()

        self.assertTrue(home_status.home.get_builder())
        builder = home_status.home.get_builder().__str__()

        self.assertTrue(home_status.eep_program)
        program = home_status.eep_program.__str__()

        result = home_status.__str__()

        self.assertIn(floorplan, result)
        self.assertIn(builder, result)
        self.assertIn(program, result)
        self.assertIn(str(addr), result)

    def test__str___no_floorplan(self):
        """Test __str__. home_status has no floorplan"""
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertFalse(home_status.floorplan)

        self.assertTrue(home_status.home.get_home_address_display())

        self.assertTrue(home_status.home.get_builder())
        builder = home_status.home.get_builder().__str__()

        self.assertTrue(home_status.eep_program)
        program = home_status.eep_program.__str__()

        result = home_status.__str__()
        self.assertIn(builder, result)
        self.assertIn(program, result)

    @mock.patch("axis.home.models.home.Home.get_home_address_display")
    def test__str__home_address_does_not_exists(self, get_home_address_display):
        """Test __str__. home_status has no floorplan"""
        get_home_address_display.side_effect = ObjectDoesNotExist()

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.floorplan)
        floorplan = home_status.floorplan.__str__()

        self.assertTrue(home_status.home.get_builder())
        builder = home_status.home.get_builder().__str__()

        self.assertTrue(home_status.eep_program)
        program = home_status.eep_program.__str__()

        result = home_status.__str__()
        self.assertNotIn(builder, result)
        self.assertIn(program, result)
        self.assertIn(floorplan, result)

    def test_get_absolute_url(self):
        """Test that the absolute url is returned for this model"""
        from django.urls import reverse

        home_status = EEPProgramHomeStatus.objects.first()
        absolute_url = home_status.get_absolute_url()
        expected_url = reverse("home:view", kwargs={"pk": home_status.home.id})
        self.assertEqual(expected_url, absolute_url)

    @mock.patch("axis.home.models.EEPProgramHomeStatus.get_all_questions")
    @mock.patch("axis.home.models.EEPProgramHomeStatus.get_unanswered_questions")
    def test_save(self, get_all_questions, get_unanswered_questions):
        """Test save() with kwarg should_update_stats=True"""

        class MockedQuestion(object):
            """Mocked class to simplify test"""

            is_optional = False

        get_all_questions.return_value = [MockedQuestion()]
        get_unanswered_questions.return_value = [MockedQuestion(), MockedQuestion()]

        home_status = EEPProgramHomeStatus.objects.first()
        home_status.save(update_stats=True)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertAlmostEqual(home_status.pct_complete, 50.0)

    def test_can_be_added(self):
        """Test can_be_added"""
        # TODO please revise this function, at the moment makes no sense
        user = User.objects.order_by("id").first()
        result = EEPProgramHomeStatus.can_be_added(user)
        self.assertTrue(result)

    def test_can_be_edited_by_superuser(self):
        """Test that stats can be edited by superuser"""
        from axis.core.tests.factories import general_super_user_factory

        superuser = general_super_user_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.can_be_edited(superuser))

    def test_can_be_edited_by_user_from_another_co(self):
        """Test that stats can be edited by user from another company"""
        user = User.objects.get(company__name="General1")
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.can_be_edited(user)
        self.assertNotEqual(user.company.id, home_status.company.id)
        self.assertFalse(result)

    def test_user_has_no_perm_to_change_checklist_answer(self):
        """
        Test that user has permission checklist.change_answer.
        In order to NOT fail check, user MUST have these perms:
        'checklist.change_answer' or 'home.change_home'
        having just one is not sufficient. Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=home_status.company.name)
        Permission.objects.filter(codename="change_answer").delete()
        Permission.objects.filter(codename="change_home").delete()
        self.assertFalse(user.has_perm("checklist.change_answer"))
        self.assertFalse(user.has_perm("home.change_home"))
        result = home_status.can_be_edited(user)
        self.assertFalse(result)

    def test_user_has_no_perm_to_change_home(self):
        """
        Test that user has permission 'home.change_home'.
        In order to NOT fail check, user MUST have these perms:
        'checklist.change_answer' or 'home.change_home'
        having just one is not sufficient. Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=home_status.company.name)
        Permission.objects.filter(codename="change_home").delete()
        Permission.objects.filter(codename="change_answer").delete()
        self.assertFalse(user.has_perm("home.change_home"))
        self.assertFalse(user.has_perm("checklist.change_answer"))
        result = home_status.can_be_edited(user)
        self.assertFalse(result)

    def test_stats_no_sampleset_no_incentive_payment_status(self):
        """
        Test that stats can be edited, but home_status has no sampleset home status nor Incentive
        Payment Status
        Expected result False
        """
        # prep test scenario
        stats = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(stats.get_samplesethomestatus())
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertFalse(incentive_payment_status)
        today = datetime.date.today()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=today)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.can_be_edited(user)
        self.assertFalse(result)

    def test_stats_with_finished_siblings_complete_status(self):
        """
        Test that stats can be edited, but home_status has no sampleset home status nor Incentive
        Payment Status
        Expected result False
        """
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        # prep test scenario
        stat = EEPProgramHomeStatus.objects.first()
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        stats = sampleset_home_stats.home_status
        kwargs = {"home_status": stats, "state": "complete"}
        basic_incentive_payment_status_factory(**kwargs)
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertTrue(incentive_payment_status)

        today = datetime.date.today()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=today)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.can_be_edited(user)
        self.assertFalse(result)

    def test_stats_with_finished_siblings_payment_pending_status(self):
        """
        Test that stats can be edited, but home_status has no sampleset home status nor Incentive
        Payment Status
        Expected result False
        """
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        # prep test scenario
        stat = EEPProgramHomeStatus.objects.first()
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        stats = sampleset_home_stats.home_status
        kwargs = {"home_status": stats, "state": "payment_pending"}
        basic_incentive_payment_status_factory(**kwargs)
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertTrue(incentive_payment_status)

        today = datetime.date.today()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=today)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.can_be_edited(user)
        self.assertFalse(result)

    def test_stats_with_no_finished_siblings(self):
        """
        Test that stats can be edited, home_status has sampleset home status and Incentive
        Payment Status
        Expected result True
        """
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        # prep test scenario
        stat = EEPProgramHomeStatus.objects.first()
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        stats = sampleset_home_stats.home_status
        kwargs = {"home_status": stats, "state": "pending_requirements"}
        basic_incentive_payment_status_factory(**kwargs)
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertTrue(incentive_payment_status)

        today = datetime.date.today()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=today)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.can_be_edited(user)
        self.assertTrue(result)

    def test_stats_with_incentive_status_start(self):
        """
        Test that stats can be edited, home_status has sampleset home status and Incentive
        Payment Status with state 'payment_pending'. Having state in ['payment_pending', 'complete']
        will make the home_status non editable
        Expected result False
        """
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        # prep test scenario
        stat = EEPProgramHomeStatus.objects.first()
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True
        )

        stats = sampleset_home_stats.home_status
        kwargs = {"home_status": stats, "state": "payment_pending"}
        basic_incentive_payment_status_factory(**kwargs)
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertTrue(incentive_payment_status)

        today = datetime.date.today()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=today)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.can_be_edited(user)
        self.assertFalse(result)

    def test_stats_with_company_slug_aps(self):
        """
        Test that stats can be edited, home_status.eep_program.owner.slug and user.company.slug
         equal 'aps'
        Expected result True
        """
        from axis.company.models import Company
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        # prep test scenario
        stat = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=stat.eep_program.owner.id).update(slug="aps")
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True
        )
        stats = sampleset_home_stats.home_status
        kwargs = {"home_status": stats, "state": "start"}
        basic_incentive_payment_status_factory(**kwargs)
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertTrue(incentive_payment_status)
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(company=stat.eep_program.owner)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company=stat.eep_program.owner)
        permission1 = Permission.objects.get(codename="change_answer")
        permission2 = Permission.objects.get(codename="change_home")
        user.user_permissions.add(permission1)
        user.user_permissions.add(permission2)
        self.assertEqual(user.company.id, home_status.eep_program.owner.id)
        result = home_status.can_be_edited(user)
        self.assertTrue(result)

    def test_can_be_deleted_by_superuser(self):
        """
        Since can_be_edited(user) is simply a call to can_be_edited(user). we are going to test
        it against it for just a couple of cases not all of them
        """
        from axis.core.tests.factories import general_super_user_factory

        superuser = general_super_user_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.can_be_edited(superuser))
        self.assertTrue(home_status.can_be_deleted(superuser))

    def test_can_be_deleted_by_user_from_another_co(self):
        """Test that stats can be deleted by user from another company"""
        user = User.objects.get(company__name="General1")
        home_status = EEPProgramHomeStatus.objects.first()
        result_edited = home_status.can_be_edited(user)
        self.assertNotEqual(user.company.id, home_status.company.id)
        self.assertFalse(result_edited)
        result = home_status.can_be_deleted(user)
        self.assertEqual(result, result_edited)

    def test_can_de_deleted(self):
        """
        Since can_be_edited(user) is simply a call to can_be_edited(user). we are going to test
        it against it for just a couple of cases not all of them
        """
        # prep test scenario
        stats = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(stats.get_samplesethomestatus())
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=stats)
        self.assertFalse(incentive_payment_status)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.can_be_deleted(user)
        self.assertTrue(result)
        result_edited = home_status.can_be_edited(user)
        self.assertEqual(result, result_edited)

    def test_get_state_display(self):
        """Test for get_state_display()"""
        stats = EEPProgramHomeStatus.objects.first()
        result = stats.get_state_display()
        self.assertEqual(result, stats.get_state_info().description)

    def test_get_rating_type(self):
        """Test for get_rating_type - Legacy sampling helper."""
        stats = EEPProgramHomeStatus.objects.first()
        result = stats.get_rating_type()
        self.assertEqual(0, stats.samplesethomestatus_set.count())
        self.assertEqual(result, "Confirmed Rating")

    def test_get_rating_type_test_home(self):
        """Test for get_rating_type - Legacy sampling helper."""
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory

        stat = EEPProgramHomeStatus.objects.first()
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        stats = sampleset_home_stats.home_status
        result = stats.get_rating_type()
        self.assertNotEqual(0, stats.samplesethomestatus_set.count())
        self.assertEqual(result, "Sampled Test House")

    def test_get_rating_type_sampled_home(self):
        """Test for get_rating_type - Legacy sampling helper."""
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory

        stat = EEPProgramHomeStatus.objects.first()
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        sampleset_home_stats = SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True
        )

        stats = sampleset_home_stats.home_status
        result = stats.get_rating_type()
        self.assertNotEqual(0, stats.samplesethomestatus_set.count())
        self.assertFalse(sampleset_home_stats.is_test_home)
        self.assertEqual(result, "Sampled House")

    def test_set_collection_from_program(self):
        """Test set_collection_from_program"""
        from axis.eep_program.program_builder.utils.safe_ops import derive_collection_request

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.collection_request)

        eep_program = home_status.eep_program
        collection_request = derive_collection_request(to=eep_program)
        eep_program.collection_request = collection_request
        eep_program.save()
        self.assertIsNotNone(home_status.eep_program.collection_request)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        home_status.set_collection_from_program()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertIsNotNone(home_status.eep_program.collection_request)

    def test_set_collection_from_program_has_collection_already(self):
        """Test set_collection_from_program(). Homestatus already has a collection request."""
        from django_input_collection.models import CollectionRequest

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.collection_request)
        collection_request, _ = CollectionRequest.objects.get_or_create()
        home_status.collection_request = collection_request
        home_status.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        with self.assertRaises(ValueError):
            home_status.set_collection_from_program()

    def test_get_collector_no_collection_request_set(self):
        """Test get_collector(). home_status has no collection reques set"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.collection_request)
        with self.assertRaises(ValueError):
            home_status.get_collector()

    def test_get_collector(self):
        """Test get_collector()"""
        from django_input_collection.models import CollectionRequest
        from axis.checklist.collection.collectors import ChecklistCollector

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.collection_request)
        collection_request, _ = CollectionRequest.objects.get_or_create()
        home_status.collection_request = collection_request
        home_status.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_collector()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ChecklistCollector)

    def test_get_input_values_no_collection_request(self):
        """Test get_input_values(). home_status has no collection_request"""
        from axis.checklist.tests.factories import answer_factory, checklist_factory

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": 2}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        answer_slugs = []
        for question in questions:
            answer_kwrgs = {"confirmed": True}
            answer = answer_factory(question, stats.home, user, **answer_kwrgs)
            answer_slugs.append(answer.question.slug)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertIsNone(home_status.collection_request)
        result = home_status.get_input_values()
        self.assertIsNotNone(result)
        for slug in answer_slugs:
            self.assertTrue(slug in result)

    def test_get_input_values_(self):
        """Test get_input_values. we create one "question", we are expecting to get one back"""
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [{"measure_id": "notes", "type_label": "open", "required": False}]

        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat = EEPProgramHomeStatus.objects.first()

            data = {"input": "somehting", "comment": "more comments"}
            CollectedInput.objects.get_or_create(
                collection_request=collection_request,
                instrument=instrument,
                home_status=stat,
                defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
            )

            eep_program = stat.eep_program
            eep_program.collection_request = collection_request
            eep_program.save()
            stat.collection_request = collection_request
            stat.save()
            home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
            result = home_status.get_input_values()
            self.assertIsNotNone(result)
            self.assertIn("notes", result)

    def test_full_transition_non_complete_home_status(self):
        """Test full_transition, This only updates home_status state is not 'complete'"""

        stat = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=stat.id).update(state="pending_inspection")
        user = User.objects.get(company__name=stat.company.name)

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(home_status.state, "pending_inspection")
        home_status.full_transition("inspection_transition", user)

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual("certification_pending", home_status.state)

    def test_update_stats_(self):
        """
        Test update_stats() audit=True and home_status has a certification date.
        Expected result None
        """
        home_status = EEPProgramHomeStatus.objects.first()
        today = datetime.datetime.today()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(certification_date=today)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.update_stats(audit=False)
        self.assertIsNone(result)

    @mock.patch("axis.home.models.EEPProgramHomeStatus.get_all_questions")
    @mock.patch("axis.home.models.EEPProgramHomeStatus.get_unanswered_questions")
    def test_update_stats_half_pct_complete(self, get_all_questions, get_unanswered_questions):
        """
        Test update_stats() audit=True and home_status has a certification date.
        Expected result None
        """

        class MockedQuestion(object):
            """Mocked class to simplify test"""

            is_optional = False

        get_all_questions.return_value = [MockedQuestion()]
        get_unanswered_questions.return_value = [MockedQuestion(), MockedQuestion()]
        home_status = EEPProgramHomeStatus.objects.first()

        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        home_status.update_stats(audit=False)
        result = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertAlmostEqual(50.0, result.pct_complete)

    def test_update_stats_audit(self):
        """
        Test update_stats() audit=True and home_status has a certification date.
        Expected result None
        """
        from axis.checklist.tests.factories import answer_factory, checklist_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_item

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": 2}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        answer_kwrgs = {"confirmed": True}
        answer_factory(questions[0], stats.home, user, **answer_kwrgs)
        kwrgs = {"company": stats.eep_program.owner, "customer": stats.company, "status": 1}
        incentive_distribution = IncentiveDistribution.objects.create(**kwrgs)
        kwargs = {"incentive_distribution": incentive_distribution, "home_status": stats}
        basic_incentive_payment_item(**kwargs)

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        today = datetime.datetime.today()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(certification_date=today)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        home_status.update_stats(audit=True, brief_audit=False)
        result = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertAlmostEqual(50.0, result.pct_complete)

    @mock.patch(
        "axis.certification.models.WorkflowStatusHomeStatusCompatMixin.get_progress_analysis"
    )
    def test_is_eligible_for_certification(self, get_progress_analysis):
        """
        Test for is_eligible_for_certification().
        status returned from get_progress_analysis = True
        """
        data = {"status": True}
        get_progress_analysis.return_value = data
        stats = EEPProgramHomeStatus.objects.first()
        result = stats.is_eligible_for_certification()
        self.assertTrue(result)

    @mock.patch(
        "axis.certification.models.WorkflowStatusHomeStatusCompatMixin.get_progress_analysis"
    )
    def test_is_eligible_for_certification_false(self, get_progress_analysis):
        """
        Test for is_eligible_for_certification().
        status returned from get_progress_analysis = False
        """
        data = {"status": False}
        get_progress_analysis.return_value = data
        stats = EEPProgramHomeStatus.objects.first()
        result = stats.is_eligible_for_certification()
        self.assertFalse(result)

    @mock.patch(
        "axis.certification.models.WorkflowStatusHomeStatusCompatMixin.get_progress_analysis"
    )
    def test_report_eligibility_for_certification(self, get_progress_analysis):
        """Test for report_eligibility_for_certification"""
        data = {
            "requirements": {
                1: {"status": False, "message": "Test message"},
                2: {"status": False, "message": "Another test message"},
            }
        }
        get_progress_analysis.return_value = data
        stats = EEPProgramHomeStatus.objects.first()
        result = stats.report_eligibility_for_certification()
        self.assertEqual(2, len(result))
        self.assertListEqual(["Test message", "Another test message"], result)

    @mock.patch(
        "axis.certification.models.WorkflowStatusHomeStatusCompatMixin.get_progress_analysis"
    )
    def test_report_eligibility_for_certification_empty_result(self, get_progress_analysis):
        """Test for report_eligibility_for_certification"""
        data = {"requirements": {}}
        get_progress_analysis.return_value = data
        stats = EEPProgramHomeStatus.objects.first()
        result = stats.report_eligibility_for_certification()
        self.assertFalse(result)

    def test_can_be_decertified_true(self):
        """
        Test can_be_decertified. in order to return True, the following must be true:
        home_status state =  'complete' AND have a certification_date.
        no IPPP items
        either the user's company owns the program OR the home_status co is provider
        the program is not part of the NGBS_PROGRAM_NAMES
        Expected result True
        """
        stats = EEPProgramHomeStatus.objects.first()
        today = datetime.datetime.today()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(
            certification_date=today, state="complete"
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertIsNotNone(home_status.certification_date)
        self.assertEqual(home_status.state, "complete")
        self.assertFalse(home_status.ippitem_set.all().count())
        self.assertNotIn(
            home_status.eep_program.slug, customer_hirl_app.NGBS_PROGRAM_NAMES.values()
        )
        user = User.objects.get(company=home_status.eep_program.owner)
        result = home_status.can_be_decertified(user)
        self.assertTrue(result)

    def test_can_be_decertified_false_with_report(self):
        """
        Test can_be_decertified. in order to return False, one of the following must be False:
        home_status state =  'complete' AND have a certification_date.
        no IPPP items
        either the user's company owns the program OR the home_status co is provider
        the program is not part of the NGBS_PROGRAM_NAMES
        Expected result True
        """

        home_status = EEPProgramHomeStatus.objects.first()

        self.assertIsNone(home_status.certification_date)
        self.assertNotEqual(home_status.state, "complete")
        self.assertFalse(home_status.ippitem_set.all().count())
        self.assertNotIn(
            home_status.eep_program.slug, customer_hirl_app.NGBS_PROGRAM_NAMES.values()
        )
        user = User.objects.get(company=home_status.eep_program.owner)
        result = home_status.can_be_decertified(user, report=True)
        self.assertFalse(result)

    def test_decertify_state_not_complete_check_only(self):
        """Test for decertify(). home_status state fails the 'complete' state check"""
        stats = EEPProgramHomeStatus.objects.first()
        if stats.state == "complete":
            EEPProgramHomeStatus.objects.filter(id=stats.id).update(state="pending")
        self.assertNotEqual("complete", stats.state)
        user = User.objects.get(company__name=stats.company.name)
        result, _warnings = stats.decertify(user, check_only=True, report=True, force=False)
        self.assertFalse(result)
        self.assertEqual("This program is not yet certified.", _warnings[0])

    def test_decertify_no_certification_date_check_only(self):
        """Test for decertify(). home_status fails the certification_date check"""
        stats = EEPProgramHomeStatus.objects.first()
        if stats.state != "complete":
            EEPProgramHomeStatus.objects.filter(id=stats.id).update(state="complete")
        if stats.certification_date:
            EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=None)
        stats = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertEqual("complete", stats.state)
        self.assertIsNone(stats.certification_date)
        user = User.objects.get(company__name=stats.company.name)
        result, _warnings = stats.decertify(user, check_only=True, report=True, force=False)
        self.assertFalse(result)
        self.assertIn("This program is not yet certified.", _warnings)

    def test_decertify_ippitem_check_only(self):
        """Test for decertify(). home_status fails the ippitem test and raises a warning."""
        from axis.incentive_payment.tests.factories import basic_incentive_payment_item

        stats = EEPProgramHomeStatus.objects.first()
        if not stats.ippitem_set.all().count():
            kwrgs = {"company": stats.eep_program.owner, "customer": stats.company, "status": 1}
            incentive_distribution, _ = IncentiveDistribution.objects.get_or_create(**kwrgs)
            kwargs = {"incentive_distribution": incentive_distribution, "home_status": stats}
            basic_incentive_payment_item(**kwargs)
            stats = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(stats.ippitem_set.all().count())

        user = User.objects.get(company__name=stats.company.name)
        result, _warnings = stats.decertify(user, check_only=True, report=True, force=False)
        self.assertFalse(result)
        self.assertIn("Incentives may exist as IPP items are on this.", _warnings)

    def test_decertify_by_providers_only_check_only(self):
        """
        Test for decertify(). home_status company is type 'rater' and is not the same company as the
         user. Also, users' company has no relationship with home_status.
        """
        from axis.company.models import Company

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="QA1")
        rater_co = Company.objects.get(name="Rater1")
        if stats.company.company_type != "rater":
            EEPProgramHomeStatus.objects.filter(id=stats.id).update(company=rater_co)
            stats = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(stats.company.company_type == "rater")
        self.assertTrue(stats.eep_program.owner_id != user.company.id)
        result, _warnings = stats.decertify(user, check_only=True, report=True, force=False)
        self.assertFalse(result)
        self.assertIn("Only Certification Organizations allowed to decertify this", _warnings)

    def test_decertify_ngbs_program_check_only(self):
        """Test for decertify(). home_status' eep_program name is in NGBS_PROGRAM_NAMES"""

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        upper_bound = len(customer_hirl_app.NGBS_PROGRAM_NAMES.values())
        rand_index = random.randint(0, upper_bound - 1)
        ngbs_program_slug = list(customer_hirl_app.NGBS_PROGRAM_NAMES.values())[rand_index]
        EEPProgram.objects.filter(id=stats.eep_program.id).update(slug=ngbs_program_slug)
        stats = EEPProgramHomeStatus.objects.first()
        result, _warnings = stats.decertify(user, check_only=True, report=True, force=False)
        self.assertFalse(result)
        self.assertIn("Imported programs cannot be decertified", _warnings)

    def test_decertify_ngbs_program_decertified_failed(self):
        """Test for decertify(). check_only flag set to False and report to True"""
        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        # asserting these two conditions we guaranteed that at least one warning will be appended
        self.assertNotEqual("complete", stats.state)
        self.assertIsNone(stats.certification_date)
        result = stats.decertify(user, check_only=False, report=True, force=False)
        msg = "Decertify {} on {} failed:".format(
            stats.eep_program,
            stats.home,
        )
        self.assertIn(msg, result)

    def test_decertify_ngbs_program_decertified_failed_and_forced(self):
        """
        Test for decertify(). check_only flag set to False and report to True
        home_status has certification_date, state != inspection, incentivepaymentstatus
        home_status has no qa_statuses, fasttracksubmission, questions/answers
        """
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        if stats.state == "inspection":
            EEPProgramHomeStatus.objects.filter(id=stats.id).update(state="complete")
        if not stats.certification_date:
            EEPProgramHomeStatus.objects.filter(id=stats.id).update(
                certification_date=datetime.date.today()
            )
        try:
            stats.incentivepaymentstatus.objects.count()
        except ObjectDoesNotExist:
            kwargs = {"home_status": stats, "state": "start"}
            basic_incentive_payment_status_factory(**kwargs)
        stats = EEPProgramHomeStatus.objects.get(id=stats.id)
        # asserting these two conditions we guaranteed that at least one warning will be appended
        self.assertNotEqual("inspection", stats.state)
        self.assertIsNotNone(stats.certification_date)
        self.assertTrue(stats.incentivepaymentstatus)
        result = stats.decertify(user, check_only=False, report=True, force=True)
        msg = "Decertified {} on {}".format(
            stats.eep_program,
            stats.home,
        )
        self.assertIn(msg, result)
        self.assertIn("Removed certification date", result)
        self.assertIn("reset state to active", result)
        self.assertIn("removed incentive status", result)
        self.assertIn("This program is not yet certified.", result)

    def test_decertify_unlock_answers(self):
        """Test for decertify() unlock answers"""
        from axis.checklist.tests.factories import answer_factory, checklist_factory
        from axis.checklist.models import Answer

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": 3}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions:
            answer_kwrgs = {"confirmed": True}
            answer = answer_factory(question, stats.home, user, **answer_kwrgs)
            self.assertTrue(answer.confirmed)
        result = stats.decertify(user, check_only=False, report=True, force=True)
        questions = stats.eep_program.get_checklist_question_set()
        answers = Answer.objects.filter(home=stats.home, question__in=questions).all()
        for answr in answers:
            self.assertFalse(answr.confirmed)
        self.assertIn("unlocked {} answers".format(answers.count()), result)

    def test_reassign_user(self):
        """
        Test reassign_user. home_status has floorplans, at least one has simulation (remrate). Also,
        home_status includes samplesets.
        Expected result reassignment without issues.
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory
        from axis.sampleset.tests.factories import empty_sampleset_factory

        user = User.objects.get(company__name="General1")
        home_status = EEPProgramHomeStatus.objects.first()
        floorplan = floorplan_with_remrate_factory()
        sampleset_kwrgs = {"owner": home_status.company}
        sampleset = empty_sampleset_factory(**sampleset_kwrgs)
        SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=home_status, revision=1, is_active=True
        )
        home_status.floorplans.add(floorplan)
        self.assertNotEqual(home_status.company, user.company)
        home_status.reassign_user(user=user, include_samplesets=True)
        stats = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertEqual(stats.company, user.company)
        for floorplan in list(stats.floorplans.all()):
            if floorplan.remrate_target:
                remrate = floorplan.remrate_target
                self.assertEqual(remrate.company, user.company)
        for ss in home_status.sampleset_set.all().distinct():
            self.assertEqual(ss.owner, user.company)

    def test_reassing_user_home_status_with_nofloorplan(self):
        """
        Test for reassign_user. home_status has no floorplan and no floorplans.
        Expected result complete reassignment with no issues.
        """
        user = User.objects.get(company__name="General1")
        home_status = EEPProgramHomeStatus.objects.first()
        if home_status.floorplans.count():
            home_status.floorplans.clear()
        if home_status.floorplan:
            home_status.floorplan = None
        home_status.save()
        stats = EEPProgramHomeStatus.objects.get(id=home_status.id)
        stats.reassign_user(user=user, include_samplesets=False)
        self.assertEqual(stats.company, user.company)

    def test_is_confirmed_rating(self):
        """Test for is_confirmed_rating"""
        home_status = EEPProgramHomeStatus.objects.first()
        expected = home_status.samplesethomestatus_set.count() == 0
        result = home_status.is_confirmed_rating()
        self.assertEqual(expected, result)

    def test_is_gating_qa_complete(self):
        """
        Test is_gating_qa_complete. home_status has potential QA requirements.
        Expected result True
        """
        from axis.qa.models import QARequirement

        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="QA1")
        QARequirement.objects.create(
            qa_company=user.company, type="file", eep_program=home_status.eep_program
        )
        qa_requirements = QARequirement.objects.filter_for_home_status(home_status)
        self.assertEqual(qa_requirements.count(), 1)
        requirement = qa_requirements.first()
        qastatuses = requirement.qastatus_set.filter(
            Q(home_status=home_status) | Q(subdivision__home__homestatuses=home_status)
        )
        self.assertFalse(qastatuses)
        self.assertFalse(requirement.coverage_pct >= 1)
        self.assertFalse(requirement.gate_certification)
        result = home_status.is_gating_qa_complete()
        self.assertTrue(result)

    def test_is_gating_qa_complete_gate_certification(self):
        """
        Test is_gating_qa_complete. home_status has potential QA requirements.
        requirement has gate_certification set to True
        requirement has one qa status' state is 'complete'
        expected result complete = True
        """
        from axis.qa.models import QAStatus, QARequirement

        home_status = EEPProgramHomeStatus.objects.first()
        qa_user = User.objects.get(company__name="QA1")
        requirement = QARequirement.objects.create(
            qa_company=qa_user.company,
            type="file",
            gate_certification=True,
            eep_program=home_status.eep_program,
        )
        QAStatus.objects.create(
            home_status=home_status,
            owner=qa_user.company,
            result="pass",
            state="complete",
            requirement=requirement,
        )
        qa_requirements = QARequirement.objects.filter_for_home_status(home_status)
        self.assertEqual(qa_requirements.count(), 1)
        requirement = qa_requirements.first()
        qastatuses = requirement.qastatus_set.filter(
            Q(home_status=home_status) | Q(subdivision__home__homestatuses=home_status)
        )
        self.assertTrue(qastatuses)
        self.assertTrue(requirement.gate_certification)
        self.assertFalse(
            qastatuses.filter(requirement__gate_certification=True)
            .exclude(state="complete")
            .count()
        )
        result = home_status.is_gating_qa_complete()
        self.assertTrue(result)

    def test_is_gating_qa_complete_gating_requirement_not_met(self):
        """
        Test is_gating_qa_complete. home_status has potential QA requirements.
        requirement's coverage_pct is 1.0
        requirement's gate_certification flagged
        Expected result False
        """
        from axis.qa.models import QARequirement

        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="QA1")
        QARequirement.objects.create(
            qa_company=user.company,
            type="file",
            coverage_pct=1.0,
            eep_program=home_status.eep_program,
            gate_certification=True,
        )
        qa_requirements = QARequirement.objects.filter_for_home_status(home_status)
        self.assertEqual(qa_requirements.count(), 1)
        requirement = qa_requirements.first()
        qastatuses = requirement.qastatus_set.filter(
            Q(home_status=home_status) | Q(subdivision__home__homestatuses=home_status)
        )
        self.assertFalse(qastatuses)
        self.assertTrue(requirement.coverage_pct >= 1)
        self.assertTrue(requirement.gate_certification)
        result = home_status.is_gating_qa_complete()
        self.assertFalse(result)

    def test_is_gating_qa_complete_gate_certification_gating_req_not_met(self):
        """
        Test is_gating_qa_complete. home_status has potential QA requirements.
        requirement has gate_certification set to True
        requirement has one qa status' state is NOT 'complete'
        expected result complete = True
        """
        from axis.qa.models import QAStatus, QARequirement

        home_status = EEPProgramHomeStatus.objects.first()
        qa_user = User.objects.get(company__name="QA1")
        requirement = QARequirement.objects.create(
            qa_company=qa_user.company,
            type="file",
            gate_certification=True,
            eep_program=home_status.eep_program,
        )
        QAStatus.objects.create(
            home_status=home_status,
            owner=qa_user.company,
            result="pass",
            state="initial",
            requirement=requirement,
        )
        qa_requirements = QARequirement.objects.filter_for_home_status(home_status)
        self.assertEqual(qa_requirements.count(), 1)
        requirement = qa_requirements.first()
        qastatuses = requirement.qastatus_set.filter(
            Q(home_status=home_status) | Q(subdivision__home__homestatuses=home_status)
        )
        self.assertTrue(qastatuses)
        self.assertTrue(requirement.gate_certification)
        self.assertTrue(
            qastatuses.filter(requirement__gate_certification=True)
            .exclude(state="complete")
            .count()
        )
        result = home_status.is_gating_qa_complete()
        self.assertFalse(result)

    def test_is_allowed_by_projecttracker_criteria_not_met(self):
        """
        Test is_allowed_by_projecttracker.
        home_status eep_program.slug does NOT start with eto
        home_status state is NOT complete
        home_status eep_program is not qa program
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.get(company__name="General1")
        self.assertFalse(home_status.eep_program.slug.startswith("eto"))
        self.assertFalse(home_status.state == "complete")
        self.assertFalse(home_status.eep_program.is_qa_program)
        result = home_status.is_allowed_by_projecttracker()
        self.assertFalse(result)

    def test_is_allowed_by_projecttracker_eto_slug(self):
        """
        Test is_allowed_by_projecttracker.
        home_status eep_program.slug starts with eto
        home_status state is NOT complete
        home_status eep_program is NOT qa program
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.get(company__name="General1")
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(slug="eto-program-thing")
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.slug.startswith("eto"))
        self.assertFalse(home_status.state == "complete")
        self.assertFalse(home_status.eep_program.is_qa_program)
        self.assertFalse(home_status.is_allowed_by_projecttracker())

    def test_is_allowed_by_projecttracker_complete_state(self):
        """
        Test is_allowed_by_projecttracker.
        home_status eep_program.slug does NOT start with eto
        home_status state is complete
        home_status eep_program is NOT qa program
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.get(company__name="General1")
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            state="complete",
            certification_date=datetime.date.today(),
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertFalse(home_status.eep_program.slug.startswith("eto"))
        self.assertTrue(home_status.state == "complete")
        self.assertFalse(home_status.eep_program.is_qa_program)
        result = home_status.is_allowed_by_projecttracker()
        self.assertFalse(result)

    def test_is_allowed_by_projecttracker_qa_program(self):
        """
        Test is_allowed_by_projecttracker.
        home_status eep_program.slug does NOT start with eto
        home_status state is NOT complete
        home_status eep_program is  qa program
        Expected result True
        """
        home_status = EEPProgramHomeStatus.objects.get(company__name="General1")
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(is_qa_program=True)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertFalse(home_status.eep_program.slug.startswith("eto"))
        self.assertFalse(home_status.state == "complete")
        self.assertTrue(home_status.eep_program.is_qa_program)
        result = home_status.is_allowed_by_projecttracker()
        self.assertFalse(result)

    def test_is_allowed_by_projecttracker_not_allowed(self):
        """
        Test is_allowed_by_projecttracker.
        home_status eep_program.slug starts with eto
        home_status state is complete
        home_status eep_program is qa program
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.get(company__name="General1")
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            is_qa_program=True, slug="eto-program-thing"
        )
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            state="complete",
            certification_date=datetime.date.today(),
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.slug.startswith("eto"))
        self.assertTrue(home_status.state == "complete")
        self.assertTrue(home_status.eep_program.is_qa_program)
        result = home_status.is_allowed_by_projecttracker()
        self.assertFalse(result)

    def test_is_allowed_by_projecttracker_allowed(self):
        """
        Test is_allowed_by_projecttracker.
        home_status eep_program.slug starts with eto
        home_status state is complete
        home_status eep_program is NOT qa program
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.get(company__name="General1")
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            is_qa_program=False, slug="eto-program-thing"
        )
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            state="complete",
            certification_date=datetime.date.today(),
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.slug.startswith("eto"))
        self.assertTrue(home_status.state == "complete")
        self.assertFalse(home_status.eep_program.is_qa_program)
        result = home_status.is_allowed_by_projecttracker()
        self.assertTrue(result)

    def test_can_be_submitted_to_projecttracker_no_fts(self):
        """
        Test can_be_submitted_to_projecttracker
        home_status can be submitted to projectracker if fast track submission is NOT locked
        if home_status does NOT have fasttracksubmission then is assumed NOT locked
        Expected result True
        """
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertFalse(hasattr(home_status, "fasttracksubmission"))
        result = home_status.can_be_submitted_to_projecttracker()
        self.assertFalse(result)

    def test_can_be_submitted_to_projecttracker_unlocked_fts(self):
        """
        Test can_be_submitted_to_projecttracker.
        home_status can be submitted to projectracker if fast track submission is NOT locked
        FastTrackSubmission is locked when all the following criteria is met:
        it has an eps_score (not None), and its home_status has a certification date
        """
        from axis.customer_eto.models import FastTrackSubmission

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.certification_date)
        self.assertEqual(home_status.state, "certification_pending")

        fts = FastTrackSubmission.objects.create(
            home_status=home_status, project_id="", eps_score=20
        )
        self.assertTrue(hasattr(home_status, "fasttracksubmission"))
        self.assertFalse(fts.is_locked())
        self.assertFalse(fts.can_be_sent_to_fastrack())

        self.assertEqual(home_status.fasttracksubmission.pk, fts.pk)
        self.assertFalse(home_status.can_be_submitted_to_projecttracker())

        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            certification_date=datetime.date.today(), state="complete"
        )

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.fasttracksubmission.is_locked())
        self.assertTrue(home_status.fasttracksubmission.can_be_sent_to_fastrack())
        self.assertTrue(home_status.can_be_submitted_to_projecttracker())

    def test_can_be_submitted_to_projecttracker_locked_fts(self):
        """
        Test can_be_submitted_to_projecttracker.
        home_status can be submitted to projectracker if fast track submission is NOT locked
        FastTrackSubmission is locked when all the following criteria is met:
        it has a project_id, eps_score (not None), and its home_status has a certification date
        """
        from axis.customer_eto.models import FastTrackSubmission

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            certification_date=datetime.date.today(), state="complete"
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        fts = FastTrackSubmission.objects.create(
            home_status=home_status, project_id=20, eps_score=10
        )

        self.assertEqual(home_status.fasttracksubmission.pk, fts.pk)
        self.assertTrue(fts.is_locked())
        self.assertFalse(fts.can_be_sent_to_fastrack())
        self.assertFalse(home_status.can_be_submitted_to_projecttracker())

    def test_get_certification_agent_no_certification_agent(self):
        """Test get_certification_agent"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertFalse(home_status.eep_program.certifiable_by.exists())
        result = home_status.get_certification_agent()
        self.assertEqual(result, home_status.company)

    def test_get_certification_agent_with_certification_agent(self):
        """Test get_certification_agent()"""
        from axis.company.models import Company

        eep1 = Company.objects.get(name="EEP1")
        home_status = EEPProgramHomeStatus.objects.filter(company__name="Provider1").first()
        eep_program = home_status.eep_program
        eep_program.certifiable_by.add(eep1)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.certifiable_by.exists())
        result = home_status.get_certification_agent()
        self.assertNotEqual(result, home_status.company)
        self.assertEqual(result, eep1)

    def test_get_certification_agent_multiple_candidate_agents(self):
        """
        Test get_certification_agent(). having multiple candidate agents shouldn't affect getting
        back a certification agent. raises a log warning
        """
        from axis.company.models import Company

        eep1 = Company.objects.get(name="EEP1")
        eep2 = Company.objects.get(name="Rater1")
        home_status = EEPProgramHomeStatus.objects.filter(company__name="Provider1").first()
        eep_program = home_status.eep_program
        eep_program.certifiable_by.add(eep1)
        eep_program.certifiable_by.add(eep2)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.certifiable_by.exists())
        result = home_status.get_certification_agent()
        self.assertNotEqual(result, home_status.company)
        self.assertEqual(result, eep1)

    @mock.patch(
        "axis.certification.models.WorkflowStatusHomeStatusCompatMixin.get_progress_analysis"
    )
    def test_can_user_certify_failed_eligibility_check(self, get_progress_analysis):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is NOT
        eligible for certification
        """
        data = {"status": False}
        get_progress_analysis.return_value = data

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertFalse(home_status.is_eligible_for_certification())
        user = User.objects.get(company__name="General1")
        result = home_status.can_user_certify(user, perform_eligiblity_check=True)
        self.assertFalse(result)

    def test_can_user_certify_for_mutual_company(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.is_eligible_for_certification())
        self.assertFalse(home_status.get_sampleset())
        self.assertTrue(home_status.is_gating_qa_complete())
        user = User.objects.get(company__name="General1")
        self.assertFalse(user.is_superuser)
        self.assertFalse(home_status.eep_program.owner == home_status.company == user.company)
        self.assertIn(home_status.company.id, get_mutual_company_ids_including_self(user.company))
        result = home_status.can_user_certify(user, perform_eligiblity_check=True)
        self.assertFalse(result)

    def test_can_user_certify_for_superuser(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        from axis.core.tests.factories import general_super_user_factory

        superuser = general_super_user_factory()

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.is_eligible_for_certification())
        self.assertFalse(home_status.get_sampleset())
        self.assertTrue(home_status.is_gating_qa_complete())

        self.assertTrue(superuser.is_superuser)
        result = home_status.can_user_certify(superuser, perform_eligiblity_check=True)
        self.assertTrue(result)

    def test_can_user_certify_for_rater(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """

        user = User.objects.get(company__name="Rater1")
        stats = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(company=user.company)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(owner=user.company)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertFalse(home_status.get_sampleset())
        self.assertTrue(home_status.is_gating_qa_complete())
        self.assertFalse(user.is_superuser)
        self.assertTrue(home_status.eep_program.owner == home_status.company == user.company)
        result = home_status.can_user_certify(user, perform_eligiblity_check=False)
        self.assertTrue(result)

    @mock.patch("axis.home.models.EEPProgramHomeStatus.is_gating_qa_complete")
    def test_can_user_certify_gating_qa_not_complete(self, is_gating_qa_complete):
        """
        Test can_user_certify(). perform_eligiblity_check set False, home_status has no sampleset,
        home_Status gating_qa NOT complete.
        Expected result False
        """
        data = False
        is_gating_qa_complete.return_value = data
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="General1")
        self.assertFalse(home_status.get_sampleset())
        self.assertFalse(home_status.is_gating_qa_complete())
        result = home_status.can_user_certify(user, perform_eligiblity_check=False)
        self.assertFalse(result)

    def test_can_user_certify_unexpected_user(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        from axis.core.tests.factories import general_admin_factory

        general_user = general_admin_factory(company__name="Generality")
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.is_eligible_for_certification())
        self.assertFalse(home_status.get_sampleset())
        self.assertTrue(home_status.is_gating_qa_complete())

        self.assertFalse(general_user.is_superuser)
        self.assertFalse(
            home_status.eep_program.owner == home_status.company == general_user.company
        )
        self.assertNotIn(
            home_status.company.id, get_mutual_company_ids_including_self(general_user.company)
        )
        result = home_status.can_user_certify(general_user, perform_eligiblity_check=False)
        self.assertFalse(result)

    def test_can_user_certify_sampleset_no_resnet(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory

        # prep test scenario
        stat = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        EEPProgram.objects.filter(id=stat.eep_program.id).update(
            require_resnet_sampling_provider=True
        )
        sampleset = sampleset_with_subdivision_homes_factory(**{"eep_program": stat.eep_program})
        SampleSetHomeStatus.objects.create(
            sampleset=sampleset, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.get_sampleset())

        result = home_status.can_user_certify(user, perform_eligiblity_check=False)
        self.assertFalse(result)

    def test_can_user_certify_resnet_is_sampling_provider_approved(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        from axis.sampleset.tests.factories import empty_sampleset_factory
        from axis.resnet.tests.factories import resnet_company_factory
        from axis.core.tests.factories import basic_user_factory

        # prep test scenario
        provider = User.objects.get(company__name="Provider1")
        resnet_kwargs = {"company": provider.company, "is_sampling_provider": True}
        resnet_co = resnet_company_factory(**resnet_kwargs)
        user = basic_user_factory()
        user.company = resnet_co.company
        user.save()
        user = User.objects.get(id=user.id)
        stat = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=stat.eep_program.id).update(
            require_resnet_sampling_provider=True
        )
        sampleset_kwargs = {"owner": provider.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.get_sampleset())

        result = home_status.can_user_certify(user, perform_eligiblity_check=False)
        self.assertTrue(result)

    def test_can_user_certify_resnet_is_sampling_provider_not_approved(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        from axis.sampleset.tests.factories import empty_sampleset_factory
        from axis.resnet.tests.factories import resnet_company_factory
        from axis.core.tests.factories import basic_user_factory

        # prep test scenario
        provider = User.objects.get(company__name="Provider1")
        resnet_kwargs = {"company": provider.company, "is_sampling_provider": False}
        resnet_co = resnet_company_factory(**resnet_kwargs)
        user = basic_user_factory()
        user.company = resnet_co.company
        user.save()
        user = User.objects.get(id=user.id)
        stat = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=stat.eep_program.id).update(
            require_resnet_sampling_provider=True
        )
        sampleset_kwargs = {"owner": provider.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.get_sampleset())

        result = home_status.can_user_certify(user, perform_eligiblity_check=False)
        self.assertFalse(result)

    def test_can_user_certify_resnet_require_resnet_sampling_provider_user_superuser(self):
        """
        Test can_user_certify(). perform_eligiblity_check is flagged, and home_Status is eligible
        for certification
        """
        from axis.sampleset.tests.factories import empty_sampleset_factory
        from axis.core.tests.factories import general_super_user_factory

        # prep test scenario
        superuser = general_super_user_factory()
        stat = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=stat.eep_program.id).update(
            require_resnet_sampling_provider=True
        )
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertTrue(home_status.get_sampleset())

        result = home_status.can_user_certify(superuser, perform_eligiblity_check=False)
        self.assertTrue(result)

    def test__can_user_edit_for_superuser(self):
        """Test _can_user_edit(). Expected result True"""
        # prep test scenario
        from axis.core.tests.factories import general_super_user_factory

        superuser = general_super_user_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status._can_user_edit(superuser)
        self.assertTrue(result)

    def test__can_user_edit_true(self):
        """Test _can_user_edit(). Expected result True"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company=home_status.company)
        self.assertFalse(home_status.certification_date)
        result = home_status._can_user_edit(user)
        self.assertTrue(result)

    def test__can_user_edit_user_company_different(self):
        """
        Test _can_user_edit(). user's company is different from home_status' company
        Expected result False
        """
        user = User.objects.get(company__name="EEP1")
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertNotEqual(user.company.id, home_status.company.id)
        result = home_status._can_user_edit(user)
        self.assertFalse(result)

    def test__can_user_edit_user_has_no_perms(self):
        """
        Test _can_user_edit(). user has not the required permissions ['change_answer','change_home']
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=home_status.company.name)
        Permission.objects.filter(codename="change_answer").delete()
        Permission.objects.filter(codename="change_home").delete()
        # self.assertFalse(user.has_perm('checklist.change_answer'))
        perms = user.has_perm("checklist.change_answer") and user.has_perm("home.change_home")
        self.assertFalse(perms)

        self.assertEqual(user.company.id, home_status.company.id)
        result = home_status._can_user_edit(user)
        self.assertFalse(result)

    def test__can_user_edit_no_incentive_payment(self):
        """
        Test for _can_user_edit() when eepprogram owner is customer and home_status ahas a
        certification_date but incentivepaymentstatus' state is not in
        ['payment_pending', 'complete']
        Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            certification_date=datetime.date.today()
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        user = User.objects.get(company__name=home_status.company.name)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.company.id, home_status.company.id)
        perms = user.has_perm("checklist.change_answer") and user.has_perm("home.change_home")
        self.assertTrue(perms)

        self.assertTrue(home_status.eep_program.owner.is_customer)
        self.assertTrue(home_status.certification_date)
        result = home_status._can_user_edit(user)
        self.assertFalse(result)

    def test__can_user_edit_with_incentive_payment(self):
        """
        Test for _can_user_edit() when eepprogram owner is customer and home_status ahas a
        certification_date but incentivepaymentstatus' state is in ['payment_pending', 'complete']
        Expected result False
        """
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(
            certification_date=datetime.date.today()
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        kwargs = {"home_status": home_status, "state": "complete"}
        basic_incentive_payment_status_factory(**kwargs)
        incentive_payment_status = IncentivePaymentStatus.objects.filter(home_status=home_status)
        self.assertTrue(incentive_payment_status)

        user = User.objects.get(company__name=home_status.company.name)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.company.id, home_status.company.id)
        perms = user.has_perm("checklist.change_answer") and user.has_perm("home.change_home")
        self.assertTrue(perms)
        self.assertTrue(home_status.eep_program.owner.is_customer)
        self.assertTrue(home_status.certification_date)
        result = home_status._can_user_edit(user)
        self.assertFalse(result)

    def test_get_simplified_status_for_user_completed_state(self):
        """
        Test get_simplified_status_for_user(). home_status state is 'complete'
        Expected result True
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state="complete")
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertEqual("complete", home_status.state)

        user = User.objects.get(company__name=home_status.company.name)
        result = home_status.get_simplified_status_for_user(user)
        self.assertTrue(result)

    @mock.patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_simplified_status_for_user_can_edit_view(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """
        Test get_simplified_status_for_user(). home_status state is NOT 'complete'
        Expected result
        can_view, can_edit = True
        can_transition_to_certify, can_certify, completed, has_checklist = False
        """

        is_eligible_for_certification.return_value = True
        can_user_certify.return_value = True
        can_be_edited.return_value = True

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state="inspection")
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            manual_transition_on_certify=True,
            program_submit_date=datetime.date.today() - datetime.timedelta(days=1),
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)

        # makes can_transition_to_certify = False
        self.assertEqual("inspection", home_status.state)
        self.assertTrue(home_status.eep_program.manual_transition_on_certify)
        submission_check = (
            home_status.eep_program.program_submit_date
            and home_status.eep_program.program_submit_date
        )
        self.assertTrue(submission_check)

        user = User.objects.get(company__name=home_status.company.name)
        (
            can_edit,
            can_view,
            can_transition_to_certify,
            can_certify,
            completed,
            has_checklist,
        ) = home_status.get_simplified_status_for_user(user)
        self.assertTrue(can_edit)
        self.assertTrue(can_view)
        self.assertFalse(can_transition_to_certify)
        self.assertFalse(can_certify)
        self.assertFalse(completed)
        self.assertFalse(has_checklist)

    @mock.patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_simplified_status_for_user_cannot_do(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """
        Test get_simplified_status_for_user(). home_status state is NOT 'complete'
        Expected result
        can_view, can_edit = True
        can_transition_to_certify, can_certify, completed, has_checklist = False
        """
        is_eligible_for_certification.return_value = False
        can_user_certify.return_value = False
        can_be_edited.return_value = False

        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="EEP2")
        check1 = EEPProgramHomeStatus.objects.filter_by_user(user, id=home_status.id).exists()
        self.assertFalse(check1)
        (
            can_edit,
            can_view,
            can_transition_to_certify,
            can_certify,
            completed,
            has_checklist,
        ) = home_status.get_simplified_status_for_user(user)
        self.assertFalse(can_edit)
        self.assertFalse(can_view)
        self.assertFalse(can_transition_to_certify)
        self.assertFalse(can_certify)
        self.assertFalse(completed)
        self.assertFalse(has_checklist)

    @mock.patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_simplified_status_for_user_can_do_all_but_transition(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """
        Test get_simplified_status_for_user(). home_status state is NOT 'complete'
        Expected result
        can_view, can_edit = True
        can_certify, has_checklist = True
        can_transition_to_certify, completed = False
        """
        from axis.checklist.tests.factories import checklist_factory

        is_eligible_for_certification.return_value = True
        can_user_certify.return_value = True
        can_be_edited.return_value = True

        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        checklist = checklist_factory()
        eep_program.required_checklists.add(checklist)
        user = User.objects.get(company=home_status.company)
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            manual_transition_on_certify=True
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.required_checklists.exists())
        check1 = EEPProgramHomeStatus.objects.filter_by_user(user, id=home_status.id).exists()
        self.assertTrue(check1)
        (
            can_edit,
            can_view,
            can_transition_to_certify,
            can_certify,
            completed,
            has_checklist,
        ) = home_status.get_simplified_status_for_user(user)
        self.assertTrue(can_edit)
        self.assertTrue(can_view)
        self.assertFalse(can_transition_to_certify)
        self.assertTrue(can_certify)
        self.assertFalse(completed)
        self.assertTrue(has_checklist)

    @mock.patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_simplified_status_for_user_can_transition_to_certify(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """
        Test get_simplified_status_for_user(). home_status state is NOT 'complete'
        Expected result
        can_view, can_edit = True
        can_transition_to_certify, can_certify, completed, has_checklist = False
        """
        from axis.checklist.tests.factories import checklist_factory

        is_eligible_for_certification.return_value = True
        can_user_certify.return_value = True
        can_be_edited.return_value = True

        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        checklist = checklist_factory()
        eep_program.required_checklists.add(checklist)
        user = User.objects.get(company__name="EEP1")
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state="inspection")
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            manual_transition_on_certify=True
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        check1 = EEPProgramHomeStatus.objects.filter_by_user(user, id=home_status.id).exists()
        self.assertTrue(check1)
        (
            can_edit,
            can_view,
            can_transition_to_certify,
            can_certify,
            completed,
            has_checklist,
        ) = home_status.get_simplified_status_for_user(user)
        self.assertTrue(can_edit)
        self.assertTrue(can_view)
        self.assertTrue(can_transition_to_certify)
        self.assertFalse(can_certify)
        self.assertFalse(completed)
        self.assertFalse(has_checklist)

    @mock.patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_simplified_status_for_user_can_view_only(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """
        Test get_simplified_status_for_user(). home_status state is  'abandoned'
        Expected result
        can_edit = True
        can_view, can_certify,can_transition_to_certify, completed, has_checklist = False
        """
        from axis.checklist.tests.factories import checklist_factory

        is_eligible_for_certification.return_value = False
        can_user_certify.return_value = False
        can_be_edited.return_value = False

        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        checklist = checklist_factory()
        eep_program.required_checklists.add(checklist)
        user = User.objects.get(company=home_status.company)
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state="abandoned")
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.required_checklists.exists())
        check1 = EEPProgramHomeStatus.objects.filter_by_user(user, id=home_status.id).exists()
        self.assertTrue(check1)
        self.assertEqual("abandoned", home_status.state)
        (
            can_edit,
            can_view,
            can_transition_to_certify,
            can_certify,
            completed,
            has_checklist,
        ) = home_status.get_simplified_status_for_user(user)
        self.assertFalse(can_edit)
        self.assertTrue(can_view)
        self.assertFalse(can_transition_to_certify)
        self.assertFalse(can_certify)
        self.assertFalse(completed)
        self.assertFalse(has_checklist)

    def test_get_answers_for_home_no_collections(self):
        """Test get_answers_for_home.  home_status has NO collection_request"""
        from axis.checklist.tests.factories import answer_factory, checklist_factory

        TOTAL_QUESTIONS = 3
        ANSWERED_QUESTIONS = 1
        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": TOTAL_QUESTIONS}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions[:ANSWERED_QUESTIONS]:
            answer_kwrgs = {
                "confirmed": True,
                "question": question,
                "home": stats.home,
                "user": user,
            }
            answer_factory(**answer_kwrgs)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(is_qa_program=False)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        result = home_status.get_answers_for_home()
        self.assertEqual(ANSWERED_QUESTIONS, result.count())

    def test_get_answers_for_home_with_collection_request(self):
        """Test get_answers_for_home. home_status has collection_request"""
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [{"measure_id": "notes", "type_label": "open", "required": False}]

        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat = EEPProgramHomeStatus.objects.first()

            data = {"input": "somehting", "comment": "more comments"}
            CollectedInput.objects.get_or_create(
                collection_request=collection_request,
                instrument=instrument,
                home_status=stat,
                defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                user_role="rater",
            )

            stat.collection_request = collection_request
            stat.save()
            home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
            result = home_status.get_answers_for_home()
            self.assertEqual(1, result.count())
            result_data = result.first().data
            for key in data:
                self.assertIn(key, result_data)
                self.assertEqual(data[key], result_data[key])

    def test_get_qaanswers_for_home(self):
        """Test get_qaanswers_for_home.  home_status has NO collection_request"""
        from axis.checklist.tests.factories import checklist_factory
        from axis.checklist.models import QAAnswer

        TOTAL_QUESTIONS = 3
        ANSWERED_QUESTIONS = 1
        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": TOTAL_QUESTIONS}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions[:ANSWERED_QUESTIONS]:
            answer_kwrgs = {
                "confirmed": True,
                "question": question,
                "home": stats.home,
                "user": user,
            }
            QAAnswer.objects.create(**answer_kwrgs)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(is_qa_program=True)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        result = home_status.get_qaanswers_for_home()
        self.assertEqual(ANSWERED_QUESTIONS, result.count())

    def test_get_qaanswers_for_home_collection_request(self):
        """Test get_qaanswers_for_home.  home_status has collection_request"""
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [{"measure_id": "notes", "type_label": "open", "required": False}]

        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat = EEPProgramHomeStatus.objects.first()

            data = {"input": "somehting", "comment": "more comments"}
            CollectedInput.objects.get_or_create(
                collection_request=collection_request,
                instrument=instrument,
                home_status=stat,
                defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                user_role="qa",
            )
            stat.collection_request = collection_request
            stat.save()
            home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
            result = home_status.get_qaanswers_for_home()
            self.assertEqual(1, result.count())
            result_data = result.first().data
            for key in data:
                self.assertIn(key, result_data)
                self.assertEqual(data[key], result_data[key])

    def test_get_next_state_current_complete(self):
        """
        Test for get_next_state().
        home_status current state is 'complete'.
        Expected result None
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state="complete")
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_next_state()
        self.assertIsNone(result)

    def test_get_next_state_current_abandoned(self):
        """
        Test for get_next_state().  home_status current state is 'abandoned'.
        Expected result None
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state="abandoned")
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_next_state()
        self.assertEqual("abandoned_to_pending_transition", result)

    def test_get_next_state(self):
        """Test for get_next_state(). home_status current state is in ['']"""
        states = [
            "pending_inspection",
            "inspection",
            "qa_pending",
            "in_progress",
            "failed",
            "certification_pending",
            "correction_required",
        ]
        home_status = EEPProgramHomeStatus.objects.first()
        for state in states:
            EEPProgramHomeStatus.objects.filter(id=home_status.id).update(state=state)
            home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
            result = home_status.get_next_state()
            self.assertEqual("to_abandoned_transition", result)

    def test_get_provider_same_company(self):
        """Test for get_provider"""
        from axis.company.models import Company

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(
            Company.objects.filter(
                id=home_status.company.id, company_type=Company.PROVIDER_COMPANY_TYPE
            ).count()
        )
        result = home_status.get_provider()
        self.assertEqual(home_status.company, result)

    def test_get_provider(self):
        """Test for get_provider"""
        from axis.home.tests.factories import eep_program_home_status_factory, home_factory
        from axis.company.models import Company

        general_co = Company.objects.get(name="General1")
        home = home_factory()
        eep_program = EEPProgramHomeStatus.objects.first().eep_program
        home_status = eep_program_home_status_factory(
            company=general_co, eep_program=eep_program, home=home
        )
        self.assertFalse(
            Company.objects.filter(
                id=home_status.company.id, company_type=Company.PROVIDER_COMPANY_TYPE
            ).count()
        )
        result = home_status.get_provider()
        self.assertEqual(home_status.company, result)

    def test_get_providers_no_intersection(self):
        """
        Test get_providers(). for this case there's no intersection between rater_ralations and
        home relationships providers.
        Expected result [home_status.company]
        """
        home_status = EEPProgramHomeStatus.objects.first()
        rater_relations = home_status.company.relationships.get_companies(home_status.company)
        providers = home_status.home.relationships.get_provider_orgs()
        expected = list(set(rater_relations).intersection(set(providers)))
        self.assertEqual(0, len(expected))
        result = home_status.get_providers()
        self.assertIn(home_status.company, result)

    def test_get_electric_company(self):
        """Test for get_electric_company(). Expected result should find the electric company"""
        from axis.company.tests.factories import utility_organization_factory
        from axis.company.models import UtilitySettings
        from axis.relationship.models import Relationship

        ut1 = utility_organization_factory(electricity_provider=True)
        home_status = EEPProgramHomeStatus.objects.first()
        relationship, _ = Relationship.objects.validate_or_create_relations_to_entity(
            home_status.home, ut1
        )
        UtilitySettings.objects.get_or_create(
            relationship=relationship,
            is_gas_utility=ut1.gas_provider,
            is_electric_utility=ut1.electricity_provider,
        )
        result = home_status.get_electric_company()
        self.assertIsNotNone(result)
        self.assertEqual(ut1, result)

    def test_get_electric_company_find_none(self):
        """Test for get_electric_company(). Expected result None"""
        from axis.company.tests.factories import utility_organization_factory
        from axis.company.models import UtilitySettings
        from axis.relationship.models import Relationship

        ut1 = utility_organization_factory(electricity_provider=False)
        home_status = EEPProgramHomeStatus.objects.first()
        relationship, _ = Relationship.objects.validate_or_create_relations_to_entity(
            home_status.home, ut1
        )
        UtilitySettings.objects.get_or_create(
            relationship=relationship,
            is_gas_utility=ut1.gas_provider,
            is_electric_utility=ut1.electricity_provider,
        )
        result = home_status.get_electric_company()
        self.assertIsNone(result)

    def test_get_gas_company(self):
        """Test for get_gas_company(). Expected result should find the electric company"""
        from axis.company.tests.factories import utility_organization_factory
        from axis.company.models import UtilitySettings
        from axis.relationship.models import Relationship

        ut1 = utility_organization_factory(gas_provider=True)
        home_status = EEPProgramHomeStatus.objects.first()
        relationship, _ = Relationship.objects.validate_or_create_relations_to_entity(
            home_status.home, ut1
        )
        UtilitySettings.objects.get_or_create(
            relationship=relationship,
            is_gas_utility=ut1.gas_provider,
            is_electric_utility=ut1.electricity_provider,
        )
        result = home_status.get_gas_company()
        self.assertIsNotNone(result)
        self.assertEqual(ut1, result)

    def test_get_gas_company_find_none(self):
        """Test for get_gas_company(). Expected result should find the gas company"""
        from axis.company.tests.factories import utility_organization_factory
        from axis.company.models import UtilitySettings
        from axis.relationship.models import Relationship

        ut1 = utility_organization_factory(gas_provider=False)
        home_status = EEPProgramHomeStatus.objects.first()
        relationship, _ = Relationship.objects.validate_or_create_relations_to_entity(
            home_status.home, ut1
        )
        UtilitySettings.objects.get_or_create(
            relationship=relationship,
            is_gas_utility=ut1.gas_provider,
            is_electric_utility=ut1.electricity_provider,
        )
        result = home_status.get_gas_company()
        self.assertIsNone(result)

    def test_get_annotations_breakdown(self):
        """Test get_annotations_breakdown"""
        from axis.annotation.tests.factories import type_factory, annotation_factory
        from django.contrib.contenttypes.models import ContentType

        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        # eep_program.required_annotation_type
        annotation_type = type_factory()
        eep_program.required_annotation_types.add(annotation_type)
        # home_status.annotations
        company_content_type = ContentType.objects.get_for_model(EEPProgramHomeStatus)
        # Create annotations
        annotation = annotation_factory(
            content_type=company_content_type,
            type=annotation_type,
            object_id=home_status.company.id,
            content="Annotation One",
        )
        home_status.annotations.add(annotation)
        home_status.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_annotations_breakdown()
        self.assertIsNotNone(result)
        self.assertIn(annotation_type, result)

    def test_calculate_active_floorplan_floorplans_final(self):
        """Test calculate_active_floorplan()"""
        from axis.floorplan.tests.factories import floorplan_factory

        home_status = EEPProgramHomeStatus.objects.first()
        floorplan = floorplan_factory(type="final")
        home_status.floorplans.add(floorplan)
        self.assertIsNotNone(home_status.floorplans)
        result = home_status.calculate_active_floorplan()
        self.assertIsNotNone(result)
        self.assertEqual(floorplan, result)

    def test_calculate_active_floorplan(self):
        """Test calculate_active_floorplan()"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNotNone(home_status.floorplans)
        result = home_status.calculate_active_floorplan()
        self.assertIsNotNone(result)

    def test_get_sampleset_none(self):
        """Test get_sampleset. home_status has no sampleset. Expected result None"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertFalse(home_status.samplesethomestatus_set.count())
        result = home_status.get_sampleset()
        self.assertIsNone(result)

    def test_get_sampleset(self):
        """Test get_sampleset."""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stat = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertTrue(home_status.samplesethomestatus_set.count())
        result = home_status.get_sampleset()
        self.assertIsNotNone(result)

    def test_get_samplesethomestatus_none(self):
        """
        Test get_samplesethomestatus.
        home_status has no samplesethomestatus.
        Expected result None
        """
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertFalse(home_status.samplesethomestatus_set.count())
        result = home_status.get_samplesethomestatus()
        self.assertIsNone(result)
        self.assertEqual(result, home_status.get_sampleset())

    def test_get_samplesethomestatus(self):
        """Test get_samplesethomestatus"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stat = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertTrue(home_status.samplesethomestatus_set.count())
        result = home_status.get_samplesethomestatus()
        self.assertIsNotNone(result)

    def test_get_samplesethomestatus_multiple(self):
        """
        Test get_samplesethomestatus.
        home_status has no samplesethomestatus.
        Expected result None
        """
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stat = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=2, is_active=True, is_test_home=False
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertTrue(home_status.samplesethomestatus_set.count())
        result = home_status.get_samplesethomestatus()
        self.assertIsNotNone(result)
        self.assertEqual(1, result.revision)

    def test_remove_from_sampleset(self):
        """Test remove_from_sampleset()"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stat = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        result = home_status.get_sampleset()
        self.assertIsNotNone(result)
        result = home_status.remove_from_sampleset()
        self.assertIsNone(result)

    def test_remove_from_sampleset_with_nothing_to_remove(self):
        """Test remove_from_sampleset()"""
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_sampleset()
        self.assertIsNone(result)
        result = home_status.remove_from_sampleset()
        self.assertIsNone(result)

    def test_get_source_sampleset_answers_no_answers(self):
        """Test get_source_sampleset_answers()"""
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_source_sampleset_answers()
        self.assertEqual(0, result.count())

    def test_get_source_sampleset_answers(self):
        """Test get_source_sampleset_answers()"""
        from axis.home.tests.factories import eep_program_checklist_home_status_factory
        from axis.checklist.tests.factories import answer_factory

        provider_user = User.objects.get(company__name="Provider1")
        home_status = eep_program_checklist_home_status_factory(company=provider_user.company)
        question_qset = home_status.eep_program.get_checklist_question_set()
        for question in question_qset:
            answer_factory(question=question, home=home_status.home, user=provider_user)
        result = home_status.get_source_sampleset_answers()
        self.assertEqual(question_qset.count(), result.count())

    def test_get_contributed_sampleset_answers_zero(self):
        """Test get_contributed_sampleset_answers()"""
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_contributed_sampleset_answers()
        self.assertEqual(0, result.count())

    def test_get_contributed_sampleset_answers(self):
        """Test get_contributed_sampleset_answers()"""
        from axis.home.tests.factories import eep_program_checklist_home_status_factory
        from axis.checklist.tests.factories import answer_factory
        from axis.sampleset.tests.factories import empty_sampleset_factory

        provider_user = User.objects.get(company__name="Provider1")
        stat = eep_program_checklist_home_status_factory(company=provider_user.company)
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        sample_homestatus = SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)

        question_qset = home_status.eep_program.get_checklist_question_set()
        for question in question_qset:
            ans = answer_factory(question=question, home=home_status.home, user=provider_user)
            sample_homestatus.answers.add(ans)
        result = home_status.get_contributed_sampleset_answers()
        self.assertEqual(4, result.count())

    def test_get_failing_sampleset_answers_none(self):
        """Test get_failing_sampleset_answers"""
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_failing_sampleset_answers()
        self.assertEqual(0, result.count())

    def test_get_failing_sampleset_answers(self):
        """Test get_contributed_sampleset_answers()"""
        from axis.home.tests.factories import eep_program_checklist_home_status_factory
        from axis.checklist.tests.factories import answer_factory
        from axis.sampleset.tests.factories import empty_sampleset_factory

        provider_user = User.objects.get(company__name="Provider1")
        stat = eep_program_checklist_home_status_factory(company=provider_user.company)
        sampleset_kwargs = {"owner": stat.company, "eep_program": stat.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        sample_homestatus = SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stat, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)

        question_qset = home_status.eep_program.get_checklist_question_set()
        for question in question_qset:
            ans = answer_factory(
                question=question,
                home=home_status.home,
                user=provider_user,
                is_considered_failure=True,
            )
            sample_homestatus.answers.add(ans)
        result = home_status.get_failing_sampleset_answers()
        self.assertEqual(4, result.count())

    def test_get_completion_test_kwargs_collection_request(self):
        """
        Test get_completion_test_kwargs. home_status has collection_request.
        eep_program is_qa_program is True
        """
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [{"measure_id": "notes", "type_label": "open", "required": False}]

        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat = EEPProgramHomeStatus.objects.first()

            data = {"input": "somehting", "comment": "more comments"}
            CollectedInput.objects.get_or_create(
                collection_request=collection_request,
                instrument=instrument,
                home_status=stat,
                defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                user_role="qa",
            )
            stat.collection_request = collection_request
            stat.save()
            eep_program = stat.eep_program
            eep_program.is_qa_program = True
            eep_program.save()
            home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
            self.assertTrue(home_status.eep_program.is_qa_program)
            result = home_status.get_completion_test_kwargs()
            self.assertIsNotNone(result["input_values"])
            self.assertIn(question["measure_id"], result["input_values"])
            self.assertEqual(result["input_values"], home_status.get_input_values())

            self.assertEqual(result["builder"], home_status.home.get_builder())
            self.assertEqual(
                set(result["eep_companies"]),
                set(home_status.eep_program.owner.relationships.get_companies()),
            )
            self.assertEqual(
                set(result["accepted_companies"]),
                set(home_status.home.relationships.get_accepted_companies()),
            )
            self.assertEqual(
                set(result["unaccepted_companies"]),
                set(home_status.home.relationships.get_unaccepted_companies()),
            )

    def test_get_completion_test_kwargs_answers(self):
        """Test get_completion_test_kwargs. home_status has NO collection_request."""
        from axis.checklist.tests.factories import answer_factory, checklist_factory

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": 2}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions:
            answer_kwrgs = {"confirmed": True}
            answer_factory(question, stats.home, user, **answer_kwrgs)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertFalse(home_status.collection_request)
        result = home_status.get_completion_test_kwargs()
        self.assertIsNone(result["collector"])
        self.assertEqual(result["inputs"].keys(), result["input_values"].keys())
        for answer in result["inputs"]:
            self.assertIsNotNone(answer)
        self.assertEqual(result["input_values"], home_status.get_input_values())
        self.assertEqual(result["builder"], home_status.home.get_builder())
        self.assertEqual(
            set(result["eep_companies"]),
            set(home_status.eep_program.owner.relationships.get_companies()),
        )
        self.assertEqual(
            set(result["accepted_companies"]),
            set(home_status.home.relationships.get_accepted_companies()),
        )
        self.assertEqual(
            set(result["unaccepted_companies"]),
            set(home_status.home.relationships.get_unaccepted_companies()),
        )

    def test_get_already_certified_status_skip_certification_check(self):
        """Test get_already_certified_status"""
        skip_certification_check = True
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_already_certified_status(skip_certification_check)
        self.assertIsNone(result)

    def test_get_already_certified_status_no_certification_date(self):
        """Test get_already_certified_status"""
        skip_certification_check = False
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.certification_date)
        result = home_status.get_already_certified_status(skip_certification_check)
        self.assertIsNone(result)

    def test_get_already_certified_status(self):
        """Test get_already_certified_status"""

        skip_certification_check = False
        today = datetime.date.today()
        stats = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(certification_date=today)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertIsNotNone(home_status.certification_date)
        result = home_status.get_already_certified_status(skip_certification_check)
        self.assertIsNotNone(result)
        self.assertEqual(result.data, home_status.certification_date)
        self.assertEqual(result.message, strings.ALREADY_CERTIFIED)

    @mock.patch("axis.sampleset.models.SampleSetHomeStatus.find_uncovered_questions")
    def test_get_unanswered_questions_sampleset_uncovered_questions(self, find_uncovered_questions):
        """Test get_unanswered_questions"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        find_uncovered_questions.return_value = 3
        stats = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stats.company, "eep_program": stats.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stats, revision=1, is_active=True, is_test_home=True
        )
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        result = home_status.get_unanswered_questions()
        self.assertEqual(3, result)

    def test_get_unanswered_questions_collection_request_rater(self):
        """Test get_unanswered_questions. home_status has collection_request"""
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [
            {"measure_id": "notes", "type_label": "open", "required": False},
            {
                "measure_id": "smart-thermostat-brand",
                "type_label": "multiple-choice",
                "choices": ["N/A", "Nest"],
                "required": False,
            },
        ]
        stat = EEPProgramHomeStatus.objects.first()
        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat.collection_request = collection_request
            stat.save()

            if order < 2:
                data = {"input": "somehting", "comment": "more comments"}
                CollectedInput.objects.get_or_create(
                    collection_request=collection_request,
                    instrument=instrument,
                    home_status=stat,
                    defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                    user_role="rater",
                )
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        result = home_status.get_unanswered_questions()
        self.assertIsNotNone(result)
        self.assertEqual(1, result.count())

    def test_get_unanswered_questions_collection_request_qa(self):
        """Test get_unanswered_questions. home_status has collection_request"""
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [
            {"measure_id": "notes", "type_label": "open", "required": False},
            {
                "measure_id": "smart-thermostat-brand",
                "type_label": "multiple-choice",
                "choices": ["N/A", "Nest"],
                "required": False,
            },
        ]
        stat = EEPProgramHomeStatus.objects.first()
        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat.collection_request = collection_request
            stat.save()

            if order < 2:
                data = {"input": "somehting", "comment": "more comments"}
                CollectedInput.objects.get_or_create(
                    collection_request=collection_request,
                    instrument=instrument,
                    home_status=stat,
                    defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                    user_role="qa",
                )
        EEPProgram.objects.filter(id=stat.eep_program.id).update(is_qa_program=True)
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        result = home_status.get_unanswered_questions()
        self.assertIsNotNone(result)
        self.assertEqual(1, result.count())

    def test_get_unanswered_questions_no_collection_request_qa_program(self):
        """Test get_unanswered_questions. home_status has no collection_request"""
        from axis.checklist.tests.factories import checklist_factory
        from axis.checklist.models import QAAnswer

        TOTAL_QUESTIONS = 3
        ANSWERED_QUESTIONS = 1
        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": TOTAL_QUESTIONS}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions[:ANSWERED_QUESTIONS]:
            answer_kwrgs = {
                "confirmed": True,
                "question": question,
                "home": stats.home,
                "user": user,
            }
            QAAnswer.objects.create(**answer_kwrgs)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(is_qa_program=True)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        result = home_status.get_unanswered_questions()
        self.assertEqual(TOTAL_QUESTIONS - ANSWERED_QUESTIONS, result.count())

    def test_get_unanswered_questions_no_collection_request(self):
        """Test get_unanswered_questions. home_status has no collection_request"""
        from axis.checklist.tests.factories import answer_factory, checklist_factory

        TOTAL_QUESTIONS = 3
        ANSWERED_QUESTIONS = 1
        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": TOTAL_QUESTIONS}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions[:ANSWERED_QUESTIONS]:
            answer_kwrgs = {
                "confirmed": True,
                "question": question,
                "home": stats.home,
                "user": user,
            }
            answer_factory(**answer_kwrgs)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(is_qa_program=False)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        result = home_status.get_unanswered_questions()
        self.assertEqual(TOTAL_QUESTIONS - ANSWERED_QUESTIONS, result.count())

    def test_get_all_questions_no_collector(self):
        """Test get_all_questions"""
        from axis.checklist.tests.factories import checklist_factory

        TOTAL_QUESTIONS = 3
        stats = EEPProgramHomeStatus.objects.first()
        checklist_kwargs = {"question_count": TOTAL_QUESTIONS}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        result = home_status.get_all_questions()
        self.assertEqual(TOTAL_QUESTIONS, result.count())

    def test_get_questions_edit_permission_for_user_edit(self):
        """Tesst get_questions_edit_permission_for_user. Expected result 'edit'"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=home_status.company)
        result = home_status.get_questions_edit_permission_for_user(user)
        self.assertEqual("edit", result)

    def test_get_questions_edit_permission_for_user_readonly_company_relationship(self):
        """Tesst get_questions_edit_permission_for_user. Expected result 'readonly'"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Rater1")
        result = home_status.get_questions_edit_permission_for_user(user)
        self.assertEqual("readonly", result)

    def test_get_questions_edit_permission_for_user_readonly_company_association(self):
        """Tesst get_questions_edit_permission_for_user. Expected result 'readonly'"""
        from axis.relationship.utils import associate_companies_to_obj
        from axis.home.tests.factories import eep_program_checklist_home_status_factory
        from axis.core.tests.factories import general_admin_factory

        user = general_admin_factory()
        provider_user = User.objects.get(company__name="Provider1")
        home_status = eep_program_checklist_home_status_factory(company=provider_user.company)
        associate_companies_to_obj(home_status, home_status.company, user.company)
        result = home_status.get_questions_edit_permission_for_user(user)
        self.assertEqual("readonly", result)

    def test_get_questions_edit_permission_for_user_readonly_superuser(self):
        """Tesst get_questions_edit_permission_for_user. Expected result 'readonly'"""
        from axis.core.tests.factories import general_super_user_factory

        superuser = general_super_user_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_questions_edit_permission_for_user(superuser)
        self.assertEqual("readonly", result)

    def test_get_questions_edit_permission_for_user_none(self):
        """Tesst get_questions_edit_permission_for_user. Expected result None"""
        from axis.core.tests.factories import general_admin_factory

        user = general_admin_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_questions_edit_permission_for_user(user)
        self.assertIsNone(result)

    def test_get_questions_and_permission_for_user_none(self):
        """Test get_questions_and_permission_for_user"""
        from axis.core.tests.factories import general_admin_factory

        user = general_admin_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        questions, permission = home_status.get_questions_and_permission_for_user(user)
        self.assertIsNone(permission)
        self.assertEqual(0, len(questions))

    def test_get_questions_and_permission_for_user(self):
        """Test get_questions_and_permission_for_user"""
        from axis.checklist.tests.factories import answer_factory, checklist_factory

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": 3}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions:
            answer_kwrgs = {"confirmed": True}
            answer = answer_factory(question, stats.home, user, **answer_kwrgs)
            self.assertTrue(answer.confirmed)

        home_status = EEPProgramHomeStatus.objects.first()
        questions, permission = home_status.get_questions_and_permission_for_user(user)
        self.assertIsNotNone(permission)
        self.assertEqual("edit", permission)
        self.assertEqual(3, len(questions))

    def test_get_questions_and_permission_for_user_questions_but_no_permission(self):
        """Test get_questions_and_permission_for_user"""
        from axis.checklist.tests.factories import answer_factory, checklist_factory
        from axis.core.tests.factories import general_admin_factory

        stats = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name=stats.company.name)
        checklist_kwargs = {"question_count": 3}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        for question in questions:
            answer_kwrgs = {"confirmed": True}
            answer = answer_factory(question, stats.home, user, **answer_kwrgs)
            self.assertTrue(answer.confirmed)

        home_status = EEPProgramHomeStatus.objects.first()
        user = general_admin_factory()
        questions, permission = home_status.get_questions_and_permission_for_user(user)
        self.assertIsNone(permission)
        self.assertEqual(0, len(questions))

    def test_get_required_questions_remaining_status_sampleset(self):
        """Test get_required_questions_remaining_status. Expected result None"""
        home_status = EEPProgramHomeStatus.objects.first()
        kwargs = {"sampleset": True}
        result = home_status.get_required_questions_remaining_status("checklist_url", **kwargs)
        self.assertIsNone(result)

    def test_get_required_questions_remaining_status_failing(self):
        """
        Test get_required_questions_remaining_status.
        Expected result FailingStatus, since there are unanswered questions (required)
        """
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [
            {"measure_id": "notes", "type_label": "open", "required": True},
            {
                "measure_id": "smart-thermostat-brand",
                "type_label": "multiple-choice",
                "choices": ["N/A", "Nest"],
                "required": True,
            },
        ]
        stat = EEPProgramHomeStatus.objects.first()
        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat.collection_request = collection_request
            stat.save()

            if order < 2:
                data = {"input": "somehting", "comment": "more comments"}
                CollectedInput.objects.get_or_create(
                    collection_request=collection_request,
                    instrument=instrument,
                    home_status=stat,
                    defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                    user_role="rater",
                )
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        kwargs = {"sampleset": False, "collector": home_status.get_collector(user_role="rater")}
        result = home_status.get_required_questions_remaining_status("checklist_url", **kwargs)
        self.assertFalse(result.status)
        count = home_status.get_unanswered_questions(**kwargs).count()
        msg = "There are {} required checklist questions remaining.".format(count)
        self.assertEqual(msg, result.message)

    def test_get_required_questions_remaining_status_passing(self):
        """
        Test get_required_questions_remaining_status.
        Expected result PassingStatus, since there are NO unanswered questions (required)
        """
        from django_input_collection.models import CollectionRequest
        from axis.checklist.models import CollectedInput

        from axis.eep_program.program_builder.utils.safe_ops import (
            derive_group,
            derive_measure,
            derive_type,
            derive_response_policy,
            derive_instrument,
        )

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )
        questions = [
            {"measure_id": "notes", "type_label": "open", "required": False},
            {
                "measure_id": "smart-thermostat-brand",
                "type_label": "multiple-choice",
                "choices": ["N/A", "Nest"],
                "required": False,
            },
        ]
        stat = EEPProgramHomeStatus.objects.first()
        for order, question in enumerate(questions, start=1):
            group = derive_group(id=question.pop("group_id", "checklist"))
            measure = derive_measure(id=question.get("measure_id"))
            type_label = derive_type(type=question.pop("type_label"), unit=None)
            response_policy = derive_response_policy(
                restrict=bool(question.get("choices", False)),
                multiple=False,
                required=question.pop("required", True),
            )
            instrument = derive_instrument(
                text=question.pop("text", question.get("measure_id")),
                order=question.pop("order", order),
                description=question.pop("description", ""),
                help=question.pop("help", ""),
                group=group,
                measure=measure,
                type=type_label,
                response_policy=response_policy,
                collection_request=collection_request,
            )
            collection_request.collectioninstrument_set.add(instrument)
            stat.collection_request = collection_request
            stat.save()

            if order < 2:
                data = {"input": "somehting", "comment": "more comments"}
                CollectedInput.objects.get_or_create(
                    collection_request=collection_request,
                    instrument=instrument,
                    home_status=stat,
                    defaults=dict(user=stat.company.users.first(), home=stat.home, data=data),
                    user_role="rater",
                )
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        kwargs = {"sampleset": False, "collector": home_status.get_collector(user_role="rater")}
        result = home_status.get_required_questions_remaining_status("checklist_url", **kwargs)
        self.assertTrue(result.status)

    def test_get_optional_questions_remaining_status_none(self):
        """Test get_optional_questions_remaining_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        kwargs = {"sampleset": True}
        result = home_status.get_optional_questions_remaining_status("checklist_url", **kwargs)
        self.assertIsNone(result)

    def test_get_optional_questions_remaining_status(self):
        """Test get_optional_questions_remaining_status. Expected result good status"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertEqual(0, home_status.get_unanswered_questions().count())
        kwargs = {"sampleset": False}
        result = home_status.get_optional_questions_remaining_status("checklist_url", **kwargs)
        self.assertTrue(result.status)

    def test_get_optional_questions_remaining_status_bad_status(self):
        """
        Test get_optional_questions_remaining_status.
        Expected result bad status, since there are unanswered questions
        """
        from axis.checklist.tests.factories import question_factory, checklist_factory

        stats = EEPProgramHomeStatus.objects.first()
        questions = list()
        questions.append(question_factory(is_optional=True))
        questions.append(question_factory(is_optional=True))
        checklist_kwargs = {"question_count": 3, "questions": questions}
        checklist = checklist_factory(**checklist_kwargs)
        eep_program = stats.eep_program
        eep_program.required_checklists.add(checklist)
        questions = stats.eep_program.get_checklist_question_set()
        self.assertIsNotNone(questions)
        optional_unanswered_count = 2
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertEqual(optional_unanswered_count, home_status.get_unanswered_questions().count())
        kwargs = {"sampleset": False}
        result = home_status.get_optional_questions_remaining_status("checklist_url", **kwargs)
        self.assertIsNone(result.status)
        self.assertEqual(optional_unanswered_count, result.data)
        msg = strings.HAS_UNANSWERED_OPTIONAL_QUESTIONS_PLURAL
        self.assertEqual(result.message, msg.format(n=optional_unanswered_count))

    def test_get_uncovered_questions_status_samplesethomestatus_none(self):
        """Test get_uncovered_questions_status."""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.get_samplesethomestatus())
        samplesethomestatus = home_status.get_samplesethomestatus()
        result = home_status.get_uncovered_questions_status(samplesethomestatus)
        self.assertIsNone(result)

    def test_get_uncovered_questions_status_passing_status(self):
        """Test get_uncovered_questions_status. Expected PassingStatusTuple"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stats = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stats.company, "eep_program": stats.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stats, revision=1, is_active=True, is_test_home=True
        )
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stats, revision=2, is_active=True, is_test_home=False
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(home_status.samplesethomestatus_set.count())
        samplesethomestatus = home_status.get_samplesethomestatus()
        result = home_status.get_uncovered_questions_status(samplesethomestatus)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    @mock.patch("axis.sampleset.models.SampleSetHomeStatus.find_uncovered_questions")
    def test_get_uncovered_questions_status_failing_status_plural(self, find_uncovered_questions):
        """Test get_uncovered_questions_status. Expected FailingStatusTuple"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        find_uncovered_questions.count.return_value = 2

        stats = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stats.company, "eep_program": stats.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stats, revision=1, is_active=True, is_test_home=True
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        samplesethomestatus = home_status.get_samplesethomestatus()
        result = home_status.get_uncovered_questions_status(samplesethomestatus)
        self.assertFalse(result.status)
        self.assertIsNotNone(result.data)

    def test_get_sampled_house_status_none(self):
        """Test get_sampled_house_status. Expected result None"""
        home_status = EEPProgramHomeStatus.objects.first()
        samplesethomestatus = home_status.get_samplesethomestatus()
        sampleset = home_status.get_sampleset()
        result = home_status.get_sampled_house_status(sampleset, samplesethomestatus)
        self.assertIsNone(result)

    def test_get_sampled_house_status_missing_test_home(self):
        """Test get_sampled_house_status. Expected result FailingStatusTuple"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stats = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stats.company, "eep_program": stats.eep_program}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stats, revision=1, is_active=True, is_test_home=True
        )
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set, home_status=stats, revision=2, is_active=True, is_test_home=False
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(home_status.samplesethomestatus_set.count())
        home_status = EEPProgramHomeStatus.objects.first()
        samplesethomestatus = home_status.get_samplesethomestatus()
        sampleset = home_status.get_sampleset()
        self.assertFalse(
            sampleset.samplesethomestatus_set.filter(revision=sampleset.revision).exists()
        )
        result = home_status.get_sampled_house_status(sampleset, samplesethomestatus)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)

    def test_get_sampled_house_status_passing(self):
        """Test get_sampled_house_status. Expected result PassingStatusTuple"""
        from axis.sampleset.tests.factories import empty_sampleset_factory

        stats = EEPProgramHomeStatus.objects.first()
        sampleset_kwargs = {"owner": stats.company, "eep_program": stats.eep_program, "revision": 1}
        sample_set = empty_sampleset_factory(**sampleset_kwargs)
        SampleSetHomeStatus.objects.create(
            sampleset=sample_set,
            home_status=stats,
            revision=sample_set.revision,
            is_active=True,
            is_test_home=True,
        )

        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(home_status.samplesethomestatus_set.count())
        home_status = EEPProgramHomeStatus.objects.first()
        samplesethomestatus = home_status.get_samplesethomestatus()
        sampleset = home_status.get_sampleset()
        result = home_status.get_sampled_house_status(sampleset, samplesethomestatus)
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_model_file_status(self):
        """Test get_model_file_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertFalse(home_status.eep_program.require_model_file)
        result = home_status.get_model_file_status("url")
        self.assertIsNone(result)

    def test_get_model_file_status_no_floorplan(self):
        """Test get_model_file_status"""

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(require_model_file=True)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.require_model_file)
        self.assertFalse(home_status.floorplan)
        result = home_status.get_model_file_status("url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = strings.MISSING_FLOORPLAN_FILE
        self.assertEqual(msg, result.message)

    def test_get_model_file_status_missing_remrate_file(self):
        """Test get_model_file_status"""

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(require_model_file=True)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.require_model_file)
        self.assertTrue(home_status.floorplan)
        result = home_status.get_model_file_status("url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = strings.MISSING_REMRATE_FILE
        self.assertEqual(msg, result.message)

    def test_get_model_file_status_passing(self):
        """Test get_model_file_status. Expected result PassingStatusTuple"""
        from axis.floorplan.tests.factories import add_dummy_blg_data_file

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(require_model_file=True)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.require_model_file)
        self.assertTrue(home_status.floorplan)
        add_dummy_blg_data_file(home_status.floorplan)
        result = home_status.get_model_file_status("url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_model_data_status_no_require_input_data(self):
        """
        Test get_model_data_status. home_status eep_program not flagged require_input_data.
        Expected result None
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(require_input_data=False)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_model_data_status("edit_url")
        self.assertIsNone(result)

    def test_get_model_data_status_missing_remrate_data_no_floorplan(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_rem_data, but
        home_status has no floorplan.
        Expected result FailingStatusTuple
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            require_input_data=True, require_rem_data=True
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.eep_program.require_rem_data)
        self.assertFalse(home_status.floorplan)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = strings.MISSING_REMRATE_DATA
        self.assertEqual(msg, result.message)

    def test_get_model_data_status_missing_remrate_data(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_rem_data.
        home_status has floorplan, but no floorplan.remrate_target
        Expected result FailingStatusTuple
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(
            require_input_data=True, require_rem_data=True
        )
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.floorplan)
        self.assertFalse(home_status.floorplan.remrate_target)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = strings.MISSING_REMRATE_DATA
        self.assertEqual(msg, result.message)

    def test_get_model_data_status_max_hers_too_high(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_rem_data,
        home_status has floorplan, floorplan.remrate_target.
        Expected result FailingStatusTuple
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        stats = EEPProgramHomeStatus.objects.first()
        hers = 99
        max_hers_score = 90
        floorplan = floorplan_with_remrate_factory(
            remrate_target__energystar__energy_star_v3_hers_score=hers
        )
        simulation = get_or_import_rem_simulation(floorplan.remrate_target.id, use_tasks=False)
        floorplan.simulation = simulation
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(floorplan=floorplan)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(
            require_input_data=True, require_rem_data=True, max_hers_score=max_hers_score
        )
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(home_status.floorplan)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = strings.ERI_SCORE_TOO_HIGH.format(eri=hers, max=max_hers_score)
        self.assertEqual(msg, result.message)

    def test_get_model_data_status_max_hers_too_low(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_rem_data,
        home_status has floorplan, floorplan.remrate_target.
        Expected result FailingStatusTuple
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        stats = EEPProgramHomeStatus.objects.first()
        hers = 19
        max_hers_score = 90
        min_hers_score = 20
        floorplan = floorplan_with_remrate_factory(
            remrate_target__energystar__energy_star_v3_hers_score=hers
        )
        simulation = get_or_import_rem_simulation(floorplan.remrate_target.id, use_tasks=False)
        floorplan.simulation = simulation
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(floorplan=floorplan)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(
            require_input_data=True,
            require_rem_data=True,
            max_hers_score=max_hers_score,
            min_hers_score=min_hers_score,
        )
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(home_status.floorplan)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = strings.ERI_SCORE_TOO_LOW.format(eri=hers, min=min_hers_score)
        self.assertEqual(msg, result.message)

    def test_get_model_data_status_remrate_passing(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_rem_data,
        home_status has floorplan, floorplan.remrate_target.
        Expected result PassingStatusTuple
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        stats = EEPProgramHomeStatus.objects.first()
        hers = 90
        max_hers_score = 90
        min_hers_score = 20
        floorplan = floorplan_with_remrate_factory(
            remrate_target__energystar__energy_star_v3_hers_score=hers
        )
        get_or_import_rem_simulation(floorplan.remrate_target.id, use_tasks=False)

        EEPProgramHomeStatus.objects.filter(id=stats.id).update(floorplan=floorplan)
        EEPProgram.objects.filter(id=stats.eep_program.id).update(
            require_input_data=True,
            require_rem_data=True,
            max_hers_score=max_hers_score,
            min_hers_score=min_hers_score,
        )
        home_status = EEPProgramHomeStatus.objects.get(id=stats.id)
        self.assertTrue(home_status.floorplan)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_model_data_status("edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_model_data_status_missing_ekotrope_data_no_floorplan(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_ekotrope_data, but
        home_status has no floorplan.
        Expected result FailingStatusTuple
        """
        eep_program_kwargs = {
            "require_input_data": True,
            "require_rem_data": False,
            "require_ekotrope_data": True,
        }
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(**eep_program_kwargs)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertFalse(home_status.eep_program.require_rem_data)
        self.assertTrue(home_status.eep_program.require_ekotrope_data)
        self.assertFalse(home_status.floorplan)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = strings.MISSING_EKOTROPE_DATA
        self.assertEqual(msg, result.message)

    def test_get_model_data_status_missing_ekotrope_data(self):
        """
        Test get_model_data_status. home_status eep_program flagged require_ekotrope_data.
        home_status has floorplan, but no floorplan.ekotrope_houseplan
        Expected result FailingStatusTuple
        """
        eep_program_kwargs = {
            "require_input_data": True,
            "require_rem_data": False,
            "require_ekotrope_data": True,
        }
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(**eep_program_kwargs)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertFalse(home_status.eep_program.require_rem_data)
        self.assertTrue(home_status.eep_program.require_ekotrope_data)
        self.assertTrue(home_status.floorplan)
        self.assertFalse(home_status.floorplan.ekotrope_houseplan)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = strings.MISSING_EKOTROPE_DATA
        self.assertEqual(msg, result.message)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_get_model_data_status_ekotrope_import_under_way(self, import_project_tree):
        """
        Test get_model_data_status. home_status eep_program flagged require_ekotrope_data.
        home_status has floorplan, and floorplan.ekotrope_houseplan but floorplan.ekotrope_houseplan
        does not have the attribute 'analysis
        Expected result FailingStatusTuple
        cause: analysis isn't there yet, presumably the import task is still running
        """
        # mock post_save import_project_tree to skip connecting to API
        from axis.ekotrope.tests.factories import (
            house_plan_factory,
            project_factory,
            ekotrope_auth_details_factory,
        )

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.floorplan)
        # prep ekotrope
        user = self.get_admin_user(company_type="rater")
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)

        eep_program_kwargs = {
            "require_input_data": True,
            "require_rem_data": False,
            "require_ekotrope_data": True,
        }

        floorplan = home_status.floorplan
        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        EEPProgram.objects.filter(id=home_status.eep_program.id).update(**eep_program_kwargs)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        hers = home_status.floorplan.get_hers_score_for_program(home_status.eep_program)
        self.assertIsNone(hers)
        self.assertFalse(home_status.eep_program.require_rem_data)
        self.assertTrue(home_status.eep_program.require_ekotrope_data)
        self.assertTrue(home_status.floorplan.ekotrope_houseplan)
        result = home_status.get_model_data_status("edit_url")
        self.assertFalse(result.status)
        msg = "Missing associated analysis data"
        self.assertIn(msg, result.message)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_get_model_data_status_ekotrope_passing(self, import_project_tree):
        """
        Test get_model_data_status. home_status eep_program flagged require_ekotrope_data.
        home_status has floorplan, and floorplan.ekotrope_houseplan but floorplan.ekotrope_houseplan
        does not have the attribute 'analysis
        Expected result PassingStatusTuple
        """
        # mock post_save import_project_tree to skip connecting to API
        from axis.ekotrope.tests.factories import (
            house_plan_factory,
            project_factory,
            ekotrope_auth_details_factory,
            analysis_factory,
        )

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertTrue(home_status.floorplan)
        # prep ekotrope
        user = self.get_admin_user(company_type="rater")
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)
        analysis_factory(houseplan=house_plan, project=project)
        sim = get_or_import_ekotrope_simulation(houseplan_id=house_plan.id, use_tasks=False)

        eep_program_kwargs = {
            "require_input_data": True,
            "require_rem_data": False,
            "require_ekotrope_data": True,
        }

        floorplan = home_status.floorplan
        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = house_plan
        floorplan.simulation = sim
        floorplan.save()

        EEPProgram.objects.filter(id=home_status.eep_program.id).update(**eep_program_kwargs)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        hers = home_status.floorplan.get_hers_score_for_program(home_status.eep_program)
        self.assertIsNotNone(hers)
        self.assertFalse(home_status.eep_program.require_rem_data)
        self.assertTrue(home_status.eep_program.require_ekotrope_data)
        self.assertTrue(hasattr(house_plan, "analysis"))
        self.assertTrue(home_status.floorplan.ekotrope_houseplan)
        result = home_status.get_model_data_status("edit_url")
        self.assertTrue(result.status)

    def test_get_model_data_status_input_data_type_blg_data_mode(self):
        """
        Test get_model_data_status. home_status.floorplan has input_data_type = 'blg_data'
        Expected result None
        """
        from axis.floorplan.tests.factories import (
            add_dummy_blg_data_file,
            floorplan_with_remrate_factory,
        )

        eep_program_kwargs = {
            "require_input_data": True,
            "require_rem_data": False,
            "require_ekotrope_data": False,
        }
        home_status = EEPProgramHomeStatus.objects.first()

        floorplan = floorplan_with_remrate_factory()
        get_or_import_rem_simulation(floorplan.remrate_target.id, use_tasks=False)
        floorplan.process_simulation_result()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        add_dummy_blg_data_file(home_status.floorplan)

        EEPProgram.objects.filter(id=home_status.eep_program.id).update(**eep_program_kwargs)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_model_data_status("edit_url")
        self.assertTrue(result.status)

    def test_get_remrate_flavor_support_unknown_flavor(self):
        """
        Test get_remrate_flavor_support. eep_program slug is neea-efficient-homes, but there's no
        remrate.flavor
        Expected result FailingStatusTuple
        """
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(slug="neea-efficient-homes")
        self.assertIsNone(home_status.floorplan.remrate_target)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_remrate_flavor_support("url")
        self.assertFalse(result.status)
        msg = strings.INVALID_REMRATE_FLAVOR.format(flavor="Unknown", required_flavor="Northwest")
        self.assertEqual(msg, result.message)

    def test_get_remrate_flavor_support(self):
        """
        Test get_remrate_flavor_support. eep_program slug is neea-efficient-homes, and
        remrate.flavor is in ['northwest', 'washington']
        Expected result PassingStatusTuple
        """
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(slug="neea-efficient-homes")
        floorplan = floorplan_with_remrate_factory(remrate_target__flavor="northwest")
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_remrate_flavor_support("url")
        self.assertTrue(result.status)

        # now let's test 'washington'
        remrate_target = floorplan.remrate_target
        remrate_target.flavor = "washington"
        remrate_target.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertEqual("washington", home_status.floorplan.remrate_target.flavor)
        result = home_status.get_remrate_flavor_support("url")
        self.assertTrue(result.status)

    def test_get_required_annotations_status_none(self):
        """
        Test get_required_annotations_status. home_status eep_program has no annotations.
        Expected result None
        """
        home_status = EEPProgramHomeStatus.objects.first()
        program = home_status.eep_program
        cnt = program.required_annotation_types.filter(is_required=True).count()
        self.assertEqual(0, cnt)
        result = home_status.get_required_annotations_status("url")
        self.assertIsNone(result)

    def test_get_required_annotations_status_failing(self):
        """
        Test get_required_annotations_status. home_status program has annotations but some are
        missing from home_status annotations.
        Expected result FailingStatus
        """
        from axis.annotation.tests.factories import type_factory, annotation_factory

        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        # eep_program.required_annotation_type
        annotation_type = type_factory(
            is_required=True,
            applicable_content_types=[ContentType.objects.get_for_model(EEPProgramHomeStatus)],
        )
        annotation_type2 = type_factory(
            is_required=True,
            applicable_content_types=[ContentType.objects.get_for_model(EEPProgramHomeStatus)],
        )
        eep_program.required_annotation_types.add(annotation_type)
        eep_program.required_annotation_types.add(annotation_type2)
        # home_status.annotations
        company_content_type = ContentType.objects.get_for_model(EEPProgramHomeStatus)
        # Create annotations
        annotation = annotation_factory(
            content_type=company_content_type,
            type=annotation_type,
            object_id=home_status.company.id,
            content="Annotation One",
        )
        home_status.annotations.add(annotation)
        home_status.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_required_annotations_status("url")
        self.assertFalse(result.status)
        msg = strings.MISSING_REQUIRED_ANNOTATIONS.format(n=1)
        self.assertEqual(msg, result.message)

    def test_get_required_annotations_status_passing(self):
        """
        Test get_required_annotations_status. home_status annotations has NO missing annotations.
        Expected result PassingStatus
        """
        from axis.annotation.tests.factories import type_factory, annotation_factory
        from django.contrib.contenttypes.models import ContentType

        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        # eep_program.required_annotation_type
        annotation_type = type_factory(
            is_required=True,
            applicable_content_types=[ContentType.objects.get_for_model(EEPProgramHomeStatus)],
        )
        eep_program.required_annotation_types.add(annotation_type)
        # home_status.annotations
        company_content_type = ContentType.objects.get_for_model(EEPProgramHomeStatus)
        # Create annotations
        annotation = annotation_factory(
            content_type=company_content_type,
            type=annotation_type,
            object_id=home_status.company.id,
            content="Annotation One",
        )
        home_status.annotations.add(annotation)
        home_status.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_required_annotations_status("url")
        self.assertTrue(result.status)

    def test__get_company_required_status_missing_builder(self):
        """
        Test  _get_company_required_status and get_builder_required_status.
        home_status' program requires a builder assigned. there are no accepted companies or
        unaccepted
        Expected result FailingStatus

        """
        from axis.company.models import Company
        from axis.company.tests.factories import builder_organization_factory

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_builder_relationship = True
        stat.eep_program.require_builder_assigned_to_home = True
        stat.eep_program.save()
        builder_organization_factory(name="Builder1")
        accepted_cos = Company.objects.none()
        eep_companies = unaccepted_companies = Company.objects.filter(name="Provider1")
        home_status = EEPProgramHomeStatus.objects.first()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("builder", **kwargs)
        builder_required_status_result = home_status.get_builder_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result.status, builder_required_status_result.status)
        msg = strings.MISSING_BUILDER.format(program=stat.eep_program)
        self.assertEqual(result.message, msg)

    def test__get_company_required_status_builder_required_relationship_missing(self):
        """
        Test  _get_company_required_status.
        home_status' program requires an association to the builder.
        Expected result FailingStatus
        """
        from axis.company.models import Company
        from axis.company.tests.factories import builder_organization_factory

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_builder_assigned_to_home = False
        stat.eep_program.require_builder_relationship = True
        stat.eep_program.save()
        builder_organization_factory(name="Builder1")
        accepted_cos = Company.objects.filter(name="Builder1")
        eep_companies = Company.objects.filter(name="Provider1")
        unaccepted_companies = Company.objects.none()
        home_status = EEPProgramHomeStatus.objects.first()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("builder", **kwargs)
        builder_required_status_result = home_status.get_builder_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result.status, builder_required_status_result.status)
        msg = strings.MISSING_BUILDER_RELATIONSHIP.format(
            program=stat.eep_program, owner=stat.eep_program.owner
        )
        self.assertEqual(result.message, msg)

    def test__get_company_required_status_builder_passing(self):
        """
        Test  _get_company_required_status and get_builder_required_status
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_builder_assigned_to_home = False
        stat.eep_program.require_builder_relationship = True
        stat.eep_program.save()
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        home_status = EEPProgramHomeStatus.objects.first()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("builder", **kwargs)
        builder_required_status_result = home_status.get_builder_required_status(**kwargs)
        self.assertTrue(result.status)
        self.assertEqual(result.status, builder_required_status_result.status)

    def test__get_company_required_status_builder_none(self):
        """
        Test  _get_company_required_status and get_builder_required_status
        NO require_assigned_to_home set and NO accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_builder_assigned_to_home = False
        stat.eep_program.require_builder_relationship = False
        stat.eep_program.save()
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        home_status = EEPProgramHomeStatus.objects.first()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("builder", **kwargs)
        builder_required_status_result = home_status.get_builder_required_status(**kwargs)
        self.assertIsNone(result)
        self.assertEqual(result, builder_required_status_result)

    def test__get_company_required_status_missing_provider(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_provider_assigned_to_home = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = unaccepted_companies = eep_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("provider", **kwargs)
        provider_required_status_result = home_status.get_provider_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, provider_required_status_result)
        msg = strings.MISSING_PROVIDER.format(program=stat.eep_program)
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_provider_required_relationship_missing(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_provider_relationship = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="Provider1")
        eep_companies = Company.objects.filter(name="EEP2")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("provider", **kwargs)
        provider_required_status_result = home_status.get_provider_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, provider_required_status_result)
        msg = strings.MISSING_PROVIDER_RELATIONSHIP.format(
            program=stat.eep_program, owner=stat.eep_program.owner
        )
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_provider_passing(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_provider_relationship = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="Provider1")
        eep_companies = Company.objects.filter(name="Provider1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("provider", **kwargs)
        provider_required_status_result = home_status.get_provider_required_status(**kwargs)
        self.assertTrue(result.status)
        self.assertEqual(result, provider_required_status_result)

    def test__get_company_required_status_provider_none(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_provider_relationship = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="Provider1")
        eep_companies = Company.objects.filter(name="Provider1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("provider", **kwargs)
        provider_required_status_result = home_status.get_provider_required_status(**kwargs)
        self.assertIsNone(result)
        self.assertIsNone(provider_required_status_result)

    def test__get_company_required_status_missing_rater(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_rater_assigned_to_home = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = unaccepted_companies = eep_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("rater", **kwargs)
        rater_required_status_result = home_status.get_rater_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, rater_required_status_result)
        msg = strings.MISSING_RATER.format(program=stat.eep_program)
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_rater_required_relationship_missing(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_rater_relationship = True
        stat.eep_program.require_rater_assigned_to_home = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="Rater1")
        eep_companies = Company.objects.filter(name="EEP2")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("rater", **kwargs)
        rater_required_status_result = home_status.get_rater_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, rater_required_status_result)
        msg = strings.MISSING_RATER_RELATIONSHIP.format(
            program=stat.eep_program, owner=stat.eep_program.owner
        )
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_rater_passing(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_rater_relationship = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="Provider1")
        eep_companies = Company.objects.filter(name="Provider1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("rater", **kwargs)
        rater_required_status_result = home_status.get_rater_required_status(**kwargs)
        self.assertTrue(result.status)
        self.assertEqual(result, rater_required_status_result)

    def test__get_company_required_status_rater_none(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_rater_relationship = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("rater", **kwargs)
        rater_required_status_result = home_status.get_rater_required_status(**kwargs)
        self.assertIsNone(result)
        self.assertIsNone(rater_required_status_result)

    def test__get_company_required_status_missing_utility(self):
        """
        Test  _get_company_required_status() and get_utility_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_utility_assigned_to_home = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = unaccepted_companies = eep_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("utility", **kwargs)
        rater_required_status_result = home_status.get_utility_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, rater_required_status_result)
        msg = strings.MISSING_UTILITY.format(program=stat.eep_program)
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_utility_required_relationship_missing(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company
        from axis.company.tests.factories import utility_organization_factory

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_utility_relationship = True
        stat.eep_program.require_utility_assigned_to_home = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        utility_organization_factory(name="Utility1")
        accepted_cos = Company.objects.filter(name="Utility1")
        eep_companies = Company.objects.filter(name="EEP2")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("utility", **kwargs)
        rater_required_status_result = home_status.get_utility_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, rater_required_status_result)
        msg = strings.MISSING_UTILITY_RELATIONSHIP.format(
            program=stat.eep_program, owner=stat.eep_program.owner
        )
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_utility_passing(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_utility_relationship = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("utility", **kwargs)
        rater_required_status_result = home_status.get_utility_required_status(**kwargs)
        self.assertTrue(result.status)
        self.assertEqual(result, rater_required_status_result)

    def test__get_company_required_status_utility_none(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_utility_relationship = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("utility", **kwargs)
        rater_required_status_result = home_status.get_utility_required_status(**kwargs)
        self.assertIsNone(result)
        self.assertIsNone(rater_required_status_result)

    def test__get_company_required_status_missing_hvac(self):
        """
        Test  _get_company_required_status() and get_hvac_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_hvac_assigned_to_home = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = unaccepted_companies = eep_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("hvac", **kwargs)
        rater_required_status_result = home_status.get_hvac_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, rater_required_status_result)
        msg = strings.MISSING_HVAC.format(program=stat.eep_program)
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_hvac_required_relationship_missing(self):
        """
        Test  _get_company_required_status.
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company
        from axis.company.tests.factories import hvac_organization_factory

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_hvac_relationship = True
        stat.eep_program.require_hvac_assigned_to_home = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        hvac_organization_factory(name="Hvac1")
        accepted_cos = Company.objects.filter(name="Hvac1")
        eep_companies = Company.objects.filter(name="EEP2")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("hvac", **kwargs)
        rater_required_status_result = home_status.get_hvac_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, rater_required_status_result)
        msg = strings.MISSING_HVAC_RELATIONSHIP.format(
            program=stat.eep_program, owner=stat.eep_program.owner
        )
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_hvac_passing(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_hvac_relationship = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("hvac", **kwargs)
        required_status_result = home_status.get_hvac_required_status(**kwargs)
        self.assertTrue(result.status)
        self.assertEqual(result, required_status_result)

    def test__get_company_required_status_hvac_none(self):
        """
        Test  _get_company_required_status() and get_rater_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_hvac_relationship = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("hvac", **kwargs)
        required_status_result = home_status.get_hvac_required_status(**kwargs)
        self.assertIsNone(result)
        self.assertIsNone(required_status_result)

    def test__get_company_required_status_missing_qa(self):
        """
        Test  _get_company_required_status() and get_qa_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_qa_assigned_to_home = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = unaccepted_companies = eep_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("qa", **kwargs)
        required_status_result = home_status.get_qa_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, required_status_result)
        msg = strings.MISSING_QA.format(program=stat.eep_program)
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_qa_required_relationship_missing(self):
        """
        Test  _get_company_required_status() and get_qa_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_qa_relationship = True
        stat.eep_program.require_qa_assigned_to_home = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="QA1")
        eep_companies = Company.objects.filter(name="EEP2")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("qa", **kwargs)
        required_status_result = home_status.get_qa_required_status(**kwargs)
        self.assertFalse(result.status)
        self.assertEqual(result, required_status_result)
        msg = strings.MISSING_QA_RELATIONSHIP.format(
            program=stat.eep_program, owner=stat.eep_program.owner
        )
        self.assertEqual(msg, result.message)

    def test__get_company_required_status_qa_passing(self):
        """
        Test  _get_company_required_status() and get_qa_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_qa_relationship = True
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("qa", **kwargs)
        required_status_result = home_status.get_qa_required_status(**kwargs)
        self.assertTrue(result.status)
        self.assertEqual(result, required_status_result)

    def test__get_company_required_status_qa_none(self):
        """
        Test  _get_company_required_status() and get_qa_required_status()
        flag require_assigned_to_home set, but there are no accepted_companies (empty).
        """
        from axis.company.models import Company

        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program.require_qa_relationship = False
        stat.eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=stat.id)
        accepted_cos = Company.objects.filter(name="EEP1")
        eep_companies = Company.objects.filter(name="EEP1")
        unaccepted_companies = Company.objects.none()
        kwargs = {
            "eep_companies": eep_companies,
            "accepted_companies": accepted_cos,
            "unaccepted_companies": unaccepted_companies,
            "companies_edit_url": "",
        }
        result = home_status._get_company_required_status("qa", **kwargs)
        required_status_result = home_status.get_qa_required_status(**kwargs)
        self.assertIsNone(result)
        self.assertIsNone(required_status_result)

    def test_get_program_owner_attached_status_passing(self):
        """Test get_program_owner_attached_status. Expected result PassingStatusTuple"""
        from axis.company.models import Company

        home_status = EEPProgramHomeStatus.objects.first()
        program = home_status.eep_program
        incentives = program.rater_incentive_dollar_value + program.builder_incentive_dollar_value
        self.assertEqual(0, incentives)
        accepted_cos = Company.objects.all()
        result = home_status.get_program_owner_attached_status(accepted_cos)
        self.assertTrue(result.status)
        self.assertEqual(incentives, result.data)

    def test_get_program_owner_attached_status_failing(self):
        """Test get_program_owner_attached_status"""
        from axis.company.models import Company

        home_status = EEPProgramHomeStatus.objects.first()
        program = home_status.eep_program
        program.builder_incentive_dollar_value = 10
        program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        accepted_cos = Company.objects.all().exclude(id=program.owner.id)
        result = home_status.get_program_owner_attached_status(accepted_cos)
        self.assertFalse(result.status)
        msg = strings.PROGRAM_OWNER_NOT_ATTACHED.format(owner=program.owner)
        self.assertEqual(msg, result.message)

    def test_get_multiple_utility_check_status(self):
        """Test get_multiple_utility_check_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_multiple_utility_check_status("home_edit_url")
        self.assertTrue(result.status)

    @mock.patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus.get_electric_company"
    )
    def test_get_multiple_utility_check_status_failing_multiple_electric(
        self, get_electric_company
    ):
        """
        Test get_multiple_utility_check_status. get_electric_company raises a
        Relationship.MultipleObjectsReturned
        Expected result FailingStatusTuple
        """
        from axis.relationship.models import Relationship

        get_electric_company.side_effect = Relationship.MultipleObjectsReturned

        home_status = EEPProgramHomeStatus.objects.first()
        result = home_status.get_multiple_utility_check_status("home_edit_url")

        self.assertFalse(result.status)
        err = strings.MULTIPLE_SPECIFIC_UTILITY.format(utility_type="Electric Provider")
        self.assertEqual(err, result.message)

    @mock.patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.get_gas_company")
    def test_get_multiple_utility_check_status_failing_multiple_gas(self, get_gas_company):
        """
        Test get_multiple_utility_check_status. get_gas_company raises a
        Relationship.MultipleObjectsReturned
        Expected result FailingStatusTuple
        """
        from axis.relationship.models import Relationship

        # get_electric_company.return_value = None
        get_gas_company.side_effect = Relationship.MultipleObjectsReturned

        home_status = EEPProgramHomeStatus.objects.first()
        self.assertIsNone(home_status.get_electric_company(raise_errors=True))
        result = home_status.get_multiple_utility_check_status("home_edit_url")

        self.assertFalse(result.status)
        err = strings.MULTIPLE_SPECIFIC_UTILITY.format(utility_type="Gas Provider")
        self.assertEqual(err, result.message)

    def test_get_floorplan_remrate_data_error_status_no_floorplan(self):
        """Test get_floorplan_remrate_data_error_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_floorplan_remrate_data_error_status()
        self.assertIsNone(result)

    def test_get_floorplan_remrate_data_error_status_no_remrate_target(self):
        """Test get_floorplan_remrate_data_error_status"""
        home_status = EEPProgramHomeStatus.objects.filter(floorplan__isnull=False).first()
        self.assertFalse(home_status.floorplan.remrate_target)
        result = home_status.get_floorplan_remrate_data_error_status()
        self.assertIsNone(result)

    @mock.patch("axis.remrate_data.models.simulation.Simulation.compare_to_home_status")
    def test_get_floorplan_remrate_data_error_status_failing(self, compare_to_home_status):
        """Test get_floorplan_remrate_data_error_status"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        compare_to_home_status.return_value = {"error": ["error 1", "error 2"]}

        home_status = EEPProgramHomeStatus.objects.first()
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_floorplan_remrate_data_error_status()
        self.assertFalse(result.status)

    @mock.patch("axis.remrate_data.models.simulation.Simulation.compare_to_home_status")
    def test_get_floorplan_remrate_data_error_status_passing(self, compare_to_home_status):
        """Test get_floorplan_remrate_data_error_status"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        compare_to_home_status.return_value = {"error": []}

        home_status = EEPProgramHomeStatus.objects.first()
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_floorplan_remrate_data_error_status()
        self.assertTrue(result.status)

    def test_get_floorplan_remrate_data_warning_status_no_floorplan(self):
        """Test get_floorplan_remrate_data_warning_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_floorplan_remrate_data_warning_status()
        self.assertIsNone(result)

    def test_get_floorplan_remrate_data_warning_status_no_remrate_target(self):
        """Test get_floorplan_remrate_data_warning_status"""
        home_status = EEPProgramHomeStatus.objects.filter(floorplan__isnull=False).first()
        self.assertFalse(home_status.floorplan.remrate_target)
        result = home_status.get_floorplan_remrate_data_warning_status()
        self.assertIsNone(result)

    @mock.patch("axis.remrate_data.models.simulation.Simulation.compare_to_home_status")
    def test_get_floorplan_remrate_data_warning_status_failing(self, compare_to_home_status):
        """Test get_floorplan_remrate_data_warning_status"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        compare_to_home_status.return_value = {"warning": ["warning 1", "warning 2"]}

        home_status = EEPProgramHomeStatus.objects.first()
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_floorplan_remrate_data_warning_status()
        self.assertIsNone(result.status)

    @mock.patch("axis.remrate_data.models.simulation.Simulation.compare_to_home_status")
    def test_get_floorplan_remrate_data_warning_status(self, compare_to_home_status):
        """Test get_floorplan_remrate_data_warning_status"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        compare_to_home_status.return_value = {"warning": []}

        home_status = EEPProgramHomeStatus.objects.first()
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        self.assertTrue(home_status.floorplan.remrate_target)
        result = home_status.get_floorplan_remrate_data_warning_status()
        self.assertIsNone(result)

    def test_get_rater_of_record_status_no_require_rater_of_record(self):
        """Test get_rater_of_record_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        eep_program.require_rater_of_record = False
        eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_rater_of_record_status("user", "edit_url")
        self.assertIsNone(result)

    def test_get_rater_of_record_status_failing(self):
        """Test get_rater_of_record_status. Expected result FailingStatusTuple"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        eep_program = home_status.eep_program
        eep_program.require_rater_of_record = True
        eep_program.save()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(rater_of_record=None)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_rater_of_record_status(user, "edit_url")
        self.assertFalse(result.status)
        message = strings.MISSING_RATER_OF_RECORD
        self.assertEqual(message, result.message)

    def test_get_rater_of_record_status_passing(self):
        """Test get_rater_of_record_status. Expected result None"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        eep_program = home_status.eep_program
        eep_program.require_rater_of_record = True
        eep_program.save()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(rater_of_record=user)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_rater_of_record_status(user, "edit_url")
        self.assertIsNone(result)

    def test_get_energy_modeler_status_no_require_energy_modeler(self):
        """Test get_energy_modeler_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        eep_program.require_energy_modeler = False
        eep_program.save()
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_energy_modeler_status("user", "edit_url")
        self.assertIsNone(result)

    def test_get_energy_modeler_status_failing(self):
        """Test get_energy_modeler_status. Expected result FailingStatusTuple"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        eep_program = home_status.eep_program
        eep_program.require_energy_modeler = True
        eep_program.save()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(rater_of_record=None)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_energy_modeler_status(user, "edit_url")
        self.assertFalse(result.status)
        self.assertEqual(strings.MISSING_ENERGY_MODELER, result.message)

    def test_get_energy_modeler_status_passing(self):
        """Test get_energy_modeler_status. Expected result None"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        eep_program = home_status.eep_program
        eep_program.require_energy_modeler = True
        eep_program.save()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(energy_modeler=user)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_energy_modeler_status(user, "edit_url")
        self.assertIsNone(result)

    def test_get_field_inspectors_status_no_require_energy_modeler(self):
        """Test get_field_inspectors_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        eep_program = home_status.eep_program
        eep_program.require_field_inspector = False
        eep_program.save()
        result = home_status.get_field_inspectors_status("user", "edit_url")
        self.assertIsNone(result)

    def test_get_field_inspectors_status_failing(self):
        """Test get_field_inspectors_status. Expected result FailingStatusTuple"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        eep_program = home_status.eep_program
        eep_program.require_field_inspector = True
        eep_program.save()
        home_status.field_inspectors.clear()
        result = home_status.get_field_inspectors_status(user, "edit_url")
        self.assertFalse(result.status)
        self.assertEqual(strings.MISSING_FIELD_INSPECTOR, result.message)

    def test_get_field_inspectors_status_passing(self):
        """Test get_field_inspectors_status. Expected result None"""
        home_status = EEPProgramHomeStatus.objects.first()
        user = User.objects.get(company__name="Provider1")
        eep_program = home_status.eep_program
        eep_program.require_field_inspector = True
        eep_program.save()
        home_status.field_inspectors.add(user)
        result = home_status.get_field_inspectors_status(user, "edit_url")
        self.assertIsNone(result)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_no_aps_program(self):
        """Test get_floorplan_subdivision_matches_home_subdivision_status"""
        home_status = EEPProgramHomeStatus.objects.first()
        self.assertNotEqual("aps", home_status.eep_program.owner.slug)
        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertIsNone(result)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_no_floorplan(self):
        """Test get_floorplan_subdivision_matches_home_subdivision_status"""
        from axis.company.models import Company

        home_status = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=home_status.eep_program.owner.id).update(slug="aps")
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)
        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertIsNone(result)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_not_matching(self):
        """
        Test get_floorplan_subdivision_matches_home_subdivision_status.
        floorplan_subdivision does NOT match home_subdivision
        Expected result FailingStatusTuple
        """
        from axis.company.models import Company
        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory

        home_status = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=home_status.eep_program.owner.id).update(slug="aps")
        floorplan = basic_custom_home_floorplan_factory(subdivision=None)
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)

        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertFalse(result.status)
        message = "Correct Floorplan Subdivision Association"
        self.assertEqual(message, result.message)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_no_home_subdivision(self):
        """
        Test get_floorplan_subdivision_matches_home_subdivision_status.
        floorplan_subdivision does NOT match home_subdivision, because home has no subdivision
        Expected result FailingStatusTuple
        """
        from axis.company.models import Company
        from axis.home.models import Home
        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory

        home_status = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=home_status.eep_program.owner.id).update(slug="aps")
        # the factory does not create a subdivision by default, the subdivision=None might look like
        # it's assigning None to a subdivision, but instead is telling the factory to create a one
        floorplan = basic_custom_home_floorplan_factory(subdivision=None)
        Home.objects.filter(id=home_status.home.id).update(subdivision=None)
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)

        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertFalse(result.status)
        message = "Home must have Subdivision Association"
        self.assertEqual(message, result.message)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_no_floorplan_sub(self):
        """
        Test get_floorplan_subdivision_matches_home_subdivision_status.
        floorplan_subdivision does NOT match home_subdivision
        Expected result FailingStatusTuple
        """
        from axis.company.models import Company

        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory

        home_status = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=home_status.eep_program.owner.id).update(slug="aps")
        floorplan = basic_custom_home_floorplan_factory()
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)

        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertFalse(result.status)
        message = "Floorplan must have Subdivision Association"
        self.assertEqual(message, result.message)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_no_subdivisions(self):
        """
        Test get_floorplan_subdivision_matches_home_subdivision_status.
        floorplan has no subdivision, same thing for home
        Expected result None
        """
        from axis.company.models import Company
        from axis.home.models import Home
        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory

        home_status = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=home_status.eep_program.owner.id).update(slug="aps")
        # the factory does not create a subdivision by default
        floorplan = basic_custom_home_floorplan_factory()
        Home.objects.filter(id=home_status.home.id).update(subdivision=None)
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)

        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertIsNone(result)

    def test_get_floorplan_subdivision_matches_home_subdivision_status_passing(self):
        """
        Test get_floorplan_subdivision_matches_home_subdivision_status.
        floorplan_subdivision equals home_subdivision
        Expected result None
        """
        from axis.company.models import Company
        from axis.home.models import Home
        from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory

        home_status = EEPProgramHomeStatus.objects.first()
        Company.objects.filter(id=home_status.eep_program.owner.id).update(slug="aps")
        floorplan = basic_custom_home_floorplan_factory(subdivision=None)
        Home.objects.filter(id=home_status.home.id).update(
            subdivision=floorplan.subdivision_set.first()
        )
        EEPProgramHomeStatus.objects.filter(id=home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=home_status.id)

        result = home_status.get_floorplan_subdivision_matches_home_subdivision_status("url")
        self.assertIsNone(result)

    def test_annotate_customer_hirl_client_ca_status(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        builder_organization = builder_organization_factory(name="PUG Builder")

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        developer_organization = developer_organization_factory()
        communityowner_organization = communityowner_organization_factory()
        architect_organization = architect_organization_factory()

        mf_registration = hirl_project_registration_factory(
            registration_user=company_admin_rater_user,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
            community_owner_organization=communityowner_organization,
            architect_organization=architect_organization,
            project_client=HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
        )
        hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            story_count=0,
            number_of_units=0,
        )

        with self.subTest("No Client Agreement registered for client"):
            mf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_BUILDER
            mf_registration.save()
            client_ca_statuses = (
                EEPProgramHomeStatus.objects.filter(customer_hirl_project__isnull=False)
                .annotate_customer_hirl_client_ca_status()
                .values_list("client_ca_status", flat=True)
            )
            self.assertEqual(
                [
                    None,
                ],
                list(client_ca_statuses),
            )

        with self.subTest("Client Agreement exists for client"):
            mf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_BUILDER
            mf_registration.save()

            client_agreement = builder_agreement_factory(
                company=mf_registration.builder_organization, owner=hirl_company
            )

            client_ca_statuses = (
                EEPProgramHomeStatus.objects.filter(customer_hirl_project__isnull=False)
                .annotate_customer_hirl_client_ca_status()
                .values_list("client_ca_status", flat=True)
            )
            self.assertEqual(
                [
                    client_agreement.state,
                ],
                list(client_ca_statuses),
            )

        with self.subTest("Multiple Client Agreements for client"):
            mf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER
            mf_registration.save()

            client_agreement = builder_agreement_factory(
                company=mf_registration.developer_organization, owner=hirl_company
            )

            client_agreement2 = builder_agreement_factory(
                company=mf_registration.developer_organization, owner=hirl_company
            )

            client_ca_statuses = (
                EEPProgramHomeStatus.objects.filter(customer_hirl_project__isnull=False)
                .annotate_customer_hirl_client_ca_status()
                .values_list("client_ca_status", flat=True)
            )
            self.assertEqual(
                [
                    client_agreement2.state,
                ],
                list(client_ca_statuses),
            )

    def test_annotate_customer_hirl_client_coi_expiration_status(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        builder_organization = builder_organization_factory(name="PUG Builder")

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        developer_organization = developer_organization_factory()
        communityowner_organization = communityowner_organization_factory()
        architect_organization = architect_organization_factory()

        mf_registration = hirl_project_registration_factory(
            registration_user=company_admin_rater_user,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
            community_owner_organization=communityowner_organization,
            architect_organization=architect_organization,
            project_client=HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
        )
        hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            story_count=0,
            number_of_units=0,
        )

        with self.subTest("No COI registered for client"):
            mf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_BUILDER
            mf_registration.save()
            client_coi_statuses = (
                EEPProgramHomeStatus.objects.filter(customer_hirl_project__isnull=False)
                .annotate_customer_hirl_client_coi_expiration_status()
                .values_list("client_coi_status", flat=True)
            )
            self.assertEqual(
                [
                    "expired",
                ],
                list(client_coi_statuses),
            )

        with self.subTest("Multiple COI registered for client"):
            mf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT
            mf_registration.save()

            client_agreement = builder_agreement_factory(
                company=mf_registration.architect_organization, owner=hirl_company
            )

            expired_coi = coi_document_factory(
                company=architect_organization,
                expiration_date=timezone.now() - timezone.timedelta(days=365),
            )

            active_coi = coi_document_factory(
                company=architect_organization,
                expiration_date=timezone.now() + timezone.timedelta(days=365),
            )

            client_coi_statuses = (
                EEPProgramHomeStatus.objects.filter(customer_hirl_project__isnull=False)
                .annotate_customer_hirl_client_coi_expiration_status()
                .values_list("client_coi_status", flat=True)
            )
            self.assertEqual(
                [
                    "active",
                ],
                list(client_coi_statuses),
            )
