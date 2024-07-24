# TODO: skip for now, this file has
#  too many warnings that require refactoring not only fixes in Pylint
# pylint: disable-all
"""api.py: Django qa"""


import logging
import operator
from copy import deepcopy
from collections import OrderedDict
from datetime import timedelta, datetime, timezone

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.core.views.landing import DashboardMetricsControlsMixin
from axis.examine.api import ExamineViewSetAPIMixin
from axis.home.models import EEPProgramHomeStatus, Home
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.scheduling.models import TaskType, Task
from axis.subdivision.models import Subdivision
from .models import QAStatus, QANote, QARequirement, ObservationType, Observation
from .serializers import (
    QANoteSerializer,
    QAStatusSerializer,
    QARequirementSerializer,
    ObservationTypeSerializer,
)
from .utils import (
    get_success_rates_by_program,
    get_success_rates_by_rater_company,
    get_success_rates_by_rater_user,
    get_certification_metrics_by_program,
    get_program_summaries,
)

__author__ = "Steven Klass"
__date__ = "12/26/13 8:15 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..customer_neea.utils import NEEA_BPA_SLUGS

log = logging.getLogger(__name__)
User = get_user_model()


def percent(amount, out_of):
    if not out_of:
        pct = 0
    else:
        pct = amount / out_of
    return "{:.2f}%".format(pct * 100)


def get_user_full_name_getter(user_ids, default):
    users_dict = {x.id: x.get_full_name() for x in User.objects.filter(id__in=user_ids)}

    def name_getter(user_id):
        try:
            return users_dict[user_id]
        except KeyError:
            return default

    return name_getter


def get_utc_datetime_from_date(date_obj):
    return datetime(date_obj.year, date_obj.month, date_obj.day, tzinfo=timezone.utc)


class QARequirementViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = QARequirement
    serializer_class = QARequirementSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from axis.qa.views.examine import QARequirementExamineMachinery

        return QARequirementExamineMachinery


class QAStatusViewSet(DashboardMetricsControlsMixin, ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = QAStatus
    queryset = model.objects.all()
    serializer_class = QAStatusSerializer

    def filter_queryset(self, queryset):
        filters = self.request.query_params.dict()
        if "home" in filters:
            home = Home.objects.get(id=filters.pop("home"))
            filters["home_status__home"] = home
        elif "subdivision" in filters:
            subdivision = Subdivision.objects.get(id=filters.pop("subdivision"))
            filters["subdivision"] = subdivision
        filters.pop("machinery", None)
        return queryset.filter(**filters).order_by("created_on")

    def get_examine_machinery_classes(self):
        from axis.qa.views.examine import QAStatusExamineMachinery

        return {
            None: QAStatusExamineMachinery,
            "QAStatusExamineMachinery": QAStatusExamineMachinery,
        }

    def list(self, request, *args, **kwargs):
        if "full_status" in self.request.path:
            return self.full_status(request, *args, **kwargs)
        return super(QAStatusViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        from axis.home.models import EEPProgramHomeStatus

        requirement_id = request.data.get("requirement")
        if not requirement_id:
            return Response({"message": "requirement arg is required"}, status=403)
        if "home" in request.data:
            home_id = request.data["home"]
            subdivision_id = None
        elif "subdivision" in request.data:
            home_id = None
            subdivision_id = request.data["subdivision"]
        else:
            return Response({"message": "Need value for one of: home, subdivision"}, status=403)

        # FIXME: Potential required_companies issue?  Unclear who the filter_by_company() target
        # should be.
        requirement = QARequirement.objects.get(id=requirement_id)

        if home_id:
            request.data["home_status"] = EEPProgramHomeStatus.objects.get(
                eep_program__qarequirement=requirement_id, home_id=home_id
            ).id
        elif subdivision_id:
            request.data["subdivision"] = (
                Subdivision.objects.filter(
                    id=subdivision_id, home__homestatuses__eep_program__qarequirement=requirement_id
                )
                .distinct()
                .get()
                .id
            )
        request.data["owner"] = requirement.qa_company.id

        return super(QAStatusViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=["POST"])
    def customer_hirl_sync_batch(self, request, *args, **kwargs):
        parent_qa = self.get_object()
        customer_hirl_project = parent_qa.home_status.customer_hirl_project

        if parent_qa.requirement.type == QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE:
            child_projects = customer_hirl_project.vr_batch_submission_rough_childrens.all()
        else:
            child_projects = customer_hirl_project.vr_batch_submission_final_childrens.all()

        child_qas = QAStatus.objects.filter(
            home_status__customer_hirl_project__in=child_projects,
            requirement__type=parent_qa.requirement.type,
        )
        fields_to_copy = [
            "result",
            "state",
            "has_observations",
            "has_failed",
            "qa_designee",
            "hirl_verifier_points_reported",
            "hirl_verifier_points_awarded",
            "hirl_certification_level_awarded",
            "hirl_commercial_space_confirmed",
            "hirl_reviewer_wri_value_awarded",
            "hirl_water_sense_confirmed",
        ]

        hirl_badges_awarded = parent_qa.hirl_badges_awarded.all()
        for child_qa in child_qas:
            child_qa.hirl_badges_awarded.clear()
            for field_name in fields_to_copy:
                setattr(child_qa, field_name, getattr(parent_qa, field_name))
            child_qa.save()
            child_qa.hirl_badges_awarded.add(*hirl_badges_awarded)
            child_qa.save()

            # sync inspection grades
            child_qa.inspectiongrade_set.all().delete()
            for inspection_grade in parent_qa.inspectiongrade_set.all():
                inspection_grade.pk = None
                inspection_grade.qa_status = child_qa
                inspection_grade.save()

            # sync qa notes
            child_qa.qanote_set.all().delete()
            for qa_note in parent_qa.qanote_set.all():
                qa_note_new = deepcopy(qa_note)
                qa_note_new.pk = None
                qa_note_new.qa_status = child_qa
                qa_note_new.save()

                # sync qa observation
                for correction_type in qa_note.observation_set.all():
                    correction_type.pk = None
                    correction_type.qa_status = qa_note_new.qa_status
                    correction_type.qa_note = qa_note_new
                    correction_type.save()

            # sync documents
            child_qa.customer_documents.all().delete()
            for document in parent_qa.customer_documents.all():
                document.pk = None
                document.content_object = child_qa
                document.save()

        return Response("ok")

    @action(detail=True)
    def full_status(self, request, pk=None, *args, **kwargs):
        if pk:
            obj = self.get_object()
            return Response(obj.get_full_status(user=self.request.user))

        objects = self.filter_queryset(self.get_queryset())
        id_list = kwargs.get("pk_list", "").split(";")
        # FIXME: do we need to do an individual lookup for each to make sure it exists?
        objects = objects.filter(id__in=id_list)

        data = {"object_list": {o.pk: o.get_full_status(user=self.request.user) for o in objects}}

        return Response(data)

    @action(detail=False)
    def rater_file_metrics(self, request, *args, **kwargs):
        controls = self.get_filter_controls(request, use_quarters=True)
        home_stats_qs = self._get_home_stats_queryset(request, controls).exclude(
            eep_program__slug__contains="eto"
        )
        qa_stats_qs = self._get_qa_status_queryset(request, controls)
        qa_stats_qs = qa_stats_qs.filter(requirement__type="file")
        qa_stats_qs = qa_stats_qs.exclude(requirement__eep_program__slug__contains="eto")

        pending_qa_homes_qs = self._get_home_stats_queryset_base(request)
        pending_qa_homes_qs = pending_qa_homes_qs.exclude(eep_program__slug__contains="eto")

        data = self.get_rater_file_metrics(
            home_stats_qs, qa_stats_qs, controls, pending_qa_homes_qs
        )
        return self.make_metrics_response(data, controls)

    @action(detail=False)
    def rater_field_metrics(self, request, *args, **kwargs):
        controls = self.get_filter_controls(request, use_quarters=True)
        home_stats_qs = self._get_home_stats_queryset(request, controls)
        home_stats_qs = home_stats_qs.exclude(eep_program__slug__contains="eto")

        qa_stats_qs = self._get_qa_status_queryset(request, controls)
        qa_stats_qs = qa_stats_qs.filter(requirement__type="field")
        qa_stats_qs = qa_stats_qs.exclude(requirement__eep_program__slug__contains="eto")

        data = self.get_rater_field_metrics(home_stats_qs, qa_stats_qs, controls)

        return self.make_metrics_response(data, controls)

    @action(detail=False)
    def eto_rater_file_metrics(self, request, *args, **kwargs):
        controls = self.get_filter_controls(request, use_quarters=True)
        home_stats_qs = self._get_home_stats_queryset(request, controls)
        home_stats_qs = home_stats_qs.filter(eep_program__slug__contains="eto")

        qa_stats_qs = self._get_qa_status_queryset(request, controls)
        qa_stats_qs = qa_stats_qs.filter(
            requirement__type="file", requirement__eep_program__slug__contains="eto"
        )

        pending_qa_homes_qs = self._get_home_stats_queryset_base(request)
        pending_qa_homes_qs = pending_qa_homes_qs.filter(eep_program__slug__contains="eto")

        data = self.get_rater_file_metrics(
            home_stats_qs, qa_stats_qs, controls, pending_qa_homes_qs, eto_homes_count=True
        )

        return self.make_metrics_response(data, controls)

    @action(detail=False)
    def eto_rater_field_metrics(self, request, *args, **kwargs):
        controls = self.get_filter_controls(request, use_quarters=True)
        home_stats_qs = self._get_home_stats_queryset(request, controls)
        home_stats_qs = home_stats_qs.filter(eep_program__slug__contains="eto")
        qa_stats_qs = self._get_qa_status_queryset(request, controls)
        qa_stats_qs = qa_stats_qs.filter(
            requirement__type="field", requirement__eep_program__slug__contains="eto"
        )

        data = self.get_rater_field_metrics(
            home_stats_qs, qa_stats_qs, controls, eto_homes_count=True
        )

        return self.make_metrics_response(data, controls)

    @action(detail=False)
    def neea_rater_file_metrics(self, request, *args, **kwargs):
        program_slugs = NEEA_BPA_SLUGS

        controls = self.get_filter_controls(request, use_quarters=True)
        base_qs = self._get_home_stats_queryset_base(request)
        base_qs = base_qs.filter(eep_program__slug__in=program_slugs)

        home_stats_qs = self._get_home_stats_queryset(request, controls)
        home_stats_qs = home_stats_qs.filter(eep_program__slug__in=program_slugs)

        qa_stats_qs = self._get_qa_status_queryset(request, controls)
        qa_stats_qs = qa_stats_qs.filter(
            requirement__type="file", requirement__eep_program__slug__in=program_slugs
        )
        # Amend controls to show only relevant utility options for the base queryset
        # This temporarily strips the 'utility' filter out of the controls so that we see the full
        # set of data and don't get limited to a single company returned if that was the one
        # specified.
        companies_info = (
            self._get_home_stats_queryset(
                request,
                controls={
                    k: (v if k not in ["utility", "us_state"] else "") for k, v in controls.items()
                },
            )
            .filter(eep_program__slug__in=program_slugs)
            .values_list(
                "incentivepaymentstatus__owner__id",
                "incentivepaymentstatus__owner__name",
                "incentivepaymentstatus__owner__company_type",
            )
            .order_by("incentivepaymentstatus__owner__name")
            .distinct()
        )
        utility_choices = list(o[:2] for o in companies_info if o[-1] == "utility")

        data = self.get_rater_file_metrics(home_stats_qs, qa_stats_qs, controls, base_qs)
        return self.make_metrics_response(
            data,
            controls,
            {
                "utility": utility_choices,
            },
        )

    @action(detail=False)
    def neea_rater_field_metrics(self, request, *args, **kwargs):
        program_slugs = NEEA_BPA_SLUGS

        controls = self.get_filter_controls(request, use_quarters=True)

        home_stats_qs = self._get_home_stats_queryset(request, controls)
        home_stats_qs = home_stats_qs.filter(eep_program__slug__in=program_slugs)

        qa_stats_qs = self._get_qa_status_queryset(request, controls)
        qa_stats_qs = qa_stats_qs.filter(
            requirement__type="field", requirement__eep_program__slug__in=program_slugs
        )
        # Amend controls to show only relevant utility options for the base queryset
        # This temporarily strips the 'utility' filter out of the controls so that we see the full
        # set of data and don't get limited to a single company returned if that was the one
        # specified.
        companies_info = (
            self._get_home_stats_queryset(
                request,
                controls={
                    k: (v if k not in ["utility", "us_state"] else "") for k, v in controls.items()
                },
            )
            .filter(eep_program__slug__in=program_slugs)
            .values_list(
                "incentivepaymentstatus__owner__id",
                "incentivepaymentstatus__owner__name",
                "incentivepaymentstatus__owner__company_type",
            )
            .order_by("incentivepaymentstatus__owner__name")
            .distinct()
        )
        utility_choices = list(o[:2] for o in companies_info if o[-1] == "utility")

        data = self.get_rater_field_metrics(home_stats_qs, qa_stats_qs, controls)
        return self.make_metrics_response(
            data,
            controls,
            {
                "utility": utility_choices,
            },
        )

    @action(detail=False)
    def neea_utility_certified_metrics(self, request, *args, **kwargs):
        program_slugs = NEEA_BPA_SLUGS

        controls = self.get_filter_controls(request)

        def _queryset(queryset_getter, prefix, exclude_controls=[]):
            """Applies current controls and program filters to a base queryset."""
            _controls = {k: (v if k not in exclude_controls else "") for k, v in controls.items()}
            return queryset_getter(request, _controls).filter(
                **{
                    prefix + "eep_program__slug__in": program_slugs,
                }
            )

        def _homestatus_queryset(**kwargs):
            return _queryset(self._get_home_stats_queryset, prefix="", **kwargs)

        def _incentive_queryset(**kwargs):
            return _queryset(self._get_incentive_status_queryset, prefix="home_status__", **kwargs)

        home_stats_qs = _homestatus_queryset()
        incentive_stats_qs = _incentive_queryset()

        # Amend controls to show only relevant utility options for the base queryset
        # This temporarily strips the 'utility' filter out of the controls so that we see the full
        # set of data and don't get limited to a single company returned if that was the one
        # specified.
        companies_info = (
            _incentive_queryset(exclude_controls=["utility", "us_state"])
            .values_list(
                "owner__id",
                "owner__name",
                "owner__company_type",
            )
            .order_by("owner__name")
            .distinct()
        )
        utility_choices = list(o[:2] for o in companies_info if o[-1] == "utility")

        group_by = "eep_program"
        _group_by_id = group_by + "__id"
        _group_by_name = group_by + "__name"

        def _group(queryset):
            # group_by_prefix = 'home_status__'
            group_by_prefix = ""
            group_by_id = group_by_prefix + _group_by_id
            group_by_name = group_by_prefix + _group_by_name
            return queryset.values(group_by_id, group_by_name).annotate(n=Count(group_by_id))

        def _filter(queryset, prefix, group_id):
            """Filters the queryset via the current grouping field."""
            group_by_id = prefix + _group_by_id
            group_by_name = prefix + _group_by_name
            return queryset.filter(**{group_by_id: group_id})

        data = list(_group(home_stats_qs))
        for info in data:
            # group_by_prefix = 'home_status__'  # Relative to incentivepaymentstatus
            group_by_prefix = ""
            group_by_id = group_by_prefix + _group_by_id
            group_by_name = group_by_prefix + _group_by_name

            # Meta
            info.update(
                {
                    "grouped_id": info[group_by_id],
                    "grouped_name": info[group_by_name],
                }
            )

            # Incentive bulk stats
            row_incentive_queryset = _filter(incentive_stats_qs, "home_status__", info[group_by_id])
            info["stats"] = self.get_neea_v2_incentive_metrics_from_queryset(
                row_incentive_queryset, controls
            )

            # Home bulk stats
            row_homestatus_queryset = _filter(home_stats_qs, "", info[group_by_id])

            # Sum pre-rounded numbers.  Need newer version of Django to use the Round() db function
            savings_kwh = row_homestatus_queryset.exclude(
                standardprotocolcalculator=None
            ).values_list("standardprotocolcalculator__total_kwh_savings", flat=True)
            savings_therms = row_homestatus_queryset.exclude(
                standardprotocolcalculator=None
            ).values_list("standardprotocolcalculator__total_therm_savings", flat=True)

            info["stats"]["savings_kwh"] = sum(round(savings, 2) for savings in savings_kwh)
            info["stats"]["savings_therms"] = sum(round(savings, 2) for savings in savings_therms)

        return self.make_metrics_response(
            data,
            controls,
            {
                "utility": utility_choices,
            },
        )

    @action(detail=False)
    def program_metrics(self, request, *args, **kwargs):
        controls = self.get_filter_controls(request)

        user = request.user
        company = user.company
        has_neea_affliation = company.sponsors.filter(slug="neea").exists()

        date_range = [
            get_utc_datetime_from_date(controls["date_start"]),
            get_utc_datetime_from_date(controls["date_end"] + timedelta(days=1)),
        ]

        filter_kwargs = {
            "state": "complete",
            "certification_date__range": date_range,
        }
        if controls["us_state"]:
            filter_kwargs["home__city__county__state"] = controls["us_state"]

        def _get_program_queryset(controls):
            if company.company_type == "eep":
                program_queryset = EEPProgramHomeStatus.objects.filter(eep_program__owner=company)
            else:
                program_queryset = EEPProgramHomeStatus.objects.filter_by_user(user)
            return program_queryset.filter(**filter_kwargs)

        def _get_qa_queryset(controls):
            if company.company_type == "eep":
                qa_queryset = QAStatus.objects.filter(requirement__eep_program__owner=company)
            else:
                qa_queryset = QAStatus.objects.filter_by_user(user)
            return qa_queryset.filter(
                state_history__to_state__in=["in_progress", "correction_required", "complete"],
                state_history__start_time__range=date_range,
                home_status__id__in=list(program_queryset.values_list("id", flat=True)),
            ).distinct()

        def _queryset(queryset_getter, prefix, exclude_controls=[]):
            """Applies current controls and program filters to a base queryset."""
            _controls = {k: (v if k not in exclude_controls else "") for k, v in controls.items()}
            kwargs = {}
            if company.slug == "neea" or has_neea_affliation:
                kwargs[prefix + "eep_program__slug__in"] = NEEA_BPA_SLUGS
            return queryset_getter(_controls).filter(**kwargs)

        def _program_queryset(**kwargs):
            return _queryset(_get_program_queryset, "", **kwargs)

        def _qa_queryset(**kwargs):
            return _queryset(_get_qa_queryset, "requirement__", **kwargs)

        program_queryset = _program_queryset()
        qa_queryset = _qa_queryset()

        data = self.get_program_data(program_queryset, qa_queryset, company, request, controls)

        # Amend controls to show only relevant utility options for the base queryset
        # This temporarily strips the 'utility' filter out of the controls so that we see the full
        # set of data and don't get limited to a single company returned if that was the one
        # specified.
        companies_info = (
            _program_queryset(exclude_controls=["utility", "us_state"])
            .values_list(
                "company__id",
                "company__name",
                "company__company_type",
            )
            .order_by("company__name")
            .distinct()
        )
        utility_choices = list(o[:2] for o in companies_info if o[-1] == "utility")

        return self.make_metrics_response(
            data,
            controls,
            {
                "utility": utility_choices,
            },
        )

    def get_rater_file_metrics(
        self, home_stats_qs, qa_stats_qs, controls, pending_qa_homes_qs, eto_homes_count=False
    ):
        style = controls["style"]
        valid_styles = ["rater_of_record", "rater", "utility", "", None]
        if style not in valid_styles:
            raise ValueError("Metrics style must be one of %r" % valid_styles)

        if style in ["", None]:
            style = "rater_of_record"

        date_range = [
            get_utc_datetime_from_date(controls["date_start"]),
            get_utc_datetime_from_date(controls["date_end"]),
        ]

        data = []
        pending_qa_homes_qs = pending_qa_homes_qs.filter(
            state_history__to_state="qa_pending",
            state_history__start_time__range=date_range,
        )
        if controls["us_state"]:
            pending_qa_homes_qs = pending_qa_homes_qs.filter(
                home__state=controls["us_state"],
            )

        UNSET = "THIS IS AN UNSET  CONSTANT"

        def _filter(qs, value=UNSET, prefix=""):
            """Filters the given queryset with whichever query_key is active."""
            if prefix:
                prefix += "__"
            q = Q(**{(prefix + k): v for k, v in query_extra.items()})
            qs = qs.filter(q)
            if value is not UNSET:
                qs = qs.filter(**{prefix + query_key: value})
            return qs

        query_extra = {}
        query_key = None  # orm path from homestatus object to use for group-by
        values = None  # Each will be a row in the metrics table
        if style == "rater":
            query_key = "company"
            company_name_lookups = OrderedDict(
                home_stats_qs.values_list("company", "company__name").order_by("company__name")
            )
            values = list(company_name_lookups.keys())
            value_name_getter = lambda company_id: company_name_lookups[company_id]
        elif style == "utility":
            relevant_utility_company_ids = set(
                home_stats_qs.values_list("incentivepaymentstatus__owner", flat=True).distinct()
            )
            query_extra = {
                "home__relationships__utilitysettings__isnull": False,
                "home__relationships__company__company_type": "utility",
                "incentivepaymentstatus__owner__in": list(relevant_utility_company_ids),
            }
            query_key = "incentivepaymentstatus__owner"
            utility_name_lookups = OrderedDict(
                _filter(home_stats_qs)
                .values_list("incentivepaymentstatus__owner", "incentivepaymentstatus__owner__name")
                .order_by("incentivepaymentstatus__owner__name")
            )

            value_name_getter = lambda utility_id: utility_name_lookups[utility_id]
            values = set(utility_name_lookups.keys()) & relevant_utility_company_ids
            values = list(sorted(values, key=value_name_getter))
        elif style == "rater_of_record":
            query_key = "rater_of_record"

            values = (
                home_stats_qs.values_list("rater_of_record", flat=True)
                .order_by(
                    "rater_of_record__first_name",
                    "rater_of_record__last_name",
                    "rater_of_record__username",
                )
                .distinct()
            )

            values = list(filter(None, values))
            value_name_getter = get_user_full_name_getter(values, "No Rater of Record")

        for item_id in values:
            metrics_qa_qs = _filter(qa_stats_qs, prefix="home_status", value=item_id)
            homes_count = self._get_homes_count(
                _filter(home_stats_qs, value=item_id), eto_homes_count=eto_homes_count
            )
            metrics = self.get_qa_metrics_from_queryset(
                metrics_qa_qs, homes_count=homes_count, eto_homes_count=eto_homes_count
            )
            metrics.update(
                {
                    "grouped_id": item_id,
                    "grouped_name": value_name_getter(item_id),
                    "pending_qa_homes_count": _filter(pending_qa_homes_qs, value=item_id)
                    .distinct()
                    .count(),
                }
            )
            data.append(metrics)

        return data

    def get_rater_field_metrics(self, home_stats_qs, qa_stats_qs, controls, eto_homes_count=False):
        style = controls["style"]
        valid_styles = ["rater_of_record", "rater", "utility", "", None]
        if style not in valid_styles:
            raise ValueError("Metrics style must be one of %r" % valid_styles)

        if style in ["", None]:
            style = "rater_of_record"

        home_ct = ContentType.objects.get_for_model(Home)
        universal_task_types = TaskType.objects.filter(
            company=None, content_type=home_ct
        ).values_list("id", flat=True)

        UNSET = "THIS IS AN UNSET CONSTANT"

        def _filter(qs, value=UNSET, prefix=""):
            """Filters the given queryset with whichever query_key is active."""
            if prefix:
                prefix += "__"
            q = Q(**{(prefix + k): v for k, v in query_extra.items()})
            qs = qs.filter(q)
            if value is not UNSET:
                qs = qs.filter(**{prefix + query_key: value})
            return qs

        query_extra = {}
        query_key = None  # orm path from homestatus object to use for group-by
        values = None  # Each will be a row in the metrics table
        if style == "rater":
            query_key = "company"
            company_name_lookups = OrderedDict(
                home_stats_qs.values_list("company", "company__name").order_by("company__name")
            )
            values = list(company_name_lookups.keys())
            value_name_getter = lambda company_id: company_name_lookups[company_id]
        elif style == "utility":
            relevant_utility_company_ids = set(
                home_stats_qs.values_list("incentivepaymentstatus__owner", flat=True).distinct()
            )
            query_extra = {
                "home__relationships__utilitysettings__is_electric_utility": True,
                "home__relationships__company__company_type": "utility",
                "incentivepaymentstatus__owner__in": list(relevant_utility_company_ids),
            }
            query_key = "home__relationships__company"
            utility_name_lookups = OrderedDict(
                _filter(home_stats_qs)
                .values_list("incentivepaymentstatus__owner", "incentivepaymentstatus__owner__name")
                .order_by("incentivepaymentstatus__owner__name")
            )
            value_name_getter = lambda utility_id: utility_name_lookups[utility_id]
            values = set(utility_name_lookups.keys()) & relevant_utility_company_ids
            values = list(sorted(values, key=value_name_getter))
        elif style == "rater_of_record":
            query_key = "rater_of_record"
            values = list(
                filter(
                    None,
                    home_stats_qs.values_list("rater_of_record", flat=True)
                    .order_by(
                        "rater_of_record__first_name",
                        "rater_of_record__last_name",
                        "rater_of_record__username",
                    )
                    .distinct(),
                )
            )
            value_name_getter = get_user_full_name_getter(values, "No Rater of Record")

        data = []
        for item_id in values:
            base_homes = _filter(home_stats_qs, value=item_id)
            base_qa = _filter(qa_stats_qs, prefix="home_status", value=item_id)

            homes = set(base_homes.values_list("home", flat=True))
            tasks = Task.objects.filter_by_user(self.request.user).filter(
                status="completed",
                home__id__in=homes,
                task_type_id__in=list(universal_task_types),
            )

            homes_count = self._get_homes_count(base_homes, eto_homes_count=eto_homes_count)
            metrics = self.get_qa_metrics_from_queryset(
                base_qa, homes_count=homes_count, eto_homes_count=eto_homes_count
            )
            metrics.update(
                {
                    "grouped_id": item_id,
                    "grouped_name": value_name_getter(item_id),
                }
            )

            rfi = {}
            task_assignees_ids = list(
                filter(None, tasks.values_list("assignees", flat=True).distinct())
            )
            assignee_name_getter = get_user_full_name_getter(
                task_assignees_ids, "No Rating Field Inspector"
            )
            for assignee_id in task_assignees_ids:
                if item_id == assignee_id:
                    # ROR should not be listed under themselves
                    continue

                assignee_tasks = tasks.filter(assignees=assignee_id)
                assignee_tasks = assignee_tasks.values_list("object_id", flat=True)

                assignee_qa = base_qa.filter(home_status__home__id__in=list(assignee_tasks))
                assignee_name = assignee_name_getter(assignee_id)

                rfi[assignee_name] = self.get_qa_metrics_from_queryset(
                    assignee_qa,
                    homes_count=len(set(assignee_tasks)),
                    eto_homes_count=eto_homes_count,
                )

                rfi[assignee_name].update(
                    {"assignee_id": assignee_id, "assignee_name": assignee_name}
                )

            metrics.update({"rfi": rfi})
            data.append(metrics)

        return data

    def get_program_data(self, program_queryset, qa_queryset, company, request, controls):
        data = []
        for (
            program_id,
            program_name,
        ) in set(program_queryset.values_list("eep_program", "eep_program__name")):
            base = qa_queryset.filter(requirement__eep_program_id=program_id).distinct()
            file_qa = base.filter(requirement__type="file").distinct()
            field_qa = base.filter(requirement__type="field").distinct()
            file_first_time_success = file_qa.exclude(
                state_history__to_state="correction_required"
            ).distinct()
            field_first_time_success = field_qa.exclude(
                state_history__to_state="correction_required"
            ).distinct()

            file_qa_count = file_qa.count()
            field_qa_count = field_qa.count()
            file_first_time_count = file_first_time_success.count()
            field_first_time_count = field_first_time_success.count()

            home_count = len(
                set(
                    program_queryset.filter(eep_program_id=program_id).values_list(
                        "home", flat=True
                    )
                )
            )
            data.append(
                {
                    "eep_program_id": program_id,
                    "eep_program_name": program_name,
                    "total_count": home_count,
                    "file_qa_count": file_qa_count,
                    "file_qa_percentage": percent(file_qa_count, home_count),
                    "file_first_time_count": file_first_time_count,
                    "file_first_time_percentage": percent(file_first_time_count, file_qa_count),
                    "field_qa_count": field_qa_count,
                    "field_qa_percentage": percent(field_qa_count, home_count),
                    "field_first_time_count": field_first_time_count,
                    "field_first_time_percentage": percent(field_first_time_count, field_qa_count),
                }
            )

        return sorted(data, key=operator.itemgetter("eep_program_name"))

    @action(detail=False)
    def metrics(self, request, *args, **kwargs):
        # NOTE: this was designed to provide stats for File QA items, not Field QA.

        company = request.user.company
        controls = self.get_filter_controls(request)
        data = {
            "certifications_by_program": [],
            "success_by_program": [],
            "success_by_rater": [],
            "failures_by_type": [],
        }

        # Top-level Program stats
        if company.company_type == "eep":
            programs_qs = EEPProgramHomeStatus.objects.filter(eep_program__owner=company)
        else:
            programs_qs = EEPProgramHomeStatus.objects.filter_by_user(self.request.user)

        if controls["us_state"]:
            programs_qs = programs_qs.filter(home__state=controls["us_state"])

        qs = programs_qs.exclude(eep_program__is_qa_program=True).order_by("-eep_program__name")

        # Certifications
        program_metrics = []
        if company.company_type in ["eep", "utility"]:
            program_metrics = get_program_summaries(qs)
        elif company.company_type in ("provider", "rater", "qa"):
            qs = qs.filter(
                certification_date__range=[
                    controls["date_start"],
                    controls["date_end"] + timedelta(days=1),
                ]
            )
            program_metrics = get_certification_metrics_by_program(qs)

        data["program_metrics"] = sorted(
            program_metrics, key=operator.itemgetter("eep_program"), reverse=True
        )

        if company.company_type == "eep":
            success_queryset = QAStatus.objects.filter(
                requirement__eep_program__owner=self.request.company
            )
        else:
            success_queryset = QAStatus.objects.filter_by_user(self.request.user)

        if controls["us_state"]:
            success_queryset = success_queryset.filter(
                home_status__home__state=controls["us_state"]
            )

        utc_datetime_start = get_utc_datetime_from_date(controls["date_start"])
        utc_datetime_end = get_utc_datetime_from_date(controls["date_end"] + timedelta(days=1))
        success_queryset = success_queryset.filter(
            requirement__type="file",
            state_history__to_state__in=["in_progress", "correction_required", "complete"],
            state_history__start_time__gte=utc_datetime_start,
            state_history__start_time__lte=utc_datetime_end,
        )

        # distinct() in any queryset that turns things into a multi-value ValuesQuerySet is destined
        # to cause aneurysms and fail to have an impact on the queryset.
        # Re-fetch the queryset results based on unique ids so that we are not double counting
        # anything.
        id_list = set(success_queryset.values_list("id", flat=True))
        success_queryset = QAStatus.objects.filter(id__in=id_list)

        # Success by program
        by_program = get_success_rates_by_program(success_queryset)
        data["success_by_program"] = by_program

        # Success by rater
        by_rater_company = get_success_rates_by_rater_company(success_queryset)
        data["success_by_rater_company"] = by_rater_company
        by_rater_user = get_success_rates_by_rater_user(
            success_queryset.exclude(home_status__rater_of_record=None)
        )
        data["success_by_rater_user"] = by_rater_user

        # Failures by type
        qs = programs_qs.filter(qastatus__requirement__type="file").exclude(
            state__in=["complete", "abandoned"]
        )
        values_qs = (
            qs.values(
                "qastatus__observation__observation_type__id",
                "qastatus__observation__observation_type__name",
            )
            .annotate(n=Count("qastatus__observation__observation_type__name"))
            .filter(n__gt=0)
        )
        data["failures_by_type"] = list(
            {
                "type_id": d["qastatus__observation__observation_type__id"],
                "type": d["qastatus__observation__observation_type__name"],
                "n": d["n"],
            }
            for d in values_qs.order_by("-n")
        )

        return self.make_metrics_response(data, controls)

    def _get_homes_count(self, queryset, eto_homes_count=False):
        """
        Multiple Home Statuses on a home collapse to represent 1 home.
        Multiple ETO Home Statuses on a home represent themselves.
        """
        if eto_homes_count:
            return queryset.distinct().count()

        return queryset.values_list("home", flat=True).distinct().count()

    def _get_home_stats_queryset_base(self, request):
        if request.company.company_type == "eep":
            return EEPProgramHomeStatus.objects.filter(eep_program__owner=request.company)
        else:
            return EEPProgramHomeStatus.objects.filter_by_user(request.user)

    def _get_home_stats_queryset(self, request, controls):
        qs = self._get_home_stats_queryset_base(request)

        filter_kwargs = {
            "state": "complete",
            "certification_date__range": [
                controls["date_start"],
                controls["date_end"] + timedelta(days=1),
            ],
        }

        if controls["us_state"]:
            filter_kwargs["home__city__county__state"] = controls["us_state"]

        if controls["utility"]:
            filter_kwargs["home__relationships__company"] = controls["utility"]
            filter_kwargs["home__relationships__company__company_type"] = "utility"

        return qs.filter(**filter_kwargs)

    def _get_qa_status_queryset(self, request, controls):
        if request.user.company.company_type == "eep":
            qs = QAStatus.objects.filter(requirement__eep_program__owner=request.user.company)
        else:
            qs = QAStatus.objects.filter_by_user(request.user)

        filter_kwargs = {
            "home_status__certification_date__range": [
                controls["date_start"],
                controls["date_end"] + timedelta(days=1),
            ],
        }

        if controls["us_state"]:
            filter_kwargs["home_status__home__city__county__state"] = controls["us_state"]

        if controls["utility"]:
            filter_kwargs["home_status__home__relationships__company"] = controls["utility"]
            filter_kwargs["home_status__home__relationships__company__company_type"] = "utility"

        return qs.filter(**filter_kwargs)

    def _get_incentive_status_queryset(self, request, controls):
        if request.user.company.company_type == "eep":
            qs = IncentivePaymentStatus.objects.filter(
                home_status__eep_program__owner=request.user.company
            )
        else:
            qs = IncentivePaymentStatus.objects.filter_by_user(request.user)

        filter_kwargs = {
            "home_status__certification_date__range": [
                controls["date_start"],
                controls["date_end"] + timedelta(days=1),
            ],
        }

        if controls["us_state"]:
            filter_kwargs["home_status__home__city__county__state"] = controls["us_state"]

        if controls["utility"]:
            filter_kwargs["home_status__home__relationships__company"] = controls["utility"]
            filter_kwargs["home_status__home__relationships__company__company_type"] = "utility"

        return qs.filter(**filter_kwargs)

    def get_qa_metrics_from_queryset(self, queryset, homes_count=None, eto_homes_count=False):
        """
        :param queryset: QAStatus queryset
        :param homes_count: ???
        :param eto_homes_count: ???
        :returns: dict:
        """
        if homes_count is None:
            homes_count = self._get_homes_count(queryset, eto_homes_count=eto_homes_count)

        completed = queryset.filter(state="complete").distinct()
        required_corrections = (
            completed.filter(state_history__to_state="correction_required").distinct().count()
        )

        first_time = completed.count() - required_corrections
        completed_total = first_time + required_corrections

        return {
            "homes_count": homes_count,
            "in_progress_count": queryset.exclude(state="complete").distinct().count(),
            "completed_first_time_count": first_time,
            "completed_first_time_percentage": percent(first_time, completed_total),
            "completed_required_corrections_count": required_corrections,
            "completed_required_corrections_percentage": percent(
                required_corrections, completed_total
            ),
            "completed_total_count": completed_total,
            "completed_total_percentage": percent(completed_total, homes_count),
        }

    def get_neea_v2_incentive_metrics_from_queryset(self, queryset, controls):
        queryset = queryset.distinct()
        approved = queryset.filter(state="ipp_payment_automatic_requirements")
        pending = queryset.filter(state="start")

        stats = {}
        query_str = "home_status__standardprotocolcalculator__builder_incentive"

        stats.update(
            approved.aggregate(
                **{
                    "approved_payments": Count(query_str),
                }
            )
        )
        stats.update(
            pending.aggregate(
                **{
                    "pending_payments": Count(query_str),
                }
            )
        )

        # Sum pre-rounded numbers.  Need newer version of Django to use the Round() db function
        approved_dollars = approved.values_list(query_str, flat=True)

        pending_dollars = pending.values_list(query_str, flat=True)

        stats["approved_dollars"] = sum(round(incentive, 2) for incentive in approved_dollars)
        stats["pending_dollars"] = sum(round(incentive, 2) for incentive in pending_dollars)
        return stats


class QANoteViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = QANote
    queryset = model.objects.all()
    serializer_class = QANoteSerializer

    def get_examine_machinery_classes(self):
        from .views.examine import QANoteExamineMachinery
        from axis.home.views.machineries import HomeQANoteDocumentExamineMachinery

        return {
            None: QANoteExamineMachinery,
            "HomeQANoteDocumentExamineMachinery": HomeQANoteDocumentExamineMachinery,
        }


class ObservationTypeViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = ObservationType
    serializer_class = ObservationTypeSerializer

    def get_queryset(self):
        return self.model.objects.filter_by_user(self.request.user)

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.examine import ObservationTypeMachinery

        return ObservationTypeMachinery
