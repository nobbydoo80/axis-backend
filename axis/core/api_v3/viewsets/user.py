"""user.py: """

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 19:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]


import logging

import django_auto_prefetching
from django.apps import apps
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.db.models import Q, Count, Case, When, CharField, Value
from django.middleware import csrf
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from impersonate.signals import session_begin, session_end
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_simplejwt.tokens import RefreshToken

from axis.company.models import Company
from axis.core.api_v3 import (
    USER_SEARCH_FIELDS,
    USER_ORDERING_FIELDS,
    FIND_VERIFIER_LIST_SEARCH_FIELDS,
)
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.filters import UserFilter, HIRLFindVerifierFilter
from axis.core.api_v3.permissions import (
    IsAdminUserOrSuperUserPermission,
    IsCurrentUserPermission,
    IsUserImpersonatedPermission,
    UserUpdatePermission,
)
from axis.core.api_v3.serializers import (
    BasicUserSerializer,
    UserSerializer,
    ImpersonationUserSerializer,
    TokenObtainPairResponseSerializer,
    ChangePasswordSerializer,
    HIRLFindVerifierSerializer,
)
from axis.core.api_v3.viewsets.history import NestedHistoryViewSet
from axis.user_management.models import Accreditation

User = get_user_model()
log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class UserViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    retrieve:
        Find user by ID


        Returns a single User
    list:
        Get list of available users

        Returns a list of Users
    partial_update:
        Partial update an existing user


        Update one or more fields on an existing user.
    update:
        Update an existing user

        Update user
    impersonation_list:
        Get list of users available for impersonation


        Return list of users that you can impersonate
    impersonate_start:
        Impersonate user by ID

        Create a new token with impersonation info and
        modify legacy session with impersonation info
    impersonate_stop:
        Stop impersonation

        Create a new token without impersonation info and
        modify legacy session
    logout:
        Logout from current user session


        Sync logout process between JWT frontend and Legacy session
    info:
        Get system info about current user


        Returns all required information about user after login
    change_password:
        Allows user to change his password


        Change password and invalidate all old sessions, except current
    customer_hirl_find_verifier_list:
        Customer HIRL find verifiers list for external use


        Returns list of verifiers, their accreditations and verifier agreements
    """

    permission_classes = (
        IsAuthenticated,
        IsAdminUserOrSuperUserPermission,
    )
    model = User
    queryset = User.objects.all()
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = USER_SEARCH_FIELDS
    ordering_fields = USER_ORDERING_FIELDS
    ordering = ["-first_name", "-last_name", "-id"]

    @property
    def filterset_class(self):
        if self.action == "customer_hirl_find_verifier_list":
            return HIRLFindVerifierFilter
        return UserFilter

    def get_serializer_class(self):
        if self.action in ["impersonate_start", "impersonate_stop"]:
            return TokenObtainPairResponseSerializer
        if self.action == "info":
            return ImpersonationUserSerializer
        if self.action == "change_password":
            return ChangePasswordSerializer
        if self.action == "customer_hirl_find_verifier_list":
            return HIRLFindVerifierSerializer
        if self.request.user.is_superuser:
            return UserSerializer
        return BasicUserSerializer

    def get_permissions(self):
        if self.action in [
            "list",
        ]:
            self.permission_classes = (IsAuthenticated,)
        elif self.action == "customer_hirl_find_verifier_list":
            self.permission_classes = (AllowAny,)
        elif self.action in [
            "create",
        ]:
            self.permission_classes = (
                IsAuthenticated,
                IsAdminUserOrSuperUserPermission,
            )
        elif self.action in ["impersonation_list", "impersonate_start", "impersonate_stop"]:
            self.permission_classes = (
                IsAuthenticated,
                IsAdminUserOrSuperUserPermission | IsUserImpersonatedPermission,
            )
        elif self.action in ["retrieve", "update", "partial_update", "change_password"]:
            self.permission_classes = (UserUpdatePermission,)
        elif self.action in [
            "info",
        ]:
            self.permission_classes = (
                IsAuthenticated,
                IsCurrentUserPermission,
            )
        elif self.action in [
            "logout",
        ]:
            self.permission_classes = (IsAuthenticated,)
        return super(UserViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super(UserViewSet, self).get_queryset()
        if self.action == "customer_hirl_find_verifier_list":
            hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()
            companies = Company.objects.filter_by_company(company=hirl_company, include_self=True)
            queryset = (
                queryset.filter(company__in=companies)
                .common_annotations()
                .annotate(
                    active_accreditations_count=Count(
                        "accreditations",
                        filter=~Q(accreditations__state=Accreditation.INACTIVE_STATE),
                        distinct=True,
                    ),
                )
                .filter(
                    Q(company__company_type=Company.RATER_COMPANY_TYPE),
                    Q(
                        active_customer_hirl_verifier_agreements_count__gt=0,
                        active_accreditations_count__gt=0,
                    )
                    | Q(
                        Q(accreditations__name=Accreditation.NGBS_GREEN_FIELD_REP_NAME),
                        ~Q(accreditations__state=Accreditation.INACTIVE_STATE),
                    ),
                )
                .distinct()
            )
            return django_auto_prefetching.prefetch(queryset, self.get_serializer_class())

        if self.action == "impersonation_list":
            return queryset.exclude(
                Q(is_staff=True) | Q(is_superuser=True) | Q(is_active=False) | Q(is_approved=False)
            ).common_annotations()
        # ignore queryset filtering if we trying to access as Anonymous user
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset.filter_by_user(user=self.request.user).common_annotations()

    @action(detail=True, methods=["get"], filter_backends=[], pagination_class=None)
    def impersonate_start(self, request, *args, **kwargs):
        impersonator_pk = None

        if hasattr(request, "jwt") and request.jwt.get("impersonator"):
            impersonator_pk = request.jwt.get("impersonator")
        else:
            if hasattr(request, "impersonator") and request.impersonator:
                impersonator_pk = request.impersonator.pk

        impersonator = User.objects.filter(pk=impersonator_pk).first() or self.request.user

        if not impersonator.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            impersonate_user_pk = int(self.kwargs.get("pk"))
        except ValueError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        impersonate_user = self.model.objects.filter(pk=impersonate_user_pk).first()

        if not impersonate_user:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if (
            not impersonate_user.is_active
            or not impersonate_user.is_approved
            or impersonate_user.is_superuser
            or impersonate_user.is_staff
        ):
            return Response(
                "Impersonated user must be active, approved and not stuff",
                status=status.HTTP_403_FORBIDDEN,
            )

        request.session["_impersonate"] = impersonate_user.pk
        request.session.modified = True
        session_begin.send(
            sender=None,
            impersonator=impersonator,
            impersonating=impersonate_user,
            request=request,
        )

        refresh_token = RefreshToken.for_user(impersonate_user)
        refresh_token["impersonator"] = impersonator.pk

        serializer = TokenObtainPairResponseSerializer(
            data={
                "refresh": "{}".format(refresh_token),
                "access": "{}".format(refresh_token.access_token),
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], filter_backends=[], pagination_class=None)
    def impersonate_stop(self, request, *args, **kwargs):
        impersonating = request.session.pop("_impersonate", None)
        jwt_impersonator = None
        if hasattr(request, "jwt"):
            try:
                jwt_impersonator = User.objects.get(pk=request.jwt.get("impersonator"))
            except User.DoesNotExist:
                raise ValidationError("{impersonator} not found")

        if impersonating:
            request.session.modified = True
            session_end.send(
                sender=None,
                impersonator=request.impersonator,
                impersonating=impersonating,
                request=request,
            )
        if jwt_impersonator:
            refresh_token = RefreshToken.for_user(jwt_impersonator)
            serializer = TokenObtainPairResponseSerializer(
                data={
                    "refresh": "{}".format(refresh_token),
                    "access": "{}".format(refresh_token.access_token),
                }
            )
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def impersonation_list(self, request, *args, **kwargs):
        return super(UserViewSet, self).list(request, *args, **kwargs)

    @action(detail=False, filter_backends=[], pagination_class=None)
    def info(self, request):
        impersonator_pk = None

        if hasattr(request, "jwt") and request.jwt.get("impersonator"):
            impersonator_pk = request.jwt.get("impersonator")
        else:
            if hasattr(request, "impersonator") and request.impersonator:
                impersonator_pk = request.impersonator.pk

        qs = User.objects.filter(pk=impersonator_pk).common_annotations()
        impersonator = qs.first()

        qs = User.objects.filter(pk=request.user.pk).common_annotations()
        current_user = qs.first()
        user_data = UserSerializer(instance=current_user).data

        if impersonator:
            impersonator_data = UserSerializer(instance=impersonator).data
        else:
            impersonator_data = user_data
            user_data = None

        log.info(
            f"{request.user.first_name} {request.user.last_name}. "
            f"({request.user.username}) heartbeat",
            extra={"request": request},
        )
        return Response(
            {
                "impersonated": user_data,
                "user": impersonator_data,
                "csrftoken": csrf.get_token(request),
                "session_key": request.session.session_key,
            }
        )

    @swagger_auto_schema(
        responses={
            "200": openapi.Response("OK", openapi.Schema(type=openapi.TYPE_OBJECT, properties={}))
        }
    )
    @action(detail=False, filter_backends=[], pagination_class=None, permission_classes=(AllowAny,))
    def logout(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            "200": openapi.Response("OK", openapi.Schema(type=openapi.TYPE_OBJECT, properties={}))
        }
    )
    @action(detail=False, methods=["patch"], filter_backends=[], pagination_class=None)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        search_fields=FIND_VERIFIER_LIST_SEARCH_FIELDS,
        ordering_fields=[],
        ordering=[],
    )
    def customer_hirl_find_verifier_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        us_states = request.GET.get("us_states")
        final_queryset = queryset.annotate(
            is_or=Case(
                When(company__state=us_states, then=Value(0)),
                default=Value(1),
                output_field=CharField(),
            )
        ).order_by("is_or")
        page = self.paginate_queryset(final_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(final_queryset, many=True)
        return Response(serializer.data)


class UserNestedHistoryViewSet(NestedHistoryViewSet):
    permission_classes = (
        IsAuthenticated,
        IsAdminUserOrSuperUserPermission | IsCurrentUserPermission,
    )
    model = User.history.model
    queryset = model.objects.all()
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = USER_SEARCH_FIELDS
    ordering_fields = USER_ORDERING_FIELDS


class NestedUserViewSet(
    NestedViewSetMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    list:
        Get list of users


        Returns list of users
    """

    model = User
    permission_classes = (IsAuthenticated, IsAdminUserOrSuperUserPermission)
    queryset = model.objects.all().order_by("id")
    filterset_class = UserFilter
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = USER_SEARCH_FIELDS
    ordering_fields = USER_ORDERING_FIELDS

    def get_serializer_class(self):
        request = getattr(self, "request", None)
        if request and request.user.is_superuser:
            return UserSerializer
        return BasicUserSerializer

    def get_queryset(self):
        qs = super(NestedUserViewSet, self).get_queryset()
        qs = qs.filter_by_user(user=self.request.user).common_annotations()
        return django_auto_prefetching.prefetch(qs, self.get_serializer_class())
