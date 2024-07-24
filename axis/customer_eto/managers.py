"""Managers."""

__author__ = "Steven Klass"
__date__ = "9/4/13 10:20 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.db.models import Q
from django.db import models
from django.db.models.query import QuerySet
from axis.core.managers.utils import queryset_user_is_authenticated

log = logging.getLogger(__name__)


class ETOAccountQuerySet(QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        from axis.company.models import Company

        available_companies = Company.objects.filter_by_user(user)
        return self.filter(Q(company__in=available_companies) | Q(company=user.company))


class PermitAndOccupancySettingsQuerySet(QuerySet):
    """Queryset for ETO's inheritance settings workflow."""

    def filter_by_company(self, company, source=None):
        """Return instances owned by `company` on the `source` model instance."""

        from axis.company.models import Company
        from axis.subdivision.models import Subdivision
        from axis.home.models import Home

        kwargs = {}
        if isinstance(source, Home):
            kwargs["home"] = source
        elif isinstance(source, Subdivision):
            kwargs["subdivision"] = source
        elif isinstance(source, Company):
            kwargs["company"] = source
        return self.filter(owner=company, **kwargs)

    def filter_by_user(self, user, source=None):
        """Return `filter_by_company(user.company, source=source)`."""

        return self.filter_by_company(user.company, source=source)

    def get_for_company(self, company):
        """Return a single instance that `company` owns."""

        return self.filter_by_company(company).first()

    def get_for_user(self, user):
        """Return a single instance that `user.company` owns."""

        return self.filter_by_user(user).first()

    def get_for_object(self, source, user):
        """Return a single instance that `user.company` owns on the target `source`."""

        return self.filter_by_user(user, source=source).first()


class FastTrackSubmissionQuerySet(QuerySet):
    def filter_by_company(self, company):
        """Filter by company"""
        return self.filter(home_status__company=company)

    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        """Filter by user's company"""
        if user.is_superuser or user.company.slug in ["eto", "peci"]:
            return self.all()
        return self.filter_by_company(user.company)


class FastTrackSubmissionManager(models.Manager):
    def get_queryset(self):
        return FastTrackSubmissionQuerySet(self.model, using=self._db)

    def filter_by_company(self, company):
        return self.get_queryset().filter_by_company(company)

    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)
