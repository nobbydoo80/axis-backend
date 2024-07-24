"""factory.py: Django core"""
import logging
import random
import re

from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

from axis.company.tests.factories import company_access_factory
from axis.core.models import ContactCard, ContactCardEmail, ContactCardPhone
from axis.core.tasks import update_user_groups
from axis.core.tests.sources.names import first_names, last_names
from axis.core.utils import random_sequence, random_digits

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class SET_NULL:
    pass


def basic_user_factory(password="password", **kwargs) -> User:
    """A basic user factory.  get_or_create based on the field 'username'."""

    randstr = random_sequence(4)
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    username = slugify(first_name[0] + last_name) + random_digits(2)
    kwrgs = dict(
        {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{username}@home.com",
            "title": kwargs.pop("title", "Title {}".format(randstr)),
            "department": kwargs.pop("department", "Dept {}".format(randstr)),
            "is_approved": kwargs.pop("is_approved", True),
        }
    )

    kwrgs.update(kwargs)
    username = kwrgs.pop("username")

    company = kwargs.get("company")

    user, create = User.objects.get_or_create(username=username, defaults=kwrgs)

    # create company access for user by default
    if company:
        company_access_factory(user=user, company=company)

    if create:
        user.set_password(password)
        user.save()
        if company:
            user.companies.set(
                [
                    company,
                ]
            )

        # Don't depend on celery for this as time is essential.
        update_user_groups(user.id)
        user.refresh_from_db()
    return user


def non_company_user_factory(password="password", **kwargs):
    return basic_user_factory(password=password, **kwargs)


# Rater
def rater_user_factory(password="password", **kwargs):
    """A rater user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import rater_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = rater_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"rater_{random_sequence(4)}")
    kwargs["rater_id"] = kwargs.get("rater_id", random_digits(7))
    return basic_user_factory(password=password, **kwargs)


def rater_admin_factory(password="password", **kwargs):
    """A rater admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return rater_user_factory(password=password, **kwargs)


# Provider
def provider_user_factory(password="password", **kwargs):
    """A provider user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import provider_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = provider_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"provider_{random_sequence(4)}")
    kwargs["rater_id"] = kwargs.get("rater_id", random_digits(7))
    return basic_user_factory(password=password, **kwargs)


def provider_admin_factory(password="password", **kwargs):
    """A provider admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return provider_user_factory(password=password, **kwargs)


# EEP
def eep_user_factory(password="password", **kwargs):
    """A eep user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import eep_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = eep_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"eep_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def eep_admin_factory(password="password", **kwargs):
    """A eep admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return eep_user_factory(password=password, **kwargs)


# Builder
def builder_user_factory(password="password", **kwargs):
    """A builder user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import builder_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = builder_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"builder_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def builder_admin_factory(password="password", **kwargs):
    """A builder admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return builder_user_factory(password=password, **kwargs)


# Utility
def utility_user_factory(password="password", **kwargs):
    """A utility user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import utility_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = utility_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"utility_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def utility_admin_factory(password="password", **kwargs):
    """A utility admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return utility_user_factory(password=password, **kwargs)


# HVAC
def hvac_user_factory(password="password", **kwargs):
    """An HVAC user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import hvac_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = hvac_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"hvac_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def hvac_admin_factory(password="password", **kwargs):
    """An HVAC admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return hvac_user_factory(password=password, **kwargs)


# QA
def qa_user_factory(password="password", **kwargs):
    """A qa user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import qa_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = qa_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"qa_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def qa_admin_factory(password="password", **kwargs):
    """A qa admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return qa_user_factory(password=password, **kwargs)


# Architect
def architect_user_factory(password="password", **kwargs):
    """A architect user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import architect_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = architect_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"architect_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def architect_admin_factory(password="password", **kwargs):
    """A qa admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return architect_user_factory(password=password, **kwargs)


# Developer
def developer_user_factory(password="password", **kwargs):
    """A developer user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import developer_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = developer_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"developer_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def developer_admin_factory(password="password", **kwargs):
    """A qa admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return developer_user_factory(password=password, **kwargs)


# Community Owner
def communityowner_user_factory(password="password", **kwargs):
    """A developer user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import communityowner_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = communityowner_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"communityowner_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def communityowner_admin_factory(password="password", **kwargs):
    """A qa admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_company_admin"] = True
    return communityowner_user_factory(password=password, **kwargs)


# General
def general_user_factory(password="password", **kwargs):
    """A general user factory.  get_or_create based on the field 'username'.  Creates company"""
    company = kwargs.pop("company", None)
    if not company:
        from axis.company.tests.factories import general_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = general_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    kwargs["username"] = kwargs.get("username", f"general_{random_sequence(4)}")
    return basic_user_factory(password=password, **kwargs)


def general_admin_factory(password="password", **kwargs):
    """A general admin factory.  get_or_create based on the field 'username'.  Creates company"""
    return general_user_factory(password=password, is_company_admin=True, **kwargs)


def general_super_user_factory(password="password", **kwargs):
    """A general admin factory.  get_or_create based on the field 'username'.  Creates company"""
    kwargs["is_superuser"] = True
    return general_admin_factory(password=password, **kwargs)


def contact_card_factory(**kwargs):
    company = kwargs.pop("company", None)

    if not company:
        from axis.company.tests.factories import general_organization_factory

        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = general_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company

    kwrgs = dict(
        {
            "first_name": f"First_{random_sequence(4)}",
            "last_name": f"Last_{random_sequence(4)}",
            "description": f"Description_{random_sequence(4)}",
            "protected": False,
        }
    )

    kwrgs.update(kwargs)
    return ContactCard.objects.create(**kwrgs)


def contact_card_email_factory(**kwargs):
    contact_card = kwargs.pop("contact_card", None)

    if not contact_card:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("contact_card__"):
                c_kwrgs[re.sub(r"contact_card__", "", k)] = kwargs.pop(k)
        kwargs["contact"] = contact_card_factory(**c_kwrgs)
    else:
        kwargs["contact"] = contact_card

    kwrgs = {"email": f"{slugify(random_sequence(8))}@home.com"}

    kwrgs.update(kwargs)
    return ContactCardEmail.objects.create(**kwrgs)


def contact_card_phone_factory(**kwargs):
    contact_card = kwargs.pop("contact_card", None)

    if not contact_card:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("contact_card__"):
                c_kwrgs[re.sub(r"contact_card__", "", k)] = kwargs.pop(k)
        kwargs["contact"] = contact_card_factory(**c_kwrgs)
    else:
        kwargs["contact"] = contact_card

    kwrgs = dict({"phone": "4806545674"})

    kwrgs.update(kwargs)
    return ContactCardPhone.objects.create(**kwrgs)
