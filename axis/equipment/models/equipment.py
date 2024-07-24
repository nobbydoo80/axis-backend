"""equipment.py: """


from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone

from axis.equipment.managers import EquipmentQuerySet
from axis.equipment.states import EquipmentSponsorStatusStates

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 16:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class Equipment(models.Model):
    """Equipment"""

    MANOMETER_EQUIPMENT_TYPE = 3
    BLOWER_DOOR_FAN_EQUIPMENT_TYPE = 1
    LASER_TAPE_MEASURE_EQUIPMENT_TYPE = 2

    EQUIPMENT_TYPE_CHOICES = (
        (MANOMETER_EQUIPMENT_TYPE, "Manometer"),
        (BLOWER_DOOR_FAN_EQUIPMENT_TYPE, "Blower Door Fan"),
        (LASER_TAPE_MEASURE_EQUIPMENT_TYPE, "Laser Tape Measure"),
    )

    ANNUAL_CALIBRATION_CYCLE = 3
    EVERY_2_YEARS_CALIBRATION_CYCLE = 1
    EVERY_3_YEARS_CALIBRATION_CYCLE = 2

    CALIBRATION_CYCLE_CHOICES = (
        (ANNUAL_CALIBRATION_CYCLE, "Annual"),
        (EVERY_2_YEARS_CALIBRATION_CYCLE, "Every 2 years"),
        (EVERY_3_YEARS_CALIBRATION_CYCLE, "Every 3 years"),
    )

    CALIBRATION_CYCLE_TIMEDELTA_MAP = {
        ANNUAL_CALIBRATION_CYCLE: relativedelta(years=1),
        EVERY_2_YEARS_CALIBRATION_CYCLE: relativedelta(years=2),
        EVERY_3_YEARS_CALIBRATION_CYCLE: relativedelta(years=3),
    }

    owner_company = models.ForeignKey(
        "company.Company", related_name="equipments", on_delete=models.CASCADE
    )
    sponsors = models.ManyToManyField("company.Company", through="EquipmentSponsorStatus")
    equipment_type = models.PositiveSmallIntegerField(
        verbose_name="Equipment Type",
        choices=EQUIPMENT_TYPE_CHOICES,
        default=MANOMETER_EQUIPMENT_TYPE,
    )
    brand = models.CharField(max_length=255)
    equipment_model = models.CharField(verbose_name="Model", max_length=255)
    serial = models.CharField(max_length=255)
    description = models.TextField()
    calibration_date = models.DateField(verbose_name="Calibration Date")
    calibration_cycle = models.PositiveSmallIntegerField(
        verbose_name="Calibration Cycle",
        choices=CALIBRATION_CYCLE_CHOICES,
        default=ANNUAL_CALIBRATION_CYCLE,
    )
    calibration_company = models.CharField(verbose_name="Calibration Company", max_length=255)
    calibration_documentation = models.FileField(
        verbose_name="Calibration Documentation", null=True, blank=True
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name="Assigned to", related_name="equipment_assigned"
    )

    notes = models.TextField(blank=True)
    expired_equipment = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Link to previous expired " "version of this equipment",
    )

    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    objects = EquipmentQuerySet.as_manager()

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"

    def __str__(self):
        return (
            "{equipment_type} "
            "{brand}/"
            "{equipment_model}/"
            "{serial}".format(
                equipment_type=self.get_equipment_type_display(),
                brand=self.brand,
                equipment_model=self.equipment_model,
                serial=self.serial,
            )
        )

    def get_absolute_url(self):
        return "{}#/tabs/equipment".format(
            reverse_lazy(
                "company:view",
                kwargs={"type": self.owner_company.company_type, "pk": self.owner_company.pk},
            )
        )

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        if (
            user.company == self.owner_company
            and not self.equipmentsponsorstatus_set.exclude(
                state=EquipmentSponsorStatusStates.NEW
            ).exists()
        ):
            return True

        if (
            user.company.slug
            in user.equipmentsponsorstatus_set.values_list("company__slug", flat=True).distinct()
        ):
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if (
            user.company == self.owner_company
            and not self.equipmentsponsorstatus_set.exclude(
                state=EquipmentSponsorStatusStates.NEW
            ).exists()
        ):
            return True

        if (
            user.company.slug
            in user.equipmentsponsorstatus_set.values_list("company__slug", flat=True).distinct()
        ):
            return True

        return False

    def get_expiration_date(self):
        if self.calibration_date:
            return (
                self.calibration_date + self.CALIBRATION_CYCLE_TIMEDELTA_MAP[self.calibration_cycle]
            )
        return None

    def is_expired(self):
        if self.calibration_date:
            date_diff = (
                timezone.now().date() - self.CALIBRATION_CYCLE_TIMEDELTA_MAP[self.calibration_cycle]
            )
            if self.calibration_date < date_diff:
                return True
        return False
