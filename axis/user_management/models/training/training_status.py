"""EquipmentCompanyStatus.py: """


from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords

from axis.user_management.messages import TrainingStatusStateChangedMessage
from axis.user_management.states import TrainingStatusStates

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 16:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingStatus(models.Model):
    training = models.ForeignKey("Training", on_delete=models.CASCADE)
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    approver = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.CASCADE)
    state_changed_at = models.DateTimeField(null=True, blank=True)
    state = FSMField(default=TrainingStatusStates.NEW, choices=TrainingStatusStates.choices)
    state_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        unique_together = ("training", "company")

    def __str__(self):
        return "Training <{training}> state <{state}> from company <{company}>".format(
            training=self.training,
            state=TrainingStatusStates.verbose_names.get(self.state),
            company=self.company,
        )

    # Transitions

    @transition(field=state, source=TrainingStatusStates.NEW, target=TrainingStatusStates.APPROVED)
    def approve(self, user, state_notes=""):
        self.approver = user
        self.state_changed_at = timezone.now()
        self.state_notes = state_notes
        TrainingStatusStateChangedMessage(
            url=reverse_lazy("profile:detail", kwargs={"pk": self.training.trainee.pk})
        ).send(
            user=self.training.trainee,
            context={
                "trainee": self.training.trainee,
                "url": reverse_lazy("profile:detail", kwargs={"pk": self.training.trainee.pk}),
                "training": self.training,
                "old_state": self.state,
                "new_state": TrainingStatusStates.APPROVED,
            },
        )

    @transition(
        field=state,
        source=[TrainingStatusStates.NEW, TrainingStatusStates.APPROVED],
        target=TrainingStatusStates.REJECTED,
    )
    def reject(self, user, state_notes=""):
        self.approver = user
        self.state_changed_at = timezone.now()
        self.state_notes = state_notes
        TrainingStatusStateChangedMessage(
            url=reverse_lazy("profile:detail", kwargs={"pk": self.training.trainee.pk})
        ).send(
            user=self.training.trainee,
            context={
                "trainee": self.training.trainee,
                "url": reverse_lazy("profile:detail", kwargs={"pk": self.training.trainee.pk}),
                "training": self.training,
                "old_state": self.state,
                "new_state": TrainingStatusStates.REJECTED,
            },
        )

    @transition(
        field=state,
        source=[TrainingStatusStates.NEW, TrainingStatusStates.APPROVED],
        target=TrainingStatusStates.EXPIRED,
    )
    def expire(self, user=None, state_notes=""):
        self.approver = user
        self.state_changed_at = timezone.now()
        self.state_notes = state_notes
        TrainingStatusStateChangedMessage(
            url=reverse_lazy("profile:detail", kwargs={"pk": self.training.trainee.pk})
        ).send(
            user=self.training.trainee,
            context={
                "trainee": self.training.trainee,
                "url": reverse_lazy("profile:detail", kwargs={"pk": self.training.trainee.pk}),
                "training": self.training,
                "old_state": self.state,
                "new_state": TrainingStatusStates.EXPIRED,
            },
        )
