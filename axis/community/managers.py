"""manager.py: Django community"""


import logging

from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse

from .strings import (
    FOUND_COMMUNITY,
    MULTIPLE_COMMUNITIES_FOUND,
    UNKNOWN_COMMUNITY,
    MISSING_COMMUNITY,
    COMMUNITY_EXISTS_NO_RELATION,
)

__author__ = "Steven Klass"
__date__ = "3/11/12 2:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityQueryset(QuerySet):
    def filter_by_company(self, company, show_attached=False, **kwargs):
        """A way to trim down the list of objects by company"""
        objs = company.relationships.get_communities(show_attached=show_attached).filter(**kwargs)
        return self.filter(id__in=objs.values_list("id"))

    def filter_by_user(self, user, show_attached=False, **kwargs):
        if user.is_superuser:
            return self.filter(**kwargs)
        kwargs["show_attached"] = show_attached
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class CommunityManager(models.Manager):
    def get_queryset(self):
        return CommunityQueryset(self.model, using=self._db)

    def filter_by_company(self, company, show_attached=False, **kwargs):
        """A way to trim down the list of objects by company"""
        return self.get_queryset().filter_by_company(
            company=company, show_attached=show_attached, **kwargs
        )

    def filter_by_user(self, user, show_attached=False, **kwargs):
        return self.get_queryset().filter_by_user(user=user, show_attached=show_attached, **kwargs)

    def choice_items_from_instances(self, **kwargs):
        """This is simply a more effient way to get lots of labels"""
        communities = self.filter()
        if "user" in kwargs:
            communities = self.filter_by_user(kwargs.pop("user"))
        communities = communities.filter(**kwargs)
        communities = communities.values_list(
            "id",
            "name",
        )
        results = []
        for id, name in communities:
            results.append((id, "{}".format(name)))
        return sorted(list(set(results)), key=lambda item: (item[1]))

    def verify_existence_for_company(self, name=None, company=None, ignore_missing=False, log=None):
        """Simply verify that a community is in there relationships"""

        log = log if log else logging.getLogger(__name__)

        objects, community = [], None

        from axis.company.models import COMPANY_MODELS

        assert isinstance(company, COMPANY_MODELS), "Company must be of type Company"

        if isinstance(name, str):
            name = name.strip()

        if name is None:
            if ignore_missing:
                log.debug(MISSING_COMMUNITY)
                return None
            return None
        else:
            objects = self.filter_by_company(company)
            objects = objects.filter(name__iexact=str(name))
            if not objects.count():
                available = self.filter(name__iexact=str(name))
                if available.count() == 1:
                    log.error(COMMUNITY_EXISTS_NO_RELATION.format(community=available[0]))
                else:
                    log.error(UNKNOWN_COMMUNITY.format(community=name))
            elif objects.count() > 1:
                log.error(MULTIPLE_COMMUNITIES_FOUND.format(community=name))
            else:
                community = objects[0]

        if community:
            _url = reverse("community:view", kwargs={"pk": community.id})
            log.info(FOUND_COMMUNITY.format(url=_url, community=community))
        return community
