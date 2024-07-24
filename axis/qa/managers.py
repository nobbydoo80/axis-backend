"""managers.py: Django qa"""

__author__ = "Steven Klass"
__date__ = "12/20/13 6:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
from collections import defaultdict, Counter
from datetime import timedelta

from django.apps import apps
from django.db import models
from django.db.models import Q, When, Case, F, Subquery, Value, OuterRef, IntegerField
from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django.utils import timezone

log = logging.getLogger(__name__)


class QARequirementQuerySet(QuerySet):
    def filter_by_company(self, company, company_hints=None, **kwargs):
        """Filters Stats By a Company"""

        if company.company_type == "provider":
            from axis.relationship.models import Relationship

            my_rels = (
                company.relationships.get_companies()
                .filter(company_type="qa")
                .values_list("id", flat=True)
            )
            company_ids = list(my_rels) + [company.id]
            queryset = self.filter(qa_company__id__in=company_ids, **kwargs)
        else:
            queryset = self.filter(qa_company=company, **kwargs)

        if company_hints:
            self.filter_for_company_hints(*company_hints)

        return queryset

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            kwargs.pop("company_hints", None)
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_for_company_hints(self, *company_hints):
        # NOTE: Use the company_hints list param to require that at least one company reference is
        # listed in ``required_companies`` on the QARequirement instance.
        # Querying without hints may include QARequirements which demand certain companies, so don't
        # omit hints in contexts where those demands must be met for data integrity.
        #
        # Example of when to include hints: QARequirement picker for a specific home
        # Example of when NOT to include hints: A list view of qastatuses where coming up with
        #                                       hints would only end up excluding items from the
        #                                       base queryset.

        if company_hints:
            return self.filter(Q(required_companies=None) | Q(required_companies__in=company_hints))
        return self.filter()

    def filter_for_home_status(self, home_status, **kwargs):
        """
        Filters Requirements By a Home Status
        Returns QARequirements by companies that have mutual relationships to the owner of the Home status.
        """
        from axis.relationship.models import Relationship

        company = home_status.company
        eep_program = home_status.eep_program

        comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
        if company.id in comps:
            comps = [c for c in comps if c != company.id]
        rels = company.relationships.get_companies(ids_only=True)
        _intersecting = set(rels).intersection(set(comps))

        # And intersecting must be actually attached to the home..
        _attached_companies = list(home_status.home.relationships.values_list("company", flat=True))

        intersecting = list(_intersecting.intersection(set(_attached_companies)))
        return self.filter(qa_company_id__in=intersecting, eep_program=eep_program).filter(**kwargs)

    def filter_for_add(self, content_object, user):
        from axis.home.models import Home
        from axis.subdivision.models import Subdivision

        if isinstance(content_object, Home) and content_object.pk:
            return self.filter_for_add_on_home(content_object, user)
        elif isinstance(content_object, Subdivision) and content_object.pk:
            return self.filter_for_add_on_subdivision(content_object, user)
        raise ValueError(
            "Unhandled model class %r for QARequirementQuerySet.filter_for_add()"
            % (content_object.__class__,)
        )

    def filter_for_add_on_home(self, home, user=None):
        """
        :param home: axis.home.models.Home
        :param company: axis.company.models.Company
        :return: QuerySet

        This returns any QA which could be added for a company
        """
        existing = home.homestatuses.values_list("qastatus__requirement", "eep_program")
        existing_requirements = [x[0] for x in existing if x[0] is not None]
        existing_eep_programs = [x[1] for x in existing]
        company_hints = home.relationships.all().get_orgs(ids_only=True)
        if user:
            available = self.filter_by_user(user, company_hints=company_hints)

            if user.is_customer_hirl_company_member():
                available = available.filter(
                    type__in=[
                        self.model.ROUGH_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
                        self.model.FINAL_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
                        self.model.DESKTOP_AUDIT_REQUIREMENT_TYPE,
                    ]
                )
        else:
            # Without a user, all QARequirements regrardless of company will come through.
            available = self.filter_for_company_hints(*company_hints)

        return available.filter(eep_program__id__in=existing_eep_programs).exclude(
            id__in=existing_requirements
        )

    def filter_for_add_on_subdivision(self, subdivision, user):
        """
        This returns any QA which could be added for a company
        """

        existing_requirements = list(
            subdivision.qastatus_set.filter(requirement__isnull=False).values_list(
                "requirement", flat=True
            )
        )
        existing_eep_programs = list(
            subdivision.home_set.values_list("homestatuses__eep_program", flat=True)
        )
        company_hints = subdivision.relationships.all().get_companies(ids_only=True)
        available = self.filter_by_user(
            user, eep_program__id__in=existing_eep_programs, company_hints=company_hints
        )
        return available.exclude(id__in=existing_requirements, type="field")


class QAStatusQuerySet(models.QuerySet):
    def filter_by_company(self, company, **kwargs):
        """Filters Stats By a Company"""
        from axis.relationship.models import Relationship

        comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
        if company.id in comps:
            comps = [c for c in comps if c != company.id]
        rels = company.relationships.get_companies(ids_only=True)
        intersecting = list(set(rels).intersection(set(comps)))

        if company.company_type in ["rater"]:
            intersecting += [company.id]

        program_owner_q = Q(home_status__eep_program__owner__in=intersecting)

        # FIXME: Temporary until we talk to NEEA to make this available for all EEPs.  ETO was the
        # one who asked for it, and we'll push it out to everyone eventually but we're playing it
        # slow for a few days.
        if company.slug == "eto":
            program_owner_q |= Q(home_status__eep_program__owner=company)

        conditions_q = (
            # QA owner is company
            Q(owner=company)
            |
            # Object owner is mutually related company
            (Q(home_status__company__in=intersecting) & program_owner_q)
            |
            # If the company is a provider and happens to be doing the rating this is cool.
            Q(
                home_status__company=company.id,
                home_status__company__company_type="provider",
            )
            |
            # Subdivision is defined (?)
            # FIXME: Document why this condition invalidates relationship logic
            Q(subdivision__isnull=False)
        )

        return self.filter(conditions_q, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def annotate_last_state_cycle_time_duration(self):
        transition_history_model = apps.get_model("qa", "qastatusstatelog")
        transition_state_start_time = (
            transition_history_model.objects.filter(on=OuterRef("pk"))
            .order_by("-start_time")
            .values("start_time")
        )
        return self.annotate(
            _state_transition_time_diff=timezone.now() - Subquery(transition_state_start_time[:1]),
            state_cycle_time_duration=Case(
                When(
                    _state_transition_time_diff__isnull=False,
                    then=F("_state_transition_time_diff"),
                ),
                default=timezone.now() - F("created_on"),
            ),
        )

    def annotate_customer_hirl_verifier(self):
        """
        Annotate verifier_id and verifier_name fields to queryset
        :return: queryset
        """
        from axis.qa.models import QARequirement

        return self.select_related(
            "requirement",
            "home_status__customer_hirl_rough_verifier",
            "home_status__customer_hirl_final_verifier",
        ).annotate(
            verifier_id=Case(
                When(
                    Q(requirement__type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE)
                    | Q(requirement__type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE),
                    then=F("home_status__customer_hirl_rough_verifier"),
                ),
                When(
                    requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                    then=F("home_status__customer_hirl_final_verifier"),
                ),
                default=None,
                output_field=IntegerField(),
            ),
            verifier_name=Case(
                When(
                    Q(requirement__type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE)
                    | Q(requirement__type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE),
                    then=Concat(
                        F("home_status__customer_hirl_rough_verifier__first_name"),
                        Value(" "),
                        F("home_status__customer_hirl_rough_verifier__last_name"),
                    ),
                ),
                When(
                    requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                    then=Concat(
                        F("home_status__customer_hirl_final_verifier__first_name"),
                        Value(" "),
                        F("home_status__customer_hirl_final_verifier__last_name"),
                    ),
                ),
                default=None,
            ),
        )


class QAStatusManager(models.Manager):
    def get_queryset(self):
        return QAStatusQuerySet(self.model, using=self._db)

    def filter_by_company(self, company, **kwargs):
        return self.get_queryset().filter_by_company(company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        return self.get_queryset().filter_by_user(user, **kwargs)

    def get_qa_metrics_for_home_statuses(self, home_status_ids):
        state_choices = dict(self.model.get_state_choices())

        lookup_fields = [
            "home_status",
            "state_history__from_state",
            "state_history__to_state",
            "state_history__start_time",
            "state_history__user_id",
            "requirement__type",
        ]
        qas = self.filter(home_status_id__in=home_status_ids)

        storage = defaultdict(
            lambda: {
                "transitions": defaultdict(list),
                "counts": defaultdict(Counter),
                "durations": defaultdict(lambda: defaultdict(timedelta)),
                "to_states": set(),
                "qa_types": set(),
            }
        )
        to_states = set()
        transitions = set()
        qa_types = set()
        end_times = {}

        current_home_status, end_time = None, None

        state_log = qas.values_list(*lookup_fields).order_by(
            "home_status_id", "-state_history__start_time"
        )
        for (
            home_status_id,
            from_state,
            to_state,
            start_time,
            user,
            qa_type,
        ) in state_log:
            # Fetch the last end time of this home statuses requiremtn_type
            end_time = end_times.get((home_status_id, qa_type), False)

            # There's no transitions but, there is a home status, so we get a blank tuple.
            if not all([from_state, to_state, start_time]):
                continue

            # Do the math, clean the string
            duration = (end_time - start_time) if end_time else timedelta()
            transition = "{} to {}".format(from_state, to_state)

            # Add to count
            storage[home_status_id]["counts"][to_state][qa_type] += 1
            storage[home_status_id]["counts"][qa_type][to_state] += 1
            if duration:
                storage[home_status_id]["durations"][to_state][qa_type] += duration
                storage[home_status_id]["durations"][qa_type][to_state] += duration

            storage[home_status_id]["transitions"][qa_type].append(
                (
                    home_status_id,
                    start_time,
                    end_time,
                    duration,
                    from_state,
                    to_state,
                    transition,
                )
            )

            to_states.add((to_state, state_choices[to_state]))
            storage[home_status_id]["to_states"].add((to_state, state_choices[to_state]))
            transitions.add(transition)
            qa_types.add(qa_type)
            storage[home_status_id]["qa_types"].add(qa_type)

            end_times[(home_status_id, qa_type)] = start_time

        storage = dict(storage)
        storage["to_states"] = to_states
        storage["transitions"] = transitions
        storage["qa_types"] = qa_types

        return storage


class ObservationTypeManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        from axis.relationship.models import Relationship

        comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
        if company.id in comps:
            comps = [c for c in comps if c != company.id]
        rels = company.relationships.get_companies(ids_only=True)
        intersecting = list(set(rels).intersection(set(comps)))

        if company.company_type in ["qa", "rater", "provider"]:
            intersecting += [company.id]

        return self.filter(company__in=intersecting, **kwargs)

    def filter_by_user(self, user, **kwargs):
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class ObservationManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        homestatuses = company.eepprogramhomestatus_set.all()
        # subdivisions = ?
        q = Q(qa_status__owner=company) | (
            Q(qa_status__home_status__in=homestatuses)  # | \
            # Q(qa_status__subdivision__in=subdivisions)
        )
        return self.filter(q, **kwargs)

    def filter_by_user(self, user, **kwargs):
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)
