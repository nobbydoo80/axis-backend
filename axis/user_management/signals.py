"""Signals."""

__author__ = "Artem Hruzd"
__date__ = "1/17/19 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Artem Hruzd", "Steven Klass"]

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy

from axis.user_management.messages import (
    AccreditationCreatedTraineeMessage,
    AccreditationStateChangedTraineeMessage,
    InspectionGradeCreatedUserMessage,
)
from axis.user_management.models import Accreditation, InspectionGrade


log = logging.getLogger(__name__)


@receiver(post_save, sender=Accreditation)
def notify_accreditation_trainee(sender, instance, created=False, **kwargs):
    """
    Notify trainee user about new created accreditation or accreditation state changing
    """

    original = dict()
    if hasattr(instance, "_loaded_values"):
        original = instance._loaded_values

    if created:
        AccreditationCreatedTraineeMessage().send(
            user=instance.trainee,
            context={
                "approver_company": instance.approver.company.name,
                "url": reverse_lazy("profile:detail", kwargs={"pk": instance.trainee.pk}),
                "accreditation": instance.get_name_display(),
            },
        )
    elif instance.state != original.get("state"):
        old_state = dict(Accreditation.STATE_CHOICES).get(original.get("state"))
        AccreditationStateChangedTraineeMessage(
            url=reverse_lazy("profile:detail", kwargs={"pk": instance.trainee.pk})
        ).send(
            user=instance.trainee,
            context={
                "approver_company": instance.approver.company.name,
                "url": reverse_lazy("profile:detail", kwargs={"pk": instance.trainee.pk}),
                "old_state": old_state,
                "new_state": instance.get_state_display(),
                "accreditation": instance.get_name_display(),
            },
        )


@receiver(post_save, sender=InspectionGrade)
def notify_inspection_grade_user(sender, instance, created=False, **kwargs):
    """
    Notify user about new created inspection grade
    """
    if created:
        InspectionGradeCreatedUserMessage(
            url=reverse_lazy("profile:detail", kwargs={"pk": instance.user.pk})
        ).send(
            user=instance.user,
            context={
                "approver_company": instance.approver.company.name,
                "url": reverse_lazy("profile:detail", kwargs={"pk": instance.user.pk}),
                "inspection_grade": instance.display_grade(),
            },
        )
