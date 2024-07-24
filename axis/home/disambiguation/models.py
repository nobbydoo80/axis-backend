"""Disambiguation extension (utilties)."""


import logging
from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.apps import apps

from simple_history.models import HistoricalRecords

import axis.geographic.utils.city
from axis.annotation.models import Type
from . import utils

__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


def _build_company_aliases():
    from axis.company.managers import build_company_aliases

    return build_company_aliases(company_type="builder")


class BaseCertification(models.Model):
    PROGRAM_NAME = "program"
    PROGRAM_NAMES = {
        # 'Incoming program field text': 'Final Program Name',
    }
    FIELDS = {
        # 'StreetAddress': 'street_line1',
        # 'Zip': 'zipcode',
        # ...etc
    }
    ANNOTATIONS = ()

    home = models.OneToOneField(
        "home.Home",
        blank=True,
        null=True,
        related_name="%(app_label)s_certification",
        on_delete=models.SET_NULL,
    )

    import_failed = models.BooleanField(default=False)
    import_error = models.CharField(max_length=500, blank=True, null=True)
    import_traceback = models.TextField(blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def get_annotation_label(self, slug):
        LABEL_LOOKUPS = dict(map(reversed, self.FIELDS.items()))
        return LABEL_LOOKUPS[slug]

    def get_is_multifamily(self):
        return False

    # DEVS: This fails the mccabe score and should be reworked to a score <= 10
    def find_axis_home(
        self,
        profile_threshold=utils.ADDRESS_PROFILE_THRESHOLD,
        levenshtein_threshold=utils.ADDRESS_LEVENSHTEIN_THRESHOLD,
        debug_home_ids=[],
    ):
        """
        Returns the matching Home instance for this object, False if multiple candiates are found,
        or None if there are no matches.
        """

        from axis.home.models import Home

        if self.home:
            return self.home

        # Note that we're not filtering for the builder or subdivision as part of this search, since
        # if those don't yet exist in Axis, we would be left with no candidate homes.

        street_line1 = utils.normalize_address(self.street_line1)
        profile = utils.profile_address(street_line1)
        profile_filter = Q(street_line1_profile=None) | Q(
            street_line1_profile__gte=(profile - profile_threshold),
            street_line1_profile__lte=(profile + profile_threshold),
        )
        candidates = Home.objects.filter(
            profile_filter,
            **{
                "city__name": self.city,
                # 'city__county__name': self.county,
                "city__county__state__iexact": self.state_abbreviation,
                # 'zipcode': self.zipcode,
                # Only nominate homes that aren't already assigned
                "{self._meta.app_label}_certification".format(self=self): None,
            },
        )

        if debug_home_ids:
            print(
                "??1",
                candidates.filter(id__in=debug_home_ids).count(),
                profile_filter,
                {
                    "city__name": self.city,
                    # 'city__county__name': self.county,
                    "city__county__state__iexact": self.state_abbreviation,
                    # 'zipcode': self.zipcode,
                    # Only nominate homes that aren't already assigned
                    "{self._meta.app_label}_certification".format(self=self): None,
                },
            )

        n_candidates = candidates.count()
        if n_candidates == 0:
            return None

        # Check for direct matches of normalized street_line1 values.  It's possible this will yield
        # multiple results, where lot_number is causing lots of matches.  We're not dealing with
        # lot_number collisions at all, and so we expect those to appear as candidates for human
        # eyes to check over.
        log.debug("Scanning multiple candidates for obvious matches...")
        likely_candidates = candidates.filter(street_line1_profile=profile)
        matches = []
        for candidate in likely_candidates:
            if utils.normalize_address(candidate.street_line1) == street_line1:
                matches.append(candidate)
        if debug_home_ids:
            print("??2", likely_candidates.filter(id__in=debug_home_ids).count())
        if len(matches) == 1:
            return matches[0]

        # Try harder by removing profile noise from odd suffixes.
        # NOTE: This step could be removed if we save normalized addresses directly to the homes.
        log.debug(
            "Falling back to suffix replacement... (profile=%d, address=%r)",
            profile,
            utils.normalize_address(self.street_line1),
        )
        candidate_data = list(candidates.values("id", "street_line1", "street_line1_profile"))
        distances = {}
        for item in candidate_data:
            item_street_line1 = utils.normalize_address(item["street_line1"])
            item_profile = item["street_line1_profile"]
            if item["street_line1_profile"] is None:
                item_profile = utils.profile_address(item_street_line1)
                _homes = Home.objects.filter(id=item["id"])
                _homes.update(street_line1_profile=item_profile)

            if utils.is_within_profile_threshold(
                item_profile, profile, threshold=profile_threshold
            ):
                distance = utils.get_levenshtein_distance(item_street_line1, street_line1)
                if distance <= levenshtein_threshold:
                    profile_delta = item_profile - profile
                    distances[item["id"]] = (distance, profile_delta)

        if distances:
            candidates = Home.objects.filter(id__in=distances.keys())
        else:
            candidates = Home.objects.none()

        if debug_home_ids:
            print("??3", candidates.filter(id__in=debug_home_ids).count())

        n_candidates = candidates.count()
        if n_candidates == 1:
            candidate = candidates.first()
            if distances[candidate.id][0] == 0:
                log.info("Perfect address comparison score for %r", candidate)
                return candidate
            else:
                log.info("Inconclusive single match: %r", candidate)
        if n_candidates > 0:
            log.info("Tagging %d candidates...", n_candidates)
            final_candidate_ids = sorted(distances.items(), key=lambda k_v: k_v[1][0])[:10]
            self.candidates.clear()
            self.candidates.through.objects.bulk_create(
                [
                    self.candidates.through(
                        **{
                            "certification": self,
                            "home_id": home_id,
                            "levenshtein_distance": _distance,
                            "profile_delta": _profile_delta,
                        }
                    )
                    for home_id, (_distance, _profile_delta) in final_candidate_ids
                ]
            )
            return False
        elif n_candidates == 0:
            log.info("No candidates found for threshold.")
            return None

    def ensure_axis_home(self, home=None):
        """Force a Home to be created for this object, even if candidates are not resolved."""

        if home is None:
            home = self.find_axis_home()
        app = apps.get_app_config(self._meta.app_label)
        home = utils.generate_home_data(self, app.get_customer_company(), home=home)

        related = home.neea_certification_candidates.exclude(id=self.id)
        if related:
            log.info("Regenerating candidates for items suspecting this home as their match...")
            for related_certification in related:
                log.info(
                    "Regenerating candidates: %r (%d)",
                    related_certification,
                    related_certification.candidates.count(),
                )
                self.find_axis_home(related_certification)

        return home

    def find_axis_builder(self):
        """Return an existing BuilderOrganization matching this record's `builder`, else None."""

        if not hasattr(self, "builder"):
            return

        from axis.company.models import Company
        from axis.company.managers import get_company_aliases

        all_aliases = _build_company_aliases()
        for alias in get_company_aliases(self.builder):
            if alias in all_aliases:
                builder_id = all_aliases[alias]
                return Company.objects.get(id=builder_id)

        return None

    def ensure_axis_builder(self, org_id=None):
        """Force a Builder to be created for this object, or return the existing one."""

        from axis.company.models import Company

        builder_org = None
        if org_id:
            builder_org = Company.objects.get(id=org_id, company_type=Company.BUILDER_COMPANY_TYPE)
        else:
            builder_org = self.find_axis_builder()
            if not builder_org and hasattr(self, "builder"):
                builder_org = Company.objects.create(
                    name=self.builder, company_type=Company.BUILDER_COMPANY_TYPE
                )

        return builder_org

    def find_axis_subdivision(self):
        """Return an existing Subdivision matching this record's `community_project`, else None."""

        from axis.subdivision.models import Subdivision

        if hasattr(self, "community_project") and self.community_project:
            return Subdivision.objects.filter(name__iexact=self.community_project).first()
        return None

    def ensure_axis_subdivision(self):
        """Force a Subdivision to be created for this object, or return the existing one.
        If `community_project` is not available, this will return None without doing any work.
        """

        from axis.relationship.models import Relationship
        from axis.subdivision.models import Subdivision

        if not hasattr(self, "community_project") or self.community_project is None:
            return None

        city = axis.geographic.utils.city.resolve_city(
            name=getattr(self, "city"),
            county=getattr(self, "county"),
            state_abbreviation=getattr(self, "state"),
            country=getattr(self, "country"),
        )
        builder_org = self.ensure_axis_builder()
        subdivision, _ = Subdivision.objects.get_or_create(
            **{
                "name": self.community_project,
                "city": city,
                "builder_org": builder_org,
            }
        )

        # Ensure relationships between HIRL and the builder
        app = apps.get_app_config(self._meta.app_label)
        Relationship.objects.create_mutual_relationships(app.get_customer_company(), builder_org)

        return subdivision

    def get_annotation_data(self):
        return OrderedDict(
            (
                Type.objects.update_or_create(
                    slug=type_slug,
                    defaults={
                        "name": self.get_annotation_label(type_slug),
                        "description": "",
                        "is_unique": True,
                        "data_type": "open",
                        "is_required": False,
                    },
                )[0],
                getattr(self, type_slug),
            )
            for type_slug in self.ANNOTATIONS
        )
