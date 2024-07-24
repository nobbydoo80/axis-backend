"""factories.py: Django resnet"""


import logging
import datetime
from django.utils.timezone import now

from axis.core.utils import random_sequence, random_digits
from ..models import RESNETCompany


__author__ = "Steven Klass"
__date__ = "7/28/14 1:19 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ...geographic.tests.factories import real_city_factory

log = logging.getLogger(__name__)


def resnet_company_factory(**kwargs):
    """RESNET Company Factory"""
    phone = f"480-3{random_digits(2)}-{random_digits(4)}"

    company = kwargs.get("company", None)
    try:
        provider_id = company.provider_id
        if provider_id is None:
            raise AttributeError
    except AttributeError:
        provider_id = f"{random_digits(4)}-{random_digits(3)}"

    street_line1 = "123 E. Main St"
    street_line2 = None
    zipcode = "53094"

    if company:
        street_line1 = company.street_line1
        street_line2 = company.street_line2
        city = company.city.name
        state = company.city.county.state
        zipcode = company.zipcode
    else:
        _city = real_city_factory("Watertown", "WI")
        city = _city.name
        state = _city.county.state

    kwrgs = {
        "name": company.name if company else f"Company {random_sequence(4)}",
        "street_line1": street_line1,
        "street_line2": street_line2,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "office_phone": company.office_phone if company else phone,
        "office_fax": None,
        "home_page": company.home_page if company else f"https://company_{random_sequence(4)}.com",
        "is_rater": company.company_type == "rater" if company else False,
        "is_provider": company.company_type == "provider" if company else False,
        "is_sampling_provider": False,
        "is_training_provider": False,
        "is_watersense_provider": False,
        "provider_id": provider_id,
        "resnet_expiration": datetime.datetime(now().year, 12, 31),
    }

    kwrgs.update(kwargs)
    return RESNETCompany.objects.create(**kwrgs)
