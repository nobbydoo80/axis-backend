"""managers.py: Django sampleset round 2, ding ding. """


import logging

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from . import utils

__author__ = "Autumn Valenta"
__date__ = "07/09/14  4:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSetManager(models.Manager):
    def get_queryset(self):
        return SampleSetQuerySet(self.model, using=self._db)

    def filter_by_company(self, company):
        return self.get_queryset().filter_by_company(company)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)


class SampleSetQuerySet(QuerySet):
    def filter_by_company(self, company, **kwargs):
        if company.is_eep_sponsor:
            from axis.eep_program.models import EEPProgram

            eeps = EEPProgram.objects.filter_by_company(company)
            return self.filter(home_statuses__eep_program__in=eeps)
        elif company.company_type in ["builder", "provider"]:
            from axis.relationship.models import Relationship

            comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
            # Who do I have a relationship with
            rels = company.relationships.get_companies(ids_only=True)
            ints = list(set(rels).intersection(set(comps))) + [company.id]
            # The intersection of these is what matters..
            return self.filter(owner_id__in=ints)
        return self.filter(owner=company).distinct()

    def filter_by_user(self, user, **kwargs):
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class SampleSetHomeStatusManager(models.Manager):
    """
    Default manager for the m2m Through table between SampleSet and EEPProgramHomeStatus.

    The SampleSetHomeStatus model will preserve instances of past associations of homes to the
    sampleset, so the presently active items can be retrieved via current().
    """

    # NOTE: all() returns all items, historical and current.  This is not usually a good idea.

    def get_queryset(self):
        return SampleSetHomeStatusQuerySet(self.model, using=self._db)

    ## Methods that return querysets
    def current(self):
        return self.get_queryset().current()

    def saved(self):
        return self.get_queryset().saved()

    def certified(self):
        return self.get_queryset().certified()

    def uncertified(self):
        return self.get_queryset().uncertified()

    ## Methods that return querysets from other models
    def get_current_source_answers(self):
        return self.get_queryset().get_current_source_answers()


class SampleSetHomeStatusQuerySet(QuerySet):
    def current(self):
        """Filters the queryset for only homestatuses in the sampleset's current revision."""
        return self.filter(is_active=True)

    def saved(self):
        """Filters the queryset for only homestatuses not in the sampleset's current revision."""
        return self.filter(is_active=False)

    def certified(self):
        return self.filter(
            home_status__certification_date__isnull=False, home_status__state="complete"
        )

    def uncertified(self):
        return self.filter(
            Q(home_status__certification_date=None) | ~Q(home_status__state="complete")
        )

    def get_current_source_answers(self):
        """
        Returns the answers being provided by the current test homes.  This bridges all revisions
        because these answers are stored directly on the underlying Home.
        """
        test_statuses = (
            self.current().filter(is_test_home=True).select_related("home_status__eep_program")
        )
        return utils.get_homestatus_test_answers([s.home_status for s in test_statuses])


class SamplingProviderApprovalManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        from axis.company.models import Company

        if company.company_type == "provider":
            return self.filter(provider=company).filter(**kwargs)
        providers = Company.objects.filter_by_company(
            company, include_self=True, company_type=Company.PROVIDER_COMPANY_TYPE
        )
        companies = Company.objects.filter_by_company(company, include_self=True)
        return self.filter(
            provider_id__in=list(providers.values_list("id", flat=True)),
            target_id__in=list(companies.values_list("id", flat=True)),
        ).filter(**kwargs)

    def filter_by_user(self, user, **kwargs):
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)
