""" View tests for builder_agreement app """


__author__ = "Steven Klass"
__date__ = "1/20/12 4:02 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import json
import logging
import os
import re

from django.urls import reverse

from axis.company.tests.factories import builder_organization_factory
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.core.utils import unrandomize_filename
from axis.examine.tests.utils import MachineryDriver
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.filehandling.models import CustomerDocument
from axis.relationship.models import Relationship
from axis.subdivision.tests.factories import subdivision_factory

from ...company.models import BuilderOrganization, Company

from ...core.tests.factories import eep_admin_factory, builder_admin_factory
from ...eep_program.tests.factories import basic_eep_program_factory
from ...geographic.tests.factories import real_city_factory
from ..models import BuilderAgreement

from .factories import builder_agreement_factory

log = logging.getLogger(__name__)


class BuilderAgreementViewTests(AxisTestCase):
    """Test out builder agreeement application"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        city = real_city_factory(name="Gilbert", state="AZ")

        eep_user = eep_admin_factory(company__city=city, company__slug="aps")
        eep_user.company.update_permissions("builder_agreement")

        builder_user = builder_admin_factory(company__city=city)
        builder = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=builder_user.company.id
        )

        eep_program = basic_eep_program_factory(owner=eep_user.company, no_close_dates=True)
        subdivision = subdivision_factory(city=city, builder_org=builder)

        Relationship.objects.validate_or_create_relations_to_entity(subdivision, eep_user.company)
        Relationship.objects.validate_or_create_relations_to_entity(
            subdivision, builder_user.company
        )
        Relationship.objects.create_mutual_relationships(eep_user.company, builder_user.company)

        cls.builder_agreement = builder_agreement_factory(
            company=eep_user.company,
            builder_org=builder_user.company,
            subdivision=subdivision,
            eep_programs=[eep_program],
            lots_paid=0,
        )

    def test_login_required(self):
        """Permission tests"""
        url = reverse("builder_agreement:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("builder_agreement:view", kwargs={"pk": self.builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("builder_agreement:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("builder_agreement:update", kwargs={"pk": self.builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("builder_agreement:delete", kwargs={"pk": self.builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("builder_agreement:status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_company_user_has_permissions(self):
        """Test that we can login and see builder agreements."""
        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertEqual(user.has_perm("builder_agreement.view_builderagreement"), True)
        self.assertEqual(user.has_perm("builder_agreement.change_builderagreement"), True)
        self.assertEqual(user.has_perm("builder_agreement.add_builderagreement"), True)
        self.assertEqual(user.has_perm("builder_agreement.delete_builderagreement"), True)

        url = reverse("builder_agreement:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("builder_agreement:view", kwargs={"pk": self.builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("builder_agreement:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("builder_agreement:update", kwargs={"pk": self.builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("builder_agreement:delete", kwargs={"pk": self.builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("builder_agreement:status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        """Test list view for builder agreements."""
        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("builder_agreement:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("builder_agreement:list"), ajax=True)
        self.assertEqual(response.status_code, 200)

        expected = BuilderAgreement.objects.filter_by_company(user.company)
        self.assertNotEqual(expected.count(), 0)

        match_ids = []
        data = json.loads(response.content)["data"]
        template_url = reverse("builder_agreement:view", kwargs={"pk": 0}).replace(
            "/0/", r"/(\d+)/"
        )
        for item in data:
            match = re.search(template_url, item["0"])
            if match:
                match_ids.append(int(match.group(1)))
        self.assertEqual(set(expected.values_list("id", flat=True)), set(match_ids))

    def test_create_view_subdivision(self):
        """Test creation of a builder agreement with only a subdivision."""
        from axis.geographic.models import City
        from axis.company.models import BuilderOrganization
        from axis.eep_program.models import EEPProgram

        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        city = City.objects.get(name="Gilbert", county__state="AZ")
        comps = user.company.relationships.get_companies(show_attached=True, company_type="builder")
        builder = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).filter(
            id__in=comps.values_list("id", flat=True)
        )[0]

        subdivision = subdivision_factory(city=city, builder_org=builder)
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, user.company)

        eeps = EEPProgram.objects.filter_by_company(user.company)[:2]
        eep_ids = list(eeps.values_list("id", flat=True))

        document = open(__file__)

        # Create the Builder Agreement
        data = {
            "company": user.company.id,
            "builder_org": subdivision.builder_org.id,
            "subdivision": subdivision.id,
            "total_lots": 201,
            "eep_programs": list(map(str, eep_ids)),
            "start_date": datetime.date.today(),
            "expire_date": datetime.date.today() + datetime.timedelta(days=183),
            "document": document,
            "comment": "Nice comment",
            "is_active": True,
            "is_legacy": False,
        }

        url = reverse("builder_agreement:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, data=data)

        # Fetch the object we just saved out of the database
        builder_agreement = BuilderAgreement.objects.filter_by_company(
            company=user.company, subdivision=subdivision
        ).get()

        # Verify that the post at the CreateView redirects to this details page
        success_redirect = builder_agreement.get_absolute_url()
        self.assertRedirects(response, success_redirect)

        response = self.client.get(success_redirect)
        self.assertEqual(response.status_code, 200)

        builder_agreement = response.context["object"]
        _skip_checks = {
            "subdivision",
            "eep_programs",
            "document",
            "builder_org",
            "company",
        }
        for key in set(data) - _skip_checks:
            self.assertEqual(getattr(builder_agreement, key), data[key])

        self.assertEqual(builder_agreement.subdivision.id, subdivision.id)
        self.assertEqual(builder_agreement.builder_org.id, subdivision.builder_org.id)
        self.assertEqual(builder_agreement.company.id, user.company.id)

        doc_name = builder_agreement.document.name
        uploaded_name = unrandomize_filename(os.path.basename(doc_name))
        self.assertEqual(uploaded_name, os.path.basename(__file__))

        # Verify that everything in the builder_agreement.eep_programs is in the list from earlier
        self.assertGreaterEqual(
            set(builder_agreement.eep_programs.values_list("name", flat=True)),
            set(eeps.values_list("name", flat=True)),
        )

        document.close()

    def test_create_view_builder_org(self):
        """Test creation of a builder agreement with only a builder."""
        from axis.eep_program.models import EEPProgram

        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        builder = builder_organization_factory(city=user.company.city)
        Relationship.objects.create_mutual_relationships(user.company, builder)

        eeps = EEPProgram.objects.filter_by_company(user.company)
        eep_ids = list(eeps.values_list("id", flat=True)[:2])

        document = open(__file__)

        # Create the Builder Agreement
        data = {
            "company": user.company.id,
            "builder_org": builder.id,
            "total_lots": 201,
            "eep_programs": list(map(str, eep_ids)),
            "start_date": datetime.date.today(),
            "expire_date": datetime.date.today() + datetime.timedelta(days=183),
            "document": document,
            "comment": "Nice comment",
            "is_active": True,
            "is_legacy": False,
        }

        response = self.client.post(reverse("builder_agreement:add"), data=data)
        builder_agreement = BuilderAgreement.objects.filter_by_company(
            company=user.company, builder_org=builder
        ).get()
        success_redirect = builder_agreement.get_absolute_url()
        self.assertRedirects(response, success_redirect)
        response = self.client.get(success_redirect)
        self.assertEqual(response.status_code, 200)

        builder_agreement = response.context["object"]
        _skip_checks = {
            "subdivision",
            "eep_programs",
            "document",
            "builder_org",
            "company",
        }
        for key in set(data) - _skip_checks:
            self.assertEqual(getattr(builder_agreement, key), data[key])

        self.assertEqual(builder_agreement.subdivision, None)
        self.assertEqual(builder_agreement.builder_org.id, builder.id)
        self.assertEqual(builder_agreement.company.id, user.company.id)

        document.close()

    def test_update_view(self):
        """Test update of a builder agreement."""
        from axis.eep_program.models import EEPProgram

        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        builder_agreement = BuilderAgreement.objects.filter_by_company(user.company)[0]
        eeps = EEPProgram.objects.filter_by_company(user.company)
        eep_ids = list(eeps.values_list("id", flat=True))

        document = open(__file__)

        # Update the Builder Agreement
        data = {
            "eep_programs": list(map(str, eep_ids)),
            "total_lots": 1300,
            "start_date": datetime.date.today() + datetime.timedelta(days=3),
            "expire_date": datetime.date.today() + datetime.timedelta(days=200),
            "document": document,
            "comment": "Nice Modified",
            "is_active": False,
            "is_legacy": True,
        }

        url = reverse("builder_agreement:update", kwargs={"pk": builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data=data)
        success_redirect = builder_agreement.get_absolute_url()
        self.assertRedirects(response, success_redirect)
        response = self.client.get(success_redirect)
        self.assertEqual(response.status_code, 200)

        builder_agreement = response.context["object"]
        _skip_checks = {
            "subdivision",
            "eep_programs",
            "document",
            "builder_org",
            "company",
        }
        for key in set(data) - _skip_checks:
            self.assertEqual(getattr(builder_agreement, key), data[key])

        if hasattr(builder_agreement, "subdivision") and builder_agreement.subdivision:
            self.assertEqual(
                response.context["object"].subdivision.id,
                builder_agreement.subdivision.id,
            )
        self.assertEqual(
            response.context["object"].builder_org.id, builder_agreement.builder_org.id
        )
        self.assertEqual(response.context["object"].company.id, user.company.id)

        docname = builder_agreement.document.name
        uploaded_name = unrandomize_filename(os.path.basename(docname))
        self.assertEqual(uploaded_name, os.path.basename(__file__))

        # Verify that everything in the builder_agreement.eep_programs is in the list from earlier
        self.assertGreaterEqual(
            set(builder_agreement.eep_programs.values_list("name", flat=True)),
            set(eeps.values_list("name", flat=True)),
        )

        document.close()

    def test_delete_view(self):
        """Test delete a builder agreement."""
        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        builder_agreements = BuilderAgreement.objects.filter_by_company(user.company)
        self.assertEqual(builder_agreements.count(), 1)

        builder_agreement = builder_agreements[0]
        url = reverse("builder_agreement:delete", kwargs={"pk": builder_agreement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        builder_agreements = BuilderAgreement.objects.filter_by_company(user.company)
        self.assertEqual(builder_agreements.count(), 0)

    def test_supplement_docs(self):
        """Test builder agreement additional documentation."""

        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        builder_agreement = BuilderAgreement.objects.filter_by_company(user.company)[0]
        self.assertEqual(CustomerDocument.objects.count(), 0)

        url = reverse("builder_agreement:view", kwargs={"pk": builder_agreement.id})
        self.assertEqual(builder_agreement.get_absolute_url(), url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        machinery = customerdocument_machinery_factory(BuilderAgreement)
        driver = MachineryDriver(machinery, create_new=True, request_user=user)
        data = {
            "object_id": builder_agreement.id,
            "document_raw": driver.encode_file(__file__),
            "document_raw_name": "__file__",
            "description": "Description",
            "is_public": True,
        }
        driver.bind(data)

        _ = driver.get_client_object()

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerDocument.objects.count(), 1)
        self.assertEqual(bool(response_object["document"]), True)  # path will be sort of random

    def test_status_list_view(self):
        """Test list view for builder statuses."""
        user = self.get_admin_user(company_type="eep")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("builder_agreement:status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("builder_agreement:status"), ajax=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)["data"]
        self.assertGreater(len(data), 0)
        builder_ids = []
        for item in data:
            match = re.search(r'"/app/company/builder/detail/(\d+)"', item["0"])
            if match:
                builder_ids.append(int(match.group(1)))

        response = self.client.get(
            reverse("builder_agreement:status"),
            data={"builder_id": builder_ids[0]},
            ajax=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len([x for x in builder_ids if x == builder_ids[0]]))
