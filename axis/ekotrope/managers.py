"""managers.py: Django remrate_data"""


import logging

from django.db import models
from django.db.models import Q

from axis.relationship.models import Relationship

__author__ = "Steven Klass"
__date__ = "3/8/13 2:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CompanyAndUserMixin(object):
    COMPANY_PATH = None  # something like 'project__company'

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company
        :param company: Company object
        :param kwargs: other search terms
        """
        from axis.home.models import Home

        if company.company_type == "rater":
            return self.filter(**dict({self.COMPANY_PATH: company}, **kwargs))

        if company.company_type in ["provider", "eep", "builder", "qa"] or company.is_eep_sponsor:
            # These folks can see stat data for not just their company but those who have
            # relationships with them who has a relationship with me..
            comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
            # Who do I have a relationship with
            rels = company.relationships.get_companies(ids_only=True)
            # The intersection of these is what matters..
            ints = set(rels).intersection(set(comps))

            company_q = Q(**{self.COMPANY_PATH: company}) | Q(
                **{self.COMPANY_PATH + "_id__in": ints}
            )

            if company.company_type in ["builder"]:
                home_ids = Home.objects.filter_by_company(company, show_attached=True)
                home_ids = list(home_ids.values_list("id", flat=True))
                return self.filter(
                    company_q, floorplan__homestatuses__home_id__in=home_ids, **kwargs
                ).distinct()
            return self.filter(company_q, **kwargs)
        return self.filter(**dict({self.COMPANY_PATH: company}, **kwargs))

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user
        :param user: User object
        :param kwargs: other search terms
        """
        if user.is_superuser:
            return self.filter(**kwargs)

        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class ProjectQuerySet(CompanyAndUserMixin, models.QuerySet):
    COMPANY_PATH = "company"


class HousePlanQuerySet(CompanyAndUserMixin, models.QuerySet):
    COMPANY_PATH = "project__company"

    def filter_for_fuel_type(self, fuel_type):
        "SLOW AND EXPENSIVE"
        ids = []
        for item in self.filter():
            to_add = True
            for mech in item.data.get("mechanicals", {}).get("mechanicalEquipment", []):
                if mech.get("type", {}).get("fuel").lower() != fuel_type.lower():
                    to_add = False
                    break
            if to_add:
                ids.append(item.id)
        return self.filter(id__in=ids)

    def filter_for_electric_only(self):
        return self.filter_for_fuel_type("ELECTRIC")
