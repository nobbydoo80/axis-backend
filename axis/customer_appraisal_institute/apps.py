from django.conf import settings

from axis.core import customers

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "CUSTOMER_APPRAISAL_INSTITUTE", {})


class CustomerAppraisalInstituteConfig(customers.CustomerAppConfig):
    """Customer GP configuration."""

    name = "axis.customer_appraisal_institute"
