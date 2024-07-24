"""models.py - axis"""

__author__ = "Steven K"
__date__ = "1/10/23 08:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property

from django.conf import settings
from django.db import models
from django.db.models import TextChoices
from simple_history.models import HistoricalRecords


log = logging.getLogger(__name__)


class GbrStatus(TextChoices):
    NOT_STARTED = "Not yet started"
    LEGACY_IMPORT = "Imported from HES HPXML"
    PROPERTY_VALID = "Address created and valid"
    PROPERTY_INVALID = "Address creation failed"
    SERVICE_UNAVAILABLE = "GBR Service Unavailable"
    SERVICE_THROTTLED = "GBR Throttled"
    ASSESSMENT_CREATED = "Assessment Created"
    ASSESSMENT_INVALID = "Assessment Creation Failed"


class GreenBuildingRegistry(models.Model):
    home = models.OneToOneField("home.Home", related_name="gbr", on_delete=models.CASCADE)
    gbr_id = models.CharField(max_length=32, null=True)
    status = models.CharField(
        max_length=32, choices=GbrStatus.choices, default=GbrStatus.NOT_STARTED
    )
    api_result = models.JSONField(null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Green Building Registry Entry"
        verbose_name_plural = "Green Building Registry Entries"
        ordering = ("gbr_id",)

    def __str__(self):
        return f"{self.gbr_id or '-'} ({self.get_status_display()})"

    @cached_property
    def external_url(self) -> str:
        """https://us.greenbuildingregistry.com/green-homes/OR10207819"""
        """https://us-sandbox.greenbuildingregistry.com/green-homes/OR10174323"""
        if self.gbr_id and self.status == GbrStatus.ASSESSMENT_CREATED:
            sandbox = "" if settings.SERVER_TYPE == settings.PRODUCTION_SERVER_TYPE else "-sandbox"
            return f"https://us{sandbox}.greenbuildingregistry.com/green-homes/{self.gbr_id}"
        return ""
