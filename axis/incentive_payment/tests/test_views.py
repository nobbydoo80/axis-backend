"""tests.py: Django incentive_payment"""

__author__ = "Autumn Valenta"
__date__ = "4/3/13 2:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import logging
import datetime
from bs4 import BeautifulSoup

from django.urls import reverse
from django_states.exceptions import TransitionCannotStart

from axis.core.tests.client import BaseAxisClient
from axis.core.tests.testcases import ApiV3Tests
from axis.incentive_payment.models import IncentivePaymentStatus
from ..models import IncentiveDistribution

log = logging.getLogger(__name__)


class IncentiveDistributionViewsTestCase(ApiV3Tests):
    client_class = BaseAxisClient
    app_urls = {
        "noargs": [
            "incentive_payment:list",
            "incentive_payment:pending",
            "incentive_payment:add",
            "incentive_payment:control_center",
            "incentive_payment:datatable_pending",
            "incentive_payment:datatable_rejected",
            "incentive_payment:pending_form",
            "incentive_payment:new_form",
        ],
        "pk=1": [
            "incentive_payment:view",
            "incentive_payment:update",
            "incentive_payment:delete",
            "incentive_payment:ipp_items",
            "incentive_payment:print",
            "incentive_payment:print_detail",
        ],
    }

    perms = [
        "incentive_payment.view_incentivedistribution",
        "incentive_payment.change_incentivedistribution",
        "incentive_payment.add_incentivedistribution",
        "incentive_payment.delete_incentivedistribution",
        "incentive_payment.view_ippitem",
        "incentive_payment.change_ippitem",
        "incentive_payment.add_ippitem",
        "incentive_payment.delete_ippitem",
    ]

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
        from axis.company.models import Company
        from axis.home.models import EEPProgramHomeStatus
        from axis.relationship.models import Relationship

        from axis.geographic.tests.factories import real_city_factory

        city = real_city_factory("Crete", "NE")
        user = general_super_user_factory(company__city=city)
        general_admin_factory(company=user.company)
        builder_admin = builder_admin_factory(company__city=city)
        utility_admin = utility_admin_factory(company__city=city, company__slug="aps")
        provider_admin = provider_admin_factory(company__city=city)

        Relationship.objects.create_mutual_relationships(
            user.company, builder_admin.company, utility_admin.company, provider_admin.company
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

        # This one can be deleted
        distribution = basic_pending_builder_incentive_distribution_factory(
            customer=builder_admin.company,
            company=utility_admin.company,
            rater=provider_admin.company,
        )
        distribution.save()
        assert distribution.is_paid == False
        assert IncentiveDistribution.objects.get(id=distribution.id).can_be_deleted(utility_admin)
        # For this distribution to be deletable, the IPPStat needs to be in payment pending
        ipp_stat = IncentivePaymentStatus.objects.get(
            home_status__ippitem__incentive_distribution_id=distribution.id
        )
        ipp_stat.state = "payment_pending"
        ipp_stat.save()

        # This one is done..
        distribution = basic_pending_builder_incentive_distribution_factory(
            customer=builder_admin.company,
            company=utility_admin.company,
            rater=provider_admin.company,
        )
        distribution.paid_date = datetime.datetime.today() - datetime.timedelta(days=-1)
        distribution.check_number = "3929292"
        distribution.is_paid = True
        distribution.save()
        home_stat_ids = distribution.ippitem_set.all().values_list("home_status_id", flat=True)
        stats = IncentivePaymentStatus.objects.filter(home_status_id__in=home_stat_ids)
        for stat in stats:
            for step in flow:
                try:
                    stat.make_transition(step, user=utility_admin)
                except TransitionCannotStart:
                    pass
        assert not (
            IncentiveDistribution.objects.get(id=distribution.id).can_be_deleted(utility_admin)
        )

        assert Company.objects.all().count() == 4, "Company counts"
        assert EEPProgramHomeStatus.objects.all().count() == 9, "Status counts"
        assert IncentivePaymentStatus.objects.all().count() == 9, "Status counts"
        assert IncentiveDistribution.objects.all().count() == 2, "Distribuions"

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
            IncentivePaymentStatus.objects.filter(state="payment_pending").count() == 2
        ), "Pending"
        assert IncentivePaymentStatus.objects.filter(state="complete").count() == 2, "Complete"

    def setUp(self):
        self.user = self.user_model.objects.order_by("id").first()
        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

    def test_company_user_has_permissions(self):
        # FIXME: I feel like this is the wrong place to test permissions. Especially since we're
        #  adding them, then checking them...
        perms_user = self.user_model.objects.get(
            is_superuser=False, is_company_admin=True, company__company_type="utility"
        )

        # for model, ct in ContentType.objects.get_for_models(IncentiveDistribution, IPPItem).items():
        #     perms_user.user_permissions.add(*Permission.objects.filter(content_type=ct))

        for perm in self.perms:
            self.assertEqual(perms_user.has_perm(perm), True)

    def test_login_required(self):
        self.client.logout()

        login_url = reverse("auth:login")
        redirect_format = "{url}?next={from_url}"
        existing_id = IncentiveDistribution.objects.first().id

        for url in self.app_urls["noargs"]:
            url = reverse(url)
            response = self.client.get(url)
            self.assertRedirects(response, redirect_format.format(url=login_url, from_url=url))

        for url in self.app_urls["pk=1"]:
            url = reverse(url, kwargs={"pk": existing_id})
            response = self.client.get(url)
            self.assertRedirects(response, redirect_format.format(url=login_url, from_url=url))

        self.assertTrue(
            self.client.login(username=self.user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (self.user.username, self.user.pk),
        )

        for url in self.app_urls["noargs"]:
            url = reverse(url)
            try:
                response = self.client.get(url)
            except:
                log.error("Issue calling: %r", url)
                raise
            # if response.status_code != 200:
            #     print(response)
            self.assertEqual(response.status_code, 200)

        for url in self.app_urls["pk=1"]:
            url = reverse(url, kwargs={"pk": existing_id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        """Verifies ajax response returns slug[:8] and ids of first-page items."""
        url = reverse("incentive_payment:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get_json(url, ajax=True)
        self.assertEqual(response.status_code, 200)

        expected = IncentiveDistribution.objects.filter_by_user(self.user)
        self.assertGreater(expected.count(), 0)

        expected_ids = set(expected.values_list("id", flat=True))
        expected_slugs = set([x[:8] for x in expected.values_list("slug", flat=True)])
        match_ids, match_slugs = [], []
        data = response.json_content["data"]

        for item in data:
            item = BeautifulSoup(item.get("0"), "lxml").find("a")
            match_ids.append(int(item.get("href").split("/")[2]))
            match_slugs.append(item.text)

        self.assertEqual(expected_ids, set(match_ids))
        self.assertEqual(expected_slugs, set(match_slugs))

    def test_create_view(self):
        url = reverse("incentive_payment:add")

        stats = IncentivePaymentStatus.objects.filter_by_user(self.user)
        stats = stats.filter(state="ipp_payment_automatic_requirements")

        stat = stats[0]
        customer = stat.home_status.home.get_builder()

        data = {
            "customer": customer.id,
            "comment": "test comment",
            "check_requested_date": datetime.date.today(),
            "stats": [stat.id],
        }

        # GET the add page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST to add page and get redirected
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

        # GET the page redirected to and check the object
        response = self.client.get(response["Location"])
        self.assertEqual(response.status_code, 200)

        obj = response.context["object"]

        for item in [
            "company",
            "customer",
            "check_to_name",
            "check_requested",
            "is_paid",
            "status",
            "total",
        ]:
            self.assertIsNotNone(getattr(obj, item))

        self.assertEqual(getattr(obj, "company"), self.user.company)
        self.assertEqual(getattr(obj, "comment"), data["comment"])
        self.assertEqual(getattr(obj, "check_requested_date"), data["check_requested_date"])
        self.assertEqual(getattr(obj, "customer").id, data["customer"])

    def test_update_view(self):
        not_allowed_states = ["start", "ipp_payment_failed_requirements"]
        ipp = IncentiveDistribution.objects.exclude(
            ippitem__home_status__incentivepaymentstatus__state__in=not_allowed_states
        )[0]

        new_data = {
            "customer": ipp.customer.id,
            "check_requested_date": datetime.date.today(),
            "paid_date": datetime.date.today(),
            "check_number": "RandomCheckNumber",
            "comment": "Test Comment",
            "total": ipp.total,
        }

        # GET the update page
        response = self.client.get(reverse("incentive_payment:update", kwargs={"pk": ipp.id}))
        self.assertEqual(response.status_code, 200)
        # POST to the update page with new changed and assert redirect
        response = self.client.post(
            reverse("incentive_payment:update", kwargs={"pk": ipp.id}), new_data
        )
        self.assertRedirects(response, ipp.get_absolute_url())
        # GET the page we were redirected to
        response = self.client.get(response["Location"])
        self.assertEqual(response.status_code, 200)

        for item in ["customer", "check_requested_date", "paid_date", "check_number", "comment"]:
            self.assertIsNotNone(getattr(response.context["object"], item))
            if item == "customer":
                self.assertEqual(getattr(response.context["object"], item).id, new_data[item])
            else:
                self.assertEqual(getattr(response.context["object"], item), new_data[item])

    def test_delete_company_view(self):
        user = self.user_model.objects.get(company__company_type="utility", is_company_admin=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        incentive_distribution = IncentiveDistribution.objects.filter(is_paid=True)[0]
        url = reverse("incentive_payment:delete", kwargs={"pk": incentive_distribution.id})
        self.assertEqual(incentive_distribution.can_be_deleted(user), False)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_view(self):
        incentive_distribution = IncentiveDistribution.objects.filter(is_paid=False)[0]
        url = reverse("incentive_payment:delete", kwargs={"pk": incentive_distribution.id})
        incentive_distributions_initial = IncentiveDistribution.objects.all().count()

        self.assertEqual(incentive_distribution.can_be_deleted(self.user), True)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url)
        self.assertRedirects(response, reverse("incentive_payment:list"))

        incentive_distributions = IncentiveDistribution.objects.all()
        self.assertEqual(incentive_distributions.count(), incentive_distributions_initial - 1)
