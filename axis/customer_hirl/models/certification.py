"""certification.py: """

__author__ = "Artem Hruzd"
__date__ = "07/26/2020 18:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging
from functools import cached_property

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

from axis.annotation.models import Type
from axis.core.fields import AxisJSONField
from axis.customer_hirl.managers import HIRLLegacyCertificationQuerySet

from axis.eep_program.models import EEPProgram

log = logging.getLogger(__name__)
User = get_user_model()
app = apps.get_app_config("customer_hirl")


class Certification(models.Model):
    """
    DEPRECATED: This model have incorrect data from NGBS and must be removed.
    Original and trust source for NGBS data is HIRLLegacyCertification model


    Model of mssql data coming from the NGBS db.
    The field names are normalized for snake_case, mapped via the `CertificationForm`.
    """

    home = models.OneToOneField(
        "home.Home",
        blank=True,
        null=True,
        related_name="hirl_certification",
        on_delete=models.SET_NULL,
    )
    candidates = models.ManyToManyField(
        "home.Home", through="Candidate", blank=True, related_name="hirl_certification_candidates"
    )
    import_failed = models.BooleanField(default=False)
    import_error = models.CharField(max_length=500, blank=True, null=True)
    import_traceback = models.TextField(blank=True, null=True)

    id = models.IntegerField(primary_key=True)
    project_id = models.CharField(max_length=25, blank=True, null=True)
    checklist = models.CharField(max_length=100)
    scoring_path = models.CharField(max_length=50)
    builder = models.CharField(max_length=100)
    rough_in_location = models.CharField(max_length=255, blank=True, null=True)
    street_line1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=25, blank=True, null=True)
    state_abbreviation = models.CharField(max_length=25)
    state = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=15, blank=True, null=True)
    county = models.CharField(max_length=50, blank=True, null=True)
    unit_count = models.IntegerField(default=0)
    certification_level = models.CharField(max_length=25, blank=True, null=True)
    certificate_number = models.IntegerField(blank=True, null=True)
    certificate_sent_date = models.DateField(blank=True, null=True)
    community_project = models.CharField(max_length=100, blank=True, null=True)
    certification_type = models.CharField(max_length=25, blank=True, null=True)
    hers_score = models.CharField(max_length=25, blank=True, null=True)
    builder_organization_id = models.IntegerField(blank=True, null=True)
    scoring_path_id = models.IntegerField(blank=True, null=True)
    checklist_id = models.IntegerField(blank=True, null=True)
    verifier_name = models.CharField(max_length=45, blank=True, null=True)
    verifier_id = models.IntegerField(blank=True, null=True)
    eri = models.IntegerField(null=True, blank=True)
    water_path = models.IntegerField(null=True, blank=True)
    wri = models.IntegerField(null=True, blank=True)
    hud_disaster_case_number = models.CharField(max_length=255, blank=True, null=True)
    verifier_certification_energy_path_id = models.IntegerField(null=True, blank=True)
    energy_path = models.CharField(max_length=255, blank=True, null=True)
    rough_reviewer = models.CharField(max_length=255, blank=True, null=True)
    final_reviewer = models.CharField(max_length=255, blank=True, null=True)
    rough_verifier_grades_id = models.IntegerField(blank=True, null=True)
    final_verifier_grades_id = models.IntegerField(blank=True, null=True)
    rough_grade = models.CharField(max_length=255, blank=True, null=True)
    final_grade = models.CharField(max_length=255, blank=True, null=True)
    rough_verifier_grade_notes = models.CharField(max_length=255, blank=True, null=True)
    final_verifier_grade_notes = models.CharField(max_length=255, blank=True, null=True)
    water_path_selected = models.CharField(max_length=255, blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        pass

    def __str__(self):
        return self.street_line1

    def get_annotation_data(self):
        return dict(
            [
                (Type.objects.get(slug="certified-nat-gbs"), self.certification_level),
                (Type.objects.get(slug="certification-standard"), self.checklist),
                (Type.objects.get(slug="certification-date"), self.certificate_sent_date),
                (Type.objects.get(slug="certification-number"), self.certificate_number),
                (Type.objects.get(slug="certification-record-id"), self.id),
                (Type.objects.get(slug="project-id"), self.project_id),
                (Type.objects.get(slug="unit-count"), self.unit_count),
                (Type.objects.get(slug="hers-score"), self.hers_score),
                (Type.objects.get(slug="hud-disaster-case-number"), self.hud_disaster_case_number),
            ]
        )


class HIRLLegacyCertification(models.Model):
    """
    Contains raw certification data from NGBS.
    Certification is old model that contains flattened limited amount of keys
    """

    project = models.ForeignKey("HIRLProject", on_delete=models.SET_NULL, blank=True, null=True)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID", blank=True)
    hirl_project_id = models.TextField(
        verbose_name="Project ID", blank=True, help_text="Legacy Project ID"
    )
    scoring_path_name = models.TextField(blank=True)
    data = AxisJSONField(default=dict)
    convert_to_registration_error = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    objects = HIRLLegacyCertificationQuerySet.as_manager()

    class Meta:
        pass

    @cached_property
    def address(self):
        data = []
        if "AddressL1" in self.data and self.data["AddressL1"] and len(self.data["AddressL1"]):
            data.append(self.data["AddressL1"])
        if "AddressL2" in self.data and self.data["AddressL2"] and len(self.data["AddressL2"]):
            data.append(self.data["AddressL2"])
        return ", ".join(data)

    @cached_property
    def program(self):
        try:
            return EEPProgram.objects.get(slug=app.NGBS_PROGRAM_NAMES[self.scoring_path_name])
        except EEPProgram.DoesNotExist:
            return ""

    @cached_property
    def is_certified(self):
        return (
            "CertificateNumber" in self.data
            and self.data["CertificateNumber"] not in ["", None]
            and "CertificateNumber" in self.data
            and self.data["CertificateNumber"] is not None
            and "fkCertificationStatus" in self.data
            and self.data["fkCertificationStatus"] == 7
        )

    @cached_property
    def unit_count(self):
        if "mf" in self.scoring_path_name.lower() or "multi" in self.scoring_path_name.lower():
            if "UnitCount" in self.data and self.data["UnitCount"] is not None:
                return int(self.data["UnitCount"])
            if self.data["UnitCount"] in [0, None]:
                return 1

    @cached_property
    def status(self):
        if self.is_certified:
            return "Certified"

        if "fkCertificationStatus" in self.data and self.data["fkCertificationStatus"] is not None:
            if self.data["fkCertificationStatus"] == 2:
                return "Old"
            elif self.data["fkCertificationStatus"] == 4:
                return "New"
            elif self.data["fkCertificationStatus"] == 5:
                return "Pre-Paid"
            elif self.data["fkCertificationStatus"] == 7:
                return "In-Progress"
        return "Unknown"

    def __str__(self):
        data = [self.address]
        if self.program:
            data.append(self.program.name)
        data.append(f"({self.status})")
        if self.unit_count is not None:
            data.append(f" - {self.unit_count} Units")
        return " ".join(data)
