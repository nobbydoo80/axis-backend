"""alt_name.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

from django.apps import apps
from django.db import models
from simple_history.models import HistoricalRecords

from axis.company import strings
from axis.company.managers import AltNameQueryset

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class AltName(models.Model):
    """Provides an alternate name for a target ``company``."""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    name = models.CharField(
        max_length=128, help_text=strings.SUBDIVISION_HELP_TEXT_ALTERNATIVE_NAMES
    )

    objects = AltNameQueryset.as_manager()
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        verbose_name = "Alternative Name"

    def __str__(self):
        return self.name

    @classmethod
    def can_be_added(self, user):
        return user.has_perm("company.add_altname")

    def can_be_edited(self, user):
        return user.has_perm("company.change_altname")

    def can_be_deleted(self, user):
        return user.has_perm("company.delete_altname")
