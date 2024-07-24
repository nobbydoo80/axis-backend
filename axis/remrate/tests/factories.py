"""factories.py: Django remrate"""


import logging
import re

from axis.core.utils import random_sequence
from axis.company.tests.factories import rater_organization_factory
from ..models import RemRateUser

__author__ = "Steven Klass"
__date__ = "11/16/13 6:44 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def remrate_user_factory(**kwargs):
    """A remrate user factory.  get_or_create based on the field 'username'."""
    company = kwargs.pop("company", None)
    if not company:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = rater_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company
    username = kwargs.pop("username", f"user_{random_sequence(4)}")
    remrateuser, create = RemRateUser.objects.get_or_create(username=username, defaults=kwargs)
    return remrateuser
