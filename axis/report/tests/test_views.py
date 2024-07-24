"""tests.py: Django report.tests"""


import random

import re
import logging
import os
from django.contrib.contenttypes.models import ContentType

from django.urls import reverse
from django.test import TestCase

from axis.core.tests.client import AxisClient

__author__ = "Michael Jeffrey"
__date__ = "9/3/13 3:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

from axis.core.tests.testcases import AxisTestCase

from axis.home.tests.mixins import HostStatusReportMixin

log = logging.getLogger(__name__)


class ECBReportViewTests(HostStatusReportMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        from axis.subdivision.models import Subdivision
        from axis.company.models import Company

        sub = random.choice(list(Subdivision.objects.all()))
        company = random.choice(list(Company.objects.all()))
        kwargs = {"subdivision_id": sub.id, "company_id": company.id}
        url = reverse("report:energy_cost", kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"])
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_report_view(self):
        from axis.relationship.models import Relationship
        from axis.subdivision.models import Subdivision
        from axis.company.models import Company
        from axis.core.tests.factories import (
            rater_admin_factory,
            provider_admin_factory,
            eep_admin_factory,
            builder_admin_factory,
            utility_admin_factory,
            hvac_admin_factory,
            qa_admin_factory,
            general_admin_factory,
        )

        ct = ContentType.objects.get_for_model(Subdivision)
        rels = Relationship.objects.filter(content_type=ct).values_list("company__id", flat=True)
        company = random.choice(list(Company.objects.filter(id__in=rels)))
        admin_factory = eval("{}_admin_factory".format(company.company_type))
        user = admin_factory(company=company)

        sub = Subdivision.objects.filter_by_user(user)[0]
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        kwargs = {"subdivision_id": sub.id, "company_id": user.company.id}

        url = reverse("report:energy_cost", kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
