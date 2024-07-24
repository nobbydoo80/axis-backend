"""models.py: Django home"""

import datetime
import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.core.utils import slugify_uniquely
from axis.geographic.placedmodels import GeneralPlacedModel
from axis.geographic.utils.legacy import get_address_designator
from axis.relationship.models import Relationship, RelationshipUtilsMixin
from . import messages
from . import strings
from .managers import (
    SubdivisionManager,
    EEPProgramSubdivisionStatusManager,
    FloorplanApprovalQuerySet,
)

__author__ = "Steven Klass"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Subdivision(RelationshipUtilsMixin, GeneralPlacedModel):
    """A plot of land that homes will be built on that is tied to a single builder"""

    name = models.CharField(
        max_length=64,
        verbose_name=strings.SUBDIVISION_VERBOSE_NAME_NAME,
        help_text=strings.SUBDIVISION_HELP_TEXT_NAME,
    )
    builder_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=strings.SUBDIVISION_VERBOSE_NAME_BUILDER_NAME,
        help_text=strings.SUBDIVISION_HELP_TEXT_BUILDER_NAME,
    )
    builder_org = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="builder_org_subdivisions",
        verbose_name=strings.SUBDIVISION_VERBOSE_NAME_BUILDER_ORG,
        help_text=strings.SUBDIVISION_HELP_TEXT_BUILDER_ORG,
    )
    community = models.ForeignKey(
        "community.Community",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=strings.SUBDIVISION_VERBOSE_NAME_COMMUNITY,
        help_text=strings.SUBDIVISION_HELP_TEXT_COMMUNITY,
    )
    city = models.ForeignKey(
        "geographic.City",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=strings.SUBDIVISION_VERBOSE_NAME_CITY,
        help_text=strings.SUBDIVISION_HELP_TEXT_CITY,
    )

    eep_programs = models.ManyToManyField(
        "eep_program.EEPProgram",
        through="EEPProgramSubdivisionStatus",
    )
    floorplans = models.ManyToManyField("floorplan.Floorplan", through="FloorplanApproval")

    relationships = GenericRelation("relationship.Relationship")

    # Docs
    customer_documents = GenericRelation("filehandling.CustomerDocument")

    use_sampling = models.BooleanField(default=True)
    use_metro_sampling = models.BooleanField(default=True)

    # Misc
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(editable=False, unique=True, max_length=64)

    annotations = GenericRelation("annotation.Annotation")

    objects = SubdivisionManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Subdivision"
        unique_together = ("name", "city", "builder_org", "community")
        ordering = ("name", "community")

    def save(self, **kwargs):
        """
        Saves the current instance..

        :param using: Backend
        :param force_update: Must be SQL update
        :param force_insert: Must be SQL Insert

        Note that right now geographic data on Subdivision is kept in sync with
        its related Place object. In order to make that work, we had to add a
        kwarg to the method signature.

        """
        if self.city is None and self.community:
            self.city = self.community.city

        assert self.city is not None, "You need to have a city"

        if self.county is None and self.city.county:  # pylint:
            # disable=access-member-before-definition
            self.county = self.city.county
        if self.county:
            if not hasattr(self, "climate_zone") or self.climate_zone is None:
                self.climate_zone = self.county.climate_zone
            if (not hasattr(self, "metro") or self.metro is None) and self.county.metro:
                self.metro = self.county.metro
            if self.state is None:
                self.state = self.county.state
        if not self.slug:
            name = "%s %s %s" % (self.name, self.city, self.builder_org)
            self.slug = slugify_uniquely(name[:60], self.__class__)

        if not self.cross_roads:
            self.address_override = True

        return super(Subdivision, self).save(**kwargs)

    def __str__(self):
        """A string representation of the object.

        :return: str
        """
        try:
            name = "{} at {}".format(self.name, self.community.name)
        except (AttributeError, ObjectDoesNotExist):
            name = self.name
        if self.builder_name:
            name += " ({})".format(self.builder_name)
        return name

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("subdivision:view", kwargs={"pk": self.id})

    @classmethod
    def can_be_added(cls, user):
        """Returns whether the user can add any subdivision

        :param user: django.contrib.auth.models.User
        :return: bool
        """
        return user.has_perm("subdivision.add_subdivision")

    def can_be_edited(self, user):
        """Returns whether the user can edit this subdivision

        :param user: django.contrib.auth.models.User
        :return: bool
        """
        if user.is_superuser:
            return True

        if self.relationships.filter_by_company(user.company, show_attached=False).exists():
            return True
        return user.has_perm("subdivision.change_subdivision")

    def can_be_deleted(self, user):
        """Returns whether the user can delete this subdivision

        :param user: django.contrib.auth.models.User
        :return: bool
        """
        if not user.has_perm("subdivision.delete_subdivision"):
            return False

        try:
            relationships = self.relationships.filter(is_owned=True)
            relationships = relationships.exclude(company__auto_add_direct_relationships=True)
            relationship = relationships.get()
        except (Relationship.MultipleObjectsReturned, Relationship.DoesNotExist):
            return False
        else:
            if user.company.id == relationship.company_id and self.home_set.count() == 0:
                return True
        return False

    def get_address_designator(self):
        """Returns a visual indiaction on whether the object has been geocoded.

        :return: str
        """
        return get_address_designator(self)

    def get_id(self):
        """Returns a padded ID

        :return: str
        """
        return "{:06}".format(self.id)

    def get_sample_eligibility(self, raterorg):  # pylint: disable=inconsistent-return-statements
        """Determines the sampling eligibility of a company with respect to a subdivision.

        :param raterorg: axis.company.models.Company
        :return: str subdivision|metro|None
        """
        try:
            if raterorg.__class__.__name__ == "Company":
                raterorg = Company.objects.get(pk=raterorg.pk)
            if raterorg.is_sample_eligible:
                if self.use_sampling:
                    if self.use_metro_sampling:
                        log.debug("%s can sample %s at metro level" % (raterorg, self))
                        return "metro"
                    log.debug("%s can sample %s at subdivision level" % (raterorg, self))
                    return "subdivision"
            log.debug("%s is not eligible for sampling" % raterorg)
        except (Company.DoesNotExist, AttributeError):
            return None

    def get_fuel_types(self, user):
        """Get the fuel types for the subdivision"""
        from axis.floorplan.models import Floorplan

        floorplans = (
            Floorplan.objects.filter_by_user_and_subdivision(user=user, subdivision=self)
            .filter(remrate_target__isnull=False)
            .select_related("remrate_target")
            .prefetch_related("remrate_target__installedequipment_set")
        )

        fuel_types = set(
            x.equipment.get_fuel_type_display()
            for f in floorplans
            for x in f.remrate_target.get_installed_equipment()
        )
        fuel_types = sorted(fuel_types)
        return ", ".join(fuel_types)

    def set_builder(self, builder_org, user):
        """Replace a builder on a subdivision.

        :param builder_org: axis.company.models.BuilderOrganization
        :param user: django.contrib.auth.models.User
        """
        self.builder_org = builder_org
        self.save()
        if builder_org:
            # Delete any old relationships so we don't get shadowed copies left behind
            self.relationships.filter(company__company_type="builder").exclude(
                company=builder_org
            ).delete()

            Relationship.objects.validate_or_create_relations_to_entity(
                entity=self, direct_relation=user.company, implied_relations=[builder_org]
            )

        self.post_relationship_modification_data(
            {"builder": builder_org},
            [builder_org.id],
            [builder_org],
            has_new_relationships=False,
            user=user,
        )

    def pre_relationship_modification_data(
        self, relationship_data, ids, companies, user, request=None
    ):
        """Get the relationships prior to modification"""
        self._new_providers = None
        existing_providers = self.relationships.filter(company__company_type="provider").exists()
        new_providers = relationship_data.get("provider")
        if new_providers and not existing_providers:
            self._new_providers = list(new_providers)

    def post_relationship_modification_data(
        self, relationship_data, ids, companies, has_new_relationships, user, request=None
    ):
        """Extend the relationships after modification"""
        # Extend the company relationships to the underlying Community
        if self.community:
            Relationship.objects.validate_or_create_relations_to_entity(
                entity=self.community, direct_relation=user.company, implied_relations=companies
            )

        # Notify provider of new subdivision (APS 2015-03-03)
        if getattr(self, "_new_providers", None):
            url = self.get_absolute_url()
            subdivision_repr = "{}".format(self)
            for company in self._new_providers:
                context = {
                    "subdivision": subdivision_repr,
                    "url": url,
                }
                messages.SubdivisionAvailableForREMUploads(url=url).send(
                    company=company,
                    context=context,
                )
        self._new_providers = None

    def is_aps_thermostat_incentive_applicable(self, user):
        """Should the APS thermostat incentive status be shown"""
        if self.city and self.city.county and self.city.county.state == "AZ":
            sponsored = "aps" in user.company.sponsors.values_list("slug", flat=True)
            return user.is_superuser or user.company.slug == "aps" or sponsored
        return False

    def get_aps_thermostat_option(self, pretty=False):
        """Is this home sudivision eligible"""
        if not hasattr(self, "aps_thermostat_option"):
            return "N/A" if pretty else False
        if pretty:
            return self.aps_thermostat_option.get_eligibility_display()
        return self.aps_thermostat_option.eligibility


class EEPProgramSubdivisionStatus(models.Model):
    """Each company manages their own Programs.  This allows for that."""

    subdivision = models.ForeignKey("Subdivision", on_delete=models.CASCADE)
    eep_program = models.ForeignKey("eep_program.EEPProgram", on_delete=models.CASCADE)
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    date_added = models.DateField(default=datetime.date.today, editable=False)

    objects = EEPProgramSubdivisionStatusManager()

    def __str__(self):
        return "{}".format(self.eep_program)


THERMOSTAT_CHOICES = ((0, "0"), (1, "1"), (2, "2"), (3, "3"))


class FloorplanApproval(models.Model):
    """APS Required model for Floorplan Approval"""

    objects = FloorplanApprovalQuerySet.as_manager()

    subdivision = models.ForeignKey("Subdivision", on_delete=models.CASCADE)
    floorplan = models.ForeignKey("floorplan.Floorplan", on_delete=models.CASCADE)

    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    thermostat_qty = models.IntegerField(choices=THERMOSTAT_CHOICES, blank=False, default=0)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ("subdivision", "floorplan")
