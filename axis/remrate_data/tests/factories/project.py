"""project.py: Django factories"""


import random

from .utils import random_digits, random_sequence
from ...models import Project

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def project_factory(**kwargs):
    """A Project Factory"""

    phone = f"{random_digits(3)}-{random_digits(3)}-{random_digits(4)}"

    kwrgs = {
        "_result_number": int(random_digits(6)),
        "_building_number": int(random_digits(6)),
        "name": f"Name {random_sequence()}",
        "property_owner": f"Owner {random_sequence()}",
        "property_address": f"{random_digits(3)} W. {random_sequence(4)} St",
        "property_city": f"City {random_sequence(4)}",
        "property_state": random.choice(["AZ", "NM", "WI", "CO"]),
        "property_zip": random_digits(5),
        "property_phone": phone,
        "builder_permit": f"{random_digits(3)}-{random_digits(3)}",
        "builder_name": f"Builder {random_sequence(4)}",
        "builder_address": f"{random_digits(3)} E. {random_digits(4)} Builder St",
        "builder_address2": random_digits(3),
        "builder_email": f"{random_sequence(4)}@bldr.com",
        "builder_phone": phone,
        "builder_model": f"Builder Model {random_sequence(4)}",
        "builder_development": f"Development {random_sequence(4)}",
        "rating_organization": f"Rating Org {random_sequence(4)}",
        "rating_organization_address": f"{random_digits(3)} S. {random_sequence(4)} Rater St",
        "rating_organization_city": f"Rater City {random_sequence(4)}",
        "rating_organization_state": f"Rater State {random_sequence(4)}",
        "rating_organization_zip": f"Rater Zip {random_digits(5)}",
        "rating_organization_phone": phone,
        "rating_organization_website": f"www.{random_sequence(4)}.com",
        "provider_id": f"{random_digits(3)}-{random_digits(4)}",
        "rater_name": f"Builder {random_sequence(4)}",
        "rater_id": random_digits(7),
        "rater_email": f"{random_sequence(4)}@rater.com",
        "rating_date": "2014",
        "rating_number": f"{random_sequence(4)}-{random_digits(10)}",
        "rating_type": "Confirmed Rating",
        "rating_reason": "Final",
        "sampleset_id": "",
        "resnet_registry_id": random_digits(9),
    }

    if not kwargs.get("building"):
        raise NotImplemented("Circular not supported - Start with Simulation")

    kwrgs.update(kwargs)
    _result_number = kwrgs.pop("_result_number")
    return Project.objects.get_or_create(_result_number=_result_number, defaults=kwrgs)[0]
