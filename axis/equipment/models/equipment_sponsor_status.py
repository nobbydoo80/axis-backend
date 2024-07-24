"""EquipmentCompanyStatus.py: """

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 16:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords

from ..messages import EquipmentSponsorStatusStateChangedMessage
from ..states import EquipmentSponsorStatusStates


User = get_user_model()


class EquipmentSponsorStatus(models.Model):
    equipment = models.ForeignKey("Equipment", on_delete=models.CASCADE)
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    state_changed_at = models.DateTimeField(null=True, blank=True)
    state = FSMField(
        default=EquipmentSponsorStatusStates.NEW, choices=EquipmentSponsorStatusStates.choices
    )
    state_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        unique_together = ("equipment", "company")

    def __str__(self):
        return "Equipment <{equipment}> state <{state}> from company <{company}>".format(
            equipment=self.equipment,
            state=EquipmentSponsorStatusStates.verbose_names.get(self.state),
            company=self.company,
        )

    # Transitions

    @transition(
        field=state,
        source=EquipmentSponsorStatusStates.NEW,
        target=EquipmentSponsorStatusStates.ACTIVE,
    )
    def active(self, user, state_notes=""):
        self.approver = user
        self.state_changed_at = timezone.now()
        self.state_notes = state_notes
        EquipmentSponsorStatusStateChangedMessage().send(
            company=self.equipment.owner_company,
            context={
                "owner_company": self.equipment.owner_company,
                "url": reverse_lazy(
                    "company:view",
                    kwargs={
                        "type": self.equipment.owner_company.company_type,
                        "pk": self.equipment.owner_company.pk,
                    },
                ),
                "equipment": self.equipment,
                "old_state": self.state,
                "new_state": EquipmentSponsorStatusStates.ACTIVE,
            },
        )

    @transition(
        field=state,
        source=[EquipmentSponsorStatusStates.NEW, EquipmentSponsorStatusStates.ACTIVE],
        target=EquipmentSponsorStatusStates.REJECTED,
    )
    def reject(self, user, state_notes=""):
        self.approver = user
        self.state_changed_at = timezone.now()
        self.state_notes = state_notes
        EquipmentSponsorStatusStateChangedMessage().send(
            company=self.equipment.owner_company,
            context={
                "owner_company": self.equipment.owner_company,
                "url": reverse_lazy(
                    "company:view",
                    kwargs={
                        "type": self.equipment.owner_company.company_type,
                        "pk": self.equipment.owner_company.pk,
                    },
                ),
                "equipment": self.equipment,
                "old_state": self.state,
                "new_state": EquipmentSponsorStatusStates.REJECTED,
            },
        )

    @transition(
        field=state,
        source=EquipmentSponsorStatusStates.ACTIVE,
        target=EquipmentSponsorStatusStates.EXPIRED,
    )
    def expire(self, user=None, state_notes=""):
        self.approver = user
        self.state_changed_at = timezone.now()
        self.state_notes = state_notes
        EquipmentSponsorStatusStateChangedMessage().send(
            company=self.equipment.owner_company,
            context={
                "owner_company": self.equipment.owner_company,
                "url": reverse_lazy(
                    "company:view",
                    kwargs={
                        "type": self.equipment.owner_company.company_type,
                        "pk": self.equipment.owner_company.pk,
                    },
                ),
                "equipment": self.equipment,
                "old_state": self.state,
                "new_state": EquipmentSponsorStatusStates.EXPIRED,
            },
        )
