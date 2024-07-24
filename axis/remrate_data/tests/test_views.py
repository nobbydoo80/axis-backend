"""tests.py: Django remrate_data"""


import json
import logging

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from ..models import Simulation

__author__ = "Steven Klass"
__date__ = "2/17/13 1:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RemRateDataViewTests(AxisTestCase):
    """Test out the remrate user creation and deletion"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        from axis.home.tests.factories import (
            certified_custom_home_with_basic_eep_factory_and_remrate,
        )
        from .factories import simulation_factory

        stat = certified_custom_home_with_basic_eep_factory_and_remrate(
            eep_program__no_close_dates=True
        )
        simulation_factory(company=stat.company, remrate_user=stat.company.remrate_user_ids.get())
        simulation_factory(company__name="unrelated__rater")

        assert stat.state == "complete", "We aren't done.."
        assert stat.certification_date != None, "We aren't done.. (Cert Date)"
        assert stat.floorplan.remrate_target, "No RemRate"

    def test_login_required(self):
        simulation = Simulation.objects.first()

        url = reverse("floorplan:input:remrate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("floorplan:input:remrate", kwargs={"pk": simulation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("remrate_data:delete", kwargs={"pk": simulation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_user_has_permissions(self):
        """Test that we can login and see communities"""

        user = self.get_admin_user(company_type=["rater"])
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        for app in ["building", "simulation"]:
            # Add does not come from here - it only comes from remrate
            self.assertFalse(user.has_perm("remrate_data.add_{}".format(app)))
            self.assertTrue(user.has_perm("remrate_data.view_{}".format(app)))
            self.assertTrue(user.has_perm("remrate_data.change_{}".format(app)))
            self.assertTrue(user.has_perm("remrate_data.delete_{}".format(app)))

        simulation = Simulation.objects.filter_by_user(user, floorplan__isnull=True).first()

        url = reverse("floorplan:input:remrate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("floorplan:input:remrate", kwargs={"pk": simulation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(simulation.can_be_deleted(user))
        self.assertTrue(user.is_company_admin)
        self.assertTrue(user.company == simulation.company)

        url = reverse("remrate_data:delete", kwargs={"pk": simulation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        """Test list view for communities"""
        user = self.get_admin_user(company_type=["rater", "provider"])
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("floorplan:input:remrate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("floorplan:input:remrate"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)

        expected = Simulation.objects.filter_by_company(user.company)
        self.assertGreater(expected.count(), 0)
        self.assertGreater(Simulation.objects.all().count(), expected.count())
        match_ids = []
        data = json.loads(response.content)["data"]
        for item in data:
            match_ids.append(int(item.get("DT_RowId")))
        self.assertEqual(set(expected.values_list("id", flat=True)), set(match_ids))

    def test_view(self):
        """Test the viewing of remrate data"""
        user = self.get_admin_user(company_type=["rater", "provider"])
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        simulation = Simulation.objects.filter_by_company(user.company).all()[0]
        response = self.client.get(simulation.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object"].version)

    def test_delete_ipp_view(self):
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        user = self.get_admin_user(company_type=["rater"])
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        simulations = Simulation.objects.filter_by_company(user.company)
        simulations_initial = simulations.count()

        simulation = simulations.get(floorplan__homestatuses__certification_date__isnull=False)
        url = reverse("remrate_data:delete", kwargs={"pk": simulation.id})

        # Verify Simulation.can_be_deleted() is blocking
        self.assertEqual(simulation.can_be_deleted(user), False)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        stat = simulation.floorplan.homestatuses.all()[0]

        # Now add an ipp with a status that would allow deletion
        ipp_kwargs = {"home_status": stat}
        ipp = basic_incentive_payment_status_factory(**ipp_kwargs)
        self.assertEqual(ipp.state, "start")
        self.assertEqual(simulation.can_be_deleted(user), True)

        # Now switch the state and assert deletion is now blocked
        ipp.state = "payment_pending"
        ipp.save()
        self.assertEqual(simulation.can_be_deleted(user), False)

    def test_delete_view(self):
        """Test delete a Remrate"""
        # user = self.get_admin_user(company_type=['rater', 'provider'])
        user = self.get_admin_user(company_type=["rater"])
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        simulations = Simulation.objects.filter_by_company(user.company)
        simulations_initial = simulations.count()

        simulation = simulations.get(floorplan__homestatuses__certification_date__isnull=False)
        url = reverse("remrate_data:delete", kwargs={"pk": simulation.id})

        # Verify Simulation.can_be_deleted() is blocking
        self.assertEqual(simulation.can_be_deleted(user), False)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        # Verify IPP status is not there to block deletion
        for state in simulation.floorplan.homestatuses.values_list(
            "incentivepaymentstatus", flat=True
        ):
            self.assertEqual(None, state)

        # Now get one that can be deleted
        simulation = simulations.get(
            floorplan__homestatuses__certification_date__isnull=True,
            company=user.company,
        )
        self.assertEqual(simulation.can_be_deleted(user), True)

        url = reverse("remrate_data:delete", kwargs={"pk": simulation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url)
        self.assertRedirects(response, reverse("floorplan:input:remrate"))

        simulations = Simulation.objects.filter_by_company(user.company)
        self.assertEqual(simulations_initial - 1, simulations.count())
