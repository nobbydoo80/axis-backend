"""factories.py: Django """


import logging
import re

from axis.hes.models import HESCredentials

__author__ = "Steven K"
__date__ = "11/20/2019 16:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def HESCredentialFactory(**kwargs):
    from axis.core.tests.factories import rater_admin_factory

    user = kwargs.pop("user", None)

    if user is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("user__"):
                _kwrgs[re.sub(r"user__", "", k)] = kwargs.pop(k)
        user = rater_admin_factory(**_kwrgs)

    kw = {
        "user": user,
        "company": user.company,
        "username": kwargs.get("username", "username"),
        "password": kwargs.get("password", "password"),
    }
    return HESCredentials.objects.create(**kw)
