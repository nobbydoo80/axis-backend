"""subdivision_tests.py: Django subdivision.tests"""


import json
import logging
import os
import re

from django.urls import reverse
from django.core.files import File

from axis.examine.tests.utils import MachineryDriver
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.filehandling.models import CustomerDocument

from ..models import Subdivision
from ..views.examine import SubdivisionExamineMachinery
from .mixins import SubdivisionViewTestMixin


__author__ = "Steven Klass"
__date__ = "12/5/11 1:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ...company.models import Company

log = logging.getLogger(__name__)


def get_test_doc_file(doc_name):
    """
    A simple helper to return file objects for included test files

    Example::

        somefile = get_test_doc_file('doc-1.txt')

    """
    fp = os.path.join(os.path.dirname(__file__), doc_name)
    return open(fp, "rb")


class SubdivisionViewTests(SubdivisionViewTestMixin, AxisTestCase):
    """Test out floorplan application"""

    client_class = AxisClient

    def test_login_required(self):
        subdivision = Subdivision.objects.first()

        url = reverse("subdivision:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("subdivision:view", kwargs={"pk": subdivision.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("subdivision:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_company_user_has_permissions(self):
        """Test that we can login and see subdivisions"""
        user = self.get_admin_user()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        self.assertEqual(user.has_perm("subdivision.view_subdivision"), True)
        self.assertEqual(user.has_perm("subdivision.change_subdivision"), True)
        self.assertEqual(user.has_perm("subdivision.add_subdivision"), True)
        self.assertEqual(user.has_perm("subdivision.delete_subdivision"), True)

        subdivision = Subdivision.objects.filter_by_user(user).first()

        url = reverse("subdivision:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("subdivision:view", kwargs={"pk": subdivision.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("subdivision:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_examine_create(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        class DummyRequest(object):
            pass

        dummy_request = DummyRequest()
        dummy_request.user = user

        driver = MachineryDriver(
            SubdivisionExamineMachinery, create_new=True, context={"request": dummy_request}
        )

        builder_org = user.company.relationships.get_companies(is_customer=False).filter(
            company_type="builder"
        )[0]
        data = dict(
            self.create_intersection_address_kwargs(),
            **{
                "builder_org": builder_org.id,
                "builder_name": "3203-1",
                "is_multi_family": False,
            },
        )
        driver.bind(data)

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subdivision.objects.filter(id=response_object["id"]).exists(), True)

    def test_examine_create_with_community(self):
        from axis.community.models import Community

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        class DummyRequest(object):
            pass

        dummy_request = DummyRequest()
        dummy_request.user = user

        driver = MachineryDriver(
            SubdivisionExamineMachinery, create_new=True, context={"request": dummy_request}
        )

        community = Community.objects.filter_by_company(user.company).get()
        builder_org = user.company.relationships.get_companies(is_customer=False).filter(
            company_type="builder"
        )[0]
        data = dict(
            self.create_intersection_address_kwargs(),
            **{
                "builder_org": builder_org.id,
                "builder_name": "3203-1",
                "community": community.id,
            },
        )
        driver.bind(data)

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subdivision.objects.filter(id=response_object["id"]).exists(), True)

    def test_examine_update(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        class DummyRequest(object):
            pass

        dummy_request = DummyRequest()
        dummy_request.user = user

        driver = MachineryDriver(
            SubdivisionExamineMachinery,
            instance=Subdivision.objects.all()[0],
            context={"request": dummy_request},
        )
        driver.set_ignore_fields(
            "modified_date", "city_name", "geocoded_address", "cross_roads_display", "city_display"
        )
        builder_org = user.company.relationships.get_companies(is_customer=False).filter(
            company_type="builder"
        )[0]
        data = dict(
            self.update_intersection_address_kwargs(),
            **{
                "builder_org": builder_org.id,
                "builder_name": "3203-1",
            },
        )
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_object, response_object)

    def test_list_view(self):
        """Test list view for subdivisions"""
        user = self.random_user
        self.assertEqual(self.client.login(username=user.username, password="password"), True)

        url = reverse("subdivision:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.has_perm("subdivision.view_subdivision"), True)

        expected = Subdivision.objects.filter_by_company(user.company, show_attached=True)
        self.assertGreater(expected.count(), 0)

        response = self.client.get(
            reverse("subdivision:list"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)

        match_ids = []
        data = json.loads(response.content)["data"]
        for item in data:
            m = re.search(r"\"/subdivision/(\d+)/\"", item.get("0"))
            if m:
                match_ids.append(int(m.group(1)))
        self.assertEqual(set(expected.values_list("id", flat=True)), set(match_ids))

    def test_create_relationship_and_lookups(self):
        """Test to verify that we can create a relationship to a subdivision"""
        from axis.geographic.models import City
        from axis.company.models import BuilderOrganization
        from ..fields import SubdivisionChoiceWidget

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

        subdivision = Subdivision.objects.create(
            name="SubRelTest",
            city=city,
            county=city.county,
            state=city.county.state,
            builder_org=builder,
            climate_zone=city.county.climate_zone,
        )

        # Verify that one of our subdivision does return in the list..
        existing = Subdivision.objects.filter_by_company(user.company)[0]
        existing_data = SubdivisionChoiceWidget.get_reverse_data(term=existing.name[0:4])
        my_subdivisions = reverse("django_select2-json")
        response = self.client.get(my_subdivisions, data=existing_data)
        self.assertEqual(response.status_code, 200)
        match_ids = [str(item["id"]) for item in json.loads(response.content)["results"]]
        self.assertIn(str(existing.id), match_ids)

        # Verify our new subdivision isn't in my subdivisions
        existing_data = SubdivisionChoiceWidget.get_reverse_data(term=subdivision.name[0:2])
        response = self.client.get(my_subdivisions, data=existing_data)
        match_ids = [str(item["id"]) for item in json.loads(response.content)["results"]]
        self.assertNotIn(str(subdivision.id), match_ids)

        # Add the relationship
        kwargs = {"model": "subdivision", "app_label": "subdivision"}
        url = reverse("relationship:add", kwargs=kwargs)
        response = self.client.post(url, {"object": subdivision.id})

        success_redirect = reverse("subdivision:list")
        self.assertRedirects(response, success_redirect)

        # Finally verify our new subdivision shows up in the list.
        response = self.client.get(my_subdivisions, data=existing_data)
        match_ids = [str(item["id"]) for item in json.loads(response.content)["results"]]
        self.assertIn(str(subdivision.id), match_ids)

    def test_remove_relationship(self):
        """Test to verify that we can remove a relationship to subdivision"""

        user = self.admin_user
        self.assertEqual(self.client.login(username=user.username, password="password"), True)

        url = reverse("subdivision:list")
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        match_ids = []
        for item in json.loads(response.content)["data"]:
            last_column = sorted([int(x) for x in item.keys() if re.search(r"[0-9]+", x)])[-1]
            m = re.search(r"\"/subdivision/(\d+)/\"", item.get("0"))
            m2 = re.search(r'href=[\'"]?([^\'" >]+)', item.get(str(last_column)))
            match_ids.append((int(m.group(1)), m2.group(1)))

        target_id, target_url = match_ids[0]
        kwargs = {"model": "subdivision", "app_label": "subdivision", "object_id": target_id}
        url = reverse("relationship:remove_id", kwargs=kwargs)
        self.assertEqual(url, target_url)

        response = self.client.post(url)
        self.assertRedirects(response, reverse("subdivision:list"))

        match_ids = Subdivision.objects.filter_by_company(user.company, show_attached=True)
        match_ids = match_ids.values_list("id", flat=True)
        self.assertNotIn(target_id, match_ids)

    def test_examine_subdivisiondocument_create(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        subdivision = Subdivision.objects.filter_by_company(user.company, show_attached=True)[0]

        M = customerdocument_machinery_factory(Subdivision)
        driver = MachineryDriver(M, create_new=True, request_user=user)
        data = {
            "subdivision": subdivision.id,
            "document_raw": driver.encode_file(__file__),
            "document_raw_name": "__file__",
            "description": "First Description",
            "is_public": True,
            "object_id": subdivision.id,
        }
        driver.bind(data)

        driver.get_client_object()

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerDocument.objects.filter(id=response_object["id"]).exists(), True)
        self.assertEqual(bool(response_object["document"]), True)  # path will be sort of random

    def test_examine_subdivisiondocument_update(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        # Make sure existing data is available
        self.test_examine_subdivisiondocument_create()
        subdivision = Subdivision.objects.filter_by_company(user.company, show_attached=True)[0]
        document = subdivision.customer_documents.all()[0]

        M = customerdocument_machinery_factory(Subdivision)
        driver = MachineryDriver(M, instance=document, request_user=user)
        driver.set_ignore_fields("last_update", "preview_link")
        data = {
            "object_id": subdivision.id,
            "description": "Update description",
            "is_public": False,
        }
        driver.bind(data)

        client_object = driver.get_client_object()
        # response object is going to have a full url for the document, but the client object will
        # just know about a path based in the MEDIA_URL.
        client_object["document"] = client_object["document"]

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(client_object["document"])
        client_object.pop("document")

        self.assertIsNotNone(response_object["document"])
        response_object.pop("document")

        self.assertEqual(client_object, response_object)

    def test_shared_supplement_docs(self):
        """Test the document sharing capability for both one-way and bi-directional
        relationships"""

        user = self.get_admin_user(company_type="rater")
        self.assertEqual(self.client.login(username=user.username, password="password"), True)

        subdivision = Subdivision.objects.filter_by_company(user.company, show_attached=True)[0]
        target = subdivision.relationships.get_hvac_orgs().get()
        target_admin = target.users.filter(is_company_admin=True).get()

        initial = CustomerDocument.objects.count()

        # Ensure we are bi-directional friends
        self.assertIn(user.company, target.relationships.get_companies())
        self.assertIn(target, user.company.relationships.get_companies())
        self.assertIn(subdivision, user.company.relationships.get_subdivisions())
        self.assertIn(subdivision, target_admin.company.relationships.get_subdivisions())

        # Create a public document
        f = File(open(__file__), name="test.txt")
        CustomerDocument.objects.create(
            document=f,
            description="First Description",
            is_public=True,
            company=user.company,
            content_object=subdivision,
        )
        self.assertEqual(CustomerDocument.objects.count(), initial + 1)
        self.assertEqual(CustomerDocument.objects.count(), 1)
        self.assertEqual(CustomerDocument.objects.all()[0].is_public, True)

    def test_multi_family_raises_error_when_community_is_not_multi_family(self):
        from axis.community.models import Community

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        class DummyRequest(object):
            pass

        dummy_request = DummyRequest()
        dummy_request.user = user

        driver = MachineryDriver(
            SubdivisionExamineMachinery, create_new=True, context={"request": dummy_request}
        )

        community = Community.objects.filter_by_company(user.company).get()
        builder_org = user.company.relationships.get_companies(is_customer=False).filter(
            company_type="builder"
        )[0]
        data = dict(
            self.create_intersection_address_kwargs(),
            **{
                "builder_org": builder_org.id,
                "builder_name": "3203-1",
                "community": community.id,
                "is_multi_family": True,
            },
        )
        driver.bind(data)

        driver.raise_response_errors = False
        response = driver.submit(self.client, method="post")
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.maxDiff = None
        self.assertEqual(
            response_data["is_multi_family"], ["Multi-family setting must match community."]
        )

    def test_multi_family_allowed_when_community_is_multi_family(self):
        from axis.community.models import Community

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        class DummyRequest(object):
            pass

        dummy_request = DummyRequest()
        dummy_request.user = user

        driver = MachineryDriver(
            SubdivisionExamineMachinery, create_new=True, context={"request": dummy_request}
        )

        community = Community.objects.filter_by_company(user.company).get()
        community.is_multi_family = True
        community.save()
        builder_org = user.company.relationships.get_companies(is_customer=False).filter(
            company_type="builder"
        )[0]
        data = dict(
            self.create_intersection_address_kwargs(),
            **{
                "builder_org": builder_org.id,
                "builder_name": "3203-1",
                "community": community.id,
                "is_multi_family": True,
            },
        )
        driver.bind(data)

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subdivision.objects.filter(id=response_object["id"]).exists(), True)
