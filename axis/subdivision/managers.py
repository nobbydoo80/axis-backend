"""managers.py: Django subdivision"""


import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.urls import reverse

from axis.company.models import Company
from axis.core.validators import represents_integer

try:
    from . import strings
except ValueError:
    from axis.subdivision import strings

__author__ = "Steven Klass"
__date__ = "3/5/12 1:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SubdivisionQueryset(QuerySet):
    def filter_by_company(self, company, **kwargs):
        """Performs a lookup based on a company relationships and optional kwargs

        :param company: axis.company.models.Company
        :param kwargs: dict
        :return: django.db.models.query.QuerySet
        """
        objs = company.relationships.get_subdivisions(
            show_attached=kwargs.pop("show_attached", False)
        ).filter(**kwargs)
        return self.filter(id__in=objs.values_list("id"))

    def filter_by_user(self, user, **kwargs):
        """Performs a lookup based on a user

        :param user: django.contrib.auth.models.User
        :param kwargs: dict
        :return: django.db.models.query.QuerySet
        """
        show_attached = kwargs.pop("show_attached", False)
        if user.is_superuser:
            return self.filter(**kwargs)
        kwargs["show_attached"] = show_attached

        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()

        qs = self.filter_by_company(**kwargs)

        return qs


class SubdivisionManager(models.Manager):
    """Subdivision Manager"""

    def get_queryset(self):
        return SubdivisionQueryset(self.model, using=self._db)

    def filter_by_company(self, company, show_attached=False, **kwargs):
        """Performs a lookup based on a company relationships and optional kwargs"""
        return self.get_queryset().filter_by_company(
            company=company, show_attached=show_attached, **kwargs
        )

    def filter_by_user(self, user, show_attached=False, **kwargs):
        """Performs a lookup based on a user"""
        return self.get_queryset().filter_by_user(user=user, show_attached=show_attached, **kwargs)

    def choice_items_from_instances(self, user=None, *args, **kwargs):
        #        """This is simply a more effient way to get lots of labels"""
        """An efficient way to get labels for use in select widget.  This will
        return a list of tuples [(id, label), (id, label)]

        :param user: django.contrib.auth.models.User
        :param args: list
        :param kwargs: dict
        :return: list
        """
        from axis.community.models import Community

        subs = self.filter(*args, **kwargs)
        if user:
            subs = self.filter_by_user(user).filter(*args, **kwargs)

        community_ids = subs.values_list("community_id", flat=True)
        communities = Community.objects.filter(id__in=community_ids)
        communities = dict(communities.values_list("id", "name"))

        results = []
        subs = subs.values_list("id", "name", "community", "builder_name")
        for _id, name, community, builder_name in subs:
            community = communities.get(community)
            value = "{}{}{}".format(
                name,
                " at {}".format(community) if community else "",
                " ({})".format(builder_name) if builder_name else "",
            )
            results.append((_id, value))
        return sorted(list(set(results)), key=lambda item: (item[1]))

    def verify_for_company(
        self, name=None, builder_name=None, community=None, builder=None, company=None, log=None
    ):
        """This will validate a subdivision is meets all needs for a bulk upload.

        :param name: str
        :param builder_name: str
        :param community: axis.community.models.Community
        :param builder: axis.company.models.Company
        :param company: axis.company.models.Company
        :param log: logging.Logger
        :return: axis.company.models.Subdivision
        """
        log = log if log else logging.getLogger(__name__)

        objects, subdivision = [], None

        from axis.company.models import COMPANY_MODELS
        from axis.community.models import Community

        assert isinstance(company, COMPANY_MODELS), "Company must be of type Company"
        assert isinstance(
            builder, (type(None), COMPANY_MODELS)
        ), "If specified Builder must be of Type Company"
        assert isinstance(
            community, (type(None), Community)
        ), "If specified Community must be of type Community"

        if isinstance(name, str):
            name = name.strip()

        if name is None and builder_name is None:
            log.error(strings.MISSING_SUBDIVISION)
        elif represents_integer(name):
            try:
                subdivision = self.filter_by_company(company).get(id=int(name))
            except ObjectDoesNotExist:
                log.error(strings.UNKNOWN_SUBDIVISION_BY_ID.format(id=name))
        else:
            name_query = Q()
            if name:
                name_query |= Q(name__iexact=name)
            if builder_name:
                name_query |= Q(builder_name__iexact=builder_name)

            base_objects = self.filter_by_company(company=company)
            if community:
                base_objects = base_objects.filter(community=community)
            if builder:
                base_objects = base_objects.filter(builder_org=builder)

            objects = base_objects.filter(name__iexact=name)
            if builder_name:
                objects = base_objects.filter(name_query)
            if not objects.count():
                available = self.filter(name_query)
                if available.count() == 1:
                    available_obj = available.get()
                    if builder and available_obj.builder_org_id != builder.id:
                        log.error(
                            strings.SUBDIVISION_NOT_EXIST_WITH_BUILDER.format(
                                subdivision=available_obj, builder=builder
                            )
                        )
                    else:
                        log.error(
                            strings.SUBDIVISION_EXISTS_NO_RELATION.format(subdivision=available_obj)
                        )
                else:
                    found = False
                    if name:
                        split_up = re.search(r"(.*)(\sat\s|\s?@\s?)(.*)", name)
                        if split_up:
                            objects = base_objects.filter(name__iexact=split_up.group(1).strip())
                            if objects.count() > 1:
                                objects = base_objects.filter(
                                    community__name__iexact=split_up.group(3).strip()
                                )
                            if objects.count() == 1:
                                found = True
                    if not found:
                        if name is None and builder_name:
                            log.error(
                                strings.UNKNOWN_SUBDIVISION_WITH_BUILDER_NAME.format(
                                    builder_name=builder_name
                                )
                            )
                        elif name and builder:
                            log.error(
                                strings.SUBDIVISION_NOT_EXIST_WITH_BUILDER.format(
                                    subdivision=name, builder=builder
                                )
                            )
                        else:
                            log.error(strings.UNKNOWN_SUBDIVISION.format(subdivision=name))
            elif objects.count() > 1:
                log.error(strings.MULTIPLE_SUBDIVISIONS_FOUND.format(subdivision=name))
            else:
                subdivision = objects[0]
        if subdivision:
            _url = reverse("subdivision:view", kwargs={"pk": subdivision.id})
            if community and subdivision.community != community:
                log.error(
                    strings.SUBDIVISION_INCORRECT_COMMUNITY.format(
                        subdivision=subdivision, url=_url, community=community
                    )
                )
                return
            if community and community.is_multi_family != subdivision.is_multi_family:
                log.error(
                    strings.SUBDIVISION_MULTIFAMILY_MISMATCH.format(
                        subdivision=subdivision, url=_url, community=community
                    )
                )

            log.info(strings.FOUND_SUBDIVISION.format(subdivision=subdivision, url=_url))
            return subdivision


class EEPProgramSubdivisionStatusManager(models.Manager):
    """Manager for EEP Program Statuses"""

    def filter_by_company(self, company, **kwargs):
        """Performs a lookup based on a company relationships and optional kwargs

        :param company: axis.company.models.Company
        :param kwargs: dict
        :return: django.db.models.query.QuerySet
        """
        if company.is_eep_sponsor:
            return self.filter(eep_program__owner=company)
        return self.filter(company=company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """Performs a lookup based on a user

        :param user: django.contrib.auth.models.User
        :param kwargs: dict
        :return: django.db.models.query.QuerySet
        """
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def verify_and_create_for_company(
        self, company, subdivision=None, eep_program=None, create=False, log=None, **kwargs
    ):
        """

        :param company: axis.company.models.Company
        :param subdivision: axis.subdivision.models.Subdivision
        :param eep_program: axis.eep_program.models.EEPProgram
        :param create: bool
        :param log: logging.logger
        :param kwargs: dict
        :return: axis.company.models.EEPProgramSubdivisionStatus
        """

        log = log if log else logging.getLogger(__name__)

        from axis.company.models import COMPANY_MODELS
        from axis.eep_program.models import EEPProgram
        from .models import Subdivision

        objects, sub_stat = [], None

        assert isinstance(company, COMPANY_MODELS), "Company must be of type Company"
        assert isinstance(
            subdivision, (type(None), Subdivision)
        ), "If specified subdivision must of type Subdivision"
        assert isinstance(
            eep_program, (type(None), EEPProgram)
        ), "If specified eep_program must of type EEPProgram"

        if None in [eep_program, subdivision]:
            return None

        _surl = reverse("subdivision:view", kwargs={"pk": subdivision.id})
        if eep_program.owner not in subdivision.relationships.get_accepted_companies():
            if (
                eep_program.rater_incentive_dollar_value
                or eep_program.builder_incentive_dollar_value
            ):
                log.error(
                    strings.PROGRAM_OWNER_UNATTACHED.format(
                        owner=eep_program.owner, url=_surl, subdivision=subdivision
                    )
                )
            else:
                if eep_program.owner.users.count():
                    log.warning(
                        strings.PROGRAM_OWNER_UNATTACHED.format(
                            owner=eep_program.owner, url=_surl, subdivision=subdivision
                        )
                    )

        objects = self.filter(eep_program=eep_program, subdivision=subdivision)

        if objects.count() > 1:
            objects = objects.exclude(company=company)
            comps = ", ".join([x.company.name for x in objects if x.company.id != company.id])
            log.warning(
                strings.PROGRAM_IN_USE.format(
                    program=eep_program, company=comps, url=_surl, subdivision=subdivision
                )
            )
        elif objects.count() == 1:
            if company and company.id != objects[0].company.id:
                log.warning(
                    strings.PROGRAM_IN_USE.format(
                        program=eep_program, company=company, url=_surl, subdivision=subdivision
                    )
                )
            else:
                sub_stat = objects[0]
        else:
            if create:
                company = Company.objects.get(id=company.id)
                sub_stat, create = self.get_or_create(
                    subdivision=subdivision, eep_program=eep_program, company=company
                )
                log.debug(
                    strings.SUBSTAT_USED_CREATE.format(
                        create="Created" if create else "Used existing",
                        company=company,
                        program=eep_program,
                        url=_surl,
                        subdivision=subdivision,
                    )
                )
        return sub_stat

    def verify_for_company(self, **kwargs):
        kwargs["create"] = False
        return self.verify_and_create_for_company(**kwargs)


class FloorplanApprovalQuerySet(QuerySet):
    """
    Meant to match some of the FloorplanQuerySet API so that this model can be used in place of
    Floorplan in certain situations.
    """

    def filter_by_company(self, company, show_attached=False):
        """A way to trim down the list of objects by company
        :param company: Company Object
        :param kwargs: kwargs
        """

        from axis.floorplan.models import Floorplan

        ids = Floorplan.objects.filter_by_company(
            company, ids_only=True, show_attached=show_attached
        )
        return self.filter(floorplan__id__in=ids)

    def filter_by_user(self, user, show_attached=False):
        """A way to trim down the list of objects by user
        :param user: User Object
        :param kwargs: kwargs
        """
        if user.is_superuser:
            return self.filter()
        return self.filter_by_company(user.company, show_attached=show_attached)

    def filter_by_user_and_subdivision(self, user, subdivision):
        subdivision_q = (
            # Directly specified on the FloorplanApproval
            Q(subdivision=subdivision)  # | \
            # FIXME: Remove this?  I think migrations will have associated everything directly.
            # Implied
            # Q(floorplan__homestatuses__home__subdivision=subdivision)
        )
        return self.filter_by_user(user=user, show_attached=True).filter(subdivision_q).distinct()
