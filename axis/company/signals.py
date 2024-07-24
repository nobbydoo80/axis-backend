"""signals.py: Django company"""

__author__ = "Steven Klass"
__date__ = "1/17/17 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver


from .models import (
    Company,
    HvacOrganization,
    COMPANY_MODELS,
    SponsorPreferences,
    BuilderOrganization,
    DeveloperOrganization,
    ArchitectOrganization,
    CommunityOwnerOrganization,
    CompanyAccess,
)

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


def register_signals():
    """Nested to avoid tangling import during initial load."""

    post_save.connect(update_hvac_homes, sender=HvacOrganization)
    post_delete.connect(update_hvac_homes, sender=HvacOrganization)

    for company_model in COMPANY_MODELS:
        post_save.connect(handler_update_company_groups, sender=company_model)
        post_save.connect(create_contact_card, sender=company_model)


def handler_update_company_groups(sender, instance, raw=None, **kwargs):
    if raw and (sender is not Company):
        return
    from .tasks import update_company_groups

    update_company_groups.delay(company_id=instance.id)


def create_contact_card(sender, instance, created, **kwargs):
    if created:
        instance.create_contact_card()


@receiver(post_save, sender=SponsorPreferences)
def sponsor_preferences_post_save(sender, instance, **kwargs):
    from .tasks import update_company_groups

    update_company_groups.delay(company_id=instance.sponsored_company.id)


def update_hvac_homes(sender, **kwargs):
    """Attempt to move the state of QA forward"""
    from .tasks import update_stats_based_on_company_change

    company = kwargs.get("instance")
    if kwargs.get("raw", False):
        return
    update_stats_based_on_company_change.delay(company_id=company.id)


@receiver(post_save, sender=Company)
@receiver(post_save, sender=BuilderOrganization)
def create_customer_hirl_builder_organization_post_save(sender, instance, created, **kwargs):
    """
    Create HIRLBuilderOrganization to continue support NGBS legacy builder IDS
    :param sender: BuilderOrganization
    :param instance: BuilderOrganization
    :param created: Boolean
    :param kwargs:
    :return:
    """
    from axis.customer_hirl.models import HIRLBuilderOrganization

    if instance.__class__ != Company:
        company = instance.company_ptr
    else:
        company = instance

    if not kwargs.get("raw") and created:
        _ = HIRLBuilderOrganization.objects.create(builder_organization=company)


@receiver(post_save, sender=Company)
@receiver(post_save, sender=BuilderOrganization)
@receiver(post_save, sender=DeveloperOrganization)
@receiver(post_save, sender=ArchitectOrganization)
@receiver(post_save, sender=CommunityOwnerOrganization)
def create_customer_hirl_client_organization(sender, instance, created, **kwargs):
    """
    Create HIRLCompanyClient with own NGBS ID system
    :param sender: Company
    :param instance: Company
    :param created: Boolean
    :param kwargs:
    :return:
    """
    from axis.customer_hirl.models import HIRLCompanyClient

    if instance.__class__ != Company:
        company = instance.company_ptr
    else:
        company = instance

    if (
        not kwargs.get("raw")
        and created
        and company.company_type
        in [
            Company.BUILDER_COMPANY_TYPE,
            Company.DEVELOPER_COMPANY_TYPE,
            Company.ARCHITECT_COMPANY_TYPE,
            Company.COMMUNITY_OWNER_COMPANY_TYPE,
        ]
    ):
        _ = HIRLCompanyClient.objects.create(company=company)


@receiver(post_save, sender=SponsorPreferences)
def create_customer_hirl_legacy_rater_user_post_save(sender, instance, created, **kwargs):
    if not kwargs.get("raw") and created:
        from axis.customer_hirl.models import HIRLRaterUser

        if (
            instance.sponsored_company.company_type == Company.RATER_COMPANY_TYPE
            and instance.sponsor.slug == customer_hirl_app.CUSTOMER_SLUG
        ):
            for user in instance.sponsored_company.users.filter(hirlrateruser__isnull=True):
                _ = HIRLRaterUser.objects.create(user=user)


@receiver(m2m_changed, sender=CompanyAccess.roles)
def company_access_roles_m2m_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        User.objects.update(id=instance.user.id, is_company_admin=True)
    else:
        User.objects.update(id=instance.user.id, is_company_admin=False)
