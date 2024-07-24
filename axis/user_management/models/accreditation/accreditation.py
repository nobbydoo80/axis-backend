"""accreditation.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2019 13:25"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from simple_history.models import HistoricalRecords

from axis.user_management.managers import AccreditationQuerySet

User = get_user_model()


class Accreditation(models.Model):
    ANNUAL_ACCREDITATION_CYCLE = 1
    EVERY_2_YEARS_ACCREDITATION_CYCLE = 2
    EVERY_3_YEARS_ACCREDITATION_CYCLE = 3
    EVERY_4_YEARS_ACCREDITATION_CYCLE = 4

    MODELER_ROLE = 1
    VERIFIER_ROLE = 2
    SENIOR_ROLE = 3
    RFI_ROLE = 4
    QA_ROLE = 5

    INACTIVE_STATE = 1
    ACTIVE_STATE = 2
    PROBATION_NEW_STATE = 3
    PROBATION_DISCIPLINARY_STATE = 4
    SUSPENDED_ADMINISTRATIVE_STATE = 5
    SUSPENDED_DISCIPLINARY_STATE = 6
    TERMINATED_ADMINISTRATIVE_STATE = 7
    TERMINATED_DISCIPLINARY_STATE = 8

    ACCREDITATION_CYCLE_CHOICES = (
        (ANNUAL_ACCREDITATION_CYCLE, "Annual"),
        (EVERY_2_YEARS_ACCREDITATION_CYCLE, "Every 2 years"),
        (EVERY_3_YEARS_ACCREDITATION_CYCLE, "Every 3 years"),
        (EVERY_4_YEARS_ACCREDITATION_CYCLE, "Every 4 years"),
    )

    ACCREDITATION_CYCLE_TIMEDELTA_MAP = {
        ANNUAL_ACCREDITATION_CYCLE: relativedelta(years=1),
        EVERY_2_YEARS_ACCREDITATION_CYCLE: relativedelta(years=2),
        EVERY_3_YEARS_ACCREDITATION_CYCLE: relativedelta(years=3),
        EVERY_4_YEARS_ACCREDITATION_CYCLE: relativedelta(years=4),
    }

    ROLE_CHOICES = (
        (MODELER_ROLE, "Energy Modeler"),
        (VERIFIER_ROLE, "Verifier"),
        (SENIOR_ROLE, "Rater/Verifier"),
        (RFI_ROLE, "Rating Field Inspector"),
        (QA_ROLE, "QA Designee"),
    )

    STATE_CHOICES = (
        (INACTIVE_STATE, "Inactive"),
        (ACTIVE_STATE, "Active"),
        (PROBATION_NEW_STATE, "Probation – New"),
        (PROBATION_DISCIPLINARY_STATE, "Probation – Disciplinary"),
        (SUSPENDED_ADMINISTRATIVE_STATE, "Suspended – Administrative"),
        (SUSPENDED_DISCIPLINARY_STATE, "Suspended – Disciplinary"),
        (TERMINATED_ADMINISTRATIVE_STATE, "Terminated – Administrative"),
        (TERMINATED_DISCIPLINARY_STATE, "Terminated – Disciplinary (Revoked)"),
    )

    NGBS_2020_NAME = "ngbs-2020"
    NGBS_2015_NAME = "ngbs-2015"
    NGBS_2012_NAME = "ngbs-2012"
    NGBS_2008_NAME = "ngbs-2008"
    MASTER_VERIFIER_NAME = "master-verifier"
    NGBS_WRI_VERIFIER_NAME = "ngbs-wri-verifier"
    NGBS_GREEN_FIELD_REP_NAME = "ngbs-green-field-rep"

    NAME_CHOICES = (
        (NGBS_2020_NAME, "NGBS 2020"),
        (NGBS_2015_NAME, "NGBS 2015"),
        (NGBS_2012_NAME, "NGBS 2012"),
        (MASTER_VERIFIER_NAME, "NGBS Master Verifier"),
        (NGBS_WRI_VERIFIER_NAME, "NGBS WRI Verifier"),
        (NGBS_GREEN_FIELD_REP_NAME, "NGBS Green Field Rep"),
    )

    trainee = models.ForeignKey(User, related_name="accreditations", on_delete=models.CASCADE)
    name = models.CharField(max_length=45, choices=NAME_CHOICES)
    accreditation_id = models.CharField(
        verbose_name="Accreditation ID",
        max_length=255,
    )
    role = models.SmallIntegerField(choices=ROLE_CHOICES, default=MODELER_ROLE)
    state = models.SmallIntegerField(
        verbose_name="Accreditation Status", choices=STATE_CHOICES, default=INACTIVE_STATE
    )
    state_changed_at = models.DateTimeField(null=True, blank=True)
    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="approved_accreditations",
        help_text="User who approved this accreditation",
    )
    accreditation_cycle = models.SmallIntegerField(
        verbose_name="Accreditation Cycle",
        choices=ACCREDITATION_CYCLE_CHOICES,
        default=ANNUAL_ACCREDITATION_CYCLE,
    )
    date_initial = models.DateField(
        verbose_name="Initial Accreditation Date", null=True, blank=True
    )
    date_last = models.DateField(
        verbose_name="Most Recent Accreditation Date", null=True, blank=True
    )
    manual_expiration_date = models.DateField(
        verbose_name="Accreditation Expiration",
        help_text="If not set then expiration date will be "
        'calculated automatically based on "Most Recent Accreditation Date" and "Accreditation Cycle"',
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()
    objects = AccreditationQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return "{name} {accreditation_id}".format(
            name=self.get_name_display(),
            accreditation_id=self.accreditation_id,
        )

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Accreditation, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, **kwargs):
        original = dict()
        if hasattr(self, "_loaded_values"):
            original = self._loaded_values

        if original.get("state") != self.state:
            self.state_changed_at = timezone.now()
        return super(Accreditation, self).save(**kwargs)

    def get_absolute_url(self):
        return "{}#/tabs/training".format(
            reverse_lazy("profile:detail", kwargs={"pk": self.trainee.pk})
        )

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        if user.company == self.approver.company:
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if user.company == self.approver.company:
            return True

        return False

    def get_expiration_date(self):
        if self.manual_expiration_date:
            return self.manual_expiration_date

        if self.date_last:
            return self.date_last + self.ACCREDITATION_CYCLE_TIMEDELTA_MAP[self.accreditation_cycle]
        return None

    def is_expired(self):
        if self.manual_expiration_date:
            if self.manual_expiration_date < timezone.now().date():
                return True
            else:
                return False

        if self.date_last:
            date_diff = (
                timezone.now().date()
                - self.ACCREDITATION_CYCLE_TIMEDELTA_MAP[self.accreditation_cycle]
            )
            if self.date_last < date_diff:
                return True
        return False
