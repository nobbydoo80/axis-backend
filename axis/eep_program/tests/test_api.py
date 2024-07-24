"""test_utils.py: Django eep_program utils tests"""


__author__ = "Johnny Fang"
__date__ = "24/7/19 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

import logging

from django.urls import reverse

from axis.core.tests.testcases import AxisTestCase
from axis.core.tests.client import AxisClient
from django.contrib.auth import get_user_model
from axis.eep_program.models import EEPProgram
from axis.eep_program.strings import NEEA_ENERGY_STAR_V3_PERFORMANCE_PROGRAM_NOTE
from axis.eep_program.tests.mixins import EEPProgramManagerTestMixin, EEPProgramHomeStatusTestMixin

log = logging.getLogger(__name__)

User = get_user_model()


class EEPProgramViewSetTests(EEPProgramManagerTestMixin, AxisTestCase):
    """Test for api.EEPProgramViewSet"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        super(EEPProgramViewSetTests, cls).setUpTestData()
        EEPProgramHomeStatusTestMixin().setUpTestData()

    def test_note(self):
        """
        Test for note. programs slug could be either neea-energy-star-v3-performance or
        neea-performance-2015 if so we get the note found in eep_program.strings under program
        specific notes
        """
        user = self.nonadmin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        first = EEPProgram.objects.first()
        EEPProgram.objects.filter(name=first.name).update(slug="neea-energy-star-v3-performance")
        program = EEPProgram.objects.get(slug="neea-energy-star-v3-performance")

        url = reverse("apiv2:eep_program-note", kwargs={"pk": program.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, NEEA_ENERGY_STAR_V3_PERFORMANCE_PROGRAM_NOTE)

    # test builder_program_metrics
    def test_builder_program_metrics(self):
        """
        Test for builder_program_metrics, we should get back a dictionary with these keys
        ['sums', 'data', 'controls', 'choices']
        """
        user = User.objects.get(company__name="EEP3")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        url = reverse("apiv2:eep_program-builder-program-metrics")
        data = {"filter_type": "certification_date"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            sorted(["sums", "data", "controls", "choices"]), sorted(response.data.keys())
        )
