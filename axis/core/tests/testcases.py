""" A base class for testcases"""
import json
import random
import sys
from collections import OrderedDict
import datetime
from pprint import pformat
from typing import Any

from django.db.models import Q
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils.serializer_helpers import ReturnList

__author__ = "Autumn Valenta"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


NON_USER_OR_FILTER = (
    Q(username__istartswith="noperm_")
    | Q(username__istartswith="nonuser")
    | Q(company__name__istartswith="unrelated_")
)


class AxisTestCaseUserMixin(object):
    """Base class mixin for users"""

    @property
    def user_model(self):
        """Gets the user model"""
        from django.contrib.auth import get_user_model

        return get_user_model()

    def get_user(self, **kwargs):
        return self.return_user(self.user_model.objects.filter(**kwargs))

    def return_user(self, objects, **kwargs):
        """Gets a random user from a list of users"""
        objects = list(objects)
        if not objects:
            raise IndexError("No users found based on filtering %r" % kwargs)
        if len(objects) == 1:
            return objects[0]
        return random.choice(list(objects))

    def get_admin_user(self, company_type=None, only_related=False):
        """Explicitly gets a company admin user"""

        objects = self.user_model.objects.filter(is_company_admin=True)
        objects = objects.exclude(NON_USER_OR_FILTER).exclude(is_superuser=True)
        if company_type:
            if not isinstance(company_type, (list, tuple)):
                company_type = [company_type]
            objects = objects.filter(company__company_type__in=company_type)
        if only_related:
            objects = objects.exclude(username__istartswith="unrelated_")
        return self.return_user(objects, company_type=company_type, type="admin")

    @property
    def admin_user(self):
        """An admin user"""
        return self.get_admin_user()

    def get_nonadmin_user(self, company_type=None, only_related=False):
        """Explicitly gets a non-company admin user"""
        objects = self.user_model.objects.filter(is_company_admin=False)
        objects = objects.exclude(NON_USER_OR_FILTER).exclude(is_superuser=True)
        if company_type:
            if not isinstance(company_type, (list, tuple)):
                company_type = [company_type]
            objects = objects.filter(company__company_type__in=company_type)
        if only_related:
            objects = objects.exclude(username__istartswith="unrelated_")
        return self.return_user(objects, company_type=company_type, type="nonadmin")

    @property
    def nonadmin_user(self):
        """A non admin user"""
        return self.get_nonadmin_user()

    def get_random_user(self, company_type=None):
        """Get a random user"""
        objects = self.user_model.objects.exclude(NON_USER_OR_FILTER).exclude(is_superuser=True)
        if company_type:
            if not isinstance(company_type, (list, tuple)):
                company_type = [company_type]
            objects = objects.filter(company__company_type__in=company_type)
        return self.return_user(objects, company_type=company_type, type="random")

    @property
    def random_user(self):
        """A random user"""
        return self.get_random_user()

    @property
    def noperms_user(self):
        """A no perms user"""
        objects = self.user_model.objects.filter(NON_USER_OR_FILTER)
        objects = objects.filter(Q(company__is_customer=False) | Q(company__isnull=True))
        objects = objects.exclude(is_superuser=True)
        return self.return_user(objects, type="noperms")

    @property
    def super_user(self):
        """A Super"""
        objects = self.user_model.objects.filter(is_superuser=True)
        return self.return_user(objects, type="super")


class AxisTestCase(TestCase, AxisTestCaseUserMixin):
    """Base class for Axis Test cases"""

    @classmethod
    def dump_test_data(
        cls, data: Any, object_name: str | bool = False, output=None, dump_json: bool = False
    ):
        """Helper function for generating test expectations - See test_dump_test_case for a full example"""

        from django.db.models import Model
        from django.forms import model_to_dict

        object_name = "data" if object_name is False else object_name
        if isinstance(data, Model):
            data = model_to_dict(data)

        if output is None:
            output = sys.stdout.write

        if dump_json:
            output(json.dumps(data, indent=4, default=str))

        if isinstance(data, (list, ReturnList)):
            output(f"self.assertEqual(len({object_name}), {len(data)})\n")
            for idx, item in enumerate(data):
                cls.dump_test_data(item, object_name=f"{object_name}[{idx}]", output=output)
            return
        if isinstance(data, (dict, OrderedDict)):
            for k, v in data.items():
                if "[" not in object_name:
                    _object_name = f"{object_name}.{k}"
                else:
                    _object_name = f"{object_name}['{k}']"
                cls.dump_test_data(v, object_name=_object_name, output=output)
            return
        if isinstance(data, type(None)):
            output(f"self.assertIsNone({object_name})\n")
        elif isinstance(data, (int, str)):
            if (
                object_name.endswith("_id")
                or object_name.endswith("['id']")
                or object_name.endswith("_id']")
                or object_name.endswith(".id")
                or "password" in object_name
            ):
                output(f"self.assertIsNotNone({object_name})\n")
            elif object_name.endswith("_date") or object_name.endswith("_date']"):
                output(f"self.assertIsNotNone({object_name})\n")
            else:
                output(f"self.assertEqual({object_name}, {data!r})\n")
        elif isinstance(data, (datetime.datetime, datetime.date)):
            output(f"self.assertEqual(str({object_name}), {str(data)!r})\n")
        elif isinstance(data, (float)):
            float_v = 4 if data < 1 else 2
            output(f"self.assertAlmostEqual({object_name}, {data!r}, {float_v})\n")
        elif isinstance(data, bool):
            if data is True:
                output(f"self.assertTrue({object_name})\n")
            else:
                output(f"self.assertFalse({object_name})\n")
        else:
            # print(type(data))
            output(f"self.assertIsNotNone({object_name})\n")


class ApiV3Tests(APITestCase, AxisTestCaseUserMixin):
    def list(self, url, user, expected_status=status.HTTP_200_OK):
        """Return a list with the list action."""
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="json")
        data = response.data.get("results")
        self.assertEqual(
            response.status_code,
            expected_status,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        self.assertIsInstance(
            data,
            list,
            "{url}: List endpoint did not return a list: {data}".format(
                url=url, data=pformat(data)
            ),
        )
        return data

    def create(
        self, url, user, data=None, data_format="json", expected_status=status.HTTP_201_CREATED
    ):
        """
        Return an object with the create action.
        """
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data=data, format=data_format)
        data = response.data
        self.assertEqual(
            response.status_code,
            expected_status,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        return data

    def retrieve(self, url, user, expected_status=status.HTTP_200_OK):
        """Return an object with the retrieve action."""
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="json")
        data = response.data
        self.assertEqual(
            response.status_code,
            expected_status,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        return data

    def update(
        self,
        url,
        user,
        data=None,
        partial=False,
        data_format="json",
        expected_status=status.HTTP_200_OK,
    ):
        """Update an object with the update action."""
        self.client.force_authenticate(user=user)
        method = self.client.put
        if partial:
            method = self.client.patch
        response = method(url, data=data, format=data_format)
        data = response.data
        self.assertEqual(
            response.status_code,
            expected_status,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        return data

    def delete(self, url, user, expected_status=status.HTTP_204_NO_CONTENT):
        """Delete an object with the delete action."""
        self.client.force_authenticate(user=user)
        response = self.client.delete(url, format="json")
        data = response.data
        self.assertEqual(
            response.status_code,
            expected_status,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        return None

    def options(self, url, user, expected_status=status.HTTP_200_OK):
        self.client.force_authenticate(user=user)
        response = self.client.options(url, format="json")
        data = response.data
        self.assertEqual(
            response.status_code,
            expected_status,
            "{url}: OPTIONS - Unexpected status code {response.status_code}: {data}".format(
                **locals()
            ),
        )
        return data
