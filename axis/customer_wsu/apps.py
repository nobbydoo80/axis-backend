"""apps.py: """

from django.conf import settings

from axis.core import customers

__author__ = "Artem Hruzd"
__date__ = "11/25/2020 22:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


settings = getattr(settings, "CUSTOMER_WSU", {})


class CustomerWSUConfig(customers.CustomerAppConfig):
    name = "axis.customer_wsu"
    CUSTOMER_SLUG = "provider-washington-state-university-extension-ene"

    HERS_BROCHURE_PROGRAM_SLUGS = [
        "wsu-hers-2020",
    ]
