"""managers.py: Django builder_agreement"""


import logging

from django.db import models
from django.db.models import Q

__author__ = "Steven Klass"
__date__ = "3/26/12 8:27 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """Returns objects where the subdivision belongs to ``company`` (or is null)."""
        from axis.subdivision.models import Subdivision

        subs = Subdivision.objects.filter_by_company(company=company, show_attached=True)
        if company.is_eep_sponsor or company.company_type == "eep":
            return self.filter(
                Q(subdivision__in=subs) | Q(subdivision__isnull=True), company=company, **kwargs
            )
        if company.company_type == "builder":
            return self.filter(
                Q(subdivision__in=subs) | Q(subdivision__isnull=True), builder_org=company
            )
        from axis.company.models import Company

        bld_ids = Company.objects.filter_by_company(company, company_type="builder").values_list(
            "id", flat=True
        )
        return self.filter(
            Q(subdivision__in=subs) | Q(subdivision__isnull=True, builder_org_id__in=bld_ids)
        )

    def filter_by_user(self, user, **kwargs):
        """
        Finds the user company and calls ``filter_by_company()``. For superusers, no filtering takes
        place (i.e., ``**kwargs`` are forwarded directly to ``filter()``.)

        """
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_by_hers_score_for_user(self, user, min_hers=None, max_hers=None):
        from axis.home.models import Home

        kw = {}
        if min_hers:
            kw[
                "homestatuses__floorplan__remrate_target__energystar__energy_star_v2p5_pv_score__gte"
            ] = min_hers
        if max_hers:
            kw[
                "homestatuses__floorplan__remrate_target__energystar__energy_star_v2p5_pv_score__lte"
            ] = max_hers

        homes = Home.objects.filter_by_user(user, **kw)
        subdivision_ids = homes.values_list("subdivision")
        builder_ids = homes.filter(
            subdivision__isnull=True, relationships__company__company_type="builder"
        )
        builder_ids = builder_ids.values_list("relationships__company_id")
        return self.filter(
            Q(subdivision__in=subdivision_ids)
            | Q(subdivision__isnull=True, builder_org_id__in=builder_ids)
        )

    def get_raters_and_providers(self, builder_org_id, subdivision_id):
        from axis.company.models import Company

        if subdivision_id:
            from axis.subdivision.models import Subdivision

            subdivision = Subdivision.objects.get(id=subdivision_id)
            companies = subdivision.relationships.filter(
                company__company_type__in=["rater", "provider"]
            )
            companies = companies.values_list("company_id", flat=True)
        else:
            # STOP HERE - NEED TO FIGURE OUT HOW TO LOOK UP A THE PROVIDERS WHO HAVE DONE WORK FOR BUILDER
            from django.contrib.contenttypes.models import ContentType
            from axis.company.models import COMPANY_MODELS
            from axis.relationship.models import Relationship

            cts = ContentType.objects.get_for_models(*COMPANY_MODELS).values
            rels = Relationship.objects.filter(
                content_type__in=cts,
                object_id=builder_org_id,
                company__company_type__in=["rater", "provider"],
            )
            companies = rels.values_list("company_id", flat=True)
        return Company.objects.filter(id__in=companies)

    def get_floorplans_for_user(
        self, user, company_id, builder_org_id, subdivision_id=None, min_hers=None, max_hers=None
    ):
        from axis.floorplan.models import Floorplan

        kw = {
            "owner_id": company_id,
            "floorplanapproval__is_approved": True,
        }

        if subdivision_id:
            kw["floorplanapproval__subdivision__id"] = subdivision_id

        if builder_org_id:
            kw["floorplanapproval__subdivision__builder_org_id"] = builder_org_id

        if min_hers:
            kw["remrate_target__cenergystar__energy_star_v2p5_pv_score__gte"] = min_hers
        if max_hers:
            kw["remrate_target__cenergystar__energy_star_v2p5_pv_score__lte"] = max_hers

        return Floorplan.objects.filter_by_user(user, show_attached=True).filter(**kw)
