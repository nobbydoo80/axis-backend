import logging
from collections import defaultdict

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse

from axis.core.fields import AxisJSONField
from . import validators
from .managers import ProjectQuerySet, HousePlanQuerySet

__author__ = "Autumn Valenta"
__date__ = "10/31/16 09:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EkotropeAuthDetails(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Auth for their API preview
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Ekotrope Auth Details"

    def __str__(self):
        return "{}{}".format(self.user, " ({})".format(self.id))


class RemoteObject(models.Model):
    """An object stub that supports late loading of data from the remote Ekotrope API."""

    id = models.CharField(max_length=8, primary_key=True, validators=[validators.validate_id])
    name = models.CharField(max_length=500, blank=True)
    data = AxisJSONField(default=dict)

    import_failed = models.BooleanField(default=False)
    import_error = models.CharField(max_length=500, blank=True, null=True)
    import_traceback = models.TextField(blank=True, null=True)
    import_request = models.TextField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Project(RemoteObject):
    objects = ProjectQuerySet.as_manager()

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    class Meta:
        pass

    def __str__(self):
        return "{}{}".format(
            self.name,
            " ({})".format(self.id) if self.name else self.id,
        )

    @property
    def climate_zone(self):
        from axis.geographic.strings import DOE_MOISTURE_REGIMES_MAP

        MOISTURE_MAP = {k.upper(): v for k, v in DOE_MOISTURE_REGIMES_MAP.items()}

        try:
            cz = self.data.get("location", {}).get("climateZone")
            return "%s" % cz.get("zone") + MOISTURE_MAP.get(cz.get("moistureRegime"))
        except KeyError:
            return "--"


class HousePlan(RemoteObject):
    objects = HousePlanQuerySet.as_manager()
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    class Meta:
        pass

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        return "{}{}".format(
            self.name,
            " ({})".format(self.id) if self.name else self.id,
        )

    def get_absolute_url(self):
        return reverse("floorplan:input:ekotrope", kwargs={"pk": self.pk})

    def can_be_deleted(self, user):
        """Can we delete this"""
        if user.is_superuser:
            return True
        try:
            payments = self.floorplan.homestatuses.filter(
                Q(incentivepaymentstatus__isnull=True)
                | ~Q(
                    incentivepaymentstatus__state__in=["start", "ipp_payment_failed_requirements"]
                ),
                certification_date__isnull=False,
            )
            if payments.count():
                return False
        except:
            pass

        # if user.is_company_admin and user.company == self.company:
        #     return True
        return False

    def can_be_edited(self, user):
        return False

    def get_validation_errors(self):
        errors = []
        if self.import_failed:
            if self.import_error:
                errors.append(self.import_error)
            else:
                errors.append("Houseplan import failure")
        try:
            if self.project.import_failed:
                if self.project.import_error:
                    errors.append(self.project.import_error)
                else:
                    errors.append("Project import failure")
        except AttributeError:
            errors.append("Missing associated project data")

        try:
            if self.analysis.import_failed:
                if self.analysis.import_error:
                    errors.append(self.analysis.import_error)
                else:
                    errors.append("Analysis import failure")
        except AttributeError:
            errors.append("Missing associated analysis data")

        return errors


class Analysis(RemoteObject):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    houseplan = models.OneToOneField("HousePlan", on_delete=models.CASCADE)

    class Meta:
        pass

    @property
    def compliances(self):
        """Turns the compliance list into a dictionary for easier lookups"""
        if not hasattr(self, "_compliances"):
            statuses = {
                "Pass": True,
                "Warn": "warn",
                "Fail": False,
                "NotChecked": None,
            }
            self._compliances = defaultdict(lambda: None)
            self._compliances.update(
                {
                    item["code"]: statuses[item["complianceStatus"]]
                    for item in self.data.get("compliance", [])
                }
            )
        return self._compliances
