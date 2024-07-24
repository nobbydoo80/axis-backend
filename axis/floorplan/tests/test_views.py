__author__ = "Steven Klass"
__date__ = "12/5/11 1:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import json
import logging
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from axis.annotation.models import Annotation
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.ekotrope.tests.factories import analysis_factory as eko_analysis_factory
from axis.ekotrope.tests.factories import (
    house_plan_factory,
    ekotrope_auth_details_factory,
    project_factory,
)
from axis.examine.tests.utils import MachineryDriver
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.filehandling.models import CustomerDocument
from axis.floorplan.views.examine import (
    get_floorplan_annotations_machinery_class,
)
from axis.home.tests.factories import eep_program_custom_home_status_factory
from axis.remrate_data.fields import UnattachedSimulationChoiceWidget
from .mixins import FloorplanTestMixin
from ..models import Floorplan

log = logging.getLogger(__name__)


class FloorplanViewTests(FloorplanTestMixin, AxisTestCase):
    """Test out floorplan application"""

    client_class = AxisClient

    def test_floorplan_remrate_input_list_view(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        floorplan = Floorplan.objects.filter(remrate_target__isnull=False).first()

        url = reverse("floorplan:input:remrate")
        response = self.client.get(url)
        self.assertContains(response, "Upload")

        # do ajax request to get datatable generated data
        response = self.client.get(
            url, content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        json_data = json.loads(response.content)

        self.assertEqual(
            floorplan.remrate_target.building.project.property_address, json_data["data"][0]["1"]
        )
        self.assertIn(floorplan.remrate_target.building.project.name, json_data["data"][0]["0"])

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_floorplan_ekotrope_input_list_view(self, import_project_tree):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        floorplan = Floorplan.objects.filter_by_user(user).first()
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)

        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        url = reverse("floorplan:input:ekotrope")
        response = self.client.get(url)
        self.assertContains(response, "Ekotrope ID")

        # do ajax request to get datatable generated data
        response = self.client.get(
            url, content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        json_data = json.loads(response.content)
        self.assertIn(floorplan.ekotrope_houseplan.name, json_data["data"][0]["0"])
        self.assertEqual(floorplan.ekotrope_houseplan.id, json_data["data"][0]["5"])

    def test_floorplan_remrate_input_detail_view(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        floorplan = (
            Floorplan.objects.filter_by_user(user).filter(remrate_target__isnull=False).first()
        )
        url = reverse("floorplan:input:remrate", kwargs={"pk": floorplan.remrate_target.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, floorplan.remrate_target.axis_id)
        self.assertEqual(response.context_data["summary"].axis_id, floorplan.remrate_target.axis_id)
        self.assertEqual(response.context_data["homes"].count(), 0)
        self.assertEqual(response.context_data["view"].mode, "remrate")
        self.assertFalse(response.context_data["view"].show_edit_button)
        self.assertFalse(response.context_data["view"].show_add_button)
        self.assertTrue(response.context_data["view"].show_delete_button)

    @mock.patch("axis.ekotrope.utils.import_project_tree")
    def test_floorplan_ekotrope_input_detail_view(self, import_project_tree):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        floorplan = Floorplan.objects.filter_by_user(user).first()
        project = project_factory(company=user.company)
        ekotrope_auth_details_factory(user=user)
        # mock post_save import_project_tree to skip connecting to API
        import_project_tree.return_value = project
        house_plan = house_plan_factory(project=project)

        # create custom home status to check context_data['homes'] query works correct
        eep_program_custom_home_status_factory(company=user.company, floorplan=floorplan)
        floorplan.remrate_target = None
        floorplan.ekotrope_houseplan = house_plan
        floorplan.save()

        url = reverse("floorplan:input:ekotrope", kwargs={"pk": floorplan.ekotrope_houseplan.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, floorplan.ekotrope_houseplan.project.data["algorithmVersion"])
        self.assertEqual(
            response.context_data["summary"]["project"], floorplan.ekotrope_houseplan.project.data
        )
        self.assertEqual(response.context_data["homes"].count(), 1)
        self.assertEqual(response.context_data["view"].mode, "ekotrope")
        self.assertFalse(response.context_data["view"].show_edit_button)
        self.assertFalse(response.context_data["view"].show_add_button)
        self.assertTrue(response.context_data["view"].show_delete_button)

    def test_queryset_for_providers(self):
        """This will test out the remrate querysets for providers"""
        from axis.relationship.models import Relationship
        from axis.company.models import Company

        provider = Company.objects.filter(company_type="provider").get()
        floorplan = Floorplan.objects.get_or_create(owner=provider, name="test")[0]
        self.assertIn(floorplan, Floorplan.objects.filter_by_company(provider))

        # Build up an unrelated company
        unrelated_rater = Company.objects.filter(company_type="rater", slug="unrelated_rater").get()
        # Assert that neither of these has a relationship with each other.
        self.assertNotIn(unrelated_rater, provider.relationships.get_companies())
        self.assertNotIn(provider, unrelated_rater.relationships.get_companies())

        # No relationship == no visibility.
        rater_floorplan = Floorplan.objects.get_or_create(owner=unrelated_rater, name="test2")[0]
        self.assertIn(rater_floorplan, Floorplan.objects.filter_by_company(unrelated_rater))
        self.assertEqual(rater_floorplan in Floorplan.objects.filter_by_company(provider), False)

        # Assign a relationship to it.  This is either done via preliminary share or adding a
        # subdivision
        Relationship.objects.validate_or_create_relations_to_entity(
            direct_relation=provider, entity=rater_floorplan
        )
        self.assertIn(rater_floorplan, Floorplan.objects.filter_by_company(provider))


class FloorplanExamineTests(FloorplanTestMixin, AxisTestCase):
    client_class = AxisClient

    def _get_remrate_targets(self, user):
        from axis.remrate_data.models import Simulation

        unattached = reverse("django_select2-json")
        term = Simulation.objects.filter(floorplan__isnull=True).get().building.project.name[0]
        unattached_data = UnattachedSimulationChoiceWidget.get_reverse_data(term=term)
        response = self.client.get(unattached, data=unattached_data)
        self.assertEqual(response.status_code, 200)
        remrate_targets = [str(item["id"]) for item in json.loads(response.content)["results"]]
        self.assertEqual(len(remrate_targets), 1)

        return remrate_targets

    def _get_blg_file(self):
        from django.core.files.base import ContentFile

        file_name = "test.blg"
        return ContentFile(b"test content", name=file_name)

    def _get_ekotrope_houseplan(self, user):
        ekotrope_auth_details_factory(user=user)
        analysis = eko_analysis_factory(company=user.company)
        return analysis.houseplan

    def _get_related_companies_for_user(self, user, **kwargs):
        return user.company.relationships.get_companies().filter(
            is_eep_sponsor=True, is_customer=True, **kwargs
        )

    def test_examine_create_note(self):
        from axis.annotation.tests.factories import type_factory

        type_factory(slug="note")
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter_by_company(user.company).first()

        machinery_class = get_floorplan_annotations_machinery_class()
        driver = MachineryDriver(machinery_class, create_new=True, request_user=user)
        data = {
            "content": "Test note",
            "is_public": True,
            "object_id": floorplan.id,
        }
        driver.bind(data)

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Annotation.objects.filter(id=response_object["id"]).exists(), True)

    def test_examine_update_note(self):
        from axis.annotation.tests.factories import type_factory

        annotation_type = type_factory(
            slug="note",
            applicable_content_types=[ContentType.objects.get_for_model(Floorplan)],
        )

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter_by_company(user.company).first()
        annotation = Annotation.objects.create(
            type=annotation_type, content="Old content", content_object=floorplan, is_public=True
        )

        machinery_class = get_floorplan_annotations_machinery_class()
        driver = MachineryDriver(machinery_class, instance=annotation, request_user=user)
        data = {"content": "New content", "is_public": False}
        driver.bind(data)

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_object["content"], data["content"])
        self.assertEqual(response_object["is_public"], data["is_public"])

    def test_examine_delete_note(self):
        from axis.annotation.tests.factories import type_factory

        annotation_type = type_factory(
            slug="note",
            applicable_content_types=[ContentType.objects.get_for_model(Floorplan)],
        )

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter_by_company(user.company).first()
        annotation = Annotation.objects.create(
            type=annotation_type,
            content="Default content",
            content_object=floorplan,
            is_public=True,
        )

        machinery_class = get_floorplan_annotations_machinery_class()
        driver = MachineryDriver(machinery_class, instance=annotation, request_user=user)

        response = driver.submit(self.client, method="delete")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Annotation.objects.count(), 0)

    def test_examine_create_document(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter_by_company(user.company).first()

        machinery_class = customerdocument_machinery_factory(Floorplan)
        driver = MachineryDriver(machinery_class, create_new=True, request_user=user)
        data = {
            "object_id": floorplan.id,
            "document_raw": driver.encode_file(__file__),
            "document_raw_name": "__file__",
            "description": "Description",
            "is_public": True,
        }
        driver.bind(data)

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerDocument.objects.filter(id=response_object["id"]).exists(), True)
        self.assertEqual(bool(response_object["document"]), True)

    def test_examine_update_document(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter_by_company(user.company).first()
        old_file = SimpleUploadedFile(name="old_file.txt", content=b"old content")

        old_document = CustomerDocument.objects.create(
            company=user.company, document=old_file, content_object=floorplan, is_public=True
        )

        machinery_class = customerdocument_machinery_factory(Floorplan)
        driver = MachineryDriver(machinery_class, instance=old_document, request_user=user)

        data = {
            "document_raw": driver.encode_file(__file__),
            "document_raw_name": "__file__",
            "description": "Description",
            "is_public": False,
        }
        driver.bind(data)

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response_object["description"], old_document.description)
        self.assertNotEqual(response_object["is_public"], old_document.is_public)
        self.assertNotEqual(response_object["url"], old_document.document.url)

    def test_examine_delete_document(self):
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        floorplan = Floorplan.objects.filter_by_company(user.company).first()
        document_file = SimpleUploadedFile(name="file.txt", content=b"file content")

        document = CustomerDocument.objects.create(
            company=user.company, document=document_file, content_object=floorplan, is_public=True
        )

        machinery_class = customerdocument_machinery_factory(Floorplan)
        driver = MachineryDriver(machinery_class, instance=document, request_user=user)

        response = driver.submit(self.client, method="delete")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomerDocument.objects.count(), 0)
