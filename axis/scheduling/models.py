"""models.py: Django scheduling"""

__author__ = "Gaurav Kapoor"
__date__ = "6/25/12 9:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Gaurav Kapoor",
    "Steven Klass",
]

import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import SET_NULL
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords

from .managers import (
    ConstructionStageManager,
    ConstructionStatusManager,
    TaskTypeManager,
    TaskManager,
)


class ConstructionStage(models.Model):
    """Defines the Construction Stages for a home"""

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(unique=True)
    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    objects = ConstructionStageManager()

    class Meta:
        """Non-Field options"""

        ordering = ("order",)

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        return self.name

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("construction_stage_detail", kwargs={"pk": self.id})


class ConstructionStatus(models.Model):
    """This is used to track the current construction stage of a home"""

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    stage = models.ForeignKey("ConstructionStage", on_delete=models.CASCADE)
    home = models.ForeignKey("home.Home", on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=SET_NULL)
    objects = ConstructionStatusManager()
    history = HistoricalRecords()

    def __str__(self):
        return "{}".format(self.stage)

    class Meta:
        """Non-Field options"""

        verbose_name_plural = "Construction Status"
        get_latest_by = ("stage__order", "-pk")


class TaskType(models.Model):
    """A type of Task a company is allowed to assign to a user."""

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField("Task Name", max_length=100)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    priority = models.IntegerField(default=0, help_text="Using for ordering items in list")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()
    objects = TaskTypeManager()

    class Meta:
        ordering = ("-priority", "-name")

    def __str__(self):
        return self.name

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if self.company is None:
            return False

        if self.company == user.company and user.is_company_admin:
            return True

        return False

    def can_be_edited(self, user):
        return self.can_be_deleted(user)


class Task(models.Model):
    SCHEDULED_CONFIRMED_STATUS = "scheduled_confirmed"
    SCHEDULED_TENTATIVE_STATUS = "scheduled_tentative"
    COMPLETED_STATUS = "completed"
    POSTPONED_STATUS = "postponed"
    CANCELLED_STATUS = "cancelled"

    TASK_STATUS_CHOICES = (
        (SCHEDULED_CONFIRMED_STATUS, "Scheduled (Confirmed)"),
        (SCHEDULED_TENTATIVE_STATUS, "Scheduled (Tentative)"),
        (COMPLETED_STATUS, "Completed"),
        (POSTPONED_STATUS, "Postponed"),
        (CANCELLED_STATUS, "Cancelled"),
    )

    APPROVAL_STATE_NEW = "new"
    APPROVAL_STATE_APPROVED = "approved"
    APPROVAL_STATE_REJECTED = "rejected"

    APPROVAL_STATE_CHOICES = (
        (APPROVAL_STATE_NEW, "New (Unapproved)"),
        (APPROVAL_STATE_APPROVED, "Approved"),
        (APPROVAL_STATE_REJECTED, "Rejected"),
    )

    STATE_METHODS_MAP = {
        APPROVAL_STATE_APPROVED: "approve",
        APPROVAL_STATE_NEW: "new",
        APPROVAL_STATE_REJECTED: "reject",
    }

    task_type = models.ForeignKey("scheduling.TaskType", on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    assigner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Assigner",
        related_name="tasks_created",
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Assigned To",
        related_name="tasks_assigned",
        blank=True,
    )
    status = models.CharField("Status", choices=TASK_STATUS_CHOICES, max_length=25)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Status approver",
        related_name="task_status_approver",
    )
    status_annotation = models.TextField(blank=True)
    note = models.TextField("Note", blank=True, null=True)
    is_public = models.BooleanField("is public", default=False)

    approval_state_changed_at = models.DateTimeField(null=True, blank=True)
    approval_state = FSMField(default=APPROVAL_STATE_NEW, choices=APPROVAL_STATE_CHOICES)
    approval_annotation = models.TextField(blank=True)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Approver",
    )

    # objects where we can attach Task
    home = models.ForeignKey(
        "home.Home",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()
    objects = TaskManager()

    class Meta:
        """Non-Field options"""

        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return "Task #{}".format(self.id)

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if self.assigner.company == user.company and user.is_company_admin:
            return True

        return False

    def can_be_edited(self, user):
        if user in self.assignees.all():
            return True

        return self.can_be_deleted(user)

    @property
    def event_datetime(self):
        """The combined event_date and event_time (or 10 A.M if unset)."""
        return datetime.datetime.combine(
            self.date,
            self.time if self.time is not None else datetime.time(hour=10, minute=0, second=0),
        )

    # Transitions

    @transition(field=approval_state, source=APPROVAL_STATE_NEW, target=APPROVAL_STATE_APPROVED)
    def approve(self, user, approval_annotation=""):
        self.approver = user
        self.approval_state_changed_at = timezone.now()
        self.approval_annotation = approval_annotation

    @transition(
        field=approval_state,
        source=[APPROVAL_STATE_NEW, APPROVAL_STATE_APPROVED],
        target=APPROVAL_STATE_REJECTED,
    )
    def reject(self, user, approval_annotation):
        self.approver = user
        self.approval_state_changed_at = timezone.now()
        self.approval_annotation = approval_annotation

    def get_task_list_url(self):
        """
        Get task list location based on object attached to Task.
        :return: str url or empty str in case of new object
        """
        if self.home_id:
            return "{}#/tabs/tasks".format(reverse_lazy("home:view", kwargs={"pk": self.home_id}))
        return ""
