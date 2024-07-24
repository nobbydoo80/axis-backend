"""sponsor_preferences.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import logging

from django.apps import apps
from django.db import models

from axis.company.managers import (
    SponsorPreferencesManager,
)
from axis.relationship.models import Relationship

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class SponsorPreferences(models.Model):
    # This is really hard to wrap the head around with the nitpicky naming going on.  Sorry.

    objects = SponsorPreferencesManager()

    # The sponsorED company.  A sponsored company accesses its enforced preferences via:
    #     somecompany.sponsor_preferences.all()
    # Because this is the first ForeignKey to Company defined on this intermediate class, it is the
    # one selected by Django to be the anchor from where the m2m is defined on Company.  This FK is
    # therefore a referenced to the **sponsored** company.
    sponsored_company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="sponsor_preferences"
    )

    # The sponsorING company.  A sponsoring company accesses the preferences it has set for its
    # sponsored companies via:
    #     somecompany.sponsored_preferences.all()
    sponsor = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="sponsored_preferences"
    )

    can_edit_profile = models.BooleanField(default=True)
    can_edit_identity_fields = models.BooleanField(default=True)
    notify_sponsor_on_update = models.BooleanField(default=True)

    def __str__(self):
        return "{}(can_edit_profile={}, can_edit_identity_fields={}, notify_sponsor_on_update={})".format(
            self.__class__.__name__,
            self.can_edit_profile,
            self.can_edit_identity_fields,
            self.notify_sponsor_on_update,
        )

    class Meta:
        ordering = ("sponsored_company__name",)
        verbose_name_plural = "Sponsor preferences"

    def save(self, *args, **kwargs):
        """
        On creation, checks for a defaults supplier method based on the company's slug.

        If the slug has any '-', they are converted to underscores for the purposes of method
        resolution.
        """
        created = False

        if not self.pk:
            slug = self.sponsor.slug.replace("-", "_")
            try:
                get_defaults = getattr(self, "get_{}_sponsored_defaults".format(slug))
            except AttributeError:
                pass
            else:
                for k, v in get_defaults().items():
                    setattr(self, k, v)

            created = True

        super(SponsorPreferences, self).save(*args, **kwargs)

        if created:
            Relationship.objects.create_mutual_relationships(self.sponsor, self.sponsored_company)

    # Defaults suppliers for slugs "aps" and "neea"
    def get_aps_sponsored_defaults(self):
        return {
            "can_edit_profile": True,
            "can_edit_identity_fields": False,
            "notify_sponsor_on_update": True,
        }

    def get_neea_sponsored_defaults(self):
        return {
            "can_edit_profile": True,
            "can_edit_identity_fields": False,
            "notify_sponsor_on_update": False,
        }

    def get_eto_sponsored_defaults(self):
        return {
            "can_edit_profile": True,
            "can_edit_identity_fields": False,
            "notify_sponsor_on_update": True,
        }
