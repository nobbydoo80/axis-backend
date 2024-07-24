"""utility_settings.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

from django.apps import apps
from django.db import models

from axis.company.models import Company

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class UtilitySettings(models.Model):
    """
    Connects to a relationship association and declares extra info about the usage of the utility
    company on a Home.
    """

    # Attaches to the relationship so that this information can be removed automatically if the
    # relationship is deleted.
    relationship = models.OneToOneField("relationship.Relationship", on_delete=models.CASCADE)

    # Hints about this utility in the context of the home it's been associated to.
    is_gas_utility = models.BooleanField(default=False)
    is_electric_utility = models.BooleanField(default=False)

    class Meta:
        # TODO: Migration to avoid having to declare this
        db_table = "home_utilitysettings"

    def save(self, *args, **kwargs):
        """Stops the save operation if the target company is not a utility."""
        if not self.relationship.company.company_type == Company.UTILITY_COMPANY_TYPE:
            raise ValueError("'{}' is not a UtilityOrganization.")
        super(UtilitySettings, self).save(*args, **kwargs)
