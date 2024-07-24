"""company.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging
import os.path

import requests
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from axis.company import strings
from axis.company.managers import (
    CompanyManager,
)
from axis.company.strings import COMPANY_TYPES
from axis.company.utils import (
    can_view_or_edit_eto_account,
    can_edit_eto_ccb_number,
    can_edit_hquito_status,
)
from axis.company.validators import validate_provider_id
from axis.core.utils import slugify_uniquely, randomize_filename, get_frontend_url
from axis.geographic.placedmodels import AddressedPlacedModel
from axis.relationship.managers import AssociationsInspector
from axis.relationship.models import Relationship
from .company_role import CompanyRole

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
customer_wsu = apps.get_app_config("customer_wsu")


def logo_image_upload_to(instance, filename):
    return os.path.join(
        "documents", instance.company_type, instance.slug, "logos", randomize_filename(filename)
    )


class Company(AddressedPlacedModel):
    """
    The basics of a company.

    Nulls are okay on some of the fields, since imported data may not have some fields, but once a
    person updates the object, they will need full details.
    """

    LETTER_INSPECTION_GRADE = 1
    NUMERIC_INSPECTION_GRADE = 2

    INSPECTION_GRADE_CHOICES = (
        (LETTER_INSPECTION_GRADE, "Letter grades"),
        (NUMERIC_INSPECTION_GRADE, "Numeric grades"),
    )

    HQUITO_CHOICES = ((None, "Unknown"), (True, "Accredited"), (False, "Not Accredited"))

    # Non-field hint for subclasses to override
    COMPANY_TYPE = None

    BUILDER_COMPANY_TYPE = "builder"
    ARCHITECT_COMPANY_TYPE = "architect"
    EEP_COMPANY_TYPE = "eep"
    PROVIDER_COMPANY_TYPE = "provider"
    RATER_COMPANY_TYPE = "rater"
    UTILITY_COMPANY_TYPE = "utility"
    HVAC_COMPANY_TYPE = "hvac"
    QA_COMPANY_TYPE = "qa"
    DEVELOPER_COMPANY_TYPE = "developer"
    COMMUNITY_OWNER_COMPANY_TYPE = "communityowner"
    GENERAL_COMPANY_TYPE = "general"

    name = models.CharField(max_length=255, help_text=strings.SUBDIVISION_HELP_TEXT_NAME)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name="%(app_label)s_%(class)s_related"
    )

    office_phone = PhoneNumberField(
        blank=True, null=True, help_text=strings.SUBDIVISION_HELP_TEXT_OFFICE_PHONE
    )
    home_page = models.URLField(
        blank=True, null=True, help_text=strings.SUBDIVISION_HELP_TEXT_HOME_PAGE
    )
    description = models.TextField(blank=True, null=True)

    default_email = models.EmailField(
        blank=True, null=True, help_text=strings.SUBDIVISION_HELP_TEXT_DEFAULT_EMAIL
    )

    shipping_geocode = models.ForeignKey(
        "geocoder.Geocode", related_name="+", blank=True, null=True, on_delete=models.SET_NULL
    )
    shipping_geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Selected by user in case of multiple valid results, "
        "automatically when we have one result and "
        "empty when geocode do not have valid results",
    )

    # This will help narrow your scope on almost everything..
    counties = models.ManyToManyField(
        "geographic.County",
        blank=True,
        related_name="companies",
        help_text=strings.SUBDIVISION_HELP_TEXT_COUNTIES,
    )
    countries = models.ManyToManyField(
        "geographic.Country",
        blank=True,
        related_name="companies",
        help_text=strings.SUBDIVISION_HELP_TEXT_COUNTRIES,
    )
    company_type = models.CharField(max_length=32, choices=COMPANY_TYPES)

    slug = models.SlugField("slug", unique=True)

    # Provider specific fields
    provider_id = models.CharField(
        "Provider ID", max_length=8, validators=[validate_provider_id], blank=True, null=True
    )
    auto_submit_to_registry = models.BooleanField(
        default=False, help_text=strings.HELP_TEXT_AUTO_SUBMIT_TO_REGISTRY
    )
    is_sample_eligible = models.BooleanField(default=False)

    # Rater specific fields
    certification_number = models.CharField(max_length=16, unique=True, blank=True, null=True)

    # HVAC specific fields
    hquito_accredited = models.BooleanField(
        null=True, default=None, choices=HQUITO_CHOICES, help_text=strings.HELP_TEXT_HQUITO_STATUS
    )

    # Utility specific fields
    electricity_provider = models.BooleanField(default=False)
    gas_provider = models.BooleanField(default=False)
    water_provider = models.BooleanField(default=False)

    # Overall
    is_active = models.BooleanField(default=True, help_text=strings.SUBDIVISION_HELP_TEXT_IS_ACTIVE)

    # Visibility Toggle
    is_public = models.BooleanField(
        default=False, help_text=strings.SUBDIVISION_HELP_TEXT_IS_PUBLIC
    )

    # Customer Options
    is_customer = models.BooleanField(default=False, help_text=strings.HELP_TEXT_IS_CUSTOMER)
    is_eep_sponsor = models.BooleanField(default=False)

    # Auto add relationships
    auto_add_direct_relationships = models.BooleanField(
        default=True, help_text=strings.SUBDIVISION_HELP_TEXT_AUTO_ADD_DIRECT_RELATIONSHIPS
    )

    # User management
    inspection_grade_type = models.IntegerField(
        choices=INSPECTION_GRADE_CHOICES, default=LETTER_INSPECTION_GRADE
    )

    # Customer HIRL
    worker_compensation_insurance = models.BooleanField(
        default=False,
        help_text="Worker Compensation insurance is not required in "
        "the state(s) that this company operates in",
    )

    sponsors = models.ManyToManyField(
        "self",
        through="SponsorPreferences",
        symmetrical=False,
        blank=True,
        related_name="sponsored_companies",
    )

    customer_documents = GenericRelation("filehandling.CustomerDocument")
    recently_viewed = GenericRelation("core.RecentlyViewed")

    display_raw_addresses = models.BooleanField(
        default=False, help_text=strings.SUBDIVISION_HELP_TEXT_DISPLAY_RAW_ADDRESSES
    )

    logo = models.ImageField("Logo", upload_to=logo_image_upload_to, null=True, blank=True)

    objects = CompanyManager()
    history = HistoricalRecords()
    associations = AssociationsInspector()

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ("name",)
        unique_together = (("name", "city", "state", "company_type"),)

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        return self.name

    def natural_key(self):
        """A unique name used for serialization."""
        return (self.slug,)

    def save(self, *args, **kwargs):
        """
        Copies ``state`` from the ``city.county`` if missing, and set the ``slug`` and ``group``.
        """

        co_type = self.company_type.capitalize()
        try:
            module_name = apps.get_model(app_label="company", model_name="%sOrganization" % co_type)
            module_name = module_name._meta.model_name
        except LookupError:
            module_name = apps.get_model(app_label="company", model_name="Company")
            module_name = module_name._meta.model_name

        # First save
        if not self.slug:
            name = "{} {}".format(self.company_type, self.name)
            self.slug = slugify_uniquely(name, self.__class__)
        if not self.group:
            group_name = "%s.%s.%s" % (self._meta.app_label, module_name, self.slug)
            self.group, create = Group.objects.get_or_create(name=group_name)

        # populate redundant US state field
        if self.city:
            self.state = self.city.state

        super(Company, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Removes relationships tied to this company before deleting the instance."""
        from .models import COMPANY_MODELS

        content_types = ContentType.objects.get_for_models(*COMPANY_MODELS).values()
        ref_companies = Relationship.objects.filter(
            content_type__in=content_types, object_id=self.id
        )
        for indirect_relationship in ref_companies:
            indirect_relationship.delete()
        for direct_relationship in self.relationships.all():
            direct_relationship.delete()
        return super(Company, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return get_frontend_url("company", self.company_type, "detail", self.id)

    def get_users(self):
        """
        Returns Common users from this company based
        on CompanyAccess without any Roles
        """
        user_model = get_user_model()
        if self.pk:
            users = user_model.objects.filter(
                id__in=self.companyaccess_set.filter(roles__isnull=True).values("user")
            )
            return users.order_by("-is_active", "username")
        return user_model.objects.none()

    def get_admins(self):
        """
        Returns the company_admin users from this company based
        on CompanyAccess IS_COMPANY_ADMIN role
        """
        user_model = get_user_model()
        if self.pk:
            users = user_model.objects.filter(
                id__in=self.companyaccess_set.filter(
                    roles__slug=CompanyRole.IS_COMPANY_ADMIN
                ).values("user")
            )
            return users.order_by("-is_active", "username")
        return user_model.objects.none()

    def get_admin_group(self):
        """Returns the admin group for this company."""
        if self.pk:
            try:
                grp = self.group.name
            except AttributeError:
                return None
            if len(grp) > 72:
                grp = grp[:72]
            admin_group_name = "{}_admins".format(grp)
            group, _ = Group.objects.get_or_create(name=admin_group_name)
            return group

    @property
    def is_paying_customer(self):
        return self.pk and self.is_active and self.is_customer

    @property
    def is_sponsored(self):
        return self.pk and self.is_active and self.sponsors.count()

    @property
    def is_sponsor(self):
        return self.pk and self.is_active and self.sponsored_companies.count()

    def is_sponsored_by(self, company_slugs, only_sponsor=False):
        """
        Check whether company sponsored by list of provided company slugs.
        :param company_slugs: list of company slugs
        :param only_sponsor: If True - then check that there must be only one sponsor
        :return: Boolean
        """
        if self.pk:
            if only_sponsor:
                sponsors_count = self.sponsors.count()
                if not sponsors_count:
                    return False
                if sponsors_count > 1:
                    return False
            return self.sponsors.filter(slug__in=company_slugs).exists()
        return False

    def is_sponsored_by_customer_hirl(self, only_sponsor=False):
        """
        Check whether company sponsored by NGBS company
        :param only_sponsor: If True - then check that there must be only NGBS sponsor
        :return: Boolean
        """
        return self.is_sponsored_by(
            company_slugs=[
                customer_hirl_app.CUSTOMER_SLUG,
            ],
            only_sponsor=only_sponsor,
        )

    def is_sponsored_by_customer_wsu(self, only_sponsor=False):
        """
        Check whether company sponsored by WSU company
        :param only_sponsor: If True - then check that there must be only WSU sponsor
        :return: Boolean
        """
        return self.is_sponsored_by(
            company_slugs=[
                customer_wsu.CUSTOMER_SLUG,
            ],
            only_sponsor=only_sponsor,
        )

    def update_permissions(self, app=None, confirm=False, show_retained=False, report_only=False):
        from axis.core.management.commands.set_permissions import AxisPermissionsGenerator

        perm_gen = AxisPermissionsGenerator()
        return perm_gen.update_groups(
            companies=[self],
            app=app,
            confirm=confirm,
            show_retained=show_retained,
            report_only=report_only,
        )

    def get_address_display(self, include_name=True):
        """Return the fully-formed address with lot number."""
        return "{}{}{}{}".format(
            "{} - ".format(self.name) if include_name else "",
            self.street_line1,
            ", {}".format(self.street_line2) if self.street_line2 else "",
            ", {} {}, {}".format(self.city.name, self.state, self.zipcode),
        )

    @classmethod
    def can_be_added(self, user):
        return user.is_company_admin

    def can_be_edited(self, user):
        """
        Returns True for admins of this company.  Alternately, if the user is generally a company
        admin for a different company, and the company isn't set as ``is_customer``, True will also
        be the return value.
        """

        # Little short-circuit, since logic after this is not about the object, but the
        # relationships governing access.
        if user.is_superuser:
            return True

        if user.is_company_admin:
            if self.id == user.company.id:
                return True

            if not self.get_admins().count():
                return user.has_perm("company.change_%sorganization" % self.company_type)
        return False

    def can_be_deleted(self, user):
        """
        Returns True if exactly one relationship exists on the company, and that relationship's
        primary company is the user's company.

        Returns False if ``is_customer`` is set.
        """
        from .models import COMPANY_MODELS

        if not user.has_perm("company.delete_%sorganization" % self.company_type):
            return False
        if user.is_superuser:
            return True
        content_types = ContentType.objects.get_for_models(*COMPANY_MODELS).values()
        ref_companies = Relationship.objects.filter(
            content_type__in=content_types, object_id=self.id
        )
        if ref_companies.count() > 1:
            return False

        if (
            ref_companies.count()
            and ref_companies[0].company == user.company
            and not self.is_customer
        ):
            return True
        return False

    @classmethod
    def get_company_type_pretty_name(cls):
        """Returns the corresponding pretty name for a ``cls.COMPANY_TYPE`` specifier."""
        return "Company"

    def add_sponsor(self, company, **kwargs):
        """
        Forwards ``kwargs`` to a creation of a new SponsorPreferences instance where ``company``
        is the sponsor for ``self``.

        This method helps to make the creation processes easier, since we now use an intermediate
        ``through`` model in the relationship.
        """
        self.sponsor_preferences.create(sponsor=company, **kwargs)

    def clean(self):
        """Assigns the implied ``company_type``."""
        if self.COMPANY_TYPE:
            self.company_type = self.COMPANY_TYPE
        super(Company, self).clean()

    def show_eto_account(self, user):
        return can_view_or_edit_eto_account(user, self.company_type)

    def show_ccb_number(self, user):
        return can_edit_eto_ccb_number(user, self.company_type)

    def get_geocoding_type(self):
        # Return generic type, instead of the actual full class name.
        return "company"

    def get_id(self):
        """Returns a nice prepadded ID"""
        return "{0:06}".format(self.id) if self.id else None

    def show_hquito_accredited(self, user):
        return can_edit_hquito_status(user, self, self.company_type)

    def is_floorplan_approval_entity(self):
        """
        Returns a boolean for if the company leverages programs where the floorplan approval setting
        is enabled.
        """
        return self.eepprogram_set.filter(require_floorplan_approval=True).exists()

    def has_mutual_relationship(self, company):
        """
        Check if mutual relationship exists with company
        :param company: Company object
        :return: Boolean
        """
        model = type(self)
        return model.objects.has_mutual_relationship(company=self, other_company=company)

    def guess_manual_floorplan_approval_requirement(self, obj):
        """
        Determines if ``obj`` (a Relationship-enabled object) carries a relationship for a company
        who owns an EEPProgram with the ``require_floorplan_approval`` flag set to True.

        This SHOULD be used when a floorplan is being created without the benefit of any context,
        namely the EEPProgram of some future homestatus it hasn't yet been assigned to.

        This should NOT be used if you have access to a specific EEPProgram.
        In that situation, use ``EEPProgram.requires_manual_floorplan_approval(company)`` instead,
        where ``company`` in this instance is this company object (self).
        """
        from axis.eep_program.models import EEPProgram

        assert hasattr(obj, "relationships"), "'obj' must have a Relationship manager."

        obj_rels = obj.relationships.all()

        likely_eep_rels = obj_rels.filter(
            Q(company__company_type="eep") | Q(company__is_eep_sponsor=True),
        )
        sponsor_ids = set(likely_eep_rels.values_list("company__id", flat=True))
        manual_approval_programs = EEPProgram.objects.filter(
            require_floorplan_approval=True, owner__id__in=sponsor_ids
        )
        return manual_approval_programs.exists()

    def create_contact_card(self):
        from axis.core.models import ContactCardPhone, ContactCard, ContactCardEmail

        contact_card = ContactCard.objects.create(
            protected=False, company_id=self.id  # when using self, this cause issue in fixtures
        )

        phone_numbers_map = [{"description": "Office Phone", "attr": "office_phone"}]

        for phone_number_map in phone_numbers_map:
            phone = getattr(self, phone_number_map["attr"], "")
            if phone:
                ContactCardPhone.objects.update_or_create(
                    contact=contact_card,
                    description=phone_number_map["description"],
                    defaults={"phone": phone},
                )
            else:
                ContactCardPhone.objects.filter(
                    contact=contact_card, description=phone_number_map["description"]
                ).delete()

        emails_map = [{"description": "Main Email", "attr": "default_email"}]

        for email_map in emails_map:
            email = getattr(self, email_map["attr"], "")
            if email:
                ContactCardEmail.objects.update_or_create(
                    contact=contact_card,
                    description=email_map["description"],
                    defaults={"email": email},
                )
            else:
                ContactCardEmail.objects.filter(
                    contact=contact_card, description=email_map["description"]
                ).delete()
        return contact_card

    # customer_hirl methods
    def get_customer_hirl_legacy_id(self):
        """
        Returns Ngbs legacy company ID based on company type
        :return: Legacy ID(str) or None
        """
        if getattr(self, "hirlcompanyclient", None):
            return self.hirlcompanyclient.id
        return None

    def is_water_sense_partner(self) -> bool:
        """
        Check whether NGBS builder company is water sense partner.
        Check performs via external api call
        :return: Boolean
        """
        if self.company_type == "builder":
            response = requests.get(
                url="https://lookforwatersense.epa.gov/api/partners/",
                params={
                    "partnerType": "Builder",
                    "keyword": self.name,
                    "state": self.state,
                },
            )

            if response.status_code != 200:
                return False

            data = response.json()
            try:
                results_count = data["count"]
            except KeyError:
                return False

            if results_count:
                return True
        return False

    def clean_provider_id(self):
        if self.provider_id != "":
            if Company.objects.filter(provider_id=self.provider_id):
                log.warning("%s already exists in database" % self.provider_id)
        if self.provider_id.strip() == "":
            self.provider_id = None

    def clean_certification_number(self):
        if self.certification_number != "":
            if Company.objects.filter(certification_number=self.certification_number):
                raise ValidationError("%s already exists in database" % self.certification_number)
        if self.certification_number.strip() == "":
            self.certification_number = None

    def get_utility_type(self):
        output = []
        if self.electricity_provider:
            output.append("Electric")
        if self.gas_provider:
            output.append("Gas")
        if self.water_provider:
            output.append("Water")
        return ", ".join(output)
