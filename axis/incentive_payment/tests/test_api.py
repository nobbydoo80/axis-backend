"""test_api.py: Django incentive_payment"""


import logging
import datetime

from django.urls import reverse

import lxml.html
from django_states.exceptions import TransitionCannotStart
from rest_framework.test import APIClient

from axis.core.tests.testcases import ApiV3Tests

from ..models import IncentivePaymentStatus
from .. import strings

__author__ = "Steven Klass"
__date__ = "12/19/13 3:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IncentivePaymentControlCenterApiTest(ApiV3Tests):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        from axis.core.tests.factories import (
            general_super_user_factory,
            general_admin_factory,
            utility_admin_factory,
            provider_admin_factory,
            builder_admin_factory,
        )

        from axis.incentive_payment.tests.factories import (
            basic_pending_builder_incentive_distribution_factory,
            basic_incentive_payment_status_factory,
        )
        from axis.company.models import Company, SponsorPreferences
        from axis.home.models import EEPProgramHomeStatus
        from axis.relationship.models import Relationship

        from axis.geographic.tests.factories import real_city_factory

        city = real_city_factory("Natchez", "MS")
        user = general_super_user_factory(company__city=city)
        general_admin_factory(company=user.company)

        builder_admin = builder_admin_factory(company__city=city)
        utility_admin = utility_admin_factory(company__slug="aps", company__city=city)
        provider_admin = provider_admin_factory(company__city=city)

        assert Company.objects.all().count() == 4, "Company counts"

        Relationship.objects.create_mutual_relationships(
            user.company, builder_admin.company, utility_admin.company, provider_admin.company
        )
        SponsorPreferences.objects.get_or_create(
            sponsor=utility_admin.company, sponsored_company=builder_admin.company
        )
        SponsorPreferences.objects.get_or_create(
            sponsor=utility_admin.company, sponsored_company=provider_admin.company
        )

        start = []
        ipp_payment_requirements = ["pending_requirements"]
        ipp_payment_failed_requirements = ["failed_requirements"]
        ipp_failed_restart = ipp_payment_failed_requirements + ["corrected_requirements"]
        ipp_payment_automatic_requirements = ipp_payment_requirements + [
            "pending_automatic_requirements"
        ]
        payment_pending = ipp_payment_automatic_requirements + ["pending_payment_requirements"]
        complete = payment_pending + ["pending_complete"]

        state_transitions = [
            start,
            ipp_payment_requirements,
            ipp_payment_failed_requirements,
            ipp_failed_restart,
            ipp_payment_automatic_requirements,
            payment_pending,
            complete,
        ]

        for flow in state_transitions:
            kwrgs = {
                "home_status__company": provider_admin.company,
                "home_status__eep_program__owner": utility_admin.company,
                "home_status__home__builder_org": builder_admin.company,
                "home_status__eep_program__builder_incentive_dollar_value": 200,
                "home_status__eep_program__no_close_dates": True,
            }
            ipp_stat = basic_incentive_payment_status_factory(**kwrgs)
            kwrgs.pop("home_status__eep_program__owner")
            kwrgs.pop("home_status__eep_program__builder_incentive_dollar_value")
            kwrgs["home_status__eep_program"] = ipp_stat.home_status.eep_program
            kwrgs["home_status__floorplan"] = ipp_stat.home_status.floorplan
            kwrgs["home_status__company"] = ipp_stat.home_status.company
            kwrgs["owner"] = ipp_stat.home_status.company
            for step in flow:
                ipp_stat.make_transition(step)

        bid = basic_pending_builder_incentive_distribution_factory(
            customer=builder_admin.company,
            company=utility_admin.company,
            rater=provider_admin.company,
        )

        assert Company.objects.all().count() == 4, "Company counts"

        home_stat_ids = bid.ippitem_set.all().values_list("home_status_id", flat=True)
        stats = IncentivePaymentStatus.objects.filter(home_status_id__in=home_stat_ids)
        for stat in stats:
            for step in flow:
                try:
                    stat.make_transition(step)
                except TransitionCannotStart:
                    pass

        assert Company.objects.all().count() == 4, "Company counts"
        assert EEPProgramHomeStatus.objects.all().count() == 8, "Status counts"
        assert IncentivePaymentStatus.objects.all().count() == 8, "Status counts"

        assert IncentivePaymentStatus.objects.filter(state="start").count() == 1, "start"
        assert (
            IncentivePaymentStatus.objects.filter(state="ipp_failed_restart").count() == 1
        ), "ipp_failed_restart"
        assert (
            IncentivePaymentStatus.objects.filter(state="ipp_payment_requirements").count() == 0
        ), "ipp_payment_requirements"
        assert (
            IncentivePaymentStatus.objects.filter(state="ipp_payment_failed_requirements").count()
            == 1
        ), "ipp_payment_failed_requirements"
        assert (
            IncentivePaymentStatus.objects.filter(state="payment_pending").count() == 1
        ), "Pending"
        assert IncentivePaymentStatus.objects.filter(state="complete").count() == 2, "Complete"

    def setUp(self):
        super(IncentivePaymentControlCenterApiTest, self).setUp()
        self.user = self.get_admin_user(company_type="utility")
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

    def test_get_datatable(self):
        datatables = ["pending", "received", "required", "approved", "distribution"]
        url = reverse("apiv2:ipp-datatable", kwargs={"datatable": datatables[0]})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = lxml.html.fromstring(response.data)
        self.assertEqual(html.tag, "table")

    def test_get_datatable_bad_request(self):
        url = reverse("apiv2:ipp-datatable", kwargs={"datatable": "something"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_get_form(self):
        forms = ["pending", "new"]
        url = reverse("apiv2:ipp-form", kwargs={"form": forms[0]})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = lxml.html.fromstring(response.data)
        self.assertEqual(html.tag, "form")

    def test_get_form_bad_request(self):
        forms = ["new", "pending"]
        url = reverse("apiv2:ipp-form", kwargs={"form": "something"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_revert_stats(self):
        url = reverse("apiv2:ipp-form", kwargs={"form": "new"})
        states = ["payment_pending", "ipp_payment_automatic_requirements"]
        stats = IncentivePaymentStatus.objects.filter(state__in=states)
        ids = list(stats.values_list("id", flat=True))
        data = {
            "submit": "revert",
            "annotation": "this is an annotation",
            "stats": ids,
        }

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("success", r.data)

        stats = IncentivePaymentStatus.objects.filter(id__in=ids)
        self.assertGreater(stats.count(), 0)
        for stat in stats:
            self.assertEqual(stat.state, "start")

    def test_fail_revert_stats(self):
        url = reverse("apiv2:ipp-form", kwargs={"form": "new"})
        states = ["payment_pending", "ipp_payment_automatic_requirements", "start"]
        stats = IncentivePaymentStatus.objects.exclude(state__in=states)
        ids = list(stats.values_list("id", flat=True))
        data = {"submit": "revert", "annotation": "This is an annotation", "stats": ids}

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("error", r.data)
        self.assertIn("stats", r.data["error"])

        stats = IncentivePaymentStatus.objects.filter(id__in=ids)
        self.assertGreater(stats.count(), 0)
        for stat in stats:
            self.assertNotEqual(stat.state, "start")

    def test_advance_state(self):
        url = reverse("apiv2:ipp-form", kwargs={"form": "pending"})
        stats = IncentivePaymentStatus.objects.filter(state="start")
        ids = list(stats.values_list("id", flat=True))
        new_state = "ipp_payment_failed_requirements"
        data = {
            "submit": "update",
            "new_state": new_state,
            "annotation": "This is an annotation",
            "stats": ids,
            "progress": 1,
            "number": 2,
        }

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)

        self.assertIn("success", r.data)

        stats = IncentivePaymentStatus.objects.filter(id__in=ids)
        self.assertGreater(stats.count(), 0)
        for stat in stats:
            self.assertEqual(stat.state, new_state)

    def test_fail_advance_state(self):
        url = reverse("apiv2:ipp-form", kwargs={"form": "pending"})
        current_state = "ipp_payment_automatic_requirements"
        new_state = "ipp_payment_requirements"
        stats = IncentivePaymentStatus.objects.filter(state=current_state)

        ids = list(stats.values_list("id", flat=True))
        data = {
            "submit": "update",
            "new_state": new_state,
            "annotation": "This is an annotation",
            "stats": ids,
            "progress": 1,
            "number": 4,
        }

        states = dict(IncentivePaymentStatus.get_state_choices())
        current_state_description = states[current_state]
        new_state_description = states[new_state]

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("info", r.data)
        self.assertIn("message", r.data["info"])
        self.assertEqual(
            r.data["info"]["message"],
            strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                ostate=current_state_description, tstate=new_state_description
            ),
        )

        stats = IncentivePaymentStatus.objects.filter(id__in=ids)
        self.assertGreater(stats.count(), 0)
        for stat in stats:
            self.assertEqual(stat.state, current_state)

    def test_incentive_distribution(self):
        from axis.company.models import Company
        from axis.incentive_payment.models import IncentiveDistribution

        before_count = IncentiveDistribution.objects.count()
        url = reverse("apiv2:ipp-form", kwargs={"form": "new"})
        state = "ipp_payment_automatic_requirements"
        stats = IncentivePaymentStatus.objects.filter(state=state)
        ids = list(stats.values_list("id", flat=True))
        builder = Company.objects.get(company_type="builder")
        data = {
            "submit": "update",
            "customer": builder.id,
            "check_requested_date": datetime.date.today(),
            "comment": "this is a comment",
            "stats": ids,
            "progress": 1,
        }

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("success", r.data)

        after_count = IncentiveDistribution.objects.count()
        self.assertNotEqual(before_count, after_count)

    def test_fail_incentive_distribution(self):
        from axis.company.models import Company
        from axis.incentive_payment.models import IncentiveDistribution

        url = reverse("apiv2:ipp-form", kwargs={"form": "new"})
        builder = Company.objects.get(company_type="builder")
        before_count = IncentiveDistribution.objects.count()
        data = {
            "submit": "update",
            "customer": builder.id,
            "check_requested_date": datetime.date.today(),
            "comment": "this is a comment",
            "stats": [],
            "progress": 1,
        }

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("error", r.data)

        after_count = IncentiveDistribution.objects.count()
        self.assertEqual(before_count, after_count)

    def test_annotate_stats(self):
        url = reverse("apiv2:ipp-form", kwargs={"form": "annotate"})
        stats = IncentivePaymentStatus.objects.all()
        ids = list(stats.values_list("id", flat=True))
        anno = "This is a test annotation"
        data = {"submit": "annotate", "annotation": anno, "stats": ids}

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("success", r.data)

        stats = IncentivePaymentStatus.objects.filter(id__in=ids)
        self.assertGreater(stats.count(), 0)
        for stat in stats:
            for annotation in stat.annotations.all():
                self.assertEqual(annotation.content, anno)

    def test_fail_annotate_stats(self):
        url = reverse("apiv2:ipp-form", kwargs={"form": "annotate"})
        stats = IncentivePaymentStatus.objects.all()
        ids = list(stats.values_list("id", flat=True))
        anno = ""
        data = {"submit": "annotate", "annotation": anno, "stats": ids}

        r = self.client.post(url, data)
        self.assertEqual(r.status_code, 200)
        self.assertIn("error", r.data)
        self.assertIn("annotation", r.data["error"])

        stats = IncentivePaymentStatus.objects.filter(id__in=ids)
        self.assertGreater(stats.count(), 0)
        for stat in stats:
            for annotation in stat.annotations.all():
                self.assertNotIn(annotation.content, [None, "", "undefined"])
