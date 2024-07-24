"""eto_2019.py - Axis"""

__author__ = "Steven K"
__date__ = "8/26/21 10:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from ...program_checks.test_eto_2019 import ETO2019ProgramTestMixin
from ....api_v3.viewsets import ProjectTrackerXMLViewSet
from ....models import FastTrackSubmission


log = logging.getLogger(__name__)


class TestProjectTrackerETO2019(ETO2019ProgramTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestProjectTrackerETO2019, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)

        collection_mixin = CollectionRequestMixin()
        collection_mixin.add_collected_input(
            value="Gas Furnace",
            measure_id="primary-heating-equipment-type",
            home_status=cls.home_status,
        )

        cls.project_tracker = FastTrackSubmission.objects.create(
            home_status=cls.home_status,
            builder_incentive=125.69,
            rater_incentive=225.21,
        )

    def render(self, response):
        response.render()
        return response.content.decode("utf8")

    def test_viewset_context_data(self):
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_legacy_calculator_context(self.project_tracker)

        # for k, v in data.items():
        #     if isinstance(v, str):
        #         print(f"self.assertEqual(data[{k!r}], {v!r})")
        #     else:
        #         print(f"self.assertEqual(round(data[{k!r}], 2), round({round(v, 3)}, 2))")

        self.assertEqual(round(data["annual_cost_electric"], 2), round(1200.0, 2))
        self.assertEqual(round(data["annual_cost_gas"], 2), round(250.0, 2))
        self.assertEqual(round(data["carbon_score"], 2), round(2.176, 2))
        self.assertEqual(round(data["code_carbon_score"], 2), round(2.755, 2))
        self.assertEqual(round(data["code_carbon_similar"], 2), round(9.973, 2))
        self.assertEqual(data["eto_path"], "Pathway 2")
        self.assertEqual(data["home_config"], "Gas Heat - Ele DHW")
        self.assertEqual(round(data["code_eps_score"], 2), round(25.363, 2))
        self.assertEqual(round(data["eps_similar"], 2), round(111.677, 2))
        self.assertEqual(round(data["total_kwh"], 2), round(2920.0, 2))
        self.assertEqual(round(data["total_therms"], 2), round(100.0, 2))
        self.assertEqual(round(data["estimated_annual_cost"], 2), round(1450.0, 2))
        self.assertEqual(round(data["eps_score"], 2), round(20.036, 2))
        self.assertEqual(round(data["estimated_monthly_cost"], 2), round(120.833, 2))
        self.assertEqual(round(data["percentage_improvement"], 2), round(20.0, 2))

    def test_xml_basic(self):
        url = reverse_lazy("api_v3:project_tracker-xml", kwargs={"pk": self.home_status.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        #
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
