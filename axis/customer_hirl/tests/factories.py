"""factories.py: Django """

__author__ = "Steven Klass"
__date__ = "06/17/2019 13:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import re

from django.apps import apps
from django.utils import timezone

from axis.company.tests.factories import (
    builder_organization_factory,
    provider_organization_factory,
    developer_organization_factory,
    architect_organization_factory,
    communityowner_organization_factory,
)
from axis.core.tests.factories import (
    rater_admin_factory,
    contact_card_factory,
    contact_card_email_factory,
    contact_card_phone_factory,
    SET_NULL,
)
from axis.core.utils import random_sequence
from axis.customer_hirl.models import (
    BuilderAgreement,
    HIRLProject,
    VerifierAgreement,
    COIDocument,
    HIRLGreenEnergyBadge,
)
from axis.customer_hirl.models.project import HIRLProjectRegistration
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import real_city_factory
from axis.geographic.utils.legacy import format_geographic_input
from axis.home.tests.factories import eep_program_custom_home_status_factory

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


def builder_agreement_factory(**kwargs):
    """A HIRL Builder Agreement Factory"""
    owner = kwargs.pop("owner", None)
    company = kwargs.pop("company", None)

    street_line1 = kwargs.pop("street_line1", "479 Washington St")
    street_line2 = kwargs.pop("street_line2", "")
    city = kwargs.pop("city", None)
    zipcode = kwargs.pop("zipcode", "34342")

    if city is None:
        city = real_city_factory("Providence", "RI")

    raw_address, raw_parts, entity_type = format_geographic_input(
        street_line1=street_line1, street_line2=street_line2, city=city, zipcode=zipcode
    )

    geocode, _created = Geocode.objects.get_or_create(
        raw_address=raw_address,
        entity_type=entity_type,
        defaults=dict(immediate=kwargs.get("immediate", True), **raw_parts),
    )

    if owner is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("owner__"):
                _kwrgs[re.sub(r"owner__", "", k)] = kwargs.pop(k)
        if "owner__slug" not in _kwrgs:
            _kwrgs["owner__slug"] = app.CUSTOMER_SLUG
        owner = provider_organization_factory(**_kwrgs)
        owner.update_permissions(app.app_name())

    if company is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                _kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        company = builder_organization_factory(**_kwrgs)
        company.update_permissions(app.app_name())

    kwrgs = {
        "owner": owner,
        "company": company,
        "state": BuilderAgreement.NEW,
        "mailing_geocode": geocode,
        "shipping_geocode": geocode,
        "website": "website",
        "primary_contact_first_name": "primary_contact_first_name",
        "primary_contact_last_name": "primary_contact_last_name",
        "primary_contact_title": "primary_contact_title",
        "primary_contact_phone_number": "primary_contact_phone_number",
        "primary_contact_cell_number": "primary_contact_cell_number",
        "primary_contact_email_address": "primary_contact_email_address",
        "secondary_contact_first_name": "secondary_contact_first_name",
        "secondary_contact_last_name": "secondary_contact_last_name",
        "secondary_contact_title": "secondary_contact_title",
        "secondary_contact_phone_number": "secondary_contact_phone_number",
        "secondary_contact_cell_number": "secondary_contact_cell_number",
        "secondary_contact_email_address": "secondary_contact_email_address",
        "payment_contact_first_name": "payment_contact_first_name",
        "payment_contact_last_name": "payment_contact_last_name",
        "payment_contact_title": "payment_contact_title",
        "payment_contact_phone_number": "payment_contact_phone_number",
        "payment_contact_cell_number": "payment_contact_cell_number",
        "payment_contact_email_address": "payment_contact_email_address",
        "use_payment_contact_in_ngbs_green_projects": True,
        "marketing_contact_first_name": "marketing_contact_first_name",
        "marketing_contact_last_name": "marketing_contact_last_name",
        "marketing_contact_title": "marketing_contact_title",
        "marketing_contact_phone_number": "marketing_contact_phone_number",
        "marketing_contact_cell_number": "marketing_contact_cell_number",
        "marketing_contact_email_address": "marketing_contact_email_address",
        "website_contact_first_name": "website_contact_first_name",
        "website_contact_last_name": "website_contact_last_name",
        "website_contact_title": "website_contact_title",
        "website_contact_phone_number": "website_contact_phone_number",
        "website_contact_cell_number": "website_contact_cell_number",
        "website_contact_email_address": "website_contact_email_address",
    }
    kwrgs.update(kwargs)

    owner = kwrgs.pop("owner")
    company = kwrgs.pop("company")

    agreement, create = BuilderAgreement.objects.get_or_create(
        owner=owner, company=company, **kwrgs
    )

    return agreement


def verifier_agreement_factory(**kwargs):
    verifier = kwargs.pop("verifier", None)
    if verifier is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("verifier__"):
                _kwrgs[re.sub(r"verifier__", "", k)] = kwargs.pop(k)
        verifier = rater_admin_factory(**_kwrgs)
        verifier.company.update_permissions(app.app_name())

    owner = kwargs.pop("owner", None)
    if not owner:
        owner = provider_organization_factory()
    kwrgs = {"verifier": verifier, "owner": owner, "state": VerifierAgreementStates.NEW}
    kwrgs.update(kwargs)
    verifier_agreement = VerifierAgreement.objects.create(**kwrgs)
    return verifier_agreement


def coi_document_factory(**kwargs):
    company = kwargs.pop("company", None)

    if company is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                _kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        builder_organization = builder_organization_factory(**_kwrgs)
        builder_organization.update_permissions()

    document = kwargs.pop("document", None)
    if document is None:
        document = __file__

    kwrgs = {
        "company": company,
        "policy_number": random_sequence(4),
        "start_date": timezone.now() - timezone.timedelta(days=365),
        "expiration_date": timezone.now() + timezone.timedelta(days=365),
        "document": document,
    }

    kwrgs.update(kwargs)
    coi_document = COIDocument.objects.create(**kwrgs)
    return coi_document


def hirl_green_energy_badge_factory(**kwargs):
    kwrgs = {"name": random_sequence(4), "slug": f"{random_sequence(14)}", "cost": 0}
    kwrgs.update(kwargs)
    hirl_green_energy_badge = HIRLGreenEnergyBadge.objects.create(**kwrgs)
    return hirl_green_energy_badge


def hirl_project_registration_factory(project_type, **kwargs):
    registration_user = kwargs.pop("registration_user", None)
    builder_organization = kwargs.pop("builder_organization", None)
    architect_organization = kwargs.pop("architect_organization", None)
    developer_organization = kwargs.pop("developer_organization", None)
    community_owner_organization = kwargs.pop("community_owner_organization", None)
    eep_program = kwargs.pop("eep_program", None)
    builder_organization_contact = kwargs.pop("builder_organization_contact", None)

    if registration_user is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("verifier__"):
                _kwrgs[re.sub(r"registration_user__", "", k)] = kwargs.pop(k)
        registration_user = rater_admin_factory(**_kwrgs)
        registration_user.company.update_permissions(app.app_name())

    if builder_organization is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("builder_organization__"):
                _kwrgs[re.sub(r"builder_organization__", "", k)] = kwargs.pop(k)
        builder_organization = builder_organization_factory(**_kwrgs)
        builder_organization.update_permissions(app.app_name())

    if community_owner_organization is SET_NULL:
        community_owner_organization = None
    elif community_owner_organization is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("community_owner_organization__"):
                _kwrgs[re.sub(r"community_owner_organization__", "", k)] = kwargs.pop(k)
        community_owner_organization = communityowner_organization_factory(**_kwrgs)
        community_owner_organization.update_permissions(app.app_name())

    if architect_organization is SET_NULL:
        architect_organization = None
    elif architect_organization is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("architect_organization__"):
                _kwrgs[re.sub(r"architect_organization__", "", k)] = kwargs.pop(k)
        architect_organization = architect_organization_factory(**_kwrgs)
        architect_organization.update_permissions(app.app_name())

    if developer_organization is SET_NULL:
        developer_organization = None
    if developer_organization is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("developer_organization__"):
                _kwrgs[re.sub(r"developer_organization__", "", k)] = kwargs.pop(k)
        developer_organization = developer_organization_factory(**_kwrgs)
        developer_organization.update_permissions(app.app_name())

    if eep_program is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("eep_program__"):
                _kwrgs[re.sub(r"eep_program__", "", k)] = kwargs.pop(k)
        eep_program = basic_eep_program_factory(**_kwrgs)

    if builder_organization_contact is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("eep_program__"):
                _kwrgs[re.sub(r"builder_organization_contact__", "", k)] = kwargs.pop(k)
        builder_organization_contact = contact_card_factory(company=builder_organization, **_kwrgs)
        contact_card_email_factory(contact_card=builder_organization_contact)
        contact_card_phone_factory(contact_card=builder_organization_contact)

    kwrgs = {
        "registration_user": registration_user,
        "project_type": project_type,
        "eep_program": eep_program,
        "builder_organization": builder_organization,
        "builder_organization_contact": builder_organization_contact,
        "community_owner_organization": community_owner_organization,
        "architect_organization": architect_organization,
        "developer_organization": developer_organization,
        "project_client": HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
    }

    if project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
        kwrgs.update(
            {
                "project_name": random_sequence(4),
            }
        )

    kwrgs.update(kwargs)

    registration = HIRLProjectRegistration.objects.create(**kwrgs)
    return registration


def hirl_project_factory(registration, **kwargs):
    street_line1 = kwargs.pop("street_line1", "479 Washington St")
    city = kwargs.pop("city", None)
    zipcode = kwargs.pop("zipcode", "34342")

    home_status = kwargs.pop("home_status", None)

    if home_status is SET_NULL:
        home_status = None
    elif home_status is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("home_status__"):
                _kwrgs[re.sub(r"home_status__", "", k)] = kwargs.pop(k)
        home_status = eep_program_custom_home_status_factory(**_kwrgs)
    else:
        street_line1 = home_status.home.street_line1
        city = home_status.home.city
        zipcode = home_status.home.zipcode

    if city is None:
        city = real_city_factory("Providence", "RI")

    # We intentionally set street_line2 to "" b/c we don't really care about the unit.
    geocode_response = Geocode.objects.get_matches(
        street_line1=street_line1, street_line2="", city=city, zipcode=zipcode
    ).first()

    kwrgs = {
        "registration": registration,
        "home_status": home_status,
        "is_accessory_structure": False,
        "is_accessory_dwelling_unit": False,
        "home_address_geocode": geocode_response.geocode if geocode_response else None,
        "home_address_geocode_response": geocode_response,
        "hud_disaster_case_number": 1,
    }
    kwrgs.update(kwargs)
    project = HIRLProject.objects.create(**kwrgs)
    return project
