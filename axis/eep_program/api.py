"""api.py: Django eep_program"""


import logging
import operator
from datetime import timedelta

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.core.views.landing import DashboardMetricsControlsMixin
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.home.models import EEPProgramHomeStatus
from axis.qa.utils import get_program_summaries
from . import strings
from .models import EEPProgram
from .serializers import EEPProgramSerializer

__author__ = "Steven Klass"
__date__ = "7/29/13 9:13 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EEPProgramViewSet(
    DashboardMetricsControlsMixin, ExamineViewSetAPIMixin, viewsets.ModelViewSet
):
    """EEPProgram api"""

    model = EEPProgram
    queryset = model.objects.all()
    serializer_class = EEPProgramSerializer

    def create(self, request, *args, **kwargs):
        """Creates a program (EEPProgram)"""
        sponsor = request.data.get("sponsor")
        if sponsor:
            request.data["owner"] = sponsor
        return super(EEPProgramViewSet, self).create(request, *args, **kwargs)

    def get_examine_machinery_classes(self):
        """Imports required machinery"""
        from .views import (
            EEPProgramExamineMachinery,
            EEPProgramRequirementsMachinery,
            EEPProgramSettingsMachinery,
            EEPProgramAnnotationsMachinery,
            EEPProgramChecklistMachinery,
            EEPProgramCustomerHIRLExamineMachinery,
        )

        return {
            None: EEPProgramExamineMachinery,
            "EEPProgramCustomerHIRLExamineMachinery": EEPProgramCustomerHIRLExamineMachinery,
            "EEPProgramExamineMachinery": EEPProgramExamineMachinery,
            "EEPProgramRequirementsMachinery": EEPProgramRequirementsMachinery,
            "EEPProgramSettingsMachinery": EEPProgramSettingsMachinery,
            "EEPProgramAnnotationsMachinery": EEPProgramAnnotationsMachinery,
            "EEPProgramChecklistMachinery": EEPProgramChecklistMachinery,
        }

    def filter_queryset(self, queryset):
        """Extends filter_queryset with another two possible params"""
        lookup = self.request.query_params.dict().copy()
        lookup.pop("machinery", None)
        lookup.pop("fieldset", None)
        return queryset.filter(**lookup)

    @action(detail=True)
    def note(self, request, *args, **kwargs):
        """For a given EEEP_PROGRAM, takes its slug and gives back a note if matched"""
        obj = self.get_object()

        lookup = obj.slug.replace("-", "_").upper()
        note = getattr(strings, "{}_PROGRAM_NOTE".format(lookup), "")

        return Response(note)

    @action(detail=False)
    def builder_program_metrics(self, request, *args, **kwargs):
        """Calculates and sends back builder program metrics"""
        filter_type = request.query_params.get("filter_type")
        use_date_filter = filter_type in ["creation_date", "certification_date"]

        controls_kwargs = {}
        if use_date_filter:
            controls_kwargs["day_range"] = 90  # Default range
        controls = self.get_filter_controls(request, **controls_kwargs)
        stats = EEPProgramHomeStatus.objects.filter_by_user(request.user).filter(
            eep_program__is_active=True
        )

        if use_date_filter and controls["date_start"]:
            if filter_type == "creation_date":
                stats = stats.filter(created_date__gte=controls["date_start"])
            elif filter_type == "certification_date":
                query = Q(certification_date__gte=controls["date_start"]) | Q(
                    certification_date__isnull=True
                )
                stats = stats.filter(query)

        if use_date_filter and controls["date_end"]:
            filter_date_end = controls["date_end"] + timedelta(days=1)
            if filter_type == "creation_date":
                stats = stats.filter(created_date__lte=filter_date_end)
            elif filter_type == "certification_date":
                query = Q(certification_date__lte=filter_date_end) | Q(
                    certification_date__isnull=True
                )
                stats = stats.filter(query)

        if controls["us_state"]:
            stats = stats.filter(home__city__county__state=controls["us_state"])

        ipp_payments_kwargs = {}
        if request.user.company.company_type in ["rater", "provider", "builder"]:
            _key = "ippitem__incentive_distribution__customer__company_type"
            ipp_payments_kwargs[_key] = request.user.company.company_type
        program_metrics = get_program_summaries(stats, ipp_payments_kwargs=ipp_payments_kwargs)
        program_metrics = sorted(
            program_metrics, key=operator.itemgetter("eep_program"), reverse=True
        )
        return self.make_metrics_response(program_metrics, controls)
