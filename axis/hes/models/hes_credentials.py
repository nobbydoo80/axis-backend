import logging

from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords
from axis.core.fields import EncryptedCharField
from ..managers import HESQuerySet

__author__ = "Benjamin S"
__date__ = "6/8/2022 09:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin S",
]

log = logging.getLogger(__name__)


class HESCredentials(models.Model):
    """A container to store the user info for logging into HES"""

    user = models.OneToOneField(
        get_user_model(), related_name="hes_credentials", on_delete=models.CASCADE
    )
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    username = models.CharField(max_length=64, blank=True)
    password = EncryptedCharField(max_length=64, blank=True)

    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()
    objects = HESQuerySet.as_manager()
