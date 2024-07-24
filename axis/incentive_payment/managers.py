"""managers.py: Django incentive_payment"""


import logging
from collections import namedtuple, defaultdict
from operator import itemgetter
import datetime

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils import formats
from django.utils.timezone import now

from axis.company.models import Company
from . import messages

__author__ = "Steven Klass"
__date__ = "3/16/12 1:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IncentivePaymentStatusManager(models.Manager):
    """Default Manager for IncentivePaymentStatus"""

    def get_queryset(self):
        return IncentivePaymentStatusQuerySet(self.model, using=self._db)

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        from .models import IPPItem

        ipp_items = IPPItem.objects.filter_by_company(company)
        ipp_items = list(ipp_items.values_list("home_status", flat=True))

        return (
            self.filter(
                Q(owner=company)
                | Q(home_status__company=company)
                | Q(home_status_id__in=ipp_items),
            )
            .filter(**kwargs)
            .distinct()
        )

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_by_company_id(self, company_id, **kwargs):
        return self.get_queryset().filter_by_company_id(company_id, **kwargs)

    def filter_by_subdivision_id(self, subdivision_id, **kwargs):
        return self.get_queryset().filter_by_subdivision_id(subdivision_id, **kwargs)

    def filter_by_provider_id(self, provider_id, **kwargs):
        return self.get_queryset().filter_by_provider_id(provider_id, **kwargs)

    def choice_builder_items_for_user(self, user, **kwargs):
        """This will return a very efficient list of builder choices based on a queryset"""
        # TODO: why are we not just returning the companies?
        _bqs = (
            self.filter_by_user(
                user=user,
                home_status__home__relationships__company__company_type="builder",
                **kwargs,
            )
            .distinct()
            .values_list(
                "home_status__home__relationships__company_id",
                "home_status__home__relationships__company__name",
            )
        )
        return sorted(list(_bqs), key=itemgetter(1))

    def choice_subdivision_items_for_user(self, user, **kwargs):
        """This will return a very efficient list of subdivision choices based on a queryset"""
        from axis.subdivision.models import Subdivision

        include_custom = kwargs.pop("include_custom", True)
        sub_ids = self.filter_by_user(user, **kwargs).values_list(
            "home_status__home__subdivision_id", flat=True
        )
        subs = Subdivision.objects.choice_items_from_instances(id__in=list(set(sub_ids)))
        if include_custom:
            if self.filter(home_status__home__subdivision__isnull=True, **kwargs).all().exists():
                subs += [("custom", "Custom")]
        return sorted(subs, key=itemgetter(1))

    def choice_provider_items_for_user(self, user, **kwargs):
        _rqs = (
            self.filter_by_user(user=user)
            .distinct()
            .values_list("home_status__company__id", "home_status__company__name")
        )
        return sorted(list(_rqs), key=itemgetter(1))

    def send_notification_failure_message(self, company, **kwargs):
        """Send a notification message"""
        _qs = self.filter_by_company(company, **kwargs)
        values = _qs.values_list("id", "home_status__company_id")
        provider_dict = defaultdict(list)
        [provider_dict[co].append(id) for id, co in values]
        for provider_id, stats in provider_dict.items():
            url = reverse("incentive_payment:failures")
            context = {
                "company": company,
                "num_homes": len(stats) if len(stats) > 1 else "a",
                "plural": "s" if len(stats) > 1 else "",
                "date": formats.date_format(now(), "SHORT_DATE_FORMAT"),
                "url": url,
            }
            messages.IPPFailureMessage(url=url).send(
                context=context,
                company=Company.objects.get(id=provider_id),
            )
        return True

    def send_notification_corrected_message(self, company, **kwargs):
        """Send a message that the homes were corrected"""
        _qs = self.filter_by_company(company, **kwargs)
        values = _qs.values_list("id", "owner_id")
        owner_dict = defaultdict(list)
        [owner_dict[co].append(id) for id, co in values]
        for owner_id, stats in owner_dict.items():
            url = reverse("incentive_payment:control_center")
            context = {
                "company": company,
                "num_homes": len(stats) if len(stats) > 1 else "a",
                "plural": "s" if len(stats) > 1 else "",
                "date": formats.date_format(now(), "SHORT_DATE_FORMAT"),
                "url": url,
            }
            messages.IPPCorrectionMessage(url=url).send(
                context=context,
                company=Company.objects.get(id=owner_id),
            )
        return True

    def send_notification_approved_message(self, company, **kwargs):
        """Send a message that the homes were approved to the home_status company"""
        _qs = self.filter_by_company(company, **kwargs)
        values = _qs.values_list("id", "home_status__company_id")
        owner_dict = defaultdict(list)
        [owner_dict[co].append(id) for id, co in values]
        for owner_id, stats in owner_dict.items():
            url = reverse("home:report:status")
            url += "?ipp_state=ipp_payment_automatic_requirements&state=complete"
            context = {
                "company": company,
                "num_homes": len(stats) if len(stats) > 1 else "a",
                "plural": "s" if len(stats) > 1 else "",
                "date": formats.date_format(now(), "SHORT_DATE_FORMAT"),
            }
            messages.IPPApprovedPayment(url=url).send(
                context=context,
                company=Company.objects.get(id=owner_id),
            )
        return True


class IncentivePaymentStatusQuerySet(QuerySet):
    def filter_by_company_id(self, company_id, **kwargs):
        return self.filter(home_status__home__relationships__company_id=company_id, **kwargs)

    def filter_by_subdivision_id(self, subdivision_id, **kwargs):
        """Filter this based on subdivision - can be "custom"""
        if subdivision_id == "custom":
            return self.filter(home_status__home__subdivision__isnull=True, **kwargs)
        return self.filter(home_status__home__subdivision_id=subdivision_id, **kwargs)

    def filter_by_provider_id(self, provider_id, **kwargs):
        return self.filter(home_status__company_id=provider_id)


class IncentiveDistributionManager(models.Manager):
    """Generic Manager Class"""

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if not company.is_eep_sponsor:
            return self.filter(customer=company).filter(**kwargs)
        return self.filter(company=company).filter(**kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_by_company_or_customer_for_home(self, user, home):
        """A way to trim down the list of company by company"""
        return self.filter_by_user(user).filter(ippitem__home_status__home=home)


class IPPItemManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if not company.is_eep_sponsor:
            return self.filter(incentive_distribution__customer=company)
        return self.filter(incentive_distribution__company=company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        kwargs["company"] = user.company
        return self.filter_by_company(**kwargs)
