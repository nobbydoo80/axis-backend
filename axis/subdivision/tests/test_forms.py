__author__ = "Johnny Fang"
__date__ = "10/6/19 10:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

import logging

from django.contrib.auth import get_user_model
from axis.company.models import BuilderOrganization, Company
from axis.core.tests.testcases import AxisTestCase
from axis.subdivision.forms import SubdivisionForm
from axis.subdivision.tests.mixins import SubdivisionManagerTestsMixin

log = logging.getLogger(__name__)
User = get_user_model()


class SubdivisionFormTest(SubdivisionManagerTestsMixin, AxisTestCase):
    form = SubdivisionForm

    def test_fail_no_required_fields_supplied(self):
        user = User.objects.order_by("id").first()
        form = self.form(data={}, user=user)

        self.assertEqual(form.is_valid(), False)

    def test_valid_required_fields_supplied(self):
        user = User.objects.order_by("id").first()
        builder_org = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).first()
        data = {"name": "name-", "builder_org": builder_org}
        form = self.form(data=data, user=user)

        self.assertEqual(form.is_valid(), True)

    def test_invalid_required_fields_supplied(self):
        user = User.objects.order_by("id").first()
        data = {"name": "name-", "builder_org": "xx"}
        form = self.form(data=data, user=user)

        self.assertEqual(form.is_valid(), False)
