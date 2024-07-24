"""managers.py: Django eep_program"""


import datetime
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.urls import reverse

from axis.core.validators import represents_integer
from . import strings

__author__ = "Steven Klass"
__date__ = "3/11/12 7:33 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# pylint: disable=C0103
# pylint: disable=R0913
# pylint: disable=R0201
# pylint: disable=W0613
# I didn't want to mess with the parameters not being used, since I don't know where they could be
# used, and break things up


class EEPProgramQuerySet(QuerySet):
    """Collection of QuerySets for EPPProgram"""

    def get_by_natural_key(self, name, slug):
        """Used for serialization
        :param name: Group Name
        :param slug: Company Slug
        """
        return self.get(name=name, owner__slug=slug)

    def order_by_customer_status(self):
        """Orders by paying customer and oldest opened programs first"""
        return self.order_by(
            "-owner__is_customer",  # Is a paying customer
            "program_start_date",  # Oldest opened programs first
        )

    def filter_potential_sponsors_for_user(self, user):
        """Return companies which can be used for a company
        :param user: User Object
        """
        from axis.company.models import Company

        companies = Company.objects.filter(Q(company_type="eep") | Q(is_eep_sponsor=True))
        if user.is_superuser:
            return companies
        elif user.company.is_eep_sponsor or user.company.company_type == "eep":
            return companies.filter(id=user.company.id)
        elif user.company.is_customer:
            my_rels = user.company.relationships.get_companies()
            my_rels = my_rels.filter(is_customer=False).values_list("id", flat=True)
            return Company.objects.filter(id__in=list(my_rels) + [user.company.id])
        return user.company.sponsors.filter(Q(company_type="eep") | Q(is_eep_sponsor=True))

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company.  This should return
        :param kwargs: Any other filtering
        :param company: Company Object

        If I'm a customer:
            return my eep_programs and eep_programs with owners that have a relationship
            with me that I have a relationship with.
        else:
            return companies which have a relationship with me that are eep_sponsors

        """
        ignore_dates = kwargs.pop("ignore_dates", False)
        visible_for_use = kwargs.pop("visible_for_use", False)

        # These start and end filters only get used if ignore_dates is ``False``.
        start_filter = Q(program_start_date__isnull=True) | Q(
            program_start_date__lte=datetime.datetime.today()
        )
        if visible_for_use:
            start_filter = Q(program_visibility_date__isnull=True) | Q(
                program_visibility_date__lte=datetime.datetime.today()
            )
        end_filter = Q(program_end_date__isnull=True) | Q(
            program_end_date__gte=datetime.datetime.today()
        )

        public = self.filter(is_public=True)
        if not ignore_dates:
            public = public.filter(start_filter, end_filter, is_active=True)
        public = list(public.values_list("id", flat=True))

        my_rels = company.relationships.get_companies()
        non_customer = self.filter(
            owner__in=my_rels.filter(
                is_customer=False, sponsors__isnull=True, sponsored_companies__isnull=True
            )
        )
        if not ignore_dates:
            non_customer = non_customer.filter(start_filter, end_filter, is_active=True)
        non_customer = list(non_customer.values_list("id", flat=True))

        qs = self.filter()

        if company.is_customer:
            from axis.relationship.models import Relationship

            comps = Relationship.objects.get_reversed_companies(company)

            # comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
            # # Who do I have a relationship with
            # my_rels = company.relationships.get_companies(ids_only=True)
            # # The intersection of these is what matters..
            # ints = set(my_rels).intersection(set(comps))

            active = self.filter(owner__in=comps.filter(is_eep_sponsor=True, is_customer=True))
            if not ignore_dates:
                active = active.filter(start_filter, end_filter, is_active=True)
            active = list(active.values_list("id", flat=True))

            me = self.filter(owner=company).values_list("id", flat=True)
            qs = qs.filter(id__in=public + active + non_customer + list(me)).filter(**kwargs)
        else:
            sponsor_cos = company.sponsors.filter(is_eep_sponsor=True)
            sponsors = self.filter(owner__in=sponsor_cos)
            if not ignore_dates:
                sponsors = sponsors.filter(start_filter, end_filter, is_active=True)

            sponsors = list(sponsors.values_list("id", flat=True))
            qs = qs.filter(id__in=public + sponsors + non_customer).filter(**kwargs)

        # Add programs exposed via Association sharing
        shared_slugs = company.associations.eepprogramhomestatusassociation.values_list(
            "eepprogramhomestatus__eep_program__slug", flat=True
        ).distinct()
        qs |= self.filter(slug__in=list(shared_slugs))

        # Earth Advantage Certified Home is a private Program offered by NEEA
        # to Earth Advantage (Rater)
        # We keep is_public=False so it doesn't show up for anyone, ever.
        # Then explicitly add it to the queryset for NEEA and EA.
        # Supers can see it because we bypass all this filtering in filter_by_user
        if company.slug in ["neea", "earth-advantage-institute"]:
            qs |= self.filter(slug="earth-advantage-certified-home")

        # always filter viewable by
        # Remove items the company doesn't own AND has restrictions AND
        # they fall into those restrictions
        query = Q(
            ~Q(owner=company)
            & Q(viewable_by_company_type__isnull=False)
            & ~Q(viewable_by_company_type__contains=company.company_type)
        )
        return qs.exclude(query).distinct()

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user
        :param kwargs: Any other filtering
        :param user: User object
        """
        if user.is_superuser:
            if kwargs.get("ignore_dates"):
                kwargs.pop("ignore_dates")
            if kwargs.get("visible_for_use"):
                kwargs.pop("visible_for_use")
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_by_collection_support(self):
        """Filter programs with the collection_request flag false"""
        return self.filter(collection_request__isnull=False)

    def filter_active_for_home_status_creation_by_user(self, user, *args, **kwargs):
        """
        Convenience method for getting Company determined list of Programs when creating
        a Home Status.
        Regular Programs Company has access to, subtract Programs Company has chosen to
        ignore through the Company Detail page's Description/Misc tab.
        Args and Kwargs are passed through to filter_by_company, because there are some specific
         kwargs that cannot be passed to the .filter() method.
        """
        if user.is_superuser:
            return self.filter_by_user(user, **kwargs)

        # opt in AND company in list
        opt_in_query = Q(opt_in=True, opt_in_out_list=user.company)
        # opt out and in not in list
        opt_out_query = Q(opt_in=False) & ~Q(opt_in_out_list=user.company)

        # Closed filter
        close_filter = Q(
            Q(program_close_date__isnull=True)
            | Q(program_close_date__gte=datetime.datetime.today())
        )

        return (
            self.filter_by_user(user, **kwargs)
            .filter(opt_in_query | opt_out_query)
            .filter(close_filter)
        )

    def filter_questions(self, eep_program):
        """
        Grabs all checklists and returns them as a dictionary
        :param eep_program:
        :return: dict with questions
        """
        checklist_list = eep_program.required_checklists.all()
        question_dict = {}
        for checklist in checklist_list:
            for question in checklist.questions.all():
                question_dict[question.id] = question
        return question_dict

    def verify_for_company(
        self,
        name=None,
        company=None,
        subdivision=None,  # noqa: MC0001
        is_test_home=None,
        ignore_missing=False,
        log=None,
    ):  # noqa: MC0001
        """Validate the Program and it's requirements"""
        # The ``is_test_home`` flag is forwarded from the bulk uploader if the row for which
        # verification is performed appeared to be from a sampled scenario.  None indicates no such
        # sampling, and True/False reflects the type of home is doing the verification.

        from axis.subdivision.models import EEPProgramSubdivisionStatus
        from axis.company.models import COMPANY_MODELS
        from axis.subdivision.models import Subdivision

        log = log if log else logging.getLogger(__name__)

        assert isinstance(company, COMPANY_MODELS), "Company must be of type Company"
        assert isinstance(
            subdivision, (type(None), Subdivision)
        ), "If specified subdivision must of type Subdivision"

        objects, eep_program = [], None

        if isinstance(name, str):
            name = name.strip()

        if name is None:
            if ignore_missing:
                return None
            log.error(strings.MISSING_PROGRAM)
            return None
        elif represents_integer(name):
            try:
                eep_program = self.filter_by_company(company).get(id=int(name))
            except ObjectDoesNotExist:
                log.error(strings.UNKNOWN_PROGRAM_BY_ID.format(id=name))
        else:
            objects = self.filter_by_company(company=company)
            objects = objects.filter(name__iexact=name)
            if not objects.count():
                available = self.filter(name__iexact=name)
                if available.count() == 1:
                    log.error(
                        strings.PROGRAM_EXISTS_NO_RELATION.format(
                            program=name, owner=available[0].owner
                        )
                    )
                else:
                    if not ignore_missing:
                        log.error(strings.UNKNOWN_PROGRAM.format(program=name))
            elif objects.count() > 1:
                log.error(strings.MULTIPLE_PROGRAMS_FOUND.format(program=name))
            else:
                eep_program = objects[0]

        if not eep_program:
            return

        errors = False
        if subdivision and eep_program:
            comp_eep = EEPProgramSubdivisionStatus.objects.filter(
                eep_program=eep_program, subdivision=subdivision
            )
            comp_eep = comp_eep.exclude(company=company).distinct()
            if comp_eep.count():
                comps = ", ".join([x.company.name for x in comp_eep.all()])
                _url = reverse("subdivision:view", kwargs={"pk": subdivision.id})
                log.warning(
                    strings.PROGRAM_ALREADY_IN_USE.format(
                        program=eep_program, company=comps, url=_url, subdivision=subdivision
                    )
                )
                errors = True

        _url = reverse("eep_program:view", kwargs={"pk": eep_program.id})
        if (is_test_home is not None) and eep_program and not eep_program.allow_sampling:
            log.error(strings.PROGRAM_DISALLOW_SAMPLING.format(program=eep_program, url=_url))
            errors = True
        if not errors:
            log.debug(strings.FOUND_PROGRAM.format(url=_url, program=eep_program))
        return eep_program

    def filter_for_APS(self, user, meterset_date=None):
        """I'm still trying to figure out what's this for"""
        return self.filter_active_for_home_status_creation_by_user(user=user)
