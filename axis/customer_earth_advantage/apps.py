from django.conf import settings

from axis.core import customers
from .appraisal_addendum import AppraisalAddendumConfig

__author__ = "Autumn Valenta"
__date__ = "10-10-2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "CUSTOMER_EARTH_ADVANTAGE", {})


class CustomerEarthAdvantageConfig(customers.CustomerAppConfig):
    """Customer Earth Advantage configuration."""

    name = "axis.customer_earth_advantage"
    extensions = (AppraisalAddendumConfig,)
