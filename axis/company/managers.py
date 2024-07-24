"""managers.py: Django company"""


import itertools
import logging
import re
from collections import namedtuple, defaultdict
from functools import reduce

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.urls import reverse

from axis.core.managers.mixins import OwnedObjectMixin
from axis.core.validators import represents_integer
from axis.relationship.models import Relationship
from .strings import *

__author__ = "Steven Klass"
__date__ = "3/2/12 2:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..core.managers.utils import queryset_user_is_authenticated

log = logging.getLogger(__name__)

SponsorPreferencesPermissionTuple = namedtuple(
    "SponsorPreferencesPermissionTuple", ["has_permission", "warning"]
)
LoggingResultTuple = namedtuple("LoggingResultTuple", ("errors", "warnings", "info"))


def get_company_aliases(_name):
    """Priority name is ALWAYS the input lowered"""
    names = list()
    name = _name.strip().lower()
    names.append(name)

    sub_name = re.sub(r",", "", name).strip()
    names.append(sub_name)

    sub_name = re.sub(r"\.", "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r"\.", "", name).strip())

    sub_name = re.sub(r"'", "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r"'", "", sub_name).strip())

    sub_name = re.sub(r'"', "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r'"', "", sub_name).strip())

    sub_name = re.sub(r"\(.*\)", "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r"\(.*\)", "", sub_name).strip())

    sub_name = re.sub(r"\bllc\b", "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r",?\s*llc\.?(?:\b|$)", "", name).strip())

    sub_name = re.sub(r"\binc\b", "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r",?\s*inc\.?(?:\b|$)", "", name).strip())

    sub_name = re.sub(r"\bco\b", "", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r",?\s*co\.?(?:\b|$)", "", name).strip())

    sub_name = re.sub(r"\s&\s", " and ", sub_name).strip()
    names.append(sub_name)
    names.append(re.sub(r"\s&\s", " and ", name).strip())

    seen = set()
    return [x for x in names if x not in seen and not seen.add(x)]


def build_company_aliases(company_type=None, company=None, user=None):
    """Builds a fanout of common aliases for company names.  You want to look at ALL companies
    when considering this so use this upstream"""
    from axis.company.models import Company, AltName

    results = defaultdict(set)
    priority_names = defaultdict(set)

    companies = Company.objects.all()
    alt_names = AltName.objects.all()
    if user:
        companies = Company.objects.filter_by_user(user)
        alt_names = alt_names.filter(company__in=companies)
    elif company:
        companies = Company.objects.filter_by_company(company)
        alt_names = alt_names.filter(company__in=companies)

    if company_type:
        companies = companies.filter(company_type=company_type)
        alt_names = alt_names.filter(company__company_type=company_type)

    companies = companies.values_list("id", "name")
    slug_companies = companies.values_list("id", "slug")
    alt_names = alt_names.values_list("company", "name")

    for _id, _name in list(alt_names) + list(companies):
        names = get_company_aliases(_name)
        for idx, name in enumerate(names):
            if idx == 0:
                priority_names[name].add(_id)
            results[name].add(_id)

    for _id, _name in list(slug_companies):
        results[_name].add(_id)

    final = dict()
    for k, v in results.items():
        v = list(v)
        if len(v) == 1:
            final[k] = v[0]
        if len(v) > 1:
            try:
                final[k] = list(priority_names[k])[0]
            except IndexError:
                log.info("Conflicting names {} - skipping {}".format(k, v))

    return final


class CompanyDocumentManager(models.Manager):
    def filter_by_company_for_shared_company(self, company, shared_company):
        """
        Returns public documents shared by ``shared_company``, where the company_type is not the
        same as ``company.company_type``.
        """
        docs = self.filter(company=shared_company, is_public=True)
        docs = docs.exclude(company__company_type=company.company_type)
        return docs


class CompanyManager(models.Manager):
    def __init__(self, company_type=None, *args, **kwargs):
        self._company_type = company_type
        super(CompanyManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = CompanyQueryset(self.model, using=self._db)
        if self._company_type:
            queryset = queryset.filter(company_type=self._company_type)
        return queryset

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        return self.get_queryset().filter_by_company(company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        return self.get_queryset().filter_by_user(user, **kwargs)

    def has_mutual_relationship(self, company, other_company):
        """
        Check if mutual relationships exist between companies
        :param company: Company object
        :param other_company: Company object
        :return: Boolean
        """

        if other_company is None:
            return False

        from axis.company.models import COMPANY_MODELS

        relations = Relationship.objects.filter_by_company(company, show_attached=True).filter(
            is_viewable=True
        )
        content_types = ContentType.objects.get_for_models(*COMPANY_MODELS).values()
        relations = relations.filter(content_type__in=content_types)
        return relations.filter(object_id=other_company.id).exists()

    def sponsoring_eep_providers(self):
        """Returns companies whose sponsor company type is ``'eep'``"""
        return self.filter(sponsors__company_type="eep")

    def unclaimed_companies(self, company, include_self=False):
        """
        Filters the companies from ``filter_by_company()`` to leave only non-customers that have no
        associated sponsor.
        """
        companies = self.filter_by_company(company=company, include_self=include_self)
        companies = companies.filter(is_customer=False, sponsors__isnull=True)
        return companies

    def filter_by_community(self, community, show_attached=True):
        """Returns companies associated to ``community``."""
        from axis.community.models import Community

        content_type = ContentType.objects.get_for_model(Community)
        relations = Relationship.objects.show_attached(show_attached)
        relations = relations.filter(content_type=content_type, object_id=community.id)
        return self.filter(id__in=list(relations.values_list("company_id", flat=True)))

    def filter_by_subdivision(self, subdivision, show_attached=True):
        """Returns companies associated to ``subdivision``"""
        from axis.subdivision.models import Subdivision

        content_type = ContentType.objects.get_for_model(Subdivision)
        relations = Relationship.objects.show_attached(show_attached)
        relations = relations.filter(content_type=content_type, object_id=subdivision.id)
        return self.filter(id__in=list(relations.values_list("company_id", flat=True)))

    def filter_by_home(self, home, show_attached=True):
        """Returns companies associated to ``home``."""
        from axis.home.models import Home

        content_type = ContentType.objects.get_for_model(Home)
        relations = Relationship.objects.show_attached(show_attached)
        relations = relations.filter(content_type=content_type, object_id=home.id)
        return self.filter(id__in=list(relations.values_list("company_id", flat=True)))

    def verify_existence_for_company(
        self, name=None, company=None, company_type=None, log=None, **kwargs
    ):
        """
        Verifies that company ``name`` is found in ``company``'s relation network.  If provided,
        ``company_type`` restricts the search accordingly.

        If ``name`` is not found, but appears to correspond to a company outside of the relationship
        network, an error notice is generated to indicate this.

        If ``name`` does not correspond to any known company, an error message is generated.

        If ``name`` corresponds to multiple companies, an error message is generated.

        """
        log = log if log else logging.getLogger(__name__)
        log_errors = kwargs.get("log_errors", True)

        company_obj = None

        from .models import COMPANY_MODELS

        assert isinstance(company, COMPANY_MODELS)

        if self._company_type:
            company_type = self._company_type
        pretty_company_type = (
            "Company" if not company_type else dict(COMPANY_TYPES).get(company_type)
        )

        if isinstance(name, str):
            name = name.strip()

        if name is None:
            if log_errors:
                log.error(MISSING_COMPANY.format(company_type=pretty_company_type))
        elif represents_integer(name):
            try:
                company_obj = self.filter_by_company(company).get(id=int(name))
            except ObjectDoesNotExist:
                if log_errors:
                    log.error(
                        UNKNOWN_COMPANY_BY_ID.format(company_type=pretty_company_type, id=name)
                    )
        else:
            objects = self.filter_by_company(company)
            if company_type:
                objects = objects.filter(company_type=company_type)

            company_aliases = build_company_aliases(company_type=company_type, company=company)

            company_id = None
            for _alias in get_company_aliases(name):
                if company_aliases.get(_alias):
                    company_id = company_aliases.get(_alias)
                    if company_id:
                        objects = objects.filter(id=company_id)
                    break

            if not company_id:
                objects = objects.none()

            if not objects.count():
                if company_id:
                    company = self.get(id=company_id)
                    if log_errors:
                        log.error(
                            COMPANY_EXISTS_NO_RELATION.format(
                                company_type=pretty_company_type, company=company
                            )
                        )
                else:
                    if log_errors:
                        log.error(
                            UNKNOWN_COMPANY.format(company_type=pretty_company_type, company=name)
                        )
            else:
                company_obj = objects.get()

        if company_obj:
            _url = reverse(
                "company:view", kwargs={"pk": company_obj.id, "type": company_obj.company_type}
            )
            company_type = dict(COMPANY_TYPES).get(company_obj.company_type)
            log.debug(
                FOUND_COMPANY.format(company=company_obj, company_type=company_type, url=_url)
            )
        return company_obj


class CompanyQueryset(QuerySet):
    def filter_by_company(
        self, company, show_attached=False, include_self=False, mutual=False, **kwargs
    ):
        """A way to trim down the list of objects by company"""
        from axis.company.models import Company

        relations = Relationship.objects.filter_by_company(
            company, show_attached=show_attached
        ).filter(is_viewable=True)
        company_ct = ContentType.objects.get_for_model(Company)
        relations = relations.filter(content_type=company_ct)

        object_ids = list(relations.values_list("object_id", flat=True))

        if mutual:
            mutual_rels = Relationship.objects.filter(
                content_type=company_ct,
                object_id=company.id,
                is_owned=True,
                is_attached=True,
            )
            mutual_ids = list(mutual_rels.values_list("company_id", flat=True))
            object_ids = list(set(object_ids) & set(mutual_ids))

        if include_self:
            object_ids.append(company.id)

        return self.filter(id__in=object_ids, **kwargs)

    def filter_by_user(self, user, show_attached=False, include_self=False, **kwargs):
        """A way to trim down the list of objects by user"""
        kwargs["is_active"] = kwargs.get("is_active", True)

        if user.is_superuser:
            results = self.filter(**kwargs)
            return results

        kwargs["show_attached"] = show_attached
        kwargs["include_self"] = include_self

        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def get_contact_list(self):
        """
        Returns a python list of ``Contact`` dummy objects that refer to a company and possibly a
        ``User`` instance.  Each company in the source queryset is guaranteed at least one entry in
        the returned list, where the user is None.  If there are items at ``company.users.all()``,
        each of those will add to this default entry.  Consequently, if a company has 2 users, it
        will have 3 items in the returned list.
        """

        from .models import Contact_SPECIAL as Contact

        companies = self.prefetch_related("users")
        contacts = []
        for company in companies:
            default_contact = Contact(company=company)
            contacts.append(default_contact)

            # Add users
            for user in company.users.all():
                contacts.append(Contact(company=company, user=user))

        queryset = _ContactQueryset(model=Contact)
        queryset.contacts = contacts
        return queryset


class _ContactQueryset(QuerySet):
    """Manages a fake queryset for the Contact_SPECIAL model.  It prevents database queries."""

    contacts = None

    def __iter__(self):
        return iter(self.contacts)

    @staticmethod
    def _get_distant_attr(field_name):
        def key(instance):
            try:
                return reduce(getattr, [instance] + field_name.split("__"))
            except (AttributeError, ObjectDoesNotExist):
                return None

        return key

    def _filter_or_exclude(self, negate, *args, **kwargs):
        """Provides in-memory filtering of ``self.contacts`` based on a query object."""
        # This thing assumes icontains is the query operator and that there's only one Q object,
        # which is how datatableview ends up calling this.
        clone = self._clone()
        if args:
            q_list = args[0]
            if isinstance(q_list.children[0], Q):
                q_list = list(itertools.chain(*[q.children for q in q_list.children]))
            else:
                q_list = q_list.children
            contacts = clone.contacts
            length = len(contacts)
            for i, contact in enumerate(reversed(contacts)):
                keep = False
                for field_path, term in q_list:
                    if field_path.endswith("__icontains"):
                        term = term.lower()
                        field_path = field_path.replace("__icontains", "")
                        value = f"{self._get_distant_attr(field_path)(contact)}"
                        if value is not None and term in value.lower():
                            keep = True
                            break

                if not keep:
                    obj = clone.contacts.pop(length - 1 - i)
        return clone

    def order_by(self, *field_names):
        obj = self._clone()
        for field_name in reversed(field_names):
            reverse = field_name[0] == "-"
            if reverse:
                field_name = field_name[1:]
            obj.contacts.sort(key=self._get_distant_attr(field_name), reverse=reverse)
        return obj

    def _clone(self, **kwargs):
        c = _ContactQueryset(model=self.model)
        c.contacts = self.contacts[:]
        return c

    def _get_result_cache(self):
        return self.contacts

    def _set_result_cache(self, value):
        pass

    _result_cache = property(_get_result_cache, _set_result_cache)


class ContactQuerySet(OwnedObjectMixin, QuerySet):
    owner_field = "company"


class SponsorPreferencesManager(models.Manager):
    def get_edit_profile_policy(self):
        """
        Sifts through this company's various sponsor preferences to derive a value.

        Returns a namedtuple of (has_permission=bool, warning=bool).

        The ``"has_permission"`` item is ``False`` if any sponsors at all have set False for the
        "can_edit_profile".  The ``"warning"`` item is ``True`` if there is a disagreement of True
        and False values across preferences from multiple sponsors.
        """

        has_permission = False
        warning = False

        num_preferences = self.count()
        disallows_edits = self.filter(can_edit_profile=False).count()
        allows_edits = num_preferences - disallows_edits

        if allows_edits and disallows_edits:
            # Least permissive policy will be used
            has_permission = False
            warning = True
        elif allows_edits:
            has_permission = True
        elif disallows_edits:
            has_permission = False
        else:
            # No sponsorships exist, thus no policies
            has_permission = True

        return SponsorPreferencesPermissionTuple(has_permission, warning=warning)

    def get_edit_identity_fields_policy(self):
        """
        Sifts through this company's various sponsor preferences to derive a value.

        Returns a namedtuple of (has_permission=bool, warning=bool).

        The ``"has_permission"`` item is ``False`` if any sponsors at all have set False for the
        "can_edit_profile".  The ``"warning"`` item is ``True`` if there is a disagreement of True
        and False values across preferences from multiple sponsors.

        If ``get_edit_profile_policy().has_permission`` is False, this method will always return
        ``(has_permission=False, warning=False)``.

        """

        has_permission = False
        warning = False

        edit_profile_policy = self.get_edit_profile_policy()

        if edit_profile_policy.has_permission:
            num_preferences = self.count()
            disallows_edits = self.filter(can_edit_identity_fields=False).count()
            allows_edits = num_preferences - disallows_edits

            if allows_edits and disallows_edits:
                # Least permissive policy will be used
                has_permission = False
                warning = True
            elif allows_edits:
                has_permission = True
            elif disallows_edits:
                has_permission = False
            else:
                # No sponsorships exist, thus no policies
                has_permission = True
        else:
            return edit_profile_policy

        return SponsorPreferencesPermissionTuple(has_permission, warning=warning)

    def get_companies_to_be_notified(self, ids_only=False):
        """Returns the list of sponsor Company objects that want to be notified of updates."""
        from .models import Company

        notification_preferences = self.filter(notify_sponsor_on_update=True)
        sponsor_ids = list(notification_preferences.values_list("sponsor_id", flat=True))
        if ids_only:
            return sponsor_ids
        return Company.objects.filter(id__in=sponsor_ids)


class AltNameQueryset(QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        from axis.company.models import Company

        available_companies = Company.objects.filter_by_user(user)
        return self.filter(Q(company__in=available_companies) | Q(company=user.company))
