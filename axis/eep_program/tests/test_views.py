"""eep_program_tests.py: Django eep.tests"""


import json
import logging
import datetime
import re

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.mixins import EEPProgramsTestMixin
from axis.eep_program.views.examine import EEPProgramExamineMachinery
from axis.examine.tests.utils import MachineryDriver

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EEPProgramViewsTests(EEPProgramsTestMixin, AxisTestCase):
    """Test out company application"""

    client_class = AxisClient

    def test_login_required(self):
        eep_program = EEPProgram.objects.first()

        url = reverse("eep_program:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("eep_program:view", kwargs={"pk": eep_program.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("eep_program:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_user_has_permissions(self):
        """Test that we can login and see Programs"""
        user = self.get_admin_user(company_type="eep", only_related=True)

        eep_program = EEPProgram.objects.filter_by_user(user).first()

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        self.assertEqual(user.has_perm("eep_program.view_eepprogram"), True)
        self.assertEqual(user.has_perm("eep_program.change_eepprogram"), True)
        self.assertEqual(user.has_perm("eep_program.add_eepprogram"), True)
        self.assertEqual(user.has_perm("eep_program.delete_eepprogram"), True)

        url = reverse("eep_program:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("eep_program:view", kwargs={"pk": eep_program.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Only supers Can create programs currently.
        self.client.logout()
        user = self.super_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("eep_program:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        """Test list view for Programs"""
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("eep_program:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("eep_program:list"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)

        expected = EEPProgram.objects.filter_by_company(user.company)
        self.assertGreater(expected.count(), 0)
        match_ids = []
        data = json.loads(response.content)["data"]
        for item in data:
            m = re.search(r"\"/eep_program/(\d+)/\"", item["0"])
            if m:
                match_ids.append(int(m.group(1)))
        self.assertEqual(set(expected.values_list("id", flat=True)), set(match_ids))


class EEPProgramExamineTests(EEPProgramsTestMixin, AxisTestCase):
    client_class = AxisClient

    def _create_data(self, **kwargs):
        data = {
            "name": "My Test Program",
            "min_hers_score": 2,
            "max_hers_score": 3,
            "per_point_adder": 4.2,
            "builder_incentive_dollar_value": 20.0,
            "rater_incentive_dollar_value": 25.01,
            "required_checklists": [str(x.id) for x in kwargs.get("checklists", [])],
            "comment": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "require_rem_data": True,
            "require_model_file": True,
            "allow_sampling": False,
            "allow_metro_sampling": False,
            "is_legacy": True,
            "is_active": False,
            "require_builder_epa_is_active": True,
            "program_start_date": datetime.date.today(),
            "program_close_date": datetime.date.today() + datetime.timedelta(days=75),
            "program_submit_date": datetime.date.today() + datetime.timedelta(days=125),
            "program_end_date": datetime.date.today() + datetime.timedelta(days=175),
            "program_close_warning_date": datetime.date.today() + datetime.timedelta(days=70),
            "program_close_warning": "Close Warning!",
            "program_submit_warning_date": datetime.date.today() + datetime.timedelta(days=120),
            "program_submit_warning": "Submit Warning!",
            "require_builder_relationship": False,
            "require_builder_assigned_to_home": False,
            "require_hvac_relationship": True,
            "require_hvac_assigned_to_home": True,
            "require_utility_relationship": True,
            "require_utility_assigned_to_home": True,
            "require_rater_relationship": True,
            "require_rater_assigned_to_home": True,
            "require_provider_relationship": True,
            "require_provider_assigned_to_home": True,
            "require_qa_relationship": True,
            "require_qa_assigned_to_home": True,
        }
        data.update(**kwargs)
        return data

    def test_examine_create_basic(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(EEPProgramExamineMachinery, create_new=True, request_user=user)
        driver.set_ignore_fields("owner_name", "owner_url")

        from axis.checklist.models import CheckList

        checklists = list(CheckList.objects.filter_by_company(user.company))[0:2]

        data = self._create_data(checklists=checklists)

        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()

        # Check the values match
        # Some values are special cases since they're getting serialized
        float_fields = [
            "per_point_adder",
            "rater_incentive_dollar_value",
            "builder_incentive_dollar_value",
        ]
        date_fields = ["program_start_date", "program_end_date"]
        accepted_fields = ["name", "min_hers_score", "max_hers_score"] + float_fields + date_fields
        for key in accepted_fields:
            value = data[key]
            if key in float_fields:
                self.assertEqual(float(client_object[key]), value)
                self.assertEqual(float(response_object[key]), value)
                continue
            if key in date_fields:
                self.assertEqual(client_object[key], "{}".format(value))
                self.assertEqual(response_object[key], "{}".format(value))
                continue
            self.assertEqual(client_object[key], value)
            self.assertEqual(response_object[key], value)

        # Check the response
        # And that we're getting at least the keys we gave
        self.assertEqual(response.status_code, 201)
        # Used to test for superset. We've since changed the structure of the page and
        # serializer by breaking it up into chunks.
        self.assertEqual(set(client_object.keys()).issuperset(set(accepted_fields)), True)
        self.assertEqual(set(response_object.keys()).issuperset(set(accepted_fields)), True)

    def test_examine_update_basic(self):
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = EEPProgram.objects.filter_by_user(user).first()
        original_name = instance.name
        driver = MachineryDriver(EEPProgramExamineMachinery, instance=instance, request_user=user)

        data = {"name": "Alternate Test Program"}

        driver.bind(data)
        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()

        self.assertEqual(response.status_code, 200)

        self.assertNotEqual(client_object["name"], original_name)
        self.assertNotEqual(response_object["name"], original_name)
        self.assertEqual(client_object["name"], response_object["name"])

    def test_examine_create_superuser_sponsor_sticks(self):
        """
        Given a superuser creating an EEPProgram
        When the super user chooses a sponsor company
        Then that company should be the sponsor
        """
        from axis.core.tests.factories import general_super_user_factory

        super_user = general_super_user_factory()
        self.assertTrue(
            self.client.login(username=super_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (super_user.username, super_user.pk),
        )

        driver = MachineryDriver(
            EEPProgramExamineMachinery, create_new=True, request_user=super_user
        )

        from axis.company.models import Company

        sponsor = Company.objects.filter(company_type="eep").first()
        data = self._create_data(sponsor=sponsor.id)

        driver.bind(data)

        client_object = driver.get_client_object()
        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()

        program = EEPProgram.objects.get(id=response_object["id"])

        self.assertEqual(program.owner.id, sponsor.id)

    def test_examine_create_non_superuser_sponsor_is_creator_company(self):
        """
        Given a regular user creating an EEPProgram
        When they save a company
        Then their company should be the sponsor
        """
        user = self.get_random_user()
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(EEPProgramExamineMachinery, create_new=True, request_user=user)
        data = self._create_data()

        driver.bind(data)

        client_object = driver.get_client_object()
        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()

        program = EEPProgram.objects.get(id=response_object["id"])

        self.assertEqual(program.owner.id, user.company.id)
