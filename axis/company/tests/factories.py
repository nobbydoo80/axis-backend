"""factory.py: Django company"""


__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging
import random
import re

from django.forms import model_to_dict

from axis.company.models import Company, CompanyRole, CompanyAccess
from axis.core.utils import (
    random_sequence,
    random_digits,
    random_longitude,
    random_latitude,
)
from axis.company.tasks import update_company_groups
from axis.geographic.models import County
from axis.geographic.tests.factories import city_factory
from axis.geographic.utils.country import get_usa_default

log = logging.getLogger(__name__)


def base_company_factory(**kwargs):
    """A company factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    phone = f"480-3{random_digits(2)}-{random_digits(4)}"
    city = kwargs.pop("city", None)
    counties = kwargs.pop("counties", None)
    countries = kwargs.pop("countries", None)
    kwrgs = {
        "name": f"Company {random_sequence(4)}",
        "street_line1": "123 W Main",
        "street_line2": "",
        "zipcode": "53094",
        "latitude": random_latitude(),
        "longitude": random_longitude(),
        "confirmed_address": False,
        "address_override": False,
        "office_phone": phone,
        "home_page": f"https://company.{random_sequence(4)}.com",
        "description": f"Description {random_sequence(4)}",
        "default_email": f"company.{random_sequence(4)}@home.com",
        "is_active": True,
        "is_public": False,
        "is_customer": True,
        "is_eep_sponsor": False,
        "auto_add_direct_relationships": False,
    }

    company_type = kwargs.pop("company_type", Company.GENERAL_COMPANY_TYPE)

    if kwargs.get("slug"):
        try:
            return Company.objects.get(slug=kwargs.get("slug"), company_type=company_type)
        except Company.DoesNotExist:
            pass

    if not city:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("city__"):
                c_kwrgs[re.sub(r"city__", "", k)] = kwargs.pop(k)
        kwrgs["city"] = city_factory(**c_kwrgs)
    else:
        kwrgs["city"] = city

    if kwrgs["city"].county:
        kwrgs["state"] = kwrgs["city"].county.state

    kwrgs.update(kwargs)

    name, city = kwrgs.pop("name"), kwrgs.pop("city")
    company, create = Company.objects.get_or_create(
        name=name, city=city, company_type=company_type, defaults=kwrgs
    )
    if create:
        if not counties and "state" in kwrgs:
            counties = list(County.objects.filter(state=kwrgs["state"]))[0:5]
        if counties:
            company.counties.add(*counties)

        if not countries:
            countries = [get_usa_default()]
        company.countries.add(*countries)

        # Don't depend on celery for this as time is essential.
        update_company_groups(company.id)
        company = Company.objects.get(id=company.id)
    return company


def rater_organization_factory(**kwargs):
    """A rater factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Rating Org {random_sequence(4)}")
    kwargs["company_type"] = "rater"
    kwargs["is_sample_eligible"] = True
    kwargs["certification_number"] = kwargs.get("certification_number", None)
    return base_company_factory(**kwargs)


def provider_organization_factory(**kwargs):
    """A provider factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["company_type"] = "provider"
    kwargs["name"] = kwargs.get("name", f"Provider Org {random_sequence(4)}")
    kwargs["is_sample_eligible"] = kwargs.get("is_sample_eligible", True)
    kwargs["provider_id"] = kwargs.get("provider_id", f"{random_digits(4)}-{random_digits(3)}")
    kwargs["auto_submit_to_registry"] = kwargs.get("auto_submit_to_registry", False)
    return base_company_factory(**kwargs)


def utility_organization_factory(**kwargs):
    """A utility factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Utility Org {random_sequence(4)}")
    kwargs["company_type"] = "utility"
    kwargs["electricity_provider"] = kwargs.get("electricity_provider", bool(random.getrandbits(1)))
    kwargs["gas_provider"] = kwargs.get("gas_provider", bool(random.getrandbits(1)))
    kwargs["water_provider"] = kwargs.get("water_provider", bool(random.getrandbits(1)))
    return base_company_factory(**kwargs)


def eep_organization_factory(**kwargs):
    """A eep factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Program Sponsor {random_sequence(4)}")
    kwargs["company_type"] = "eep"
    kwargs["is_eep_sponsor"] = True
    return base_company_factory(**kwargs)


def builder_organization_factory(**kwargs):
    """A builder factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Builder {random_sequence(4)}")
    kwargs["company_type"] = "builder"
    return base_company_factory(**kwargs)


def hvac_organization_factory(**kwargs):
    """A hvac factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"HVAC Org {random_sequence(4)}")
    kwargs["company_type"] = "hvac"
    kwargs["hquito_accredited"] = kwargs.get(
        "hquito_accredited", random.choice([None, True, False])
    )
    return base_company_factory(**kwargs)


def qa_organization_factory(**kwargs):
    """A qa factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"QA Org {random_sequence(4)}")
    kwargs["company_type"] = "qa"
    return base_company_factory(**kwargs)


def architect_organization_factory(**kwargs):
    """A general factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Architect Org {random_sequence(4)}")
    kwargs["company_type"] = "architect"
    return base_company_factory(**kwargs)


def developer_organization_factory(**kwargs):
    """A general factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Developer Org {random_sequence(4)}")
    kwargs["company_type"] = "developer"
    return base_company_factory(**kwargs)


def communityowner_organization_factory(**kwargs):
    """A general factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"Community Owner Org {random_sequence(4)}")
    kwargs["company_type"] = "communityowner"
    return base_company_factory(**kwargs)


def general_organization_factory(**kwargs):
    """A general factory.  get_or_create based on the field 'name', 'company_type', 'city'."""
    kwargs["name"] = kwargs.get("name", f"General Org {random_sequence(4)}")
    kwargs["company_type"] = "general"
    return base_company_factory(**kwargs)


def company_access_factory(company, user, **kwargs):
    is_company_admin_role = company_role_factory(
        name="Is Company Admin", slug=CompanyRole.IS_COMPANY_ADMIN
    )
    kwrgs = {
        "roles": [
            is_company_admin_role,
        ],
    }
    kwrgs.update(kwargs)

    roles = kwrgs.pop("roles")
    company_access, create = CompanyAccess.objects.get_or_create(
        company=company, user=user, defaults=kwrgs
    )
    company_access.roles.set(roles)
    return company_access


def company_role_factory(**kwargs):
    kwrgs = {"name": f"{random_sequence(4)}", "slug": f"role_{random_sequence(4)}"}
    kwrgs.update(kwargs)
    company, create = CompanyRole.objects.get_or_create(slug=kwrgs["slug"], defaults=kwrgs)
    return company
