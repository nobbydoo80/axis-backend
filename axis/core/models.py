"""models.py: core models"""

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

import logging
import os
from typing import Optional, Type

import six
from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.base import ModelBase
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from timezone_field import TimeZoneField
from timezonefinder import TimezoneFinder

from axis.relationship.managers import AssociationsInspector
from .accessors import RemoteIdentifiers
from .managers import UserManager, RecentlyViewedManager, AxisFlatPageQuerySet
from .utils import randomize_filename

# Backwards support for a while.
# Our migrations import "SlugifyUniquely", which was a mistake, but not yet easily fixed.
from .utils import slugify_uniquely
from .validators import validate_rater_id

SlugifyUniquely = slugify_uniquely
log = logging.getLogger(__name__)


class UserType(ModelBase):
    """Simple metaclass that adds simple-history support to User AFTER it has been built."""

    # Simple-history generates a separate table that attributes field changes to the user that made
    # them.  This means the history table needs a foreign key to User.
    # Simple-history tries to get itself set up DURING the setup of the User model because of the
    # history manager getting set as a class attribute.  Doing it here ensures that the User model
    # is completely finished before a "HistoricalUser" table gets configured.

    # Interestingly, even pointing the simple-history "CurrentUserField" to settings.AUTH_USER_MODEL
    # doesn't work.  Django probably doesn't know how to do a lazy reference to "core.User" once
    # it's gotten that far along in the code where it already decided to start setting up the model.

    def __new__(cls, name, bases, attrs):
        User = super(UserType, cls).__new__(cls, name, bases, attrs)

        history = HistoricalRecords(excluded_fields=["company"])
        history.contribute_to_class(User, "history")

        # We end up missing the "class_prepared" signal that the User class was prepared, so
        # contribute_to_class doesn't actually finish doing everything we expect.
        history.finalize(sender=User)

        return User


def signature_image_upload_to(instance, filename):
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        "user_signatures",
        randomize_filename(filename),
    )


class User(six.with_metaclass(UserType, AbstractUser)):
    """Axis-customized User model."""

    objects = UserManager()  # slightly customized version of the default auth one
    associations = AssociationsInspector()
    identifiers = RemoteIdentifiers(choices=(("trc", "TRC UUID"),))

    company = models.ForeignKey(
        "company.Company",
        related_name="users",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    companies = models.ManyToManyField("company.Company", through="company.CompanyAccess")
    title = models.CharField(max_length=32, null=True)
    department = models.CharField(max_length=16, blank=True)
    work_phone = PhoneNumberField(null=True)
    cell_phone = PhoneNumberField(blank=True, null=True)
    alt_phone = PhoneNumberField(blank=True, null=True)
    fax_number = PhoneNumberField(blank=True, null=True)

    mailing_geocode = models.ForeignKey(
        "geocoder.Geocode",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    shipping_geocode = models.ForeignKey(
        "geocoder.Geocode",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    rater_roles = models.ManyToManyField("RaterRole", blank=True)
    rater_id = models.IntegerField(
        "RESNET RTIN", validators=[validate_rater_id], null=True, blank=True
    )
    signature_image = models.ImageField(
        "Signature",
        upload_to=signature_image_upload_to,
        max_length=512,
        blank=True,
        null=True,
    )

    resnet_username = models.CharField("RESNET Username", max_length=64, null=True, blank=True)
    resnet_password = models.CharField("RESNET Password", max_length=64, null=True, blank=True)

    is_company_admin = models.BooleanField(default=False)
    is_approved = models.BooleanField(
        default=False,
        help_text="Designates whether the user has "
        "been approved to log in by a "
        "company administrator.",
    )
    is_public = models.BooleanField(default=False)
    show_beta = models.BooleanField(
        default=False, help_text="Switch between classic and new pages view"
    )

    site = models.ForeignKey(
        Site,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Site on what user registered. "
        "This domain will use for all links in notifications "
        "that do not have request object. "
        "Empty value means default SITE_ID domain",
    )

    last_update = models.DateTimeField(auto_now=True, blank=True, null=True)

    # Valid choices are from pytz.all_timezones
    timezone_preference = TimeZoneField(default="US/Pacific")

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ("last_name", "first_name", "username")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(User, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def get_absolute_url(self):
        return reverse("profile:detail", kwargs={"pk": self.pk})

    def natural_key(self):
        """
        https://docs.djangoproject.com/en/dev/topics/serialization/#natural-keys
        Example of serialization
        "user": [
            "provideradmin"
        ],
        :return: tuple with username for correct serialization for content_type objects
        """
        return (self.username,)

    def save(self, *args, **kwargs):
        self.clean()

        tz_name = None
        tf = TimezoneFinder()

        is_new = self.pk is None

        original = dict()
        if hasattr(self, "_loaded_values"):
            original = self._loaded_values

        if self.mailing_geocode_id and (
            original.get("mailing_geocode_id") != self.mailing_geocode_id or not self.pk
        ):
            if self.mailing_geocode.raw_city:
                try:
                    tz_name = tf.timezone_at(
                        lat=self.mailing_geocode.raw_city.latitude,
                        lng=self.mailing_geocode.raw_city.longitude,
                    )
                except ValueError:
                    pass
        elif self.company_id and (original.get("company_id") != self.company_id or not self.pk):
            if self.company.city:
                try:
                    tz_name = tf.timezone_at(
                        lat=self.company.city.latitude, lng=self.company.city.longitude
                    )
                except ValueError:
                    pass

        if tz_name:
            self.timezone_preference = tz_name

        if not self._state.adding and any(
            [
                self.first_name != original.get("first_name"),
                self.last_name != original.get("last_name"),
                self.work_phone != original.get("work_phone"),
                self.cell_phone != original.get("cell_phone"),
                self.alt_phone != original.get("alt_phone"),
            ]
        ):
            self.update_or_create_protected_contact_card()

        instance = super(User, self).save(*args, **kwargs)

        if self.is_company_admin != original.get("is_company_admin"):
            self._track_changes_for_is_company_admin()

        # NGBS keep their legacy verifier IDS, so when
        # we set Rater company for user that is sponsored by NGBS we must create legacy record
        if self.company_id and (original.get("company_id") != self.company_id or is_new):
            from axis.company.models import Company

            if (
                self.company.company_type == Company.RATER_COMPANY_TYPE
                and self.company.is_sponsored_by_customer_hirl(only_sponsor=False)
                and not getattr(self, "hirlrateruser", None)
            ):
                from axis.customer_hirl.models import HIRLRaterUser

                _ = HIRLRaterUser.objects.create(user=self)

        if is_new:
            self.update_or_create_protected_contact_card()
        return instance

    def can_be_edited(self, user):
        """Allows edits for self, admins, company admins users."""
        if user == self or user.is_superuser:
            return True

        if user.company == self.company:
            if user.is_company_admin:
                return True

        return False

    def can_be_deleted(self, user):
        """We mark users inactive instead. Too dangerous to delete with FK"""
        return False

    @cached_property
    def default_company(self) -> Optional[Type["Company"]]:
        return self.companies.first()

    def is_sponsored_by_company(self, company, only_sponsor=False):
        """
        Check whether or not user Company is sponsorED by provided Company
        :param company: String(Slug) or Company Object
        :param only_sponsor: Boolean - if set then check count of sponsors for company.
        If it gather than 1 return False
        :return: Boolean
        """
        if only_sponsor and self.company.sponsors.count() != 1:
            return False
        return self.is_sponsored_by_companies(
            [
                company,
            ]
        )

    def is_sponsored_by_companies(self, companies):
        """
        Check whether or not user Company is sponsorED by provided Companies
        :param companies: List of Strings(Slugs) or List of Company Objects
        :return: Boolean
        """
        from axis.company.models import Company

        if not self.company:
            return False

        if all(isinstance(company, Company) for company in companies):
            companies = [company.slug for company in companies]

        companies = set(companies)
        user_company_sponsors = self.company.sponsors.values_list("slug", flat=True)
        user_company_sponsors = set(user_company_sponsors)

        return bool(user_company_sponsors.intersection(companies))

    def is_company_type_member(self, company_types):
        """
        Check whether or not user company belongs to provided company types
        :param company_types: List of Strings or String
        :return: Boolean
        """
        from axis.company.models import Company

        existing_company_types = set(
            [
                Company.RATER_COMPANY_TYPE,
                Company.PROVIDER_COMPANY_TYPE,
                Company.EEP_COMPANY_TYPE,
                Company.BUILDER_COMPANY_TYPE,
                Company.GENERAL_COMPANY_TYPE,
                Company.ARCHITECT_COMPANY_TYPE,
                Company.COMMUNITY_OWNER_COMPANY_TYPE,
                Company.DEVELOPER_COMPANY_TYPE,
                Company.HVAC_COMPANY_TYPE,
                Company.UTILITY_COMPANY_TYPE,
                Company.QA_COMPANY_TYPE,
            ]
        )

        if not isinstance(company_types, list):
            company_types = [
                company_types,
            ]

        company_types = set(company_types)

        if not_existing_types := company_types - existing_company_types:
            raise ValueError(
                f"Company types: " f"{not_existing_types} is not in existing AXIS Company Types"
            )

        if not self.company:
            return False

        return self.company.company_type in company_types

    def is_customer_hirl_company_member(self):
        """
        Check whether or not user a member of HOME INNOVATION RESEARCH LAB company
        :return: Boolean
        """
        customer_hirl_app = apps.get_app_config("customer_hirl")

        return self.company and self.company.slug == customer_hirl_app.CUSTOMER_SLUG

    def is_customer_hirl_company_admin_member(self):
        """
        Check whether or not user a company admin member of HOME INNOVATION RESEARCH LAB company
        :return: Boolean
        """
        customer_hirl_app = apps.get_app_config("customer_hirl")

        return (
            self.is_company_admin
            and self.company
            and self.company.slug == customer_hirl_app.CUSTOMER_SLUG
        )

    def update_or_create_protected_contact_card(self):
        """
        Contact Cards are using by Customer HIRL in projects registrations
        to define responsible person. Protected contact card is
        in sync with Core User contact fields
        :return:
        """
        contact_card, created = ContactCard.objects.update_or_create(
            user=self,
            protected=True,
            defaults={"first_name": self.first_name, "last_name": self.last_name},
        )

        phone_numbers_map = [
            {"description": "Work Phone", "attr": "work_phone"},
            {"description": "Cell Phone", "attr": "cell_phone"},
            {"description": "Alternate Phone", "attr": "alt_phone"},
        ]

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

        emails_map = [{"description": "Main Email", "attr": "email"}]

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
        return contact_card, created

    def _track_changes_for_is_company_admin(self):
        from axis.company.models import CompanyAccess, CompanyRole

        if getattr(self, "company", None):
            company_access, created = CompanyAccess.objects.update_or_create(
                company=self.company,
                user=self,
            )
            is_company_admin_role, created = CompanyRole.objects.get_or_create(
                slug="is_company_admin", defaults={"name": "Is Company Admin"}
            )
            if self.is_company_admin:
                company_access.roles.add(is_company_admin_role)
            else:
                company_access.roles.remove(is_company_admin_role)


class RaterRole(models.Model):
    title = models.CharField(max_length=50, help_text="Rater role name, eg. Energy Modeler")
    slug = models.SlugField()
    is_hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return "{}".format(
            self.title,
        )


class ContactCard(models.Model):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="contact_cards",
        on_delete=models.CASCADE,
    )
    company = models.ForeignKey(
        "company.Company",
        null=True,
        blank=True,
        related_name="contact_cards",
        on_delete=models.CASCADE,
    )
    protected = models.BooleanField(
        default=False,
        help_text="This ContactCard created and will be updated "
        "automatically based on User or Company data",
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = "Contact Card"
        verbose_name_plural = "Contact Cards"
        ordering = ("first_name", "last_name")

    def __str__(self):
        return f"Contact Card: {self.get_name()} " f"Description: {self.description} "

    def get_name(self):
        if self.user_id:
            return self.user.get_full_name()
        elif self.company_id:
            if not self.first_name and not self.last_name:
                return self.company.name
            return f"{self.first_name} {self.last_name}"
        return "Unknown"


class ContactCardPhone(models.Model):
    contact = models.ForeignKey(ContactCard, related_name="phones", on_delete=models.CASCADE)
    phone = PhoneNumberField(null=True)
    description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Phone {self.phone} for Contact Card ID: {self.contact_id}"


class ContactCardEmail(models.Model):
    contact = models.ForeignKey(ContactCard, related_name="emails", on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True)
    description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Email Address {self.email} for Contact Card ID: {self.contact_id}"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    updated_at = models.DateTimeField(auto_now=True)

    objects = RecentlyViewedManager()

    def __str__(self):
        return "{} recently viewed by {}".format(self.content_object, self.user)

    class Meta:
        verbose_name_plural = "Recently Viewed"
        ordering = ("-updated_at",)


class AxisFlatPage(FlatPage):
    order = models.PositiveIntegerField(default=0, help_text="Additional priority for static pages")
    created_at = models.DateTimeField(
        default=timezone.now,
        blank=True,
        help_text="This field is using for ordering FlatPages. " "For example: News list",
    )

    objects = AxisFlatPageQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Static page"
