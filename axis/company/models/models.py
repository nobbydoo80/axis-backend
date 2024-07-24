"""models.py: Django Company Models"""

__author__ = "Steven Klass"
__date__ = "3/2/12 2:37 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.apps import apps
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords

from axis.company.managers import (
    CompanyManager,
)
from axis.relationship.models import Relationship
from .company import Company

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")

# NOTE: COMPANY_MODELS is a constant set at the end of the file, referencing the various company
# classes.


class EepOrganization(Company):
    """An Energy Efficiency Program Sponsoring Company."""

    COMPANY_TYPE = "eep"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "Program Sponsor"


class ProviderOrganization(Company):
    """A Rating Provider."""

    COMPANY_TYPE = "provider"

    # provider_id = models.CharField(
    #     "Provider ID", max_length=8, validators=[validate_provider_id], blank=True, null=True
    # )
    # auto_submit_to_registry = models.BooleanField(
    #     default=False, help_text=strings.HELP_TEXT_AUTO_SUBMIT_TO_REGISTRY
    # )
    # is_sample_eligible = models.BooleanField(default=False)
    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "Provider"


class RaterOrganization(Company):
    """A Rater."""

    COMPANY_TYPE = "rater"

    # certification_number = models.CharField(max_length=16, unique=True, blank=True, null=True)
    # is_sample_eligible = models.BooleanField(default=False)

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "Rating Company"
        verbose_name_plural = "Rating Companies"


class BuilderOrganization(Company):
    """A Builder Company."""

    COMPANY_TYPE = "builder"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "Builder"


HQUITO_CHOICES = ((None, "Unknown"), (True, "Accredited"), (False, "Not Accredited"))


class HvacOrganization(Company):
    """A HVAC Company."""

    COMPANY_TYPE = "hvac"

    # hquito_accredited = models.BooleanField(
    #     null=True, default=None, choices=HQUITO_CHOICES, help_text=strings.HELP_TEXT_HQUITO_STATUS
    # )
    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "HVAC Company"
        verbose_name_plural = "HVAC Companies"


class UtilityOrganization(Company):
    """A Utility Company."""

    COMPANY_TYPE = "utility"

    # electricity_provider = models.BooleanField(default=False)
    # gas_provider = models.BooleanField(default=False)
    # water_provider = models.BooleanField(default=False)

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "Utility Company"
        verbose_name_plural = "Utility Companies"


class QaOrganization(Company):
    """A QA/QC Company."""

    COMPANY_TYPE = "qa"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "QA/QC Companies"


class ArchitectOrganization(Company):
    """A Community Architect Company."""

    COMPANY_TYPE = "architect"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Community Architects Companies"


class DeveloperOrganization(Company):
    """A Community Developer Owner Company."""

    COMPANY_TYPE = "developer"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Community Developer Owner Companies"


class CommunityOwnerOrganization(Company):
    """A Community Developer Owner Company."""

    COMPANY_TYPE = "communityowner"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Community Developer Companies"


class GeneralOrganization(Company):
    """A General."""

    COMPANY_TYPE = "general"

    objects = CompanyManager(company_type=COMPANY_TYPE)
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "General Companies"


COMPANY_MODELS = (
    Company,
    RaterOrganization,
    EepOrganization,
    HvacOrganization,
    ProviderOrganization,
    BuilderOrganization,
    UtilityOrganization,
    QaOrganization,
    DeveloperOrganization,
    CommunityOwnerOrganization,
    ArchitectOrganization,
    GeneralOrganization,
)

COMPANY_MODELS_MAP = dict(
    {x.COMPANY_TYPE: x for x in COMPANY_MODELS},
    gas_utility=UtilityOrganization,
    electric_utility=UtilityOrganization,
)


def update_auto_accept_relationships(sender, instance, raw=None, **kwargs):
    """This will update the relationships a company which previously did not have
    auto_add_direct_relationships set to owned"""
    if raw and (instance not in COMPANY_MODELS):
        return

    historical_auto_add = None
    historical_is_customer = None
    historical_obj = instance.history.first()
    if historical_obj:
        historical_auto_add = historical_obj.auto_add_direct_relationships
        historical_is_customer = historical_obj.is_customer

    newly_auto_added = (historical_auto_add is False) and instance.auto_add_direct_relationships
    newly_added_customer = (historical_is_customer is False) and instance.is_customer

    if newly_auto_added or newly_added_customer:
        relationships = Relationship.objects.filter(company_id=instance.id, is_owned=False)
        relationships.update(is_owned=True)
