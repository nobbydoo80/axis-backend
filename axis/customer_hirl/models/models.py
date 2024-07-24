"""NGBS Certification and Candidate tracking for pairing to home.Home instances."""

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.contrib.auth import get_user_model
from django.db import models

from axis.company.models import Company
from axis.core.fields import AxisJSONField
from axis.user_management.models import Accreditation
from .builder_agreement import BuilderAgreement
from .verifier_agreement import VerifierAgreement, COIDocument

log = logging.getLogger(__name__)
User = get_user_model()


class HIRLBuilderOrganization(models.Model):
    """
    Contains raw data from HIRL Builders database for fields that is not exist on AXIS
    """

    builder_organization = models.OneToOneField(
        Company, null=True, blank=True, on_delete=models.CASCADE
    )
    data = AxisJSONField(default=dict, blank=True)
    hirl_id = models.AutoField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.builder_organization)


class HIRLRaterOrganization(models.Model):
    """
    Contains raw data from HIRL Verifiers database for fields that is not exist on AXIS
    """

    rater_organization = models.OneToOneField(
        Company, null=True, blank=True, on_delete=models.CASCADE
    )
    data = AxisJSONField(default=dict)
    # NGBS do not have internal id for Rater Organizations yet
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.rater_organization)


class HIRLRaterUser(models.Model):
    """
    Contains raw data from HIRL Verifiers database for fields that is not exist on AXIS
    """

    hirl_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data = AxisJSONField(default=dict, blank=True)
    assigned_verifier_id = models.CharField(null=True, blank=True, max_length=255)
    email = models.CharField(null=True, blank=True, max_length=255)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.user)


class HIRLBuilderAgreementStatus(models.Model):
    """
    Contains raw data from HIRL Agreement Status database
    """

    builder_agreement = models.OneToOneField(BuilderAgreement, null=True, on_delete=models.CASCADE)
    data = AxisJSONField(default=dict)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    hirl_builder_id = models.PositiveIntegerField()
    hirl_start_date = models.DateField(null=True, blank=True)
    hirl_expiration_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.builder_agreement)


class HIRLVerifierAgreementStatus(models.Model):
    """
    Contains raw data from HIRL Agreement Status database
    """

    verifier_agreement = models.OneToOneField(
        VerifierAgreement, null=True, on_delete=models.CASCADE
    )
    data = AxisJSONField(default=dict)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    hirl_verifier_id = models.PositiveIntegerField()
    hirl_start_date = models.DateField(null=True, blank=True)
    hirl_expiration_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{}".format(self.verifier_agreement)


class HIRLBuilderInsurance(models.Model):
    AUTOMOBILE_LIABILITY_INSURANCE_TYPE = 1
    EXCESS_INSURANCE_TYPE = 2
    GENERAL_LIABILITY_INSURANCE_TYPE = 3
    PROFESSIONAL_LIABILITY_INSURANCE_TYPE = 4
    WORKERS_COMPENSATION_INSURANCE_TYPE = 5

    HIRL_INTERNAL_INSURANCE_TYPE_CHOICES = (
        (AUTOMOBILE_LIABILITY_INSURANCE_TYPE, "Automobile Liability"),
        (EXCESS_INSURANCE_TYPE, "Excess/Umbrella Liability"),
        (GENERAL_LIABILITY_INSURANCE_TYPE, "General Liability"),
        (PROFESSIONAL_LIABILITY_INSURANCE_TYPE, "Professional Liability"),
        (WORKERS_COMPENSATION_INSURANCE_TYPE, "Workers Compensation"),
    )

    builder_agreement = models.OneToOneField(BuilderAgreement, null=True, on_delete=models.CASCADE)
    data = AxisJSONField(default=dict)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    hirl_insurance_type = models.IntegerField(
        choices=HIRL_INTERNAL_INSURANCE_TYPE_CHOICES, null=True
    )
    hirl_insurance_name = models.CharField(max_length=255, blank=True)
    hirl_policy_number = models.CharField(max_length=255, blank=True)
    hirl_policy_effective_date = models.DateField(null=True, blank=True)
    hirl_policy_expiration_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{} {}".format(self.builder_agreement, self.hirl_policy_number)


class HIRLVerifierInsurance(models.Model):
    AUTOMOBILE_LIABILITY_INSURANCE_TYPE = 1
    EXCESS_INSURANCE_TYPE = 2
    GENERAL_LIABILITY_INSURANCE_TYPE = 3
    PROFESSIONAL_LIABILITY_INSURANCE_TYPE = 4
    WORKERS_COMPENSATION_INSURANCE_TYPE = 5

    HIRL_INTERNAL_INSURANCE_TYPE_CHOICES = (
        (AUTOMOBILE_LIABILITY_INSURANCE_TYPE, "Automobile Liability"),
        (EXCESS_INSURANCE_TYPE, "Excess/Umbrella Liability"),
        (GENERAL_LIABILITY_INSURANCE_TYPE, "General Liability"),
        (PROFESSIONAL_LIABILITY_INSURANCE_TYPE, "Professional Liability"),
        (WORKERS_COMPENSATION_INSURANCE_TYPE, "Workers Compensation"),
    )

    coi_document = models.OneToOneField(COIDocument, null=True, on_delete=models.CASCADE)
    data = AxisJSONField(default=dict)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    hirl_insurance_type = models.IntegerField(
        choices=HIRL_INTERNAL_INSURANCE_TYPE_CHOICES, null=True
    )
    hirl_insurance_name = models.CharField(max_length=255, blank=True)
    hirl_policy_number = models.CharField(max_length=255, blank=True)
    hirl_policy_effective_date = models.DateField(null=True, blank=True)
    hirl_policy_expiration_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "{} {}".format(self.coi_document, self.hirl_policy_number)


class HIRLVerifierAccreditationStatus(models.Model):
    accreditations = models.ManyToManyField(Accreditation)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"{self.accreditations}"


class HIRLProjectArchitect(models.Model):
    architect_organization = models.ForeignKey(Company, null=True, on_delete=models.CASCADE)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    name = models.TextField()
    website = models.TextField(blank=True)
    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class HIRLProjectDeveloper(models.Model):
    developer_organization = models.ForeignKey(Company, null=True, on_delete=models.CASCADE)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    name = models.TextField()
    website = models.TextField(blank=True)
    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class HIRLProjectOwner(models.Model):
    community_owner_organization = models.ForeignKey(Company, null=True, on_delete=models.CASCADE)
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    name = models.TextField()
    website = models.TextField(blank=True)
    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class HIRLProjectContact(models.Model):
    ARCHITECT_PROJECT_TYPE = 1
    DEVELOPER_PROJECT_TYPE = 2
    BUILDER_PROJECT_TYPE = 3
    OWNER_PROJECT_TYPE = 4

    PROJECT_TYPE_CHOICES = (
        (ARCHITECT_PROJECT_TYPE, "Architect"),
        (DEVELOPER_PROJECT_TYPE, "Developer"),
        (BUILDER_PROJECT_TYPE, "Builder"),
        (OWNER_PROJECT_TYPE, "Owner"),
    )
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    hirl_company_id = models.PositiveIntegerField(
        verbose_name="Internal fkArchitectOrDeveloperID", null=True
    )
    contact_type = models.IntegerField(choices=PROJECT_TYPE_CHOICES)
    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Project contact {self.hirl_id}"


class HIRLVerifierCommunityProject(models.Model):
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")

    hirl_architect_id = models.PositiveIntegerField(null=True, blank=True)
    hirl_architect_contact_id = models.PositiveIntegerField(null=True, blank=True)

    hirl_developer_id = models.PositiveIntegerField(null=True, blank=True)
    hirl_developer_contact_id = models.PositiveIntegerField(null=True, blank=True)

    hirl_community_owner_id = models.PositiveIntegerField(null=True, blank=True)
    hirl_community_owner_contact_id = models.PositiveIntegerField(null=True, blank=True)

    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"HIRLVerifierCommunityProject {self.hirl_id}"


class HIRLVerifierCertificationBadgesToRecords(models.Model):
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID")
    record_id = models.PositiveIntegerField(null=True, blank=True)
    sources_id = models.PositiveIntegerField(null=True, blank=True)
    verifier_certification_badges_pricing_id = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2, blank=True, null=True)
    story_count = models.IntegerField(null=True, blank=True)

    data = AxisJSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"VerifierCertificationBadgesToRecords {self.hirl_id}"
