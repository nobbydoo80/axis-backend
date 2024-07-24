"""payment_update.py - Axis"""

__author__ = "Steven K"
__date__ = "10/26/21 12:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from decimal import Decimal

from django.contrib.auth.models import Permission
from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.models import FastTrackSubmission
from axis.eep_program.models import EEPProgram

log = logging.getLogger(__name__)


class PaymentUpdateViewTests(AxisTestCase):
    client_class = AxisClient

    @classmethod
    def setUpClass(cls):
        super(PaymentUpdateViewTests, cls).setUpClass()
        from axis.home.tests.factories import certified_home_with_basic_eep_factory

        home_status = certified_home_with_basic_eep_factory()
        FastTrackSubmission.objects.create(
            home_status=home_status,
            builder_incentive=1000,
            builder_gas_incentive=200,
            builder_electric_incentive=800,
            rater_incentive=500,
            rater_gas_incentive=100,
            rater_electric_incentive=400,
        )

    def setUp(self, **kwargs):
        super(PaymentUpdateViewTests, self).setUp(**kwargs)
        from axis.home.models import EEPProgramHomeStatus

        self.home_status = EEPProgramHomeStatus.objects.get()
        self.fasttrack = FastTrackSubmission.objects.get()
        self.payment_url = reverse(
            "eto:payment_adjust", kwargs={"home_status": self.home_status.id}
        )
        self.user = self.user_model.objects.get()
        self.update_perm = Permission.objects.get(codename="change_fasttracksubmission")
        self.user.user_permissions.add(self.update_perm)
        company = self.user.company
        company.slug = "peci"
        company.save()

    def test_login_required(self):
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.payment_url, response["Location"], msg=self.payment_url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_permission_required(self):
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

        self.assertTrue(self.user.has_perm("customer_eto.change_fasttracksubmission"))
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)

        self.user.user_permissions.remove(self.update_perm)
        self.user.groups.clear()

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 403)

    def test_update_builder_payment_info(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {
            "revised_builder_electric_incentive": 2000,
            "revised_builder_gas_incentive": 3000,
            "revised_rater_electric_incentive": "",
            "revised_rater_gas_incentive": "",
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_builder_electric_incentive, 800)
        self.assertEqual(update.original_builder_gas_incentive, 200)
        self.assertEqual(update.original_builder_incentive, 1000)

        self.assertEqual(
            update.builder_electric_incentive, data["revised_builder_electric_incentive"]
        )
        self.assertEqual(update.builder_gas_incentive, data["revised_builder_gas_incentive"])
        self.assertEqual(
            update.builder_incentive,
            data["revised_builder_gas_incentive"] + data["revised_builder_electric_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_update_builder_payment_none_info(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {
            "revised_builder_electric_incentive": 2000,
            "revised_builder_gas_incentive": "",
            "revised_rater_electric_incentive": "",
            "revised_rater_gas_incentive": "",
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_builder_electric_incentive, 800)
        self.assertEqual(update.original_builder_gas_incentive, None)
        self.assertEqual(update.original_builder_incentive, 1000)

        self.assertEqual(
            update.builder_electric_incentive, data["revised_builder_electric_incentive"]
        )
        self.assertEqual(update.builder_gas_incentive, 200)
        self.assertEqual(
            update.builder_incentive,
            update.builder_gas_incentive + data["revised_builder_electric_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

        data["revised_builder_gas_incentive"] = 999
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_builder_electric_incentive, 800)
        self.assertEqual(update.original_builder_gas_incentive, 200)
        self.assertEqual(update.original_builder_incentive, 1000)

        self.assertEqual(
            update.builder_electric_incentive, data["revised_builder_electric_incentive"]
        )
        self.assertEqual(update.builder_gas_incentive, data["revised_builder_gas_incentive"])
        self.assertEqual(
            update.builder_incentive,
            data["revised_builder_gas_incentive"] + data["revised_builder_electric_incentive"],
        )

    def test_update_rater_payment_info(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {
            "revised_builder_electric_incentive": "",
            "revised_builder_gas_incentive": "",
            "revised_rater_electric_incentive": 150,
            "revised_rater_gas_incentive": 250,
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_rater_incentive, 500)
        self.assertEqual(update.original_rater_gas_incentive, 100)
        self.assertEqual(update.original_rater_electric_incentive, 400)

        self.assertEqual(update.rater_electric_incentive, data["revised_rater_electric_incentive"])
        self.assertEqual(update.rater_gas_incentive, data["revised_rater_gas_incentive"])
        self.assertEqual(
            update.rater_incentive,
            data["revised_rater_gas_incentive"] + data["revised_rater_electric_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_update_rater_payment_none_info(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {
            "revised_builder_electric_incentive": "",
            "revised_builder_gas_incentive": "",
            "revised_rater_electric_incentive": "",
            "revised_rater_gas_incentive": 190,
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_rater_incentive, 500)
        self.assertEqual(update.original_rater_gas_incentive, 100)
        self.assertEqual(update.original_rater_electric_incentive, None)

        self.assertEqual(update.rater_electric_incentive, 400)
        self.assertEqual(update.rater_gas_incentive, data["revised_rater_gas_incentive"])
        self.assertEqual(
            update.rater_incentive,
            update.rater_electric_incentive + data["revised_rater_gas_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

        data["revised_rater_electric_incentive"] = 322
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_rater_incentive, 500)
        self.assertEqual(update.original_rater_gas_incentive, 100)
        self.assertEqual(update.original_rater_electric_incentive, 400)

        self.assertEqual(update.rater_electric_incentive, data["revised_rater_electric_incentive"])
        self.assertEqual(update.rater_gas_incentive, data["revised_rater_gas_incentive"])
        self.assertEqual(
            update.rater_incentive,
            data["revised_rater_gas_incentive"] + data["revised_rater_electric_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_update_net_zero_info(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        eep_program = EEPProgram.objects.get()
        eep_program.slug = "eto-2020"
        eep_program.save()

        data = {
            "revised_builder_electric_incentive": 2000,
            "revised_builder_gas_incentive": 3000,
            "revised_net_zero_eps_incentive": 100,
            "revised_rater_electric_incentive": "",
            "revised_rater_gas_incentive": "",
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_builder_electric_incentive, 800)
        self.assertEqual(update.original_builder_gas_incentive, 200)
        self.assertEqual(update.original_net_zero_eps_incentive, 0.0)
        self.assertEqual(update.original_builder_incentive, 1000)

        self.assertEqual(
            update.builder_electric_incentive, data["revised_builder_electric_incentive"]
        )
        self.assertEqual(update.builder_gas_incentive, data["revised_builder_gas_incentive"])
        self.assertEqual(update.net_zero_eps_incentive, data["revised_net_zero_eps_incentive"])

        self.assertEqual(
            update.builder_incentive,
            data["revised_builder_gas_incentive"]
            + data["revised_builder_electric_incentive"]
            + data["revised_net_zero_eps_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_update_energy_smart_homes_eps_incentive(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        eep_program = EEPProgram.objects.get()
        eep_program.slug = "eto-2020"
        eep_program.save()

        baseline = FastTrackSubmission.objects.get()
        baseline.energy_smart_homes_eps_incentive = 500
        baseline.save()

        data = {
            "revised_energy_smart_homes_eps_incentive": 200,
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_energy_smart_homes_eps_incentive, 500.0)

        self.assertEqual(
            update.energy_smart_homes_eps_incentive,
            data["revised_energy_smart_homes_eps_incentive"],
        )

        self.assertEqual(
            update.builder_incentive,
            update.builder_gas_incentive
            + update.builder_electric_incentive
            + data["revised_energy_smart_homes_eps_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_update_net_zero_complete_incentive(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        eep_program = EEPProgram.objects.get()
        eep_program.slug = "eto-2020"
        eep_program.save()

        baseline = FastTrackSubmission.objects.get()
        baseline.energy_smart_homes_eps_incentive = 500
        baseline.save()

        data = {
            "revised_builder_electric_incentive": 2000,
            "revised_builder_gas_incentive": 3000,
            "revised_net_zero_eps_incentive": 100,
            "revised_energy_smart_homes_eps_incentive": 125,
            "revised_net_zero_solar_incentive": 200,
            "revised_energy_smart_homes_solar_incentive": 220,
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_net_zero_eps_incentive, 0.0)
        self.assertEqual(update.original_energy_smart_homes_eps_incentive, 500.0)
        self.assertEqual(update.original_net_zero_solar_incentive, 0.0)
        self.assertEqual(update.original_energy_smart_homes_solar_incentive, 0.0)

        self.assertEqual(
            update.net_zero_eps_incentive,
            data["revised_net_zero_eps_incentive"],
        )
        self.assertEqual(
            update.energy_smart_homes_eps_incentive,
            data["revised_energy_smart_homes_eps_incentive"],
        )
        self.assertEqual(
            update.net_zero_solar_incentive,
            data["revised_net_zero_solar_incentive"],
        )
        self.assertEqual(
            update.energy_smart_homes_solar_incentive,
            data["revised_energy_smart_homes_solar_incentive"],
        )

        self.assertEqual(
            update.builder_incentive,
            update.builder_gas_incentive
            + update.builder_electric_incentive
            + data["revised_net_zero_eps_incentive"]
            + data["revised_energy_smart_homes_eps_incentive"]
            + data["revised_net_zero_solar_incentive"]
            + data["revised_energy_smart_homes_solar_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_update_energy_smart_homes_solar_incentive(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        eep_program = EEPProgram.objects.get()
        eep_program.slug = "eto-2020"
        eep_program.save()

        baseline = FastTrackSubmission.objects.get()
        baseline.energy_smart_homes_solar_incentive = 500
        baseline.save()

        data = {
            "revised_energy_smart_homes_solar_incentive": 900,
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.energy_smart_homes_solar_incentive, 900.0)

        self.assertEqual(
            update.energy_smart_homes_solar_incentive,
            data["revised_energy_smart_homes_solar_incentive"],
        )

        self.assertEqual(
            update.builder_incentive,
            update.builder_gas_incentive
            + update.builder_electric_incentive
            + update.energy_smart_homes_eps_incentive
            + data["revised_energy_smart_homes_solar_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)

    def test_savings(self):
        user = self.user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        eep_program = EEPProgram.objects.get()
        eep_program.slug = "eto-2020"
        eep_program.save()

        baseline = FastTrackSubmission.objects.get()
        original_therm = baseline.therm_savings = 12345678.12345678
        original_kwh = baseline.kwh_savings = 23456789.23456789
        original_mbtu = baseline.mbtu_savings = 34567890.34567890
        baseline.save()

        data = {
            "revised_therm_savings": 87654321.87654321,
            "revised_kwh_savings": 98765432.98765432,
            "revised_mbtu_savings": 99999999.99999999,
            "payment_revision_comment": "Something",
        }

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()
        self.assertEqual(update.original_therm_savings, original_therm)
        self.assertEqual(update.original_kwh_savings, original_kwh)
        self.assertEqual(update.original_mbtu_savings, original_mbtu)

        self.assertEqual(
            update.therm_savings,
            data["revised_therm_savings"],
        )
        self.assertEqual(
            update.kwh_savings,
            data["revised_kwh_savings"],
        )
        self.assertEqual(
            update.mbtu_savings,
            data["revised_mbtu_savings"],
        )

    def test_found_error(self):
        """This was an error found in testing.  I did a model_to_dict and will use those values as
        the basis."""

        user = self.user

        data = {
            "project_id": "",
            "solar_project_id": None,
            "eps_score": 32,
            "eps_score_built_to_code_score": 49,
            "percent_improvement": 0.31,
            "percent_improvement_kwh": 0.31,
            "percent_improvement_therms": 0.0,
            "builder_incentive": Decimal("3143.00"),
            "rater_incentive": Decimal("911.00"),
            "carbon_score": 3.4,
            "carbon_built_to_code_score": 5.0,
            "estimated_annual_energy_costs": Decimal("683.41"),
            "estimated_monthly_energy_costs": Decimal("56.95"),
            "similar_size_eps_score": 109,
            "similar_size_carbon_score": 9.4,
            "builder_gas_incentive": Decimal("0.00"),
            "builder_electric_incentive": Decimal("3143.00"),
            "rater_gas_incentive": Decimal("0.00"),
            "rater_electric_incentive": Decimal("911.00"),
            "therm_savings": 0.0,
            "kwh_savings": 2900.32,
            "mbtu_savings": 9.90,
            "eps_calculator_version": datetime.date(2020, 4, 20),
            "original_builder_electric_incentive": None,
            "original_builder_gas_incentive": None,
            "original_builder_incentive": Decimal("3143.00"),
            "original_rater_electric_incentive": None,
            "original_rater_gas_incentive": None,
            "original_rater_incentive": None,
            "payment_change_user": self.user,
            "payment_change_datetime": datetime.datetime(
                2021, 6, 10, 21, 42, 8, 956121, tzinfo=datetime.timezone.utc
            ),
            "payment_revision_comment": "test",
            "net_zero_eps_incentive": Decimal("0.00"),
            "energy_smart_homes_eps_incentive": Decimal("0.00"),
            "net_zero_solar_incentive": Decimal("0.00"),
            "energy_smart_homes_solar_incentive": Decimal("0.00"),
            "original_net_zero_eps_incentive": Decimal("0.00"),
            "original_energy_smart_homes_eps_incentive": Decimal("0.00"),
            "original_net_zero_solar_incentive": Decimal("0.00"),
            "original_energy_smart_homes_solar_incentive": Decimal("0.00"),
        }

        eep_program = EEPProgram.objects.get()
        eep_program.slug = "eto-2020"
        eep_program.save()

        baseline = FastTrackSubmission.objects.get()
        for k, v in data.items():
            setattr(baseline, k, v)
        baseline.save()

        baseline = FastTrackSubmission.objects.get()
        for k, v in data.items():
            self.assertEqual(getattr(baseline, k), v)

        # Now we are even - let's update something
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {
            "revised_net_zero_eps_incentive": 100,
            "revised_energy_smart_homes_eps_incentive": 125,
            "revised_net_zero_solar_incentive": 200,
            "revised_energy_smart_homes_solar_incentive": 220,
            "payment_revision_comment": "Something",
        }

        response = self.client.post(self.payment_url, data)
        self.assertRedirects(response, self.home_status.get_absolute_url())

        update = FastTrackSubmission.objects.get()

        self.assertTrue(update.is_locked())  # We need to ensure that this data is locked.

        self.assertEqual(update.original_net_zero_eps_incentive, 0.0)
        self.assertEqual(update.original_energy_smart_homes_eps_incentive, 0.0)
        self.assertEqual(update.original_net_zero_solar_incentive, 0.0)
        self.assertEqual(update.original_energy_smart_homes_solar_incentive, 0.0)

        self.assertEqual(
            update.net_zero_eps_incentive,
            data["revised_net_zero_eps_incentive"],
        )
        self.assertEqual(
            update.energy_smart_homes_eps_incentive,
            data["revised_energy_smart_homes_eps_incentive"],
        )
        self.assertEqual(
            update.net_zero_solar_incentive,
            data["revised_net_zero_solar_incentive"],
        )
        self.assertEqual(
            update.energy_smart_homes_solar_incentive,
            data["revised_energy_smart_homes_solar_incentive"],
        )

        self.assertEqual(
            update.builder_incentive,
            update.builder_gas_incentive
            + update.builder_electric_incentive
            + data["revised_net_zero_eps_incentive"]
            + data["revised_energy_smart_homes_eps_incentive"]
            + data["revised_net_zero_solar_incentive"]
            + data["revised_energy_smart_homes_solar_incentive"],
        )

        self.assertEqual(update.payment_change_user, self.user)
        self.assertIsNotNone(update.payment_change_datetime)
