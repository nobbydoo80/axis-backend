"""models.py: Django qa"""

__author__ = "Steven Klass"
__date__ = "12/20/13 6:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
from typing import Optional
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import formats
from django.utils.timezone import now
from django_states.models import StateModel
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.customer_hirl.models import HIRLGreenEnergyBadge
from axis.home.models import EEPProgramHomeStatus
from axis.qa.messages import QADesigneeAssigneeMessage, CustomerHIRLQADesigneeAssigneeMessage
from .managers import (
    QAStatusManager,
    QARequirementQuerySet,
    ObservationManager,
    ObservationTypeManager,
)
from .state_machine import QAStateMachine
from .utils import qa_state_change_handler

if TYPE_CHECKING:
    User = get_user_model()

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class QARequirement(models.Model):
    """The defines the requirements for QA in a broad sense. It is not necessarily required"""

    FILE_QA_REQUIREMENT_TYPE = "file"
    FIELD_QA_REQUIREMENT_TYPE = "field"
    PROGRAM_REVIEW_QA_REQUIREMENT_TYPE = "program_review"
    ROUGH_INSPECTION_QA_REQUIREMENT_TYPE = "rough_inspection_qa"
    ROUGH_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE = "rough_inspection_virtual_audit"
    FINAL_INSPECTION_QA_REQUIREMENT_TYPE = "final_inspection_qa"
    DESKTOP_AUDIT_REQUIREMENT_TYPE = "desktop_audit"
    FINAL_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE = "final_inspection_virtual_audit"

    QA_REQUIREMENT_TYPES = (
        (FILE_QA_REQUIREMENT_TYPE, "File"),
        (FIELD_QA_REQUIREMENT_TYPE, "Field"),
        (PROGRAM_REVIEW_QA_REQUIREMENT_TYPE, "Program Review"),
        (ROUGH_INSPECTION_QA_REQUIREMENT_TYPE, "Rough Inspection"),
        (ROUGH_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE, "Rough Inspection Virtual Audit"),
        (FINAL_INSPECTION_QA_REQUIREMENT_TYPE, "Final Inspection"),
        (DESKTOP_AUDIT_REQUIREMENT_TYPE, "Desktop Audit"),
        (FINAL_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE, "Final Inspection Virtual Audit"),
    )
    qa_company = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    required_companies = models.ManyToManyField(
        "company.Company", related_name="enabled_qa_requirements", blank=True
    )
    coverage_pct = models.FloatField(
        default=0.20, validators=[MinValueValidator(0.0), MaxValueValidator(1)]
    )
    gate_certification = models.BooleanField(default=False)
    eep_program = models.ForeignKey("eep_program.EEPProgram", on_delete=models.CASCADE)
    type = models.CharField(choices=QA_REQUIREMENT_TYPES, max_length=64)

    objects = QARequirementQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "QA Requirement"
        verbose_name_plural = "QA Requirements"

    def __str__(self):
        return "{type} QA for {eep_program} - {company}".format(
            type=self.get_type_display(), eep_program=self.eep_program, company=self.qa_company
        )

    def can_be_edited(self, user):
        if user.is_superuser:
            return True
        return user.company.id == self.company.id

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True
        return user.company.id == self.company.id

    def get_active_coverage_pct(self):
        """This looks at homes which are not yet certified"""
        total_stats = EEPProgramHomeStatus.objects.filter_by_company(
            self.qa_company, certification_date__isnull=True
        )
        completed_qa = total_stats.filter(qastatus__requirement=self)
        try:
            return float(completed_qa.count()) / float(total_stats.count())
        except ZeroDivisionError:
            return float(0)

    def get_yearly_coverage_pct(self, year=None):
        """This will get the current pct coverage.  Coverage periods are based on the
        completion date of the qa."""

        if year is None:
            year = now().year

        start = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)

        total_stats = EEPProgramHomeStatus.objects.filter_by_company(
            self.qa_company, certification_date__gte=start, certification_date__lt=end
        )

        completed_qa = total_stats.filter(
            qastatus__requirement=self, qastatus__result__isnull=False
        )
        try:
            return float(completed_qa.count()) / float(total_stats.count())
        except ZeroDivisionError:
            return float(0)


class QAStatus(StateModel):
    """The defines the QA State of an EEP Program Home Status"""

    PASS_STATUS = "pass"
    FAIL_STATUS = "fail"

    STATUS = ((PASS_STATUS, "Pass"), (FAIL_STATUS, "Fail"))

    EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED = "emerald"
    GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED = "gold"
    SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED = "silver"
    BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED = "bronze"
    CERTIFIED_HIRL_CERTIFICATION_LEVEL_AWARDED = "certified"
    CONFORMING_HIRL_CERTIFICATION_LEVEL_AWARDED = "conforming"
    ONE_STAR_HIRL_CERTIFICATION_LEVEL_AWARDED = "one_star"
    TWO_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED = "two_stars"
    THREE_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED = "three_stars"
    FOUR_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED = "four_stars"

    HIRL_CERTIFICATION_LEVEL_AWARDED_CHOICES = (
        (BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
        (SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
        (GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
        (EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
        (CERTIFIED_HIRL_CERTIFICATION_LEVEL_AWARDED, "Certified"),
        (CONFORMING_HIRL_CERTIFICATION_LEVEL_AWARDED, "Conforming"),
        (ONE_STAR_HIRL_CERTIFICATION_LEVEL_AWARDED, "One Star"),
        (TWO_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED, "Two Star"),
        (THREE_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED, "Three Star"),
        (FOUR_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED, "Four Star"),
    )

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    requirement = models.ForeignKey(
        "QARequirement", on_delete=models.CASCADE, blank=True, null=True
    )
    qa_designee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )

    # NOTE: New contenttypes must be represented in QAStatusManager.filter_by_company() logic if
    # they are to be appropriately queried.
    # content_type = models.ForeignKey('contenttypes.ContentType')
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')
    home_status = models.ForeignKey(
        "home.EEPProgramHomeStatus", on_delete=models.CASCADE, blank=True, null=True
    )
    subdivision = models.ForeignKey(
        "subdivision.Subdivision", on_delete=models.CASCADE, blank=True, null=True
    )

    result = models.CharField(choices=STATUS, max_length=8, null=True, blank=True)

    correction_types = models.ManyToManyField("ObservationType", through="Observation")
    has_observations = models.BooleanField(default=False)
    has_failed = models.BooleanField(default=False)

    # Customer HIRL fields

    hirl_verifier_points_reported = models.IntegerField(
        verbose_name="Verifier Points Reported", blank=True, null=True
    )
    hirl_verifier_points_awarded = models.IntegerField(
        verbose_name="Reviewer Points Awarded", blank=True, null=True
    )
    hirl_certification_level_awarded = models.CharField(
        verbose_name="Certification Level Awarded",
        max_length=100,
        choices=HIRL_CERTIFICATION_LEVEL_AWARDED_CHOICES,
        blank=True,
        null=True,
    )
    hirl_badges_awarded = models.ManyToManyField(
        HIRLGreenEnergyBadge, blank=True, verbose_name="NGBS Green+ Badges Awarded"
    )
    hirl_commercial_space_confirmed = models.BooleanField(
        verbose_name="Commercial Space Confirmed", null=True
    )

    hirl_reviewer_wri_value_awarded = models.IntegerField(
        verbose_name="Reviewer WRI Value Awarded", null=True, blank=True
    )

    hirl_water_sense_confirmed = models.BooleanField(verbose_name="WaterSense Confirmed", null=True)

    customer_documents = GenericRelation("filehandling.CustomerDocument")

    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    objects = QAStatusManager()
    history = HistoricalRecords()
    Machine = QAStateMachine

    def get_absolute_url(self):
        return reverse("qa:view", kwargs={"pk": self.id})

    class Meta:
        unique_together = ("home_status", "subdivision", "requirement")
        verbose_name = "QA Status"
        verbose_name_plural = "QA Statuses"

    def __str__(self):
        return "{} for {}".format(self._meta.verbose_name, self.get_home_status().eep_program)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(QAStatus, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        queue_state_duration_message = False
        if not any((self.home_status, self.subdivision)):
            raise ValueError("Must set one of: home_status, subdivision")
        if all((self.home_status, self.subdivision)):
            raise ValueError("Only allowed to have one of: home_status, subdivision")
        if self.subdivision and self.requirement.type != "file":
            raise ValueError(
                "Unsupported QA type for Subdivision: {}".format(self.requirement.type)
            )

        original = dict()
        if hasattr(self, "_loaded_values"):
            original = self._loaded_values

        if not self.id:
            queue_state_duration_message = True

            if self.home_status and not self.home_status.eep_program.is_qa_program:
                if self.requirement.type == "field":
                    qa_program = self.requirement.eep_program.get_qa_program()
                    home_id = self.home_status.home_id
                    EEPProgramHomeStatus.objects.get_or_create(
                        eep_program=qa_program, home_id=home_id, company=self.requirement.qa_company
                    )

        else:
            # Allow these to unconditionally recalculate in case we do something funky as superuser
            self.has_observations = self.observation_set.exists()
            self.has_failed = self.state_history.filter(to_state="correction_required").exists()

        if self.home_status:
            if not self.requirement:
                self.requirement = QARequirement.objects.filter_by_company(
                    self.owner,
                    eep_program=self.home_status.eep_program,
                    company_hints=self.home_status.home.relationships.get_companies(ids_only=True),
                )

        designee_send_message = False
        if self._state.adding and self.qa_designee_id:
            designee_send_message = True
        elif (
            not self._state.adding
            and self.qa_designee_id
            and self.qa_designee_id != original.get("qa_designee_id")
        ):
            designee_send_message = True

        if designee_send_message:
            if self.home_status:
                if self.qa_designee.company.slug == customer_hirl_app.CUSTOMER_SLUG:
                    requirement_type = self.requirement.type

                    if requirement_type == QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE:
                        verifier = self.home_status.customer_hirl_rough_verifier
                    else:
                        verifier = self.home_status.customer_hirl_final_verifier

                    qa_designee_name = ""
                    if self.qa_designee:
                        qa_designee_name = self.qa_designee.get_full_name()

                    verifier_name = ""
                    verifier_url = ""
                    if verifier:
                        verifier_name = verifier.get_full_name()
                        verifier_url = verifier.get_absolute_url()

                    CustomerHIRLQADesigneeAssigneeMessage(
                        url=f"{self.home_status.home.get_absolute_url()}#/tabs/qa"
                    ).send(
                        user=self.qa_designee,
                        context={
                            "requirement_type": self.requirement.get_type_display(),
                            "home_city": self.home_status.home.city,
                            "home_address": f"{self.home_status.home.get_addr()}",
                            "qa_designee_name": qa_designee_name,
                            "verifier_name": verifier_name,
                            "verifier_url": verifier_url,
                            "home_link": self.home_status.home.get_absolute_url(),
                            "qa_status": self,
                            "notes": self.home_status.annotations.filter_by_user(
                                user=self.qa_designee
                            ).filter(type__slug="note"),
                        },
                    )
                else:
                    QADesigneeAssigneeMessage(
                        url=f"{self.home_status.home.get_absolute_url()}#/tabs/qa"
                    ).send(
                        user=self.qa_designee,
                        context={
                            "title": f"QA Designee assigned - " f"{self.home_status.home.city}",
                            "home_address": self.home_status.home.get_home_address_display(),
                            "qa_designee": self.qa_designee,
                            "home_link": self.home_status.home.get_absolute_url(),
                            "qa_status": self,
                            "notes": self.home_status.annotations.filter_by_user(
                                user=self.qa_designee
                            ).filter(type__slug="note"),
                        },
                    )

        super(QAStatus, self).save(*args, **kwargs)
        if queue_state_duration_message:
            qa_state_change_handler(self)

    def delete(self, using=None):
        if self.requirement.type == "field":
            try:
                stat = EEPProgramHomeStatus.objects.get(
                    home_id=self.home_status.home.id,
                    eep_program__slug=self.requirement.eep_program.slug + "-qa",
                )
            except EEPProgramHomeStatus.DoesNotExist:
                log.error(
                    " No EEPProgramHomeStatus could be found to delete for QAStatus %r (%i)",
                    self,
                    self.id,
                )
            else:
                stat.delete()

        super(QAStatus, self).delete(using)

    def get_parent(self):
        return self.home_status or self.subdivision

    def get_state_display(self):
        return self.get_state_info().description

    def can_be_edited(self, user):
        if user.is_superuser:
            return True
        elif hasattr(self, "owner") and user.company.id == self.owner.id:
            return True
        return self in QAStatus.objects.filter_by_user(user)

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True
        elif hasattr(self, "owner"):
            return user.company.id == self.owner.id and self.state != "complete"
        return False

    def get_possible_transition_choices_for_user(self, user):
        """Get a list of possible transitions"""
        choices = []
        if self.state == "correction_required":
            if user.company.id == self.get_home_status().company.id:
                # There should only be one choice
                choices = [(x.get_name(), "Corrected") for x in self.possible_transitions]

            if user.is_superuser or user.company.id == self.owner.id:
                choices = [
                    (x.get_name(), x.to_state_description) for x in self.possible_transitions
                ]
        else:
            if user.is_superuser or user.company.id == self.owner.id:
                choices = [
                    (x.get_name(), x.to_state_description) for x in self.possible_transitions
                ]
        if len(choices):
            return [("", "---------")] + choices
        return choices

    def get_status_display(self):
        msg = self.get_state_display()
        if self.result:
            msg += " (" + self.get_result_display() + ")"
        return msg

    def get_full_status(self, user):
        data = dict((k, v) for k, v in self.__dict__.items() if not k.startswith("_"))
        data["resource_uri"] = "/api/v2/qa_status/1/full_status"
        data["created_on"] = formats.date_format(data["created_on"], "SHORT_DATE_FORMAT")
        data["last_update"] = formats.date_format(data["last_update"], "SHORT_DATE_FORMAT")
        data["state_display"] = self.get_state_display()
        data["home_status_id"] = self.home_status_id
        data["result_display"] = self.get_result_display()
        data["status"] = self.get_status_display()
        data["possible_transitions"] = [
            dict(transition=x[0], name=x[1])
            for x in self.get_possible_transition_choices_for_user(user)
        ]
        data["notes"] = []
        for item in self.qanote_set.all():
            note = {"note": item.note}
            note["created_on"] = formats.date_format(item.created_on, "SHORT_DATE_FORMAT")
            note["last_update"] = formats.date_format(item.last_update, "SHORT_DATE_FORMAT")
            note["user"] = item.user.id
            note["user_full_name"] = item.user.get_full_name()
            data["notes"].append(note)
        try:
            data["requirement_id"] = self.requirement.id
            data["gate_certification"] = self.requirement.gate_certification
            data["current_year_active_pct"] = self.requirement.get_yearly_coverage_pct()
            data["active_coverage_pct"] = self.requirement.get_active_coverage_pct()
            data["qa_recommended"] = self.requirement.get_active_coverage_pct()
        except (ObjectDoesNotExist, AttributeError):
            data["requirement_id"] = None
            data["gate_certification"] = False
            data["current_year_active_pct"] = "Unknown"
            data["active_coverage_pct"] = "Unknown"
        return data

    def get_home_status(self):
        if self.home_status:
            return self.home_status
        elif self.subdivision:
            return EEPProgramHomeStatus.objects.filter(home__subdivision=self.subdivision).first()

    def get_hirl_certification_level_choices(self):
        """
        Filter HIRL_CERTIFICATION_LEVEL_AWARDED_CHOICES based on eep_program
        :return: tuples with certification choices
        """

        choices_map = {
            "ngbs-sf-new-construction-2020-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-mf-new-construction-2020-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-sf-whole-house-remodel-2020-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-mf-whole-house-remodel-2020-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-sf-new-construction-2015-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-mf-new-construction-2015-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-sf-whole-house-remodel-2015-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-mf-whole-house-remodel-2015-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-sf-new-construction-2012-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-mf-new-construction-2012-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-sf-whole-house-remodel-2012-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-mf-whole-house-remodel-2012-new": (
                (self.BRONZE_HIRL_CERTIFICATION_LEVEL_AWARDED, "Bronze"),
                (self.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED, "Silver"),
                (self.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Gold"),
                (self.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED, "Emerald"),
            ),
            "ngbs-sf-certified-2020-new": (
                (self.CERTIFIED_HIRL_CERTIFICATION_LEVEL_AWARDED, "Certified"),
            ),
            "ngbs-land-development-2020-new": (
                (self.ONE_STAR_HIRL_CERTIFICATION_LEVEL_AWARDED, "One Star"),
                (self.TWO_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED, "Two Stars"),
                (self.THREE_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED, "Three Stars"),
                (self.FOUR_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED, "Four Stars"),
            ),
        }

        customer_hirl_project = getattr(self.home_status, "customer_hirl_project", None)

        if customer_hirl_project:
            if (
                customer_hirl_project.is_accessory_structure
                or customer_hirl_project.is_accessory_dwelling_unit
            ):
                return ((self.CONFORMING_HIRL_CERTIFICATION_LEVEL_AWARDED, "Conforming"),)

            if customer_hirl_project.commercial_space_type:
                return ((self.CERTIFIED_HIRL_CERTIFICATION_LEVEL_AWARDED, "Certified"),)

        if self.home_status and self.home_status.eep_program:
            return choices_map.get(
                self.home_status.eep_program.slug, self.HIRL_CERTIFICATION_LEVEL_AWARDED_CHOICES
            )
        return self.HIRL_CERTIFICATION_LEVEL_AWARDED_CHOICES

    def get_customer_hirl_grading_verifier(self) -> Optional["User"]:
        """
        Customer HIRL identify Verifier for QAStatus based on QARequirement and EEPProgram
        :return: User | None
        """
        home_status = getattr(self, "home_status", None)

        if not home_status:
            return None

        verifier = None
        requirement_type = self.requirement.type

        if self.requirement.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS:
            if requirement_type in [
                QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                QARequirement.ROUGH_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
            ]:
                verifier = getattr(self.home_status, "customer_hirl_rough_verifier", None)
            elif requirement_type in [
                QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                QARequirement.FINAL_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
            ]:
                verifier = getattr(self.home_status, "customer_hirl_final_verifier", None)
            elif requirement_type == QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE:
                verifier = getattr(self.home_status, "customer_hirl_final_verifier", None)
        else:
            verifier = home_status.rater_of_record

        return verifier


class QANote(models.Model):
    qa_status = models.ForeignKey(QAStatus, on_delete=models.CASCADE)
    note = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_on = models.DateTimeField(editable=False)
    last_update = models.DateTimeField(editable=True)

    customer_documents = GenericRelation("filehandling.CustomerDocument")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "QA Note"
        verbose_name_plural = "QA Notes"

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_on = now()
        self.last_update = now()
        return super(QANote, self).save(*args, **kwargs)

    def __str__(self):
        return "{user} noted {note} on {last_update}".format(
            user=self.user.get_full_name(), **self.__dict__
        )

    def can_be_edited(self, user):
        if user.is_superuser:
            return True
        elif hasattr(self, "user") and user.company.id == self.user.company.id:
            return True
        return False

    def can_be_deleted(self, user):
        return self.can_be_edited(user)


class Observation(models.Model):
    """Through-model for the m2m between a QAStatus and the ObservationTypes made on it."""

    # Observations accumulated in the QAStatus.observation_set.all() queryset.  They are not cleared
    # as the QA state is changed, making these a record of what took place.

    objects = ObservationManager()

    qa_status = models.ForeignKey("QAStatus", on_delete=models.CASCADE)
    observation_type = models.ForeignKey("ObservationType", on_delete=models.CASCADE)

    # Record which Note was associated when the observation was made
    qa_note = models.ForeignKey("QANote", on_delete=models.CASCADE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    created_on = models.DateTimeField(editable=False, default=now)
    last_update = models.DateTimeField(editable=False)

    def __str__(self):
        return "{}: {}".format(self.user, self.observation_type)

    def save(self, *args, **kwargs):
        self.last_update = now()
        return super(Observation, self).save(*args, **kwargs)


class ObservationType(models.Model):
    """A type of QA observation a company allows to be made on the programs they use."""

    objects = ObservationTypeManager()

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        limit_choices_to={"company_type": Company.QA_COMPANY_TYPE},
    )
    name = models.CharField(max_length=100)

    created_on = models.DateTimeField(editable=False, default=now)
    last_update = models.DateTimeField(editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.last_update = now()
        return super(ObservationType, self).save(*args, **kwargs)


def get_stats_available_for_qa(user, home=None, subdivision=None):
    """Can a user add QA to a EEP Program Home Status"""
    from axis.home.models import EEPProgramHomeStatus
    from axis.relationship.models import Relationship

    if not user.has_perm("qa.add_qastatus"):
        return EEPProgramHomeStatus.objects.none()
    if user.company.company_type not in ["provider", "qa"]:
        return EEPProgramHomeStatus.objects.none()
    if user.company.company_type == "provider":
        # If you have a relationship to QA companies you remove your ability to do QA?
        if user.company.relationships.get_companies().filter(company_type="qa").count():
            return EEPProgramHomeStatus.objects.none()

    comps = Relationship.objects.get_reversed_companies(user.company, ids_only=True)
    if user.company.id in comps:
        comps = [c for c in comps if c != user.company.id]
    rels = user.company.relationships.get_companies(ids_only=True)
    intersecting = list(set(rels).intersection(set(comps)))

    kwargs = {"company__in": intersecting}
    if home:
        kwargs.update(
            {
                "qastatus__isnull": True,
                "home": home,
            }
        )
    elif subdivision:
        kwargs.update(
            {
                "home__subdivision__qastatus__isnull": True,
                "home__subdivision": subdivision,
            }
        )

    stats = EEPProgramHomeStatus.objects.filter_by_user(user)
    stats = stats.exclude(state="abandoned")
    return stats.filter(**kwargs)
