"""viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "07/07/2020 13:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import django_auto_prefetching
from django.apps import apps
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from axis.core.api_v3.filters import (
    AxisSearchFilter,
    AxisOrderingFilter,
    AxisFilterBackend,
)
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.customer_hirl.api_v3.permissions import HIRLProjectViewPermission
from axis.eep_program.api_v3 import (
    EEP_PROGRAM_SEARCH_FIELDS,
    EEP_PROGRAM_ORDERING_FIELDS,
)
from axis.eep_program.api_v3.filters import EEPProgramFilter
from axis.eep_program.api_v3.serializers import (
    BasicEEPProgramSerializer,
    EEPProgramSerializer,
)
from axis.eep_program.models import EEPProgram

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class EEPProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
        Get program by ID


        Returns a program
    list:
        Get all programs


        Returns all programs available for user
    hirl_project_programs:
        Get HIRL Project special programs


        Returns all HIRL specific programs for HIRL Project, Scoring Upload and other services.
    hirl_program_have_accreditation:
        Check whether or not Users have accreditation for current Program


        Return boolean true/false
    participate:
        Participate in program


        Only programs in which you participate will appear in
        the "Program" list when creating a new home.
        Participating in programs will not affect
        the visibility of homes associated with those programs.
    """

    model = EEPProgram
    queryset = EEPProgram.objects.all()
    filterset_class = EEPProgramFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = EEP_PROGRAM_SEARCH_FIELDS
    ordering_fields = EEP_PROGRAM_ORDERING_FIELDS

    @property
    def permission_classes(self):
        if self.action in ["hirl_project_programs", "hirl_program_have_accreditation"]:
            return (HIRLProjectViewPermission,)
        return (IsAuthenticated,)

    @property
    def ordering(self):
        """Set default ordering for actions"""
        if self.action == "hirl_project_programs":
            return ("-name",)
        return None

    def get_queryset(self):
        queryset = super(EEPProgramViewSet, self).get_queryset()

        if self.action in ["hirl_project_programs", "hirl_program_have_accreditation"]:
            queryset = self.queryset.filter(
                slug__in=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            )
        else:
            queryset = queryset.filter_by_user(user=self.request.user)

        return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return EEPProgramSerializer
        return BasicEEPProgramSerializer

    @action(detail=False, pagination_class=None)
    def hirl_project_programs(self, request, *args, **kwargs):
        return super(EEPProgramViewSet, self).list(request, *args, **kwargs)

    @action(
        detail=True,
        pagination_class=None,
        url_path=r"hirl_program_have_accreditation/(?P<user_pk>\d+)",
    )
    def hirl_program_have_accreditation(self, request, user_pk, *args, **kwargs):
        eep_program = self.get_object()
        user = User.objects.filter_by_user(user=self.request.user).get(id=user_pk)
        return Response(
            data={"exists": eep_program.hirl_program_have_accreditation_for_user(user=user)}
        )

    @swagger_auto_schema(
        methods=["patch", "delete"],
        responses={
            "200": openapi.Response("OK", openapi.Schema(type=openapi.TYPE_OBJECT, properties={}))
        },
        request_body=no_body,
    )
    @action(detail=True, methods=["patch", "delete"])
    def participate(self, request, *args, **kwargs):
        eep_program = self.get_object()
        if request.method == "PATCH":
            eep_program.opt_in_out_list.add(self.request.user.company)
        else:
            eep_program.opt_in_out_list.remove(self.request.user.company)
        return Response(status=status.HTTP_200_OK)


class EEPProgramNestedHistoryViewSet(NestedHistoryViewSet):
    model = EEPProgram.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = EEP_PROGRAM_SEARCH_FIELDS
    ordering_fields = EEP_PROGRAM_ORDERING_FIELDS
