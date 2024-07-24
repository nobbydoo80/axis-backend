__author__ = "Artem Hruzd"
__date__ = "04/16/2021 13:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import waffle
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition, can_proceed
from hashid_field import HashidAutoField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import signals
from simple_history.models import HistoricalRecords

from axis.annotation.models import Annotation, Type as AnnotationType
from axis.core.fields import AxisJSONField
from axis.customer_hirl.managers.project_registration import HIRLProjectRegistrationQuerySet
from axis.customer_hirl.messages import (
    HIRLProjectRegistrationStateChangedMessage,
    HIRLProjectRegistrationRejectedMessage,
    ProjectRegistrationERFPNotificationMessage,
)
from axis.home.models import EEPProgramHomeStatus
from axis.relationship.models import Relationship
from axis.relationship.signals import update_stats_for_home_rels

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")
frontend_app = apps.get_app_config("frontend")


class HIRLProjectRegistration(models.Model):
    SINGLE_FAMILY_PROJECT_TYPE = 1
    MULTI_FAMILY_PROJECT_TYPE = 2
    LAND_DEVELOPMENT_PROJECT_TYPE = 3

    PROJECT_TYPE_CHOICES = (
        (SINGLE_FAMILY_PROJECT_TYPE, "Single Family"),
        (MULTI_FAMILY_PROJECT_TYPE, "Multi Family"),
        (LAND_DEVELOPMENT_PROJECT_TYPE, "Multi Family"),
    )

    NEW_STATE = "new"
    ACTIVE_STATE = "active"
    PENDING_STATE = "pending"
    REJECTED_STATE = "rejected"
    ABANDONED_STATE = "abandoned"

    STATE_CHOICES = (
        (NEW_STATE, "New"),
        (PENDING_STATE, "Pending"),
        (ACTIVE_STATE, "Active"),
        (REJECTED_STATE, "Rejected"),
        (ABANDONED_STATE, "Abandoned"),
    )

    SAME_NAME_TO_BE_LISTED_ON_COMMERCIAL_CERTIFICATE = "same"
    DIFFERENT_NAME_TO_BE_LISTED_ON_COMMERCIAL_CERTIFICATE = "same"

    NAME_TO_BE_LISTED_ON_COMMERCIAL_CERTIFICATE_CHOICES = (
        (
            SAME_NAME_TO_BE_LISTED_ON_COMMERCIAL_CERTIFICATE,
            "Same Name as Residential Builder/Developer",
        ),
        (
            DIFFERENT_NAME_TO_BE_LISTED_ON_COMMERCIAL_CERTIFICATE,
            "Different Name(s) - email gbverifications",
        ),
    )

    PROJECT_CLIENT_ARCHITECT = "architect"
    PROJECT_CLIENT_BUILDER = "builder"
    PROJECT_CLIENT_DEVELOPER = "developer"
    PROJECT_CLIENT_OWNER = "owner"

    PROJECT_CLIENT_CHOICES = (
        (PROJECT_CLIENT_ARCHITECT, "Architect"),
        (PROJECT_CLIENT_BUILDER, "Builder"),
        (PROJECT_CLIENT_DEVELOPER, "Developer"),
        (PROJECT_CLIENT_OWNER, "Owner"),
    )

    ARCHITECT_RESPONSIBLE_ENTITY = "architect"
    BUILDER_RESPONSIBLE_ENTITY = "builder"
    COMMUNITY_OWNER_RESPONSIBLE_ENTITY = "community_owner"
    DEVELOPER_RESPONSIBLE_ENTITY = "developer"
    VERIFIER_RESPONSIBLE_ENTITY = "verifier"

    RESPONSIBLE_NAME_CHOICES = (
        (ARCHITECT_RESPONSIBLE_ENTITY, "Architect"),
        (BUILDER_RESPONSIBLE_ENTITY, "Builder"),
        (COMMUNITY_OWNER_RESPONSIBLE_ENTITY, "Owner"),
        (DEVELOPER_RESPONSIBLE_ENTITY, "Developer"),
        (VERIFIER_RESPONSIBLE_ENTITY, "Verifier"),
    )

    APPLICATION_PACKET_COMPLETION_CHOICES = (
        (ARCHITECT_RESPONSIBLE_ENTITY, "Architect"),
        (BUILDER_RESPONSIBLE_ENTITY, "Builder"),
        (COMMUNITY_OWNER_RESPONSIBLE_ENTITY, "Owner"),
        (DEVELOPER_RESPONSIBLE_ENTITY, "Developer"),
    )

    PARTY_NAMED_ON_CERTIFICATE_CHOICES = (
        (ARCHITECT_RESPONSIBLE_ENTITY, "Architect"),
        (BUILDER_RESPONSIBLE_ENTITY, "Builder"),
        (COMMUNITY_OWNER_RESPONSIBLE_ENTITY, "Owner"),
        (DEVELOPER_RESPONSIBLE_ENTITY, "Developer"),
    )

    NO_SAMPLING = "no_sampling"
    TESTING_AND_PRACTICES_ONLY_SAMPLING = "testing_and_practices_only"
    ROUGH_TESTING_AND_PRACTICES_ONLY_SAMPLING = "rough_testing_and_practices_only"
    FINAL_TESTING_AND_PRACTICES_ONLY_SAMPLING = "final_testing_and_practices_only"
    ALL_SAMPLING = "all"
    ROUGH_ALL_SAMPLING = "rough_all"
    FINAL_ALL_SAMPLING = "final_all"

    SAMPLING_CHOICES = (
        (NO_SAMPLING, "No Sampling"),
        (
            TESTING_AND_PRACTICES_ONLY_SAMPLING,
            "For Energy efficiency testing practices only (both Rough and Final)",
        ),
        (
            ROUGH_TESTING_AND_PRACTICES_ONLY_SAMPLING,
            "For Energy efficiency testing practices only (Rough only)",
        ),
        (
            FINAL_TESTING_AND_PRACTICES_ONLY_SAMPLING,
            "For Energy efficiency testing practices only (Final only)",
        ),
        (ALL_SAMPLING, "For All or most NGBS practices (both Rough and Final)"),
        (ROUGH_ALL_SAMPLING, "For All or most NGBS practices (Rough only)"),
        (FINAL_ALL_SAMPLING, "For All or most NGBS practices (Final only)"),
    )

    # land development specific
    LD_WORKFLOW_FULL_CERTIFICATION = "full_certification"
    LD_WORKFLOW_LETTER_OF_APPROVAL_AND_FULL_CERTIFICATION = (
        "letter_of_approval_and_full_certification"
    )

    LD_WORKFLOW_CHOICES = (
        (LD_WORKFLOW_FULL_CERTIFICATION, "Full Certification"),
        (
            LD_WORKFLOW_LETTER_OF_APPROVAL_AND_FULL_CERTIFICATION,
            "Letter of Approval and Full Certification",
        ),
    )

    id = HashidAutoField(
        primary_key=True,
        salt=f"customer_hirl.HIRLProjectRegistration{settings.HASHID_FIELD_SALT}",
        prefix="REG",
    )

    registration_user = models.ForeignKey(
        User, related_name="%(app_label)s_project_registrations", on_delete=models.CASCADE
    )

    project_type = models.PositiveSmallIntegerField(
        choices=PROJECT_TYPE_CHOICES, default=SINGLE_FAMILY_PROJECT_TYPE
    )

    state = FSMField(default=NEW_STATE, choices=STATE_CHOICES)
    state_changed_at = models.DateTimeField(auto_now_add=True)
    state_change_reason = models.TextField(blank=True)

    eep_program = models.ForeignKey(
        "eep_program.EEPProgram", verbose_name="Program", null=True, on_delete=models.CASCADE
    )

    subdivision = models.ForeignKey(
        "subdivision.Subdivision",
        verbose_name="Subdivision",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="After Approval: Subdivision automatically "
        "created for each Multi Family registration",
    )

    builder_organization = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_project_registrations_as_builder",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    builder_organization_contact = models.ForeignKey(
        "core.ContactCard",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_project_registration_builders",
    )

    # single family fields
    is_build_to_rent = models.BooleanField(
        verbose_name="Is this project Build-To-Rent?", default=False
    )

    # multi family fields
    name_to_be_listed_on_commercial_certificate = models.CharField(
        max_length=32,
        choices=NAME_TO_BE_LISTED_ON_COMMERCIAL_CERTIFICATE_CHOICES,
        blank=True,
        null=True,
    )
    project_name = models.CharField(max_length=100, null=True, blank=True)
    project_client = models.CharField(
        choices=PROJECT_CLIENT_CHOICES, max_length=100, null=True, blank=True
    )
    project_description = models.TextField(null=True, blank=True)
    estimated_completion_date = models.DateField(blank=True, null=True)
    project_website_url = models.TextField(blank=True, null=True)

    building_will_include_non_residential_space = models.BooleanField(
        verbose_name="Building(s) will include non-residential space (retail/commercial) ?",
        default=False,
        null=True,
    )
    seeking_hud_mortgage_insurance_premium_reduction = models.BooleanField(
        verbose_name="Seeking HUD Mortgage Insurance Premium Reduction?", default=False, null=True
    )
    seeking_fannie_mae_green_financing = models.BooleanField(
        verbose_name="Seeking Fannie Mae Green financing?", default=False, null=True
    )
    seeking_freddie_mac_green_financing = models.BooleanField(
        verbose_name="Seeking Freddie Mac Green financing?", default=False, null=True
    )
    intended_to_be_affordable_housing = models.BooleanField(
        verbose_name="Intended to be affordable housing?", default=False, null=True
    )

    community_named_on_certificate = models.BooleanField(null=True)

    application_packet_completion = models.CharField(
        max_length=255,
        choices=APPLICATION_PACKET_COMPLETION_CHOICES,
        default=BUILDER_RESPONSIBLE_ENTITY,
        blank=True,
        null=True,
    )
    party_named_on_certificate = models.CharField(
        max_length=255,
        choices=PARTY_NAMED_ON_CERTIFICATE_CHOICES,
        default=BUILDER_RESPONSIBLE_ENTITY,
        blank=True,
        null=True,
    )

    project_contact_first_name = models.CharField(max_length=32, blank=True, null=True)
    project_contact_last_name = models.CharField(max_length=32, blank=True, null=True)
    project_contact_email = models.EmailField(blank=True, null=True)
    project_contact_phone_number = PhoneNumberField(blank=True, null=True)

    # land development specific fields
    ld_workflow = models.CharField(
        max_length=255, choices=LD_WORKFLOW_CHOICES, blank=True, null=True
    )

    developer_organization = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_project_registrations_as_developer",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    developer_organization_contact = models.ForeignKey(
        "core.ContactCard",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_project_registration_developers",
    )

    community_owner_organization = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_project_registrations_as_communityowner",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    community_owner_organization_contact = models.ForeignKey(
        "core.ContactCard",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_project_registration_communityowners",
    )

    architect_organization = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_project_registrations_as_architect",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    architect_organization_contact = models.ForeignKey(
        "core.ContactCard",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_project_registration_architects",
    )

    marketing_first_name = models.CharField(max_length=255, blank=True, null=True)
    marketing_last_name = models.CharField(max_length=255, blank=True, null=True)
    marketing_email = models.EmailField(blank=True, null=True)
    marketing_phone = PhoneNumberField(blank=True, null=True)

    sales_phone = PhoneNumberField(blank=True, null=True)
    sales_email = models.EmailField(blank=True, null=True)
    sales_website_url = models.TextField(blank=True, null=True)

    entity_responsible_for_payment = models.CharField(
        max_length=255,
        choices=RESPONSIBLE_NAME_CHOICES,
        default=BUILDER_RESPONSIBLE_ENTITY,
        blank=True,
        null=True,
    )
    billing_first_name = models.CharField(max_length=255, blank=True, null=True)
    billing_last_name = models.CharField(max_length=255, blank=True, null=True)
    billing_email = models.EmailField(blank=True, null=True)
    billing_phone = PhoneNumberField(blank=True, null=True)

    sampling = models.CharField(
        max_length=100,
        verbose_name="Do you intend to employ the NGBS Green "
        "Alternative Multifamily Verification Protocol (Sampling) ?",
        choices=SAMPLING_CHOICES,
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = HIRLProjectRegistrationQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Project Registration"
        verbose_name_plural = "Project Registrations"
        ordering = ("-id",)

    def __str__(self):
        return f"Project Registration ID: {self.id}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(HIRLProjectRegistration, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def get_absolute_url(self):
        """
        Link to front end detail page
        :return: string
        """
        return f"/{frontend_app.DEPLOY_URL}" f"/hi/project_registrations/{self.id}"

    def can_edit(self, user):
        """
        This hook helps Examine view check permissions
        :param user: User object
        :return: Boolean
        """
        from axis.home.models import EEPProgramHomeStatus

        if user.is_superuser:
            return True

        if self.state in [
            HIRLProjectRegistration.REJECTED_STATE,
            HIRLProjectRegistration.ABANDONED_STATE,
        ]:
            return False

        if user.company_id:
            # do not allow edit registration if we have at least one certified project
            certified_projects_count = self.projects.filter(
                home_status__state=EEPProgramHomeStatus.COMPLETE_STATE
            ).count()
            if certified_projects_count:
                return False

            # NGBS can edit project in any state except "Certified"
            if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
                return True

            # For SF allow to edit Registration for Verfieir/Builder/Community Owner/Architect/Developer organizations
            # only until VR upload. So we check Project for QA objects
            qa_status_count = self.projects.filter(home_status__qastatus__isnull=False).count()

            if self.project_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE:
                if qa_status_count:
                    return False

            if user.company_id == self.registration_user.company_id:
                return True
            if self.builder_organization_id and self.builder_organization_id == user.company_id:
                return True
            if (
                self.community_owner_organization_id
                and self.community_owner_organization_id == user.company_id
            ):
                return True
            if self.architect_organization_id and self.architect_organization_id == user.company_id:
                return True
            if self.developer_organization_id and self.developer_organization_id == user.company_id:
                return True
        return False

    def save(self, **kwargs):  # noqa: C901
        """
        In save we generate unique h_number starting from 100000
        Also syncing company relations with home attached for this project
        :param kwargs:
        :return: HIRLProject
        """

        # Auto move from pending state to active
        if self.project_type == self.MULTI_FAMILY_PROJECT_TYPE:
            if self.state == self.PENDING_STATE:
                if can_proceed(self.active):
                    self.active()

        original = dict()
        if hasattr(self, "_loaded_values"):
            original = self._loaded_values

        if original.get("state") != self.state:
            self.state_changed_at = timezone.now()

        if not self.pk or self.builder_organization_id != original.get("builder_organization_id"):
            self.update_relationships(company=self.builder_organization)

            # update additional fields for subdivision
            if self.subdivision:
                builder_name = ""
                if self.builder_organization:
                    builder_name = self.builder_organization.name

                self.subdivision.builder_name = builder_name
                self.subdivision.builder_organization = self.builder_organization
                self.subdivision.save()

        if original.get("project_name") != self.project_name:
            if self.subdivision:
                subdivision_name = ""
                if self.project_name:
                    subdivision_name = self.project_name
                self.subdivision.name = subdivision_name
                self.subdivision.save()

        if not self.pk or self.architect_organization_id != original.get(
            "architect_organization_id"
        ):
            self.update_relationships(company=self.architect_organization)

        if not self.pk or self.developer_organization_id != original.get(
            "developer_organization_id"
        ):
            self.update_relationships(company=self.developer_organization)

        if not self.pk or self.community_owner_organization_id != original.get(
            "community_owner_organization_id"
        ):
            self.update_relationships(company=self.community_owner_organization)

        if self.id:
            # Send notification when ERFP changed(ignore first time)
            if self.entity_responsible_for_payment != original.get(
                "entity_responsible_for_payment"
            ):
                ProjectRegistrationERFPNotificationMessage().send(
                    company=customer_hirl_app.get_customer_hirl_provider_organization(),
                    context={
                        "new_company_type": self.get_entity_responsible_for_payment_display(),
                        "url": self.get_absolute_url(),
                        "h_numbers": ", ".join(
                            map(str, self.projects.values_list("h_number", flat=True))
                        ),
                    },
                )

            if original.get("eep_program_id") != self.eep_program_id:
                for project in self.projects.filter(home_status__isnull=False):
                    project.home_status.eep_program_id = self.eep_program_id
                    project.home_status.save()

        return super(HIRLProjectRegistration, self).save(**kwargs)

    def update_relationships(self, company):
        """
        Updates Relationships for all Projects and subdivision
        :param company: Company Object
        """
        if not company:
            return

        available_companies = [
            self.builder_organization,
            self.registration_user.company,
            self.architect_organization,
            self.community_owner_organization,
            self.developer_organization,
            customer_hirl_app.get_customer_hirl_provider_organization(),
        ]
        available_companies = [x for x in available_companies if x is not None]

        # disconnect signal to increase performance
        # we do not need to update home_status somehow at that point
        signals.post_save.disconnect(
            receiver=update_stats_for_home_rels,
            sender=Relationship,
            dispatch_uid="axis.relationship.update_stats_for_home_sub_rels",
        )
        Relationship.objects.create_mutual_relationships(*available_companies, force=True)

        if self.pk:
            for project in self.projects.all().select_related("home_status", "home_status__home"):
                if not project.home_status:
                    continue
                project.home_status.home.relationships.filter(
                    company__company_type=company.company_type
                ).delete()
                for available_company in available_companies:
                    Relationship.objects.validate_or_create_relations_to_entity(
                        entity=project.home_status.home,
                        direct_relation=available_company,
                        force=True,
                    )

        if self.subdivision:
            self.subdivision.relationships.filter(
                company__company_type=company.company_type
            ).delete()
            for available_company in available_companies:
                Relationship.objects.validate_or_create_relations_to_entity(
                    entity=self.subdivision,
                    direct_relation=available_company,
                    force=True,
                )

        # re-connect signal back
        signals.post_save.connect(
            update_stats_for_home_rels,
            sender=Relationship,
            dispatch_uid="axis.relationship.update_stats_for_home_sub_rels",
        )

    def get_project_client_company(self):
        """
        Detect which company should use for Client Agreement and COI checks
        :raise ObjectDoesNotExist - when project_client is not set
        :return: Company
        """
        if not self.project_client:
            raise ObjectDoesNotExist("Project client is not set")
        if self.project_client == self.PROJECT_CLIENT_BUILDER:
            if not self.builder_organization:
                raise ObjectDoesNotExist("Project client is not set")
            return self.builder_organization
        elif self.project_client == self.PROJECT_CLIENT_ARCHITECT:
            if not self.architect_organization:
                raise ObjectDoesNotExist("Project client is not set")
            return self.architect_organization
        elif self.project_client == self.PROJECT_CLIENT_OWNER:
            if not self.community_owner_organization:
                raise ObjectDoesNotExist("Project client is not set")
            return self.community_owner_organization
        elif self.project_client == self.PROJECT_CLIENT_DEVELOPER:
            if not self.developer_organization:
                raise ObjectDoesNotExist("Project client is not set")
            return self.developer_organization

        raise ObjectDoesNotExist("Project client is Unknown")

    def get_company_responsible_for_payment(self):
        """
        Detect which company should use for payment when we work with any payments
        :raise ObjectDoesNotExist - when entity_responsible_for_payment is not set
        :return: Company
        """

        if not self.entity_responsible_for_payment:
            raise ObjectDoesNotExist("Entity responsible for payment is not set")
        if self.entity_responsible_for_payment == self.BUILDER_RESPONSIBLE_ENTITY:
            if not self.builder_organization:
                raise ObjectDoesNotExist("Entity responsible for payment is not set")
            return self.builder_organization
        elif self.entity_responsible_for_payment == self.ARCHITECT_RESPONSIBLE_ENTITY:
            if not self.architect_organization:
                raise ObjectDoesNotExist("Entity responsible for payment is not set")
            return self.architect_organization
        elif self.entity_responsible_for_payment == self.COMMUNITY_OWNER_RESPONSIBLE_ENTITY:
            if not self.community_owner_organization:
                raise ObjectDoesNotExist("Entity responsible for payment is not set")
            return self.community_owner_organization
        elif self.entity_responsible_for_payment == self.DEVELOPER_RESPONSIBLE_ENTITY:
            if not self.developer_organization:
                raise ObjectDoesNotExist("Entity responsible for payment is not set")
            return self.developer_organization
        elif self.entity_responsible_for_payment == self.VERIFIER_RESPONSIBLE_ENTITY:
            return self.registration_user.company

        raise ObjectDoesNotExist("Entity responsible for payment is Unknown")

    # Django FSM

    @transition(
        field=state,
        source=NEW_STATE,
        target=PENDING_STATE,
        permission=lambda instance, user: user.company
        and user.company.slug == customer_hirl_app.CUSTOMER_SLUG,
    )
    def pending(self):
        msg = HIRLProjectRegistrationStateChangedMessage()
        msg.send(
            company=self.registration_user.company,
            context={
                "url": self.get_absolute_url(),
                "old_state": self.get_state_display(),
                "new_state": "Pending",
                "verifier": self.registration_user.get_full_name(),
            },
        )

    def can_active(self):
        is_allowed = True
        if self.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            check_for_empty_fields = [
                "builder_organization",
                "community_owner_organization",
                "architect_organization",
                "developer_organization",
            ]
            for field in check_for_empty_fields:
                value = getattr(self, field)
                if not value:
                    is_allowed = False
                    break
        return is_allowed

    @transition(
        field=state,
        source=[NEW_STATE, PENDING_STATE],
        target=ACTIVE_STATE,
        conditions=[
            can_active,
        ],
        permission=lambda instance, user: user.is_customer_hirl_company_member(),
    )
    def active(self):
        msg = HIRLProjectRegistrationStateChangedMessage()
        msg.send(
            company=self.registration_user.company,
            context={
                "url": self.get_absolute_url(),
                "old_state": self.get_state_display(),
                "new_state": "Active",
                "verifier": self.registration_user.get_full_name(),
            },
        )

    @transition(
        field=state,
        source=NEW_STATE,
        target=REJECTED_STATE,
        permission=lambda instance, user: user.company
        and user.company.slug == customer_hirl_app.CUSTOMER_SLUG,
    )
    def reject(self, reason):
        self.state_change_reason = reason

        msg = HIRLProjectRegistrationRejectedMessage()
        msg.send(
            company=self.registration_user.company,
            context={
                "url": self.get_absolute_url(),
                "project_registration_id": f"{self.id}",
                "reason": reason,
            },
        )

    @transition(
        field=state,
        source=[PENDING_STATE, ACTIVE_STATE],
        target=ABANDONED_STATE,
        permission=lambda instance, user: user.company
        and user.company.slug == customer_hirl_app.CUSTOMER_SLUG,
    )
    def abandon(self, user: User, billing_state: str, reason: str):
        """
        :param user: user that performs transition
        :param billing_state: HIRLProject Billing State choice
        :param reason: Reason for state transition
        """

        self.state_change_reason = reason
        annotation_type = AnnotationType.objects.get(slug="note")
        home_status_ct = ContentType.objects.get_for_model(EEPProgramHomeStatus)
        for project in self.projects.all():
            invoice_exists = project.home_status.invoiceitemgroup_set.exclude(invoice=None).exists()
            if not invoice_exists:
                project.manual_billing_state = billing_state
                project.save()
            project.home_status.make_transition(transition="to_abandoned_transition", user=user)
            Annotation.objects.create(
                content_type=home_status_ct,
                object_id=project.home_status.id,
                type=annotation_type,
                content=reason,
                user=user,
            )

        self.save()

        msg = HIRLProjectRegistrationRejectedMessage()
        msg.send(
            company=self.registration_user.company,
            context={
                "url": self.get_absolute_url(),
                "project_registration_id": f"{self.id}",
                "reason": reason,
            },
        )


class HIRLLegacyRegistration(models.Model):
    """
    NGBS API Registration data
    """

    registration = models.ForeignKey(
        "HIRLProjectRegistration", on_delete=models.SET_NULL, blank=True, null=True
    )
    hirl_id = models.PositiveIntegerField(verbose_name="Internal ID", blank=True)
    issued_project_id = models.TextField(verbose_name="Issued Project ID", blank=True)
    scoring_path_name = models.TextField(blank=True)
    is_accessory_structure = models.BooleanField(default=False)
    is_commercial_space = models.BooleanField(default=False)
    data = AxisJSONField(default=dict)
    convert_to_registration_error = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
