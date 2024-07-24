__author__ = "Artem Hruzd"
__date__ = "05/29/2020 16:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from typing import Optional

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import models, transaction
from django.db.models import Sum, DecimalField, Case, When, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from hashid_field import HashidAutoField
from simple_history.models import HistoricalRecords

from axis.core.fields import AxisJSONField
from axis.core.utils import get_frontend_url
from axis.customer_hirl.managers import HIRLProjectQuerySet, GreenEnergyBadgeQuerySet
from axis.customer_hirl.messages import HIRLProjectBillingStateChangedManuallyMessage
from axis.home.models import EEPProgramHomeStatus
from axis.home.models import Home
from axis.invoicing.models import InvoiceItemGroup, InvoiceItem, InvoiceItemTransaction
from axis.relationship.models import Relationship
from .project_registration import HIRLProjectRegistration

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")
frontend_app = apps.get_app_config("frontend")


class HIRLProject(models.Model):
    # Billing states using for Green energy exports and calculating dynamically

    # Registration approved; fees calculated; client not notified yet
    NEW_BILLING_STATE = "new"
    # Still debating whether we need to "approve" fees…
    NEW_QUEUED_BILLING_STATE = "new_queued"
    # Client notified of fees owed; no invoice generated yet
    NEW_NOTIFIED_BILLING_STATE = "new_notified"
    # Invoice generated (by client or NGBS)
    NOTICE_SENT_BILLING_STATE = "notice_sent"
    # Zero dollar balance on project and NGBS has certified the project
    COMPLETED_BILLING_STATE = "completed"

    # Project have been completed and the
    # certificates issued but the clients were not obligated to pay
    AUTOMATICALLY_BILLING_STATE = ""
    COMPLIMENTARY_BILLING_STATE = "complimentary"
    NOT_PURSUING_BILLING_STATE = "not_pursuing"
    TEST_BILLING_STATE = "test"
    VOID_BILLING_STATE = "void"
    SPECIAL_4300_BILLING_STATE = "4300"

    BILLING_STATE_DISPLAY = {
        AUTOMATICALLY_BILLING_STATE: "Automatically",
        NEW_BILLING_STATE: "New",
        NEW_QUEUED_BILLING_STATE: "New - Queued",
        NEW_NOTIFIED_BILLING_STATE: "New - Notified",
        NOTICE_SENT_BILLING_STATE: "Notice Sent",
        COMPLETED_BILLING_STATE: "Completed",
        COMPLIMENTARY_BILLING_STATE: "Сomplimentary",
        NOT_PURSUING_BILLING_STATE: "Not pursuing",
        TEST_BILLING_STATE: "Test",
        VOID_BILLING_STATE: "Void",
        SPECIAL_4300_BILLING_STATE: "4300",
    }

    BILLING_STATE_CHOICES = (
        (AUTOMATICALLY_BILLING_STATE, "Automatically"),
        (NEW_BILLING_STATE, "New"),
        (NEW_QUEUED_BILLING_STATE, "New - Queued"),
        (NEW_NOTIFIED_BILLING_STATE, "New - Notified"),
        (NOTICE_SENT_BILLING_STATE, "Notice Sent"),
        (COMPLETED_BILLING_STATE, "Completed"),
        (COMPLIMENTARY_BILLING_STATE, "Complimentary"),
        (NOT_PURSUING_BILLING_STATE, "Not pursuing"),
        (TEST_BILLING_STATE, "Test"),
        (VOID_BILLING_STATE, "Void"),
        (SPECIAL_4300_BILLING_STATE, "4300"),
    )

    CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE = "core&shell"
    FULL_COMMERCIAL_SPACE_TYPE = "full"

    COMMERCIAL_SPACE_TYPE_CHOICES = (
        (CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE, "Core & Shell"),
        (FULL_COMMERCIAL_SPACE_TYPE, "Full"),
    )

    LD_PROJECT_TYPE_LETTER_PROJECT = "letter"
    LD_PROJECT_TYPE_PHASE_PROJECT = "phase"

    LAND_DEVELOPMENT_PROJECT_TYPE_CHOICES = (
        (LD_PROJECT_TYPE_LETTER_PROJECT, "Letter of Approval"),
        (LD_PROJECT_TYPE_PHASE_PROJECT, "Phase"),
    )

    id = HashidAutoField(
        primary_key=True,
        salt=f"customer_hirl.HIRLProject{settings.HASHID_FIELD_SALT}",
        prefix="PRJ",
    )

    registration = models.ForeignKey(
        "HIRLProjectRegistration", null=True, on_delete=models.CASCADE, related_name="projects"
    )

    home_status = models.OneToOneField(
        EEPProgramHomeStatus,
        related_name="%(app_label)s_project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    billing_state = models.CharField(
        max_length=30,
        verbose_name="Billing State",
        choices=BILLING_STATE_CHOICES,
        default=NEW_BILLING_STATE,
        blank=True,
    )

    manual_billing_state = models.CharField(
        max_length=30,
        verbose_name="Billing State Override",
        choices=BILLING_STATE_CHOICES,
        help_text="Manual override Billing State",
        default=AUTOMATICALLY_BILLING_STATE,
        blank=True,
    )

    is_jamis_milestoned = models.BooleanField(
        default=False,
        help_text="Populating automatically from Billing Rule file that generated by JAMIS service",
    )
    green_energy_badges = models.ManyToManyField(
        "HIRLGreenEnergyBadge", blank=True, verbose_name="NGBS Green+ Badges"
    )

    is_accessory_structure = models.BooleanField(
        verbose_name="Is this property associated with an "
        "Accessory Structure Seeking Certification?",
        default=False,
    )
    accessory_structure_description = models.TextField(blank=True)

    is_accessory_dwelling_unit = models.BooleanField(
        verbose_name="Is this property associated with an Accessory Dwelling Unit (ADU) seeking certification?",
        default=False,
    )
    accessory_dwelling_unit_description = models.TextField(blank=True)

    lot_number = models.CharField(max_length=64, blank=True, null=True)
    home_address_geocode = models.ForeignKey(
        "geocoder.Geocode",
        related_name="+",
        on_delete=models.CASCADE,
        help_text="Geocode address entered by Verifier on project registration",
    )

    home_address_geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Selected by user in case of multiple valid results, "
        "automatically when we have one result and "
        "empty when geocode do not have valid results",
    )

    h_number = models.IntegerField(default=0, unique=True, help_text="Special Unique Key for HI")
    hud_disaster_case_number = models.CharField(
        max_length=255, verbose_name="HUD Disaster Case Number", null=True, blank=True
    )

    is_require_wri_certification = models.BooleanField(
        verbose_name="Is this project seeking a WRI?", default=False
    )
    is_require_water_sense_certification = models.BooleanField(
        verbose_name="Is the project seeking WaterSense Certification?", default=False
    )
    is_require_rough_inspection = models.BooleanField(
        verbose_name="Will this remodel project require a Rough inspection?", default=True
    )
    is_require_final_inspection = models.BooleanField(
        verbose_name="Will this project require a Final inspection?", default=True
    )

    is_appeals_project = models.BooleanField(
        verbose_name="Is this an appeals project?", default=False
    )

    # single family specific fields

    # multifamily specific fields
    building_number = models.CharField(max_length=30, null=True, blank=True)
    is_include_commercial_space = models.BooleanField(
        verbose_name="Is Include Commercial Space", default=False
    )
    commercial_space_type = models.CharField(
        max_length=32, choices=COMMERCIAL_SPACE_TYPE_CHOICES, blank=True, null=True
    )
    total_commercial_space = models.FloatField(null=True, blank=True)
    story_count = models.IntegerField(null=True, blank=True)
    number_of_units = models.IntegerField(null=True, blank=True)
    commercial_space_parent = models.ForeignKey(
        "self",
        verbose_name="Commercial Space project attached",
        null=True,
        blank=True,
        related_name="commercial_spaces",
        on_delete=models.SET_NULL,
    )

    # land development specific fields
    number_of_lots = models.IntegerField(null=True, blank=True)
    are_all_homes_in_ld_seeking_certification = models.BooleanField(blank=True, null=True)
    land_development_project_type = models.CharField(
        max_length=255, choices=LAND_DEVELOPMENT_PROJECT_TYPE_CHOICES, null=True, blank=True
    )
    land_development_phase_number = models.IntegerField(
        null=True, blank=True, help_text="Phase number for project. NULL is using for LOA projects"
    )

    # internal

    certification_counter = models.IntegerField(
        verbose_name="Certification Counter",
        default=0,
        help_text="Increased automatically when NGBS Project have been certified",
    )

    wri_certification_counter = models.IntegerField(
        verbose_name="WRI Certification Counter",
        default=0,
        help_text="Increased automatically when NGBS WRI Project have been certified",
    )

    initial_invoice_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set once when first non Appeals Invoice was created",
    )
    most_recent_notice_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent Fee notification sent to Company Responsible For Payment",
    )

    vr_batch_submission_parent_rough = models.ForeignKey(
        "self",
        verbose_name="Rough Parent project",
        null=True,
        blank=True,
        related_name="vr_batch_submission_rough_childrens",
        on_delete=models.SET_NULL,
    )

    vr_batch_submission_parent_final = models.ForeignKey(
        "self",
        verbose_name="Final Parent project",
        null=True,
        blank=True,
        related_name="vr_batch_submission_final_childrens",
        on_delete=models.SET_NULL,
    )

    system_notes = AxisJSONField(
        blank=True,
        null=True,
        help_text="Helps to identify legacy NGBS projects from different sources. "
        "This field can be used to store any information during import",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = HIRLProjectQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-id"]

    def __str__(self):
        return f"NGBS Project ID: {self.id} Registration ID: {self.registration_id}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(HIRLProject, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    # Django hooks

    def get_absolute_url(self):
        """
        Link to front end detail page
        :return: string
        """
        return get_frontend_url("hi", "project_registrations", self.registration_id)

    def can_edit(self, user):
        """
        This hook helps Examine view check permissions
        :param user: User object
        :return: Boolean
        """
        can_edit_registration = self.registration.can_edit(user=user)
        if user.company_id:
            if user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
                return can_edit_registration

        # We can edit registration for MF when VR Uploaded, but we can't edit any building
        # for this registration
        if self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            qa_status_count = self.registration.projects.filter(
                home_status__qastatus__isnull=False
            ).count()
            if qa_status_count:
                return False

        return can_edit_registration

    def save(self, **kwargs):  # noqa: C901
        """
        In save we generate unique h_number starting from 100000
        Also syncing company relations with home attached for this project
        :param kwargs:
        :return: HIRLProject
        """
        is_new = self.pk is None

        original = getattr(self, "_loaded_values", dict())
        # start h_number from 100000, using while for thread safe
        if self.h_number:
            super(HIRLProject, self).save(**kwargs)
        else:
            while not self.h_number:
                last = HIRLProject.objects.all().order_by("pk").last()
                if last:
                    h_number = last.h_number + 1
                else:
                    h_number = 100000
                self.h_number = h_number

                try:
                    super(HIRLProject, self).save(**kwargs)
                except IntegrityError:
                    self.h_number = None
        if (
            "manual_billing_state" in original
            and self.manual_billing_state != original["manual_billing_state"]
        ):
            self.calculate_billing_state()

        if not is_new:
            self._track_changes_for_home_address_geocode()
            self._track_changes_for_registration()

            # track changes for some fields
            if (
                self.registration_id
                and self.home_status_id
                and self.manual_billing_state != HIRLProject.NOT_PURSUING_BILLING_STATE
            ):
                self._track_changes_for_story_count()
                self._track_changes_for_number_of_units()
                self._track_changes_for_commercial_space_type()
                self._track_changes_for_number_of_lots()
                self._track_changes_for_is_appeals_project()

            self._track_changes_for_manual_billing_state()

    def create_home_status(self):
        """
        Create Home and other AXIS resources based on Project information.
        Attach Project to created home
        """
        from axis.subdivision.models import Subdivision
        from axis.home.tasks import update_home_states

        hirl_provider_company = customer_hirl_app.get_customer_hirl_provider_organization()
        # create Home
        is_multi_family = False

        if self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            is_multi_family = True

        if self.home_address_geocode_response:
            address = self.home_address_geocode_response.get_normalized_fields()
            street_line1 = address.get("street_line1", "")
            street_line2 = address.get("street_line2", "")
            city = address.get("city", None)
            county = address.get("county", None)
            state = address.get("state", None)
            zipcode = address.get("zipcode", None)
            geocode_response = self.home_address_geocode_response
        else:
            street_line1 = self.home_address_geocode.raw_street_line1
            street_line2 = self.home_address_geocode.raw_street_line2
            city = self.home_address_geocode.raw_city
            county = None
            state = None
            if city:
                county = city.county
                if county:
                    state = city.county.state
            zipcode = self.home_address_geocode.raw_zipcode
            geocode_response = None

        home = Home.objects.create(
            lot_number=self.lot_number,
            street_line1=street_line1,
            street_line2=street_line2,
            is_multi_family=is_multi_family,
            city=city,
            county=county,
            state=state,
            zipcode=zipcode,
            geocode_response=geocode_response,
        )

        # add created home to subdivision
        if self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            if not self.registration.subdivision:
                builder_name = ""
                if self.registration.builder_organization:
                    builder_name = self.registration.builder_organization.name
                subdivision = Subdivision.objects.create(
                    name=self.registration.project_name,
                    builder_name=builder_name,
                    builder_org=self.registration.builder_organization,
                    city=city,
                    is_multi_family=True,
                )

                self.registration.subdivision = subdivision
                self.registration.save()

            home.subdivision = self.registration.subdivision
            home.save()
        elif self.registration.project_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE:
            home.subdivision = self.registration.subdivision
            home.save()

        # create EEPProgramHomeStatus
        eep_program_home_status = EEPProgramHomeStatus.objects.create(
            home=home,
            eep_program=self.registration.eep_program,
            company=self.registration.registration_user.company,
            certification_date=None,
        )

        self.home_status = eep_program_home_status
        self.save()
        self.registration.save()

        new_invoice_group = InvoiceItemGroup.objects.create(
            home_status=eep_program_home_status, created_by=None
        )

        # certification fee
        if self.land_development_project_type != HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT:
            _ = InvoiceItem.objects.create(
                group=new_invoice_group,
                name=f"Certification Fee: {self.registration.eep_program}",
                cost=self.calculate_certification_fees_cost(),
                protected=True,
            )

        if self.land_development_project_type == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT:
            _ = InvoiceItem.objects.create(
                group=new_invoice_group,
                name=customer_hirl_app.DEFAULT_LOA_FEE_LABEL,
                cost=self.calculate_loa_fee_cost(),
                protected=True,
            )

        # per unit fee
        if (
            self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            and not self.is_include_commercial_space
            and not self.is_accessory_structure
        ):
            _ = InvoiceItem.objects.create(
                group=new_invoice_group,
                name="Certification Fee: Unit Fee",
                cost=self.calculate_per_unit_fee_cost(),
                protected=True,
            )

        # badges fee
        for green_energy_badge in self.green_energy_badges.all():
            _ = InvoiceItem.objects.create(
                group=new_invoice_group,
                name=green_energy_badge.get_name_with_invoice_label(),
                cost=green_energy_badge.calculate_cost(
                    hirl_project_registration_type=self.registration.project_type,
                    is_accessory_dwelling_unit=self.is_accessory_dwelling_unit,
                    is_accessory_structure=self.is_accessory_structure,
                    builder_organization=self.registration.builder_organization,
                    story_count=self.story_count,
                ),
                protected=True,
            )

        if self.is_appeals_project:
            appeals_invoice_item_group = InvoiceItemGroup.objects.create(
                home_status=eep_program_home_status,
                created_by=None,
                category=InvoiceItemGroup.APPEALS_FEE_CATEGORY,
            )
            _ = InvoiceItem.objects.create(
                group=appeals_invoice_item_group,
                name=customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL,
                cost=self.calculate_appeals_fee_cost(),
                protected=True,
            )

        # create relationships
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=home,
            direct_relation=hirl_provider_company,
            implied_relations=hirl_provider_company,
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=home,
            direct_relation=self.registration.registration_user.company,
            implied_relations=self.registration.registration_user.company,
        )

        self.registration.update_relationships(company=self.registration.builder_organization)
        self.registration.update_relationships(company=self.registration.architect_organization)
        self.registration.update_relationships(company=self.registration.developer_organization)
        self.registration.update_relationships(
            company=self.registration.community_owner_organization
        )

        if getattr(self.registration, "subdivision", None):
            Relationship.objects.validate_or_create_relations_to_entity(
                entity=self.registration.subdivision,
                direct_relation=hirl_provider_company,
                implied_relations=hirl_provider_company,
            )
            Relationship.objects.validate_or_create_relations_to_entity(
                entity=self.registration.subdivision,
                direct_relation=self.registration.registration_user.company,
                implied_relations=self.registration.registration_user.company,
            )

        self.calculate_billing_state()

        update_home_states(eepprogramhomestatus_id=self.home_status.id)

    def update_invoice_item_fees(self, name, new_cost, old_cost, category=None):
        """
        Create new Invoice Item group and new Invoice item if new_cos not equal old_cost
        :param name: Name for InvoiceItem
        :param new_cost: new cost
        :param old_cost: old cost
        :param category: Invoice Item Group category
        """
        diff = new_cost - old_cost

        if not category:
            category = InvoiceItemGroup.ANY_CATEGORY

        if diff:
            new_invoice_group = InvoiceItemGroup.objects.filter(
                home_status=self.home_status,
                invoice__isnull=True,
                category=category,
            ).first()
            if not new_invoice_group:
                new_invoice_group = InvoiceItemGroup.objects.create(
                    home_status=self.home_status, created_by=None
                )

            _ = InvoiceItem.objects.create(
                group=new_invoice_group, name=name, cost=diff, protected=True
            )

    def calculate_certification_fees_cost(
        self,
        certification_fee=None,
        story_count=None,
        commercial_space_type=None,
        number_of_lots=None,
        are_all_homes_in_ld_seeking_certification=None,
        build_to_rent=None,
    ):
        """
        Calculates certification Fees based on a table provided by Customer
        :param certification_fee: Allows to override
        customer_hirl_certification_fee value for fee calculation. Default to:
        self.registration.eep_program.customer_hirl_certification_fee
        :param story_count: Allows to override story_count value for fee calculation.
        Default to: self.story_count
        :param number_of_lots: Allows to override number_of_lots value for fee calculation.
        Default to: self.number_of_lots
        :param commercial_space_type: Allows to override commercial_space_type value for fee
        :param are_all_homes_in_ld_seeking_certification: Allows to override number_of_lots value for fee calculation.
        Default to: self.are_all_homes_in_ld_seeking_certification
        calculation
        :param build_to_rent: Allows to override registration.build_to_rent value
        :return: Decimal - cost
        """

        if story_count is None:
            story_count = self.story_count

        if number_of_lots is None:
            number_of_lots = self.number_of_lots

        if are_all_homes_in_ld_seeking_certification is None:
            are_all_homes_in_ld_seeking_certification = (
                self.are_all_homes_in_ld_seeking_certification
            )

        if certification_fee is None:
            certification_fee = self.registration.eep_program.customer_hirl_certification_fee

        if self.is_accessory_structure:
            return customer_hirl_app.ACCESSORY_STRUCTURE_SEEKING_CERTIFICATION_FEE

        if self.is_accessory_dwelling_unit:
            return customer_hirl_app.ACCESSORY_DWELLING_UNIT_STRUCTURE_CERTIFICATION_FEE

        if commercial_space_type is None:
            commercial_space_type = self.commercial_space_type

        if commercial_space_type == self.CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE:
            return customer_hirl_app.COMMERCIAL_SPACE_CORE_AND_SHELL_CERTIFICATION_FEE
        elif commercial_space_type == self.FULL_COMMERCIAL_SPACE_TYPE:
            return customer_hirl_app.COMMERCIAL_SPACE_FULL_FITTED_CERTIFICATION_FEE

        if build_to_rent is None:
            build_to_rent = self.registration.is_build_to_rent

        if build_to_rent:
            if (
                self.registration.eep_program.slug
                in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_NEW_CONSTRUCTION_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_REMODEL_SLUGS
            ):
                return customer_hirl_app.BUILD_TO_RENT_FEE

        if (
            self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            and self.registration.eep_program.slug not in customer_hirl_app.WRI_PROGRAM_LIST
        ):
            if 4 <= story_count <= 8:
                certification_fee = certification_fee + 400
            elif story_count >= 9:
                certification_fee = certification_fee + 700

        # land development fees
        if self.registration.project_type == HIRLProjectRegistration.LAND_DEVELOPMENT_PROJECT_TYPE:
            if self.land_development_project_type == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT:
                return 0
            else:
                if are_all_homes_in_ld_seeking_certification:
                    certification_fee = (
                        customer_hirl_app.DEFAULT_LAND_DEVELOPMENT_ALL_HOMES_SEEKING_CERTIFICATION_FEE
                    )
                else:
                    if number_of_lots <= 99:
                        certification_fee = (
                            customer_hirl_app.DEFAULT_LAND_DEVELOPMENT_CERTIFICATION_FEE
                        )
                    else:
                        certification_fee = (
                            customer_hirl_app.DEFAULT_LAND_DEVELOPMENT_MORE_THAN_100_LOTS_CERTIFICATION_FEE
                        )

        # discount
        if self.registration.project_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE:
            if self.registration.builder_organization.slug == "builder-neal-communities":
                certification_fee = 75

        return certification_fee

    def calculate_per_unit_fee_cost(self, per_unit_fee=None, number_of_units=None):
        """
        Calculates per Unit Fees based on a table provided by Customer
        :param per_unit_fee: Allow to override per_unit_fee
        customer_hirl_per_unit_fee value for fee calculation. Default to: self.story_count
        :param number_of_units: Allow to override story_count value for fee calculation.
        Default to: self.number_of_units
        :return: Decimal - cost
        """
        if self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            if number_of_units is None:
                number_of_units = self.number_of_units
            if per_unit_fee is None:
                per_unit_fee = self.registration.eep_program.customer_hirl_per_unit_fee

            return number_of_units * per_unit_fee
        return 0

    def calculate_appeals_fee_cost(self, is_appeals_project: Optional[bool] = None) -> float:
        """
        Appeals Fees - additional fee based on is_appeals_project flag

        :param is_appeals_project: Allow to override is_appeals_project flag
        :return: Decimal - cost
        """
        if is_appeals_project is None:
            is_appeals_project = self.is_appeals_project

        appeals_registration_total = (
            InvoiceItem.objects.filter(
                group__home_status__customer_hirl_project__registration=self.registration,
                group__category=InvoiceItemGroup.APPEALS_FEE_CATEGORY,
            )
            .exclude(group__home_status__customer_hirl_project=self)
            .aggregate(total=Coalesce(Sum("cost"), 0, output_field=DecimalField()))["total"]
        )
        remaining_fee = max(
            customer_hirl_app.MAX_APPEALS_FEE_PER_REGISTRATION - appeals_registration_total, 0
        )

        appeals_fee = 0

        if is_appeals_project:
            if self.is_accessory_structure:
                appeals_fee = customer_hirl_app.DEFAULT_APPEALS_ACCESSORY_STRUCTURE_FEE
            elif self.is_accessory_dwelling_unit:
                appeals_fee = customer_hirl_app.DEFAULT_APPEALS_DWELLING_UNIT_STRUCTURE_FEE
            elif self.commercial_space_type:
                appeals_fee = customer_hirl_app.DEFAULT_APPEALS_COMMERCIAL_SPACE_FEE
            elif (
                self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            ):
                appeals_fee = customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE
            elif (
                self.registration.project_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
            ):
                appeals_fee = customer_hirl_app.DEFAULT_APPEALS_SINGLE_FAMILY_FEE

        if appeals_fee > remaining_fee:
            appeals_fee = remaining_fee

        return appeals_fee

    def calculate_loa_fee_cost(self, ld_workflow: Optional[str] = None) -> float:
        if ld_workflow is None:
            ld_workflow = self.registration.ld_workflow

        if (
            ld_workflow
            == HIRLProjectRegistration.LD_WORKFLOW_LETTER_OF_APPROVAL_AND_FULL_CERTIFICATION
        ):
            return customer_hirl_app.DEFAULT_LAND_DEVELOPMENT_LETTER_OF_APPROVAL_CERTIFICATION_FEE

        return 0

    def get_billing_rule_id(self):
        """
        From JAMIS report docs:
        Billing Rule ID: The billing rule ID takes the ID number and creates
        a XXXX-XXXXXXXX-XXXXXXXX number.  The first set of 4 numbers will always be 1015.
        The second set of 8 numbers will be the ID with the addition of leading zeroes needed to
        make the number an 8-digit number.  The third set of 8 numbers will be the same ID number
        with the addition of leading zeroes needed to make the number an 8-digit number.
        For example, the ID number 034537 will create the following billing
        rule ID for JAMIS: 1015-00034537-00034537
        :return: string
        """
        if self.registration.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST:
            return f"1529-{self.h_number:08d}-{self.h_number:08d}"
        return f"1015-{self.h_number:08d}-{self.h_number:08d}"

    def get_job_id(self):
        """
        From JAMIS report docs:
        Job ID: The job ID takes the ID number and creates a XXXX-XXXXXXXX-XXXXXXXX-XXX number.
        The first set of 4 numbers will always be 1015.
        The second set of 8 numbers will be the ID number with the addition of leading
        zeroes needed to make the number an 8-digit number.
        The third set of 8 numbers will be the same ID number with the addition of
        leading zeroes needed to make the number an 8-digit number.
        The last set of 3 numbers will always be 001.  For example, the ID number
        034537 will create the following billing rule ID for JAMIS: 1015-00034537-00034537-001.
        :return: string
        """
        if self.registration.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST:
            return f"1529-{self.h_number:08d}-{self.h_number:08d}-001"
        return f"1015-{self.h_number:08d}-{self.h_number:08d}-001"

    def get_invoice_rule_id(self):
        """
        From JAMIS report docs:
        Invoice Rule ID: The invoice rule ID takes the ID number
        and creates a XXXX-XXXXXXXX number.
        The first set of 4 numbers will always be 1015.
        The second set of 8 numbers will be the ID number with the addition of leading zeroes
        needed to make the number an 8-digit number.  For example, the ID
        number 034537 will create the following billing rule ID for JAMIS: 1015-00034537
        :return: string
        """
        if self.registration.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST:
            return f"1529-{self.h_number:08d}"
        return f"1015-{self.h_number:08d}"

    def pay(self, amount, paid_by=None, date_paid=None, note=""):
        """
        Pay for project means that Amount to pay
        we divide across all InvoiceItems for this project.
        To achieve this we create a transaction per Invoice Item.
        Overpay will create additional Transaction for last Invoice Item for this project

        :raise ObjectDoesNotExist - if home_status for
        this project is not exists, e.g project is not Active and do not have home
        :raise Value error - if project do not have Invoice Items to pay

        :param amount: Decimal amount to pay for project
        :param paid_by: optional - User that is paying for this project
        :param date_paid: optional - datetime
        :param note: optional - note for created Transactions, except additional overpay Transaction
        :return: list of created transactions
        """
        if not amount:
            return []

        if not self.home_status:
            raise ObjectDoesNotExist

        if not date_paid:
            date_paid = timezone.now()

        transactions = []
        amount_left = amount

        # order fees for project by category. Pay for Appeals first
        invoice_items = InvoiceItem.objects.filter(
            group__in=self.home_status.invoiceitemgroup_set.all(), current_balance__gt=0
        ).order_by(
            Case(
                When(group__category=InvoiceItemGroup.APPEALS_FEE_CATEGORY, then=Value(0)),
                default=Value(1),
            ),
            "created_at",
        )

        for invoice_item in invoice_items:
            transaction_data = dict(item=invoice_item, note=note, created_by=paid_by)
            if amount_left - invoice_item.current_balance > 0:
                transaction_data["amount"] = invoice_item.current_balance
            else:
                transaction_data["amount"] = amount_left

            item_transaction = InvoiceItemTransaction.objects.create(**transaction_data)
            item_transaction.created_at = date_paid
            item_transaction.save()
            transactions.append(item_transaction)

            amount_left = amount_left - invoice_item.current_balance
            if amount_left <= 0:
                break

        if amount_left > 0:
            invoice_item_group = InvoiceItemGroup.objects.create(home_status=self.home_status)
            invoice_item = InvoiceItem.objects.create(
                group=invoice_item_group, name="Overpay", cost=0
            )

            item_transaction = InvoiceItemTransaction.objects.create(
                item=invoice_item,
                amount=amount_left,
                note="Overpay",
                created_by=paid_by,
            )
            item_transaction.created_at = date_paid
            item_transaction.save()
            transactions.append(item_transaction)

        return transactions

    @transaction.atomic(savepoint=False)
    def calculate_billing_state(self):
        # acquire a lock
        obj = (
            self.__class__.objects.filter(id=self.id)
            .select_related("home_status")
            .select_for_update()
            .get()
        )

        if obj.manual_billing_state != obj.AUTOMATICALLY_BILLING_STATE:
            billing_state = obj.manual_billing_state
        else:
            if not obj.home_status:
                billing_state = obj.NEW_BILLING_STATE
            else:
                if obj.home_status.state == EEPProgramHomeStatus.COMPLETE_STATE:
                    billing_state = obj.COMPLETED_BILLING_STATE
                else:
                    invoice_item_groups_count = obj.home_status.invoiceitemgroup_set.all().count()
                    invoice_item_groups_without_invoice_count = (
                        obj.home_status.invoiceitemgroup_set.filter(invoice__isnull=True).count()
                    )
                    hirllegacycertification = obj.hirllegacycertification_set.all().first()

                    if (
                        (
                            invoice_item_groups_count == 1
                            and invoice_item_groups_without_invoice_count > 0
                        )
                        or not invoice_item_groups_count
                    ) and obj.billing_state not in [
                        obj.NOTICE_SENT_BILLING_STATE,
                        obj.COMPLETED_BILLING_STATE,
                    ]:
                        if hirllegacycertification:
                            invoice_sent_date = hirllegacycertification.data.get(
                                "InvoiceSentDate", None
                            )
                            if not invoice_sent_date:
                                billing_state = obj.NEW_NOTIFIED_BILLING_STATE
                            else:
                                billing_state = obj.NOTICE_SENT_BILLING_STATE
                        else:
                            billing_state = obj.NEW_NOTIFIED_BILLING_STATE
                    else:
                        billing_state = obj.NOTICE_SENT_BILLING_STATE

        if obj.billing_state != billing_state:
            if billing_state == obj.NOTICE_SENT_BILLING_STATE:
                obj.most_recent_notice_sent = timezone.now()
            obj.billing_state = billing_state
            obj.save()

    def _track_changes_for_home_address_geocode(self):
        original = getattr(self, "_loaded_values", dict())
        if (
            self.registration_id
            and self.home_status_id
            and (
                original.get("home_address_geocode_id") != self.home_address_geocode_id
                or original.get("home_address_geocode_response_id")
                != self.home_address_geocode_response_id
            )
        ):
            if self.home_address_geocode_response:
                address = self.home_address_geocode_response.get_normalized_fields()
                street_line1 = address.get("street_line1", "")
                street_line2 = address.get("street_line2", "")
                city = address.get("city", None)
                county = address.get("county", None)
                state = address.get("state", None)
                zipcode = address.get("zipcode", None)
                geocode_response = self.home_address_geocode_response
            else:
                street_line1 = self.home_address_geocode.raw_street_line1
                street_line2 = self.home_address_geocode.raw_street_line2
                city = self.home_address_geocode.raw_city
                county = None
                state = None
                if city:
                    if city.county:
                        county = city.county
                        state = city.county.state
                zipcode = self.home_address_geocode.raw_zipcode
                geocode_response = None

            home = self.home_status.home
            home.lot_number = self.lot_number
            home.street_line1 = street_line1
            home.street_line2 = street_line2
            home.city = city
            home.county = county
            home.state = state
            home.zipcode = zipcode
            home.geocode_response = geocode_response
            home.save()

    def _track_changes_for_registration(self):
        original = getattr(self, "_loaded_values", dict())

        if original.get("registration_id") != self.registration_id and self.home_status_id:
            home = self.home_status.home
            home.subdivision = self.registration.subdivision
            home.save()

    def _track_changes_for_story_count(self):
        original = getattr(self, "_loaded_values", dict())

        if "story_count" in original and self.story_count != original["story_count"]:
            new_certification_fees_cost = self.calculate_certification_fees_cost()
            old_certification_fees = self.calculate_certification_fees_cost(
                story_count=original["story_count"]
            )

            self.update_invoice_item_fees(
                name="Certification Fee Change",
                new_cost=new_certification_fees_cost,
                old_cost=old_certification_fees,
            )

            # update green energy badges cost
            for green_energy_badge in self.green_energy_badges.all():
                new_badge_fee = green_energy_badge.calculate_cost(
                    hirl_project_registration_type=self.registration.project_type,
                    is_accessory_structure=self.is_accessory_structure,
                    is_accessory_dwelling_unit=self.is_accessory_dwelling_unit,
                    builder_organization=self.registration.builder_organization,
                    story_count=self.story_count,
                )
                old_badge_fee = green_energy_badge.calculate_cost(
                    hirl_project_registration_type=self.registration.project_type,
                    is_accessory_structure=self.is_accessory_structure,
                    is_accessory_dwelling_unit=self.is_accessory_dwelling_unit,
                    builder_organization=self.registration.builder_organization,
                    story_count=original.get("story_count", 1),
                )

                self.update_invoice_item_fees(
                    name=f"{green_energy_badge.name} Fee Change",
                    new_cost=new_badge_fee,
                    old_cost=old_badge_fee,
                )

    def _track_changes_for_number_of_units(self):
        original = getattr(self, "_loaded_values", dict())

        if "number_of_units" in original and original["number_of_units"] != self.number_of_units:
            new_per_unit_fee_cost = self.calculate_per_unit_fee_cost()
            old_per_unit_fee_cost = self.calculate_per_unit_fee_cost(
                number_of_units=original.get("number_of_units", 1)
            )

            self.update_invoice_item_fees(
                name="Per Unit Fee Change",
                new_cost=new_per_unit_fee_cost,
                old_cost=old_per_unit_fee_cost,
            )

    def _track_changes_for_commercial_space_type(self):
        original = getattr(self, "_loaded_values", dict())
        if (
            "commercial_space_type" in original
            and self.commercial_space_type != original["commercial_space_type"]
        ):
            if (
                self.registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
                and not self.is_include_commercial_space
                and not self.is_accessory_structure
                and not self.is_accessory_dwelling_unit
            ):
                new_certification_fees_cost = self.calculate_certification_fees_cost()
                old_certification_fees = self.calculate_certification_fees_cost(
                    commercial_space_type=original.get("commercial_space_type")
                )

                self.update_invoice_item_fees(
                    name="Certification Fee Change",
                    new_cost=new_certification_fees_cost,
                    old_cost=old_certification_fees,
                )

    def _track_changes_for_manual_billing_state(self):
        original = getattr(self, "_loaded_values", dict())

        if (
            "manual_billing_state" in original
            and self.manual_billing_state != original["manual_billing_state"]
        ):
            if self.manual_billing_state == HIRLProject.NOT_PURSUING_BILLING_STATE:
                # When a “Billing Status” is manually changed to “Not Pursuing” in
                # the database we have programmed the database to look at the “Payment Rcvd Date”
                # field.  If that field is empty, all the fees are changed to $0.
                # If there is a date in the “Payment Rcvd Date”, then the fees remain as
                # they were before.
                fee_total_paid = (
                    InvoiceItemTransaction.objects.filter(
                        item__group__home_status__customer_hirl_project=self
                    )
                    .values("item__group__home_status__customer_hirl_project")
                    .aggregate(
                        fee_total_paid=Coalesce(Sum("amount"), 0, output_field=DecimalField())
                    )["fee_total_paid"]
                )

                if not fee_total_paid:
                    for invoice_item in InvoiceItem.objects.filter(
                        group__home_status__customer_hirl_project=self
                    ):
                        invoice_item.cost = 0
                        invoice_item.save()
            elif (
                self.manual_billing_state == HIRLProject.VOID_BILLING_STATE
                or self.manual_billing_state == self.COMPLIMENTARY_BILLING_STATE
            ):
                for invoice_item in InvoiceItem.objects.filter(
                    group__home_status__customer_hirl_project=self
                ):
                    invoice_item.cost = 0
                    invoice_item.save()

            HIRLProjectBillingStateChangedManuallyMessage().send(
                users=customer_hirl_app.get_accounting_users(),
                context={
                    "new_state": self.manual_billing_state,
                    "project_id": self.id,
                    "h_number": self.h_number,
                    "project_url": self.get_absolute_url(),
                },
            )

    def _track_changes_for_number_of_lots(self):
        original = getattr(self, "_loaded_values", dict())
        if "number_of_lots" in original and self.number_of_lots != original["number_of_lots"]:
            new_certification_fees_cost = self.calculate_certification_fees_cost()
            old_certification_fees = self.calculate_certification_fees_cost(
                number_of_lots=original["number_of_lots"]
            )

            self.update_invoice_item_fees(
                name="Certification Fee Change",
                new_cost=new_certification_fees_cost,
                old_cost=old_certification_fees,
            )

    def _track_changes_for_are_all_homes_in_ld_seeking_certification(self):
        original = getattr(self, "_loaded_values", dict())
        if (
            "are_all_homes_in_ld_seeking_certification" in original
            and self.are_all_homes_in_ld_seeking_certification
            != original["are_all_homes_in_ld_seeking_certification"]
        ):
            new_certification_fees_cost = self.calculate_certification_fees_cost()
            old_certification_fees = self.calculate_certification_fees_cost(
                are_all_homes_in_ld_seeking_certification=original[
                    "are_all_homes_in_ld_seeking_certification"
                ]
            )

            self.update_invoice_item_fees(
                name="Certification Fee Change",
                new_cost=new_certification_fees_cost,
                old_cost=old_certification_fees,
            )

    def _track_changes_for_is_appeals_project(self):
        original = getattr(self, "_loaded_values", dict())
        if original.get("is_appeals_project") != self.is_appeals_project:
            self.update_invoice_item_fees(
                customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL,
                new_cost=self.calculate_appeals_fee_cost(),
                old_cost=self.calculate_appeals_fee_cost(
                    is_appeals_project=original.get("is_appeals_project")
                ),
                category=InvoiceItemGroup.APPEALS_FEE_CATEGORY,
            )


class HIRLGreenEnergyBadge(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    cost = models.DecimalField(
        verbose_name="Cost",
        help_text="ATTENTION: This is a base value that "
        "affects on ALL badges fees based on Project. "
        "Fees calculation performs in method `calculate_cost()`",
        default=0.00,
        max_digits=9,
        decimal_places=2,
    )
    description = models.TextField(
        blank=True, help_text="Using in Scoring Path Certificate generation"
    )

    objects = GreenEnergyBadgeQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "NGBS Green+ Badge"
        verbose_name_plural = "NGBS Green+ Badges"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"

    def get_name_with_invoice_label(self):
        """
        When we create an Invoice item we use special format `Green+ Badge Fee: + name`
        To search badges by name exactly use this method
        :return: String - formatted name
        """
        return f"Green+ Badge Fee: {self.name}"

    def calculate_cost(
        self,
        hirl_project_registration_type,
        is_accessory_structure,
        is_accessory_dwelling_unit,
        builder_organization,
        story_count,
    ):
        """
        Calculates certification Fees based on a table provided by Customer
        :param builder_organization:
        :param is_accessory_structure:
        :param is_accessory_dwelling_unit:
        :param hirl_project_registration_type: HIRLProjectRegistration project_type
        :param story_count: HIRLProject story_count
        :return: Decimal - cost
        """
        cost = self.cost

        if hirl_project_registration_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            if story_count <= 3:
                cost = self.cost * 2
            elif story_count >= 4:
                cost = self.cost * 6

        # discount
        if hirl_project_registration_type == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE:
            if not is_accessory_structure and not is_accessory_dwelling_unit:
                if self.slug == "wellness":
                    if builder_organization.slug == "builder-neal-communities":
                        cost = 0
        return cost
