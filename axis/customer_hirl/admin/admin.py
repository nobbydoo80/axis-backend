"""Auto-discovered admin registration."""

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.contrib import admin
from django.contrib.admin.decorators import register

from axis.customer_hirl.models import (
    HIRLBuilderOrganization,
    HIRLRaterOrganization,
    HIRLRaterUser,
    HIRLBuilderAgreementStatus,
    HIRLVerifierAgreementStatus,
    HIRLBuilderInsurance,
    HIRLVerifierInsurance,
    HIRLVerifierAccreditationStatus,
    HIRLProjectContact,
    HIRLVerifierCommunityProject,
    HIRLVerifierCertificationBadgesToRecords,
    COIDocument,
    HIRLProjectArchitect,
    HIRLProjectDeveloper,
    HIRLProjectOwner,
)


@register(HIRLBuilderOrganization)
class HIRLBuilderOrganizationAdmin(admin.ModelAdmin):
    raw_id_fields = ("builder_organization",)
    search_fields = ("builder_organization__name", "hirl_id")
    list_display = ("builder_organization", "hirl_id", "updated_at", "created_at")


@register(HIRLRaterOrganization)
class HIRLRaterOrganizationAdmin(admin.ModelAdmin):
    raw_id_fields = ("rater_organization",)
    search_fields = ("rater_organization__name",)
    list_display = ("rater_organization", "hirl_id", "updated_at", "created_at")


@register(HIRLRaterUser)
class HIRLRaterUserAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    search_fields = ("user__first_name", "user__last_name", "user__email", "hirl_id")
    list_display = ("user", "hirl_id", "updated_at", "created_at")


class HIRLBuilderAgreementStatusTabularInlineAdmin(admin.TabularInline):
    model = HIRLBuilderAgreementStatus
    extra = 0


@register(HIRLBuilderAgreementStatus)
class HIRLBuilderAgreementStatusAdmin(admin.ModelAdmin):
    list_display = ("builder_agreement", "hirl_id", "updated_at", "created_at")
    search_fields = ("builder_agreement__company__name",)


@register(HIRLVerifierAgreementStatus)
class HIRLVerifierAgreementStatusAdmin(admin.ModelAdmin):
    list_display = ("verifier_agreement", "hirl_id", "updated_at", "created_at")
    search_fields = (
        "verifier_agreement__verifier__first_name",
        "verifier_agreement__verifier__last_name",
        "verifier_agreement__verifier__email",
    )


class HIRLBuilderInsuranceTabularInlineAdmin(admin.TabularInline):
    model = HIRLBuilderInsurance
    extra = 0


@register(HIRLBuilderInsurance)
class HIRLBuilderInsuranceAdmin(admin.ModelAdmin):
    raw_id_fields = ("builder_agreement",)
    list_filter = (("builder_agreement", admin.EmptyFieldListFilter),)
    search_fields = ("hirl_policy_number", "hirl_id")


@register(HIRLVerifierInsurance)
class HIRLVerifierInsuranceAdmin(admin.ModelAdmin):
    raw_id_fields = ("coi_document",)
    list_display = ("coi_document", "hirl_policy_number")
    list_filter = (("coi_document", admin.EmptyFieldListFilter),)
    search_fields = ("hirl_policy_number", "hirl_id")


@register(HIRLVerifierAccreditationStatus)
class HIRLVerifierAccreditationStatusAdmin(admin.ModelAdmin):
    list_display = ("hirl_id",)
    readonly_fields = ("accreditations",)


@register(HIRLProjectContact)
class HIRLProjectContactAdmin(admin.ModelAdmin):
    search_fields = ("hirl_id", "hirl_company_id")
    list_display = ("id", "hirl_id")


@register(HIRLVerifierCommunityProject)
class HIRLVerifierCommunityProjectAdmin(admin.ModelAdmin):
    search_fields = ("hirl_id", "hirl_architect_id", "hirl_architect_contact_id")
    list_display = (
        "id",
        "hirl_id",
        "hirl_architect_id",
        "hirl_architect_contact_id",
        "hirl_developer_id",
        "hirl_developer_contact_id",
        "hirl_community_owner_id",
        "hirl_community_owner_contact_id",
    )


@register(HIRLVerifierCertificationBadgesToRecords)
class HIRLVerifierCertificationBadgesToRecordsAdmin(admin.ModelAdmin):
    search_fields = ("hirl_id",)
    list_display = (
        "id",
        "hirl_id",
    )


@register(COIDocument)
class COIDocumentAdmin(admin.ModelAdmin):
    search_fields = (
        "company__name",
        "policy_number",
        "start_date",
        "expiration_date",
        "created_at",
    )
    list_display = ("id", "company", "policy_number")
    raw_id_fields = ("company",)


@register(HIRLProjectArchitect)
class HIRLProjectArchitectAdmin(admin.ModelAdmin):
    raw_id_fields = ("architect_organization",)
    search_fields = ("architect_organization__name", "hirl_id")
    list_display = ("architect_organization", "hirl_id", "updated_at", "created_at")


@register(HIRLProjectDeveloper)
class HIRLProjectDeveloperAdmin(admin.ModelAdmin):
    raw_id_fields = ("developer_organization",)
    search_fields = ("developer_organization__name", "hirl_id")
    list_display = ("developer_organization", "hirl_id", "updated_at", "created_at")


@register(HIRLProjectOwner)
class HIRLProjectOwnerAdmin(admin.ModelAdmin):
    raw_id_fields = ("community_owner_organization",)
    search_fields = ("community_owner_organization__name", "hirl_id")
    list_display = ("community_owner_organization", "hirl_id", "updated_at", "created_at")
