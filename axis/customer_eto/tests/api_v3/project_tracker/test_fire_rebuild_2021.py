"""test_fire_rebuild_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "12/6/21 08:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now

from rest_framework import status
from rest_framework.test import APITestCase

from axis.company.models import Company
from axis.home.models import Home
from axis.incentive_payment.models import IncentivePaymentStatus
from ...factories import eto_mocked_soap_responses as mocked_post
from ...program_checks.test_fire_rebuild_2021 import FireRebuild2021ProgramBase
from ....api_v3.serializers.project_tracker.measures import MeasureSerializer
from ....api_v3.serializers.project_tracker.site import (
    SitePropertySerializer,
    SiteTechnologySerializer,
)

from ....api_v3.viewsets import ProjectTrackerXMLViewSet
from ....eep_programs.washington_code_credit import WACCFuelType, FurnaceLocation
from ....enumerations import HeatType
from ....models import FastTrackSubmission

log = logging.getLogger(__name__)


class TestProjectTrackerFireRebuild2021(FireRebuild2021ProgramBase, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestProjectTrackerFireRebuild2021, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()
        cls.home_status.report_eligibility_for_certification()

        cls.project_tracker = FastTrackSubmission.objects.get(home_status_id=cls.home_status.id)
        future = datetime.datetime.now() + datetime.timedelta(days=30)
        cls.install_date = future.strftime("%Y-%m-%d")

        cls.floorplan = cls.home_status.floorplan
        cls.simulation = cls.floorplan.simulation

    def render(self, response):
        response.render()
        return response.content.decode("utf8")

    def test_viewset_calculator_context_data(self):
        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_eto_2021_calculator_context(self.project_tracker)
        self.assertEqual(data["heat_type"], HeatType.ELECTRIC)
        self.assertEqual(data["has_triple_pane_windows"], True)
        self.assertEqual(data["has_rigid_insulation"], True)
        self.assertEqual(data["has_sealed_attic"], True)

    def test_viewset_calculator_context_data_overrides(self):
        self.project_tracker.original_kwh_savings = self.project_tracker.kwh_savings
        self.project_tracker.kwh_savings = 888.88

        self.project_tracker.original_therm_savings = self.project_tracker.therm_savings
        self.project_tracker.therm_savings = 444.44

        self.project_tracker.original_mbtu_savings = self.project_tracker.mbtu_savings
        self.project_tracker.mbtu_savings = 222.222

        self.project_tracker.payment_change_datetime = datetime.datetime.now(datetime.timezone.utc)
        self.project_tracker.save()

        viewset = ProjectTrackerXMLViewSet()
        data = viewset.get_eto_2021_calculator_context(FastTrackSubmission.objects.get())
        self.assertAlmostEqual(float(data["kwh_savings"]), 888.88, places=2)
        self.assertAlmostEqual(float(data["therm_savings"]), 444.44, places=2)
        self.assertAlmostEqual(float(data["mbtu_savings"]), 222.22, places=2)

    def test_triple_pane_windows_measure(self):
        self.floorplan.simulation = None
        self.floorplan.save()

        context = {
            "heat_type": HeatType.ELECTRIC,
            "has_triple_pane_windows": True,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]

        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSFRFRTW")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)

        self.assertEqual(data["Incentive"], "750.00")

    def test_rigid_insulation_measure(self):
        self.floorplan.simulation = None
        self.floorplan.save()

        context = {
            "heat_type": HeatType.GAS,
            "has_rigid_insulation": True,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSFRFREI")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "750.00")

    def test_sealed_attic_measure(self):
        self.floorplan.simulation = None
        self.floorplan.save()

        context = {
            "heat_type": HeatType.GAS,
            "has_sealed_attic": True,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]

        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSFRFRSA")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")  # The actual checklist answer does not
        # include this.
