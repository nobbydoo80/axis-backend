"""test_views.py: """

__author__ = "Artem Hruzd"
__date__ = "12/22/2020 14:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.core.tests.utils import create_test_image
from axis.home.models import EEPProgramHomeStatus
from django.core.files.uploadedfile import SimpleUploadedFile
from axis.home.tests.mixins import HomeViewTestsMixins


class TestCustomerWSUViews(HomeViewTestsMixins, ApiV3Tests):
    client_class = AxisClient

    def test_hers_brochure_download_view(self):
        user = self.get_admin_user(company_type=["provider"], only_related=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home_status = EEPProgramHomeStatus.objects.filter_by_company(user.company).first()

        builder_organization = home_status.home.get_builder()
        builder_organization.logo = SimpleUploadedFile("test.png", create_test_image().read())
        builder_organization.save()

        url = reverse("customer_wsu:hers_brochure", kwargs={"pk": home_status.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
