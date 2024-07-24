"""test_tasks.py: """

__author__ = "Artem Hruzd"
__date__ = "08/20/2019 20:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os
import re
from django.urls import reverse_lazy
from django.utils.text import slugify

from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.tests.test_views import AsynchronousProcessedDocumentBaseTestHandler

from axis.home.models import Home, EEPProgramHomeStatus
from axis.relationship.models import Relationship
from axis.checklist.models import CollectedInput


class BulkChecklistTaskTests(AxisTestCase, AsynchronousProcessedDocumentBaseTestHandler):
    @classmethod
    def setUpTestData(cls):
        from axis.core.tests.factories import rater_user_factory, builder_user_factory
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.geographic.tests.factories import city_factory
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.floorplan.tests.factories import floorplan_factory
        from axis.company.tests.factories import (
            builder_organization_factory,
            rater_organization_factory,
            provider_organization_factory,
            eep_organization_factory,
        )

        from axis.relationship.models import Relationship
        from axis.scheduling.models import ConstructionStage

        # ConstructionStage is using for certify objects
        # https://github.com/pivotal-energy-solutions/axis/blob/88d866ae5421c49e7fb86c57eeed5c85b059bf7c/axis/home/utils.py#L716
        ConstructionStage.objects.create(name="Completed", is_public=True, order=100)

        provider_company = provider_organization_factory()

        eep_company = eep_organization_factory(name="APS")
        builder_org = builder_organization_factory(name="Beazer Homes")
        rater_company = rater_organization_factory()
        builder_user = builder_user_factory(is_company_admin=True, company=builder_org)
        rater_user = rater_user_factory(is_company_admin=True, company=rater_company)

        tempe_city = city_factory(name="Tempe", county__name="Maricopa", county__state="AZ")
        phoenix_city = city_factory(name="Phoenix", county__name="Maricopa", county__state="AZ")

        eep_program = basic_eep_program_factory(
            name="APS 2019 Program", owner=rater_company, no_close_dates=True
        )
        subdivision = subdivision_factory(
            name="Warner Ranch Estates", builder_org=builder_org, city=tempe_city
        )
        floorplan = floorplan_factory(subdivision=subdivision, owner=rater_company)

        Relationship.objects.create_mutual_relationships(
            eep_company, builder_org, rater_company, provider_company
        )
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, rater_company)
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, eep_company)
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, provider_company)

    def test_bulk_checklist_process_with_address_typo(self):
        """
        In this test case we have a document with two homes where one home has
        a typo in address 239 E. Rhes Rd. and City Phoenix.
        Geocoder returns a correct result 239 E. Rhea Rd.
        We should make sure that raw_* address is stored correctly inside
        geocode object to display correct result in UI based on `Show addresses as-entered` option
        """
        from axis.home.models import Home

        rater_user = self.get_admin_user(company_type="rater")
        file_path = os.path.join(
            "axis", "checklist", "sources", "aps-2019-program_sub_test_190611_L91gd4iH.xlsx"
        )
        self._handle_uploading(user_id=rater_user.pk, file_obj=file_path, url="home:upload")

        self.assertEqual(Home.objects.count(), 2)

        home1, home2 = Home.objects.all()

        self.assertTrue(home1.bulk_uploaded)
        # remove punctuation to avoid test
        # fail because of different responses from google or bing
        geocode_response_without_punctuation = re.sub(
            r"[^\w\s]", "", "{}".format(home1.geocode_response)
        )

        self.assertIn("260 E Rhea Rd Tempe AZ 85284", geocode_response_without_punctuation)
        self.assertIn(
            "260 E Rhea Rd., Tempe, AZ, 85284", "{}".format(home1.geocode_response.geocode)
        )

        self.assertTrue(home2.bulk_uploaded)

        geocode_response_without_punctuation = re.sub(
            r"[^\w\s]", "", "{}".format(home2.geocode_response)
        )
        self.assertIn("239 E Rhea Rd Tempe AZ 85284", geocode_response_without_punctuation)
        self.assertIn(
            "239 E. Rhes Rd., Phoenix, AZ, 85284", "{}".format(home2.geocode_response.geocode)
        )

    def test_bulk_checklist_process_with_update(self):
        """
        If we try to re upload home with the same address we will receive warning and homes
        will not be updated
        """
        from axis.home.models import Home

        self.test_bulk_checklist_process_with_address_typo()

        rater_user = self.get_admin_user(company_type="rater")
        file_path = os.path.join(
            "axis", "checklist", "sources", "aps-2019-program_sub_test_one_home.xlsx"
        )
        self._handle_uploading(user_id=rater_user.pk, file_obj=file_path, url="home:upload")
        self.assertEqual(Home.objects.count(), 2)

        home1, home2 = Home.objects.all()

        geocode_response_without_punctuation = re.sub(
            r"[^\w\s]", "", "{}".format(home2.geocode_response)
        )
        self.assertIn("239 E Rhea Rd Tempe AZ 85284", geocode_response_without_punctuation)
        self.assertIn(
            "239 E. Rhes Rd., Phoenix, AZ, 85284", "{}".format(home2.geocode_response.geocode)
        )


class BulkCollectionRequestTaskTests(
    AxisTestCase,
    AsynchronousProcessedDocumentBaseTestHandler,
):
    """Verifies that our collection request data can be successfully uploaded.."""

    @classmethod
    def setUpTestData(cls):
        from axis.core.tests.factories import (
            eep_admin_factory,
            rater_admin_factory,
            builder_admin_factory,
        )
        from axis.geographic.tests.factories import real_city_factory
        from axis.checklist.tests.sample_programs import SuperSimpleProgramDefinition

        cls.city = real_city_factory("Wichita", "KS")
        eep_admin = eep_admin_factory(
            company__name="EEP Co", company__slug="eep", company__city=cls.city
        )
        cls.user = rater_admin = rater_admin_factory(
            first_name="Johnny",
            last_name="BeGood",
            company__name="Rater Co",
            company__slug="rater",
            company__city=cls.city,
        )
        builder_admin = builder_admin_factory(
            company__name="Builder Co", company__slug="builder", company__city=cls.city
        )
        Relationship.objects.create_mutual_relationships(
            eep_admin.company, rater_admin.company, builder_admin.company
        )
        cls.eep_program = SuperSimpleProgramDefinition().build()

        # Save single home
        # single_home = SingleHomeChecklist(user=cls.user, company=cls.user.company)
        # single_home.write(
        #     program_id=cls.eep_program.id,
        #     output=f"Single-Collection_Request_{cls.eep_program.slug}.xlsx",
        # )
        cls.single_upload_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "sources",
            "Single-Collection_Request_program.xlsx",
        )

        # Save bulk home
        # template = ExcelChecklist(
        #     eep_program_id=cls.eep_program.id,
        #     company_id=cls.user.company.id,
        #     user_id=cls.user.id,
        # )
        # with open(f"Bulk-Collection_Request_{cls.eep_program.slug}.xlsx", "wb") as fileobj:
        #     template.create_bulk_checklist(
        #         cls.user.company,
        #         eep_program=cls.eep_program,
        #         filename=fileobj,
        #     )
        cls.bulk_upload_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "sources",
            "Bulk-Collection_Request_program.xlsx",
        )

    def test_program_no_data_downloads(self):
        """Verify that we can do the various downloads"""

        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

        with self.subTest(f"{self.eep_program} Single Program"):
            url = reverse_lazy(
                "home:download_single_program", kwargs={"eep_program": self.eep_program.pk}
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["content-type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertEqual(
                response["content-disposition"],
                f"attachment; filename=Axis-Program-{self.eep_program.slug}.xlsx",
            )

        with self.subTest(f"{self.eep_program} Bulk Download"):
            url = reverse_lazy(
                "checklist:bulk_checklist_download", kwargs={"pk": self.eep_program.pk}
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["content-type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertEqual(
                response["content-disposition"],
                f"attachment; filename={slugify(self.eep_program)}.xlsx",
            )

    def _test_single_collection_request(self, home_status):
        answers = CollectedInput.objects.filter(
            home_status=home_status,
            home=home_status.home,
            collection_request=home_status.collection_request,
            user=self.user,
            user_role="rater",
        )
        answer_1 = answers.get(instrument__measure_id="question-1")
        self.assertEqual(answer_1.data["input"], "Because of the ocean..")
        self.assertNotIn("comment", answer_1.data)

        answer_2 = answers.get(instrument__measure_id="question-2")
        self.assertEqual(answer_2.data["input"], 2.3456)
        self.assertNotIn("comment", answer_2.data)

        answer_3 = answers.get(instrument__measure_id="question-3")
        self.assertEqual(answer_3.data["input"], "yes")
        self.assertIn("comment", answer_3.data)

    def test_single_home_upload_basics(self):
        """This verifies that a single uplaod with a CR works."""
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        document = self._handle_uploading(
            user_id=self.user.id, file_obj=self.single_upload_path, url="home:single_upload"
        )
        self.assertIn("Successfully uploaded", document.result["latest"])
        self.assertEqual(document.result["critical"], [])
        self.assertEqual(document.result["errors"], [])
        self.assertEqual(document.result["warnings"], [])

        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)

        home_status = EEPProgramHomeStatus.objects.get()

        self.assertEqual(CollectedInput.objects.count(), 3)

        answers = CollectedInput.objects.filter(
            home_status=home_status,
            home=home_status.home,
            collection_request=home_status.collection_request,
            user=self.user,
            user_role="rater",
        )
        self.assertEqual(answers.count(), 3)
        self._test_single_collection_request(home_status)

    def test_single_home_upload_multiples(self):
        """This verifies that multiple repeat uploads only captures one answer"""
        document = self._handle_uploading(
            user_id=self.user.id, file_obj=self.single_upload_path, url="home:single_upload"
        )
        self.assertIn("Successfully uploaded", document.result["latest"])
        self.assertEqual(CollectedInput.objects.count(), 3)

        home_status = EEPProgramHomeStatus.objects.get()
        self._test_single_collection_request(home_status)

        # Force change the answers
        CollectedInput.objects.filter(instrument__measure_id="question-1").update(
            data={"input": "foo"}
        )
        CollectedInput.objects.filter(instrument__measure_id="question-2").update(
            data={"input": 1.0}
        )
        CollectedInput.objects.filter(instrument__measure_id="question-3").update(
            data={"input": "no"}
        )

        # The answers haven't changed so we should only be updating them..
        document = self._handle_uploading(
            user_id=self.user.id, file_obj=self.single_upload_path, url="home:single_upload"
        )
        self.assertIn("Successfully uploaded", document.result["latest"])
        self.assertEqual(CollectedInput.objects.count(), 3)

        self._test_single_collection_request(home_status)

    def _test_bulk_upload_answers(self):
        with self.subTest("Verify first home data set"):
            home_status = EEPProgramHomeStatus.objects.first()

            answers = CollectedInput.objects.filter(
                home_status=home_status,
                home=home_status.home,
                collection_request=home_status.collection_request,
                user=self.user,
                user_role="rater",
            )
            self.assertEqual(answers.count(), 3)

            answer_1 = answers.get(instrument__measure_id="question-1")
            self.assertEqual(answer_1.data["input"], "Not Sure")
            self.assertIn("comment", answer_1.data)

            answer_2 = answers.get(instrument__measure_id="question-2")
            self.assertEqual(answer_2.data["input"], 4.567)
            self.assertNotIn("comment", answer_2.data)

            answer_3 = answers.get(instrument__measure_id="question-3")
            self.assertEqual(answer_3.data["input"], "no")
            self.assertIn("comment", answer_3.data)

        with self.subTest("Verify second home data set"):
            home_status = EEPProgramHomeStatus.objects.last()

            answers = CollectedInput.objects.filter(
                home_status=home_status,
                home=home_status.home,
                collection_request=home_status.collection_request,
                user=self.user,
                user_role="rater",
            )
            self.assertEqual(answers.count(), 3)

            answer_1 = answers.get(instrument__measure_id="question-1")
            self.assertEqual(answer_1.data["input"], "Because it is")
            self.assertNotIn("comment", answer_1.data)

            answer_2 = answers.get(instrument__measure_id="question-2")
            self.assertEqual(answer_2.data["input"], 5.214)
            self.assertIn("comment", answer_2.data)

            answer_3 = answers.get(instrument__measure_id="question-3")
            self.assertEqual(answer_3.data["input"], "yes")
            self.assertNotIn("comment", answer_3.data)

    def test_bulk_upload_basics(self):
        """If for some reason multiple answers exist they will get pruned out"""
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)

        document = self._handle_uploading(
            user_id=self.user.id,
            file_obj=self.bulk_upload_path,
            url="checklist:bulk_checklist_upload",
        )
        self.assertIn("Completed processing 2", document.result["latest"])
        self.assertEqual(document.result["critical"], [])
        self.assertEqual(document.result["errors"], [])
        # self.assertEqual(document.result["warnings"], [])

        # print(json.dumps(document.result, indent=4))

        self.assertEqual(Home.objects.count(), 2)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 2)
        self.assertEqual(CollectedInput.objects.count(), 6)
        self._test_bulk_upload_answers()

    def test_bulk_upload_multiples(self):
        """If for some reason multiple answers exist they will get pruned out"""
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)

        document = self._handle_uploading(
            user_id=self.user.id,
            file_obj=self.bulk_upload_path,
            url="checklist:bulk_checklist_upload",
        )
        self.assertIn("Completed processing 2", document.result["latest"])
        self.assertEqual(document.result["critical"], [])
        self.assertEqual(document.result["errors"], [])

        self.assertEqual(Home.objects.count(), 2)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 2)
        self.assertEqual(CollectedInput.objects.count(), 6)

        # Force change the answers
        CollectedInput.objects.filter(instrument__measure_id="question-1").update(
            data={"input": "foo"}
        )
        CollectedInput.objects.filter(instrument__measure_id="question-2").update(
            data={"input": 1.0}
        )
        CollectedInput.objects.filter(instrument__measure_id="question-3").update(
            data={"input": "no"}
        )

        # Second upload
        document = self._handle_uploading(
            user_id=self.user.id,
            file_obj=self.bulk_upload_path,
            url="checklist:bulk_checklist_upload",
        )
        self.assertIn("Completed processing 2", document.result["latest"])
        self.assertEqual(document.result["critical"], [])
        self.assertEqual(document.result["errors"], [])

        self.assertEqual(Home.objects.count(), 2)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 2)
        self.assertEqual(CollectedInput.objects.count(), 6)

        self._test_bulk_upload_answers()
