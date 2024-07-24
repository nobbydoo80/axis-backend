"""training.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2019 12:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy
from simple_history.models import HistoricalRecords

from axis.user_management.states import TrainingStatusStates
from axis.user_management.managers import TrainingQuerySet


User = get_user_model()


class Training(models.Model):
    VOLUNTARY_TRAINING_TYPE = 1
    MANDATORY_TRAINING_TYPE = 2

    TRAINING_TYPE_CHOICES = (
        (VOLUNTARY_TRAINING_TYPE, "Voluntary"),
        (MANDATORY_TRAINING_TYPE, "Mandatory"),
    )

    IN_PERSON_ATTENDANCE_TYPE = 1
    REMOTE_ATTENDANCE_TYPE = 2
    ABSENT_ATTENDANCE_TYPE = 3

    ATTENDANCE_TYPE_CHOICES = (
        (IN_PERSON_ATTENDANCE_TYPE, "In-person"),
        (REMOTE_ATTENDANCE_TYPE, "Remote"),
        (ABSENT_ATTENDANCE_TYPE, "ABSENT"),
    )

    trainee = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Training Name", max_length=64)
    statuses = models.ManyToManyField("company.Company", through="TrainingStatus")
    address = models.CharField(
        verbose_name="Training Company or Conference",
        max_length=255,
        help_text="Name of company delivering training or "
        "conference where training credits were earned",
    )
    training_date = models.DateField()
    training_type = models.PositiveSmallIntegerField(
        verbose_name="Training Type", choices=TRAINING_TYPE_CHOICES, default=VOLUNTARY_TRAINING_TYPE
    )
    attendance_type = models.PositiveSmallIntegerField(
        verbose_name="Attendance",
        choices=ATTENDANCE_TYPE_CHOICES,
        default=IN_PERSON_ATTENDANCE_TYPE,
    )
    certificate = models.FileField(verbose_name="Certificate", null=True, blank=True)
    credit_hours = models.FloatField(verbose_name="Credit Hours")
    notes = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()
    objects = TrainingQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}#/tabs/training".format(
            reverse_lazy("profile:detail", kwargs={"pk": self.trainee.pk})
        )

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        if (
            user == self.trainee
            and not self.trainingstatus_set.exclude(state=TrainingStatusStates.NEW).exists()
        ):
            return True

        if (
            user.company.slug
            in user.trainingstatus_set.values_list("company__slug", flat=True).distinct()
        ):
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if (
            user == self.trainee
            and not self.trainingstatus_set.exclude(state=TrainingStatusStates.NEW).exists()
        ):
            return True

        if (
            user.company.slug
            in user.trainingstatus_set.values_list("company__slug", flat=True).distinct()
        ):
            return True

        return False
