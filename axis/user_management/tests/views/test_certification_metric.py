"""certification_metric.py: """


from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase

__author__ = "Artem Hruzd"
__date__ = "12/24/2019 12:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.home.tests.mixins import CertificationTestMixin


class CertificationMetricControlCenterListViewsTest(CertificationTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_login_required(self):
        url = reverse("user_management:certification_metric:control_center_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])
