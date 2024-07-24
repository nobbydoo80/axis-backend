"""models.py: Django community"""

import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.core.utils import slugify_uniquely
from axis.geographic.placedmodels import GeneralPlacedModel
from axis.relationship.models import Relationship, RelationshipUtilsMixin
from . import strings
from .managers import CommunityManager

__author__ = "Steven Klass"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Community(RelationshipUtilsMixin, GeneralPlacedModel):
    """Community which collections of builders build in."""

    # PlacedModel options for tweaking FKs that it will set up for this model.
    CITY_IS_NULLABLE = False
    COUNTY_IS_NULLABLE = True

    name = models.CharField(max_length=100, help_text=strings.COMMUNITY_HELP_TEXT_NAME)
    website = models.URLField(blank=True, null=True, help_text=strings.COMMUNITY_HELP_TEXT_WEBSITE)

    # Misc
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True)

    relationships = GenericRelation("relationship.Relationship")

    # Managers
    objects = CommunityManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        unique_together = (("name", "city"),)
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        De-normalizes ``metro`` and ``state`` fields from the associated ``county``, and generates
        a "{name} {city.name} {state}" slug for the community.

        """
        if not self.slug:
            # This will happen again later in PlacedModel.save(), but it's important to make sure
            # we generate the slug properly.
            self.denormalize_related_references()
            name = " ".join([x for x in (self.name, self.city.name, self.state) if x is not None])
            self.slug = slugify_uniquely(name, self.__class__, max_length=255)

        if not self.cross_roads:
            self.address_override = True

        super(Community, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Deletes relationships on this instance."""
        self.relationships.all().delete()
        super(Community, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("community:view", kwargs={"pk": self.id})

    @classmethod
    def can_be_added(self, user):
        return user.has_perm("community.add_community")

    def can_be_edited(self, user):
        return user.has_perm("community.change_community")

    def can_be_deleted(self, user):
        """Check that only one relationship is exists and is owned by the user's company."""
        if user.is_superuser:
            return True
        if self.subdivision_set.count() != 0:
            return False
        if not user.has_perm("community.delete_community"):
            return False
        try:
            relationships = self.relationships.filter(is_owned=True)
            relationships = relationships.exclude(company__auto_add_direct_relationships=True)
            relationship = relationships.get()
        except (Relationship.MultipleObjectsReturned, Relationship.DoesNotExist):
            return False
        else:
            if user.company.id == relationship.company_id:
                return True

        return False

    def get_id(self):
        """Returns a nice prepadded ID"""
        return "{:06}".format(self.id)
