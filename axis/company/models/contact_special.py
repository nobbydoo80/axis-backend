"""contact_special.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

from django.apps import apps
from django.conf import settings
from django.db import models

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class Contact_SPECIAL(models.Model):
    """
    This model exists as a dummy object that we use to construct dynamic lists of virtual "contact"
    entries.  It should never actually have saved data in its database table.

    Previous this was marked as managed=False, but it turns out that deletion operations connected
    to Company and User were discovering this model as a source of related data that should be
    deleted, causing internal Django utilities to try to find the database table name (which never
    existed, due to the controlled circumstances.)

    This model's single purpose is to be a virtual "views-only" object that is at least model-like
    so that our DatatableView can treat this object as real.
    """

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return "Contact(company={}, user={})".format(
            self.company.name, getattr(self.user, "username", None)
        )

    def save(self, **kwargs):
        raise NotImplementedError
