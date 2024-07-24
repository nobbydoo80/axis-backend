"""test_standard_protocol_api.py: Django NEEA Standard Protocol API Tests"""

import logging

from django.urls import reverse
from rest_framework import status

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from .mixins import CustomerNEEABaseTestMixin

__author__ = "Steven K"
__date__ = "07/18/2019 12:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from ...company.models import Company

log = logging.getLogger(__name__)


class NEEACalculatorV2ApiTests(CustomerNEEABaseTestMixin, AxisTestCase):
    """Test out the standard protocol API endpoint"""

    client_class = AxisClient

    def setUp(self):
        """Get the setup"""

        super(NEEACalculatorV2ApiTests, self).setUp()
        self.user = self.get_admin_user(company_type="rater")
        msg = "User %s [pk=%s] is not allowed to login"
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg=msg % (self.user.username, self.user.pk),
        )
        self.base_url = reverse("neea_calculator_v2")
        self.download_url = reverse("neea_calculator_download_v2")

    def _get_core_kwargs(self):
        from axis.geographic.models import County

        return {
            "county": County.objects.filter(pnwzone__isnull=False).first().pk,
            "conditioned_area": 2501,
            "gas_utility": Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE, gas_provider=True
            )
            .first()
            .pk,
            "electric_utility": Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE, gas_provider=False
            )
            .first()
            .pk,
            "heating_fuel": "electric",
            "primary_heating_type": "Heat Pump",
            "heating_system_config": "central",
            "smart_thermostat_installed": True,
            "code_data_heating_therms": 100,
            "code_data_heating_kwh": 100,
            "code_data_cooling_kwh": 100,
            "code_data_total_consumption_kwh": 450,
            "code_data_total_consumption_therms": 120,
            "improved_data_heating_therms": 80,
            "improved_data_heating_kwh": 90,
            "improved_data_cooling_kwh": 90,
            "improved_data_total_consumption_kwh": 350,
            "improved_data_total_consumption_therms": 104,
            "water_heater_tier": "gas_ef_gte_0p7",
            "qty_shower_head_1p5": 2,
            "qty_shower_head_1p75": 1,
            "cfl_installed": 11,
            "led_installed": 12,
            "total_installed_lamps": 31,
            "estar_dishwasher_installed": False,
            "estar_front_load_clothes_washer_installed": False,
            "clothes_dryer_tier": "tier3",
            "certified_earth_advantage": "Net Zero Ready",
        }

    def test_access_ok(self):
        """Verify Access is allows for non raters / providers and neea"""
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
        neea_user = self.user_model.objects.get(company__slug="neea", is_company_admin=True)
        msg = "User %s [pk=%s] is not allowed to login"
        self.assertTrue(
            self.client.login(username=neea_user.username, password="password"),
            msg=msg % (neea_user.username, neea_user.pk),
        )
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_bad(self):
        """Verify Access is prevented for non raters / providers"""
        for company_type in ["hvac", "builder"]:
            self.client.logout()
            user = self.get_admin_user(company_type=company_type)
            msg = "User %s [pk=%s] is not allowed to login"
            self.assertTrue(
                self.client.login(username=user.username, password="password"),
                msg=msg % (user.username, user.pk),
            )

            response = self.client.get(self.base_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_good(self):
        """Verify that for a good post it works."""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(self.client.login(username=user.username, password="password"))
        response = self.client.post(self.base_url, self._get_core_kwargs())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.context.keys())
        self.assertIn("hot_water_report", response.context.keys())
        self.assertIn("lighting_report", response.context.keys())
        self.assertIn("appliance_report", response.context.keys())
        self.assertIn("thermostat_report", response.context.keys())
        self.assertIn("shower_head_report", response.context.keys())
        self.assertIn("heating_cooling_report", response.context.keys())
        self.assertIn("incentive_report", response.context.keys())
        self.assertIn("total_report", response.context.keys())

    def test_download_report(self):
        """Verify that we can download the report if needed"""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(self.client.login(username=user.username, password="password"))
        response = self.client.post(self.download_url, self._get_core_kwargs())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NEEACalculatorV3ApiTests(NEEACalculatorV2ApiTests):
    """Test out the standard protocol API endpoint"""

    client_class = AxisClient

    def setUp(self):
        """Get the setup"""
        super(NEEACalculatorV3ApiTests, self).setUp()
        self.base_url = reverse("neea_calculator_v3")
        self.download_url = reverse("neea_calculator_download_v3")

    def _get_core_kwargs(self):
        from axis.geographic.models import County

        return {
            "county": County.objects.first().pk,
            "conditioned_area": 2342,
            "electric_utility": Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE, gas_provider=False
            )
            .first()
            .pk,
            "gas_utility": Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE, gas_provider=True
            )
            .first()
            .pk,
            "heating_fuel": "electric",
            "primary_heating_type": "Propane Oil or Wood",
            "heating_system_config": "central",
            "smart_thermostat_installed": True,
            "code_data_heating_kwh": 7630.0,
            "code_data_heating_therms": 8.0,
            "code_data_cooling_kwh": 570.0,
            "code_data_total_consumption_kwh": 8500.0,
            "code_data_total_consumption_therms": 9.0,
            "improved_data_heating_kwh": 7272.0,
            "improved_data_heating_therms": 4.0,
            "improved_data_cooling_kwh": 560.0,
            "improved_data_total_consumption_kwh": 8000.0,
            "improved_data_total_consumption_therms": 5.0,
            "water_heater_tier": "tier3",
            "estar_std_refrigerators_installed": "refrigerator_other_freezer",
            "estar_dishwasher_installed": True,
            "estar_front_load_clothes_washer_installed": "washer_side_load",
            "clothes_dryer_fuel": "natural_gas",
            "clothes_dryer_tier": "",
            "certified_earth_advantage": "",
        }

    def test_post_good(self):
        """Verify that for a good post it works."""
        response = self.client.post(self.base_url, self._get_core_kwargs())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("result", response.context.keys())
        self.assertIn("hot_water_report", response.context.keys())
        self.assertIn("appliance_report", response.context.keys())
        self.assertIn("thermostat_report", response.context.keys())
        self.assertIn("heating_cooling_report", response.context.keys())
        self.assertIn("incentive_report", response.context.keys())
        self.assertIn("total_report", response.context.keys())
        self.assertNotIn("shower_head_report", response.context.keys())
        self.assertNotIn("lighting_report", response.context.keys())

    def test_download_report(self):
        """Verify that we can download the report if needed"""
        response = self.client.post(self.download_url, self._get_core_kwargs())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
