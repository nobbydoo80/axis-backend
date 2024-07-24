"""utils.py: Django company"""


import logging

__author__ = "Steven Klass"
__date__ = "5/22/12 9:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def can_view_or_edit_eto_account(user, company_type):
    """Return True for ETO and PECI viewing raters, providers, and builders."""

    if company_type in ["builder", "rater", "provider"]:
        if user.is_superuser:
            return True
        if user.company and user.company.slug in ["eto", "peci"]:
            return True
    return False


def can_edit_eto_ccb_number(user, company_type):
    """Return True if `user` is an ETO-sponsored rater or provider."""

    if company_type in ["rater", "provider"]:
        if user.is_superuser:
            return True
        if user.company:
            if (
                user.company.sponsors.filter(slug="eto").exists()
                and user.company.company_type == company_type
            ):
                return True
    return False


def can_edit_hquito_status(user, company, company_type):
    """Return True if the customer `company` belongs to `user`, or if `user` is an EEP sponsor."""

    # This accepts the ``company_type`` argument because ``company`` may be an unsaved instance
    # that doesn't yet have its type.

    if company_type != "hvac":
        return False
    if company and user.company.id == company.id and company.is_customer:
        return True
    if user.is_superuser or user.company.is_eep_sponsor:
        return True
    return False
