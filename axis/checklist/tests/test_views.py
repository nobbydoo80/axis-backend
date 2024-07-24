import datetime
import logging
import os
import pprint
from unittest import skip
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from axis.company.models import Company
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import provider_admin_factory
from axis.core.tests.testcases import AxisTestCaseUserMixin, AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.mixins import EEPProgramsTestMixin
from axis.filehandling.tests.test_views import AsynchronousProcessedDocumentBaseTestHandler
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.factories import floorplan_factory
from axis.home.models import Home, EEPProgramHomeStatus
from axis.relationship.models import Relationship
from axis.sampleset.models import SampleSet
from axis.subdivision.models import Subdivision
from axis.subdivision.tests.factories import subdivision_factory
from ..models import CheckList, Section, Question, QuestionChoice, Answer

__author__ = "Autumn Valenta"
__date__ = "1/19/13 12:14 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)
User = get_user_model()


class ChecklistTestsMixin(EEPProgramsTestMixin, TestCase, AxisTestCaseUserMixin):
    """Test out company application"""

    client_class = AxisClient
    model_urls = {}

    @classmethod
    def setUpClass(cls):
        super(ChecklistTestsMixin, cls).setUpClass()
        # Forces reverse_lazy's __proxy__ objects to resolve.
        # __proxy__ objects don't work very well with assertRedirects(), etc.
        for name, value in cls.model_urls.items():
            cls.model_urls[name] = str(value)

    def setUp(self):
        self.perms_user = self.get_admin_user(company_type=["rater", "provider"])
        self.no_perms_user = self.noperms_user

    def test_login_required(self):
        """Test ``login_required`` decoration of list, create, detail, and delete views."""

        for url in self.model_urls.values():
            response = self.client.get(url)
            self.assertRedirects(response, "{}?next={}".format(reverse("auth:login"), url))


class BulkChecklistTestsMixin(CompaniesAndUsersTestMixin, AxisTestCase):
    """No Checklists should be here"""

    include_company_types = ["rater", "provider", "general"]

    def setUp(self):
        self.perms_user = self.get_admin_user(company_type=["rater", "provider"])
        self.no_perms_user = self.noperms_user


class BulkChecklistTests(BulkChecklistTestsMixin, AsynchronousProcessedDocumentBaseTestHandler):
    def test_success_checklist_upload(self):
        """Test the checklist upload capability"""

        self.assertEqual(CheckList.objects.all().count(), 0)
        self.assertEqual(Section.objects.all().count(), 0)
        self.assertEqual(Question.objects.all().count(), 0)
        self.assertEqual(QuestionChoice.objects.all().count(), 0)

        file_obj = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "sources", "Checklist_Basic_5.xlsx"
        )
        self.assertEqual(os.path.exists(file_obj), True)
        document = self._handle_uploading(
            user_id=self.perms_user.id, file_obj=file_obj, url="checklist:checklist_upload"
        )

        if document.result.get("errors") or document.result.get("traceback"):
            pprint.pprint(document.result)
        self.assertEqual(document.final_status, "SUCCESS")

        # Now did everything get in there..
        self.assertEqual(CheckList.objects.count(), 1)
        checklist = CheckList.objects.all()[0]
        self.assertEqual(checklist.name, "Test Basic 5")
        self.assertEqual(checklist.public, True)
        self.assertEqual(checklist.description, "Company X Energy Star Checklist")
        self.assertEqual(checklist.questions.count(), 5)
        # Sections
        self.assertEqual(Section.objects.count(), 1)
        section = Section.objects.all()[0]
        self.assertEqual(section.name, "Section A")
        self.assertEqual(section.priority, 1)
        self.assertEqual(section.description, "First Section")
        # Questions
        self.assertEqual(Question.objects.count(), 5)
        question = Question.objects.get(priority=1)
        self.assertEqual(question.question, "Describe the front door")
        self.assertEqual(question.type, "open")
        self.assertEqual(question.description, "Description")
        self.assertEqual(question.help_url, "http://www.youtube.com")
        self.assertEqual(question.section_set.all()[0].name, "Section A")
        # Choices
        self.assertEqual(QuestionChoice.objects.count(), 3)
        choice = QuestionChoice.objects.get(choice_order=1)
        self.assertEqual(choice.choice, "Pass")
        self.assertEqual(choice.is_considered_failure, False)
        self.assertEqual(choice.display_as_failure, False)
        self.assertEqual(choice.email_required, False)
        self.assertEqual(choice.comment_required, False)
        self.assertEqual(choice.photo_required, False)
        self.assertEqual(choice.document_required, False)
        choice = QuestionChoice.objects.get(choice_order=2)
        self.assertEqual(choice.choice, "Fail")
        self.assertEqual(choice.is_considered_failure, True)
        self.assertEqual(choice.display_as_failure, False)
        self.assertEqual(choice.email_required, True)
        self.assertEqual(choice.comment_required, True)
        self.assertEqual(choice.photo_required, True)
        self.assertEqual(choice.document_required, True)
        choice = QuestionChoice.objects.get(choice_order=3)
        self.assertEqual(choice.choice, "N/A")
        self.assertEqual(choice.is_considered_failure, False)
        self.assertEqual(choice.display_as_failure, True)
        self.assertEqual(choice.email_required, False)
        self.assertEqual(choice.comment_required, True)
        self.assertEqual(choice.photo_required, False)
        self.assertEqual(choice.document_required, False)

    def test_failure_checklist_upload(self):
        """Test the checklist upload capability"""

        self.assertEqual(CheckList.objects.all().count(), 0)
        self.assertEqual(Section.objects.all().count(), 0)
        self.assertEqual(Question.objects.all().count(), 0)
        self.assertEqual(QuestionChoice.objects.all().count(), 0)

        file_obj = __file__
        document = self._handle_uploading(
            user_id=self.perms_user.id, file_obj=file_obj, url="checklist:checklist_upload"
        )

        self.assertIsInstance(document.result, dict)
        self.assertEqual(document.final_status, "FAILURE")
        issues = len(document.result["errors"]) or document.result["traceback"]
        self.assertGreater(issues, 0)

        self.assertEqual(CheckList.objects.all().count(), 0)
        self.assertEqual(Section.objects.all().count(), 0)
        self.assertEqual(Question.objects.all().count(), 0)
        self.assertEqual(QuestionChoice.objects.all().count(), 0)


class BulkHomeChecklistTests(ChecklistTestsMixin, AsynchronousProcessedDocumentBaseTestHandler):
    def _setup(self):
        builder_org = (
            Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE)
            .exclude(name__istartswith="unrel")
            .get()
        )
        subdivision = subdivision_factory(
            name="BulkSub", builder_org=builder_org, city=builder_org.city
        )
        provider = self.user_model.objects.get(username="provideradmin")
        # This user is referenced in the Excel file
        # and is required for consideration to be submitted to the registry.
        provider_admin_factory(username="ror_user", rater_id="1234567", company=provider.company)
        floorplan_factory(subdivision=subdivision, name="Z1", owner=provider.company)
        floorplan_factory(subdivision=subdivision, name="Z2", owner=provider.company)
        floorplan_factory(subdivision=subdivision, name="Z3", owner=provider.company)
        self.assertEqual(Subdivision.objects.all().count(), 1)
        self.assertEqual(Floorplan.objects.all().count(), 3)

        Relationship.objects.validate_or_create_relations_to_entity(subdivision, provider.company)

        eep_program = EEPProgram.objects.get(name__icontains="Single Checklist")
        eep_program.program_close_date = datetime.datetime.today() + datetime.timedelta(days=1)
        eep_program.program_end_date = datetime.datetime.today() + datetime.timedelta(days=2)
        eep_program.save()

        Relationship.objects.validate_or_create_relations_to_entity(subdivision, eep_program.owner)

        Relationship.objects.validate_or_create_relations_to_entity(
            eep_program.owner, provider.company
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            provider.company, eep_program.owner
        )

        Relationship.objects.validate_or_create_relations_to_entity(eep_program.owner, builder_org)
        Relationship.objects.validate_or_create_relations_to_entity(builder_org, eep_program.owner)

        Relationship.objects.validate_or_create_relations_to_entity(
            subdivision.builder_org, eep_program.owner
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            eep_program.owner, subdivision.builder_org
        )

    def test_success_bulk_home_upload(self):
        """Test the checklist upload capability"""

        self._setup()

        self.assertEqual(Home.objects.all().count(), 0)
        self.assertEqual(SampleSet.objects.all().count(), 0)
        self.assertEqual(Answer.objects.all().count(), 0)

        provider = self.user_model.objects.get(username="provideradmin")
        file_obj = os.path.join(os.path.dirname(__file__), "sample-checklist.xlsx")
        document = self._handle_uploading(
            user_id=provider.id, file_obj=file_obj, url="checklist:bulk_checklist_upload"
        )

        if document.result.get("errors") or document.result.get("traceback"):
            pprint.pprint(document.result)

        self.assertEqual(document.final_status, "SUCCESS")
        self.assertEqual(Home.objects.all().count(), 3)
        self.assertEqual(EEPProgramHomeStatus.objects.all().count(), 3)
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(certification_date__isnull=False).count(), 3
        )
        self.assertEqual(EEPProgramHomeStatus.objects.filter(state="complete").count(), 3)
        self.assertEqual(SampleSet.objects.all().count(), 2)
        self.assertEqual(Answer.objects.all().count(), 15)

    def test_data_validations(self):
        """This will ensure that the raw data gets saved correctly and the lot numbers come out
        correctly"""
        self._setup()
        provider = self.user_model.objects.get(username="provideradmin")
        file_obj = os.path.join(os.path.dirname(__file__), "sample-checklist.xlsx")
        document = self._handle_uploading(
            user_id=provider.id, file_obj=file_obj, url="checklist:bulk_checklist_upload"
        )
        if document.result.get("errors") or document.result.get("traceback"):
            pprint.pprint(document.result)

        self.assertEqual(document.final_status, "SUCCESS")
        self.assertEqual(Home.objects.all().count(), 3)
        self.assertEqual(EEPProgramHomeStatus.objects.all().count(), 3)

        with self.subTest("Home 1"):
            home = Home.objects.get(lot_number="3330")
            self.assertEqual(home.geocode_response.geocode.raw_street_line1, "3330 E. Maplewood St")
            self.assertEqual(home.geocode_response.geocode.raw_street_line2, "")
            self.assertEqual(home.geocode_response.geocode.raw_city.name, "Gilbert")
            self.assertEqual(
                home.geocode_response.geocode.raw_county,
                home.geocode_response.geocode.raw_city.county,
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_state.abbr,
                "AZ",
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_zipcode,
                "85295",
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_country.abbr,
                "US",
            )
            self.assertEqual(home.street_line1, "3330 E Maplewood St")
            self.assertEqual(home.street_line2, None)
            self.assertEqual(home.city.name, "Gilbert")
            self.assertEqual(home.county, home.city.county)
            self.assertEqual(home.state, home.city.county.state)
            self.assertEqual(home.zipcode, "85297")

        with self.subTest("Home 2"):
            home = Home.objects.get(lot_number="3331")
            self.assertEqual(home.geocode_response.geocode.raw_street_line1, "3331 E. Maplewood St")
            self.assertEqual(home.geocode_response.geocode.raw_street_line2, "")
            self.assertEqual(home.geocode_response.geocode.raw_city.name, "Gilbert")
            self.assertEqual(
                home.geocode_response.geocode.raw_county,
                home.geocode_response.geocode.raw_city.county,
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_state.abbr,
                "AZ",
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_zipcode,
                "85296",
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_country.abbr,
                "US",
            )
            self.assertEqual(home.street_line1, "3331 E Maplewood St")
            self.assertEqual(home.street_line2, None)
            self.assertEqual(home.city.name, "Gilbert")
            self.assertEqual(home.county, home.city.county)
            self.assertEqual(home.state, home.city.county.state)
            self.assertEqual(home.zipcode, "85297")

        with self.subTest("Home 3"):
            home = Home.objects.get(lot_number="3332")
            self.assertEqual(home.geocode_response.geocode.raw_street_line1, "3332 E. Maplewood St")
            self.assertEqual(home.geocode_response.geocode.raw_street_line2, "")
            self.assertEqual(home.geocode_response.geocode.raw_city.name, "Gilbert")
            self.assertEqual(
                home.geocode_response.geocode.raw_county,
                home.geocode_response.geocode.raw_city.county,
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_state.abbr,
                "AZ",
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_zipcode,
                "85297",
            )
            self.assertEqual(
                home.geocode_response.geocode.raw_country.abbr,
                "US",
            )
            self.assertEqual(home.street_line1, "3332 E Maplewood St")
            self.assertEqual(home.street_line2, None)
            self.assertEqual(home.city.name, "Gilbert")
            self.assertEqual(home.county, home.city.county)
            self.assertEqual(home.state, home.city.county.state)
            self.assertEqual(home.zipcode, "85297")

    def test_success_bulk_home_with_rating_type_upload(self):
        """Test the checklist upload capability"""

        self._setup()

        self.assertEqual(Home.objects.all().count(), 0)
        self.assertEqual(SampleSet.objects.all().count(), 0)
        self.assertEqual(Answer.objects.all().count(), 0)

        provider = self.user_model.objects.get(username="provideradmin")
        file_obj = os.path.join(os.path.dirname(__file__), "sample-checklist-2.xlsx")
        document = self._handle_uploading(
            user_id=provider.id, file_obj=file_obj, url="checklist:bulk_checklist_upload"
        )

        if document.result.get("errors") or document.result.get("traceback"):
            pprint.pprint(document.result)

        self.assertEqual(document.final_status, "SUCCESS")
        self.assertEqual(Home.objects.all().count(), 3)
        self.assertEqual(EEPProgramHomeStatus.objects.all().count(), 3)

        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(certification_date__isnull=False).count(), 3
        )
        self.assertEqual(EEPProgramHomeStatus.objects.filter(state="complete").count(), 3)
        self.assertEqual(SampleSet.objects.all().count(), 2)
        self.assertEqual(Answer.objects.all().count(), 15)

    def test_missing_answers_bulk_home_upload(self):
        """Test the checklist upload capability"""

        self._setup()
        provider = self.user_model.objects.get(username="provideradmin")
        file_obj = os.path.join(os.path.dirname(__file__), "sample-checklist-1.xlsx")
        # self.assertEqual(os.path.exists(file_obj), True)
        document = self._handle_uploading(
            user_id=provider.id, file_obj=file_obj, url="checklist:bulk_checklist_upload"
        )

        for stat in EEPProgramHomeStatus.objects.all():
            self.assertEqual(int(stat.pct_complete), 80)

        self.assertEqual(document.final_status, "SUCCESS")
        self.assertEqual(Home.objects.all().count(), 3)
        self.assertEqual(EEPProgramHomeStatus.objects.all().count(), 3)
        self.assertEqual(
            EEPProgramHomeStatus.objects.filter(certification_date__isnull=True).count(), 3
        )
        self.assertEqual(EEPProgramHomeStatus.objects.filter(state="inspection").count(), 3)
        self.assertEqual(SampleSet.objects.all().count(), 2)
        self.assertEqual(Answer.objects.all().count(), 12)

        bulk_uploaded = Answer.objects.filter(bulk_uploaded=True)
        self.assertEqual(bulk_uploaded.count(), 12)

        question = Question.objects.get(question__icontains="Verify the front door is on")
        self.assertEqual(question.type, "multiple-choice")
        self.assertEqual(Question.objects.filter(type="multiple-choice").count(), 1)
        self.assertEqual(Answer.objects.filter(type="multiple-choice").count(), 3)

        na_answers = Answer.objects.filter(answer="N/A")
        self.assertEqual(na_answers.count(), 1)
        display_as_failures = Answer.objects.filter(display_as_failure=True)
        self.assertEqual(display_as_failures.count(), 1)

    @skip("Currently only Super Users can submit to resnet registry.")
    @patch(
        "axis.home.models.EEPProgramHomeStatus.get_model_data_status",
        return_value=None,
        autospec=True,
    )
    @patch("axis.home.utils.submit_home_status_to_registry.delay")
    def test_upload_to_registry(self, registry_mock, get_model_data_status):
        """
        Test that an a home is uploaded to the RESNET registry.
         A rater_of_record must be provided, and upload_to_registry must be true.
        """
        self._setup()

        provider = self.user_model.objects.get(username="provideradmin")

        eep_program = EEPProgram.objects.get(name__icontains="Single Checklist")
        eep_program.require_input_data = True
        eep_program.save()

        file_obj = os.path.dirname(__file__) + "/sample-checklist.xlsx"
        document = self._handle_uploading(provider.id, file_obj, "checklist:bulk_checklist_upload")

        registry_mock.assert_called()
