"""message.py: """


import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.permissions import NestedIsCurrentUserPermission
from axis.core.api_v3.serializers.common import BulkSelectByIdSerializer
from axis.messaging.api_v3 import MESSAGE_SEARCH_FIELDS, MESSAGE_ORDERING_FIELDS
from axis.messaging.api_v3.permissions import IsMessageOwnerPermission
from axis.messaging.messages import MESSAGE_REGISTRY
from axis.messaging.models import Message, MessagingPreference, DigestPreference
from axis.messaging.utils import get_default_company_preference
from axis.messaging.utils import get_preferences_report, send_email
from ..filters import MessageFilter
from ..serializers import (
    MessageSerializer,
    MessageCategorySerializer,
    MessagePreferenceListSerializer,
    MessagePreferenceWritableSerializer,
    DigestPreferenceSerializer,
)

__author__ = "Artem Hruzd"
__date__ = "01/07/2020 12:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

log = logging.getLogger(__name__)

User = get_user_model()


class MessageViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Represents Message endpoint
    retrieve:
        Return a Message instance.
    delete:
        Delete an existing Message.
    partial_update:
        Update one or more fields on an existing Message.
    update:
        Update a Message.
    email:
        Sent notification email to user and update `date_sent` field
    """

    model = Message
    queryset = model.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated, IsMessageOwnerPermission)
    filterset_class = MessageFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = MESSAGE_SEARCH_FIELDS
    ordering_fields = MESSAGE_ORDERING_FIELDS

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, methods=["patch"])
    def email(self, request, *args, **kwargs):
        instance = self.get_object()
        send_email(message=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, methods=["patch"])
    def read(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.alert_read = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class NestedMessageViewSet(
    NestedViewSetMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    list:
        Get received messages by user ID

        Returns all received messages for user
    mark_all_read:
        Update queryset using the client's latest known message as a cutoff for marking "all" as
        read.


        This defeats race conditions that the client doesn't know about.
        Return all updated messages
    pull:
        Get recent messages limited by page size and update `date_alerted` after response.


        Return list of pulled messages
    categories:
        Get available message categories by user ID

        Return all available message categories for user
    read_action:
        Mark multiple messages as read

        Set `alert_read` field to `True` for multiple messages at once.
        Returns count of updated messages
    """

    model = Message
    permission_classes = (NestedIsCurrentUserPermission,)
    queryset = model.objects.all().order_by("-date_created")
    filterset_class = MessageFilter
    serializer_class = MessageSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = MESSAGE_SEARCH_FIELDS
    ordering_fields = MESSAGE_ORDERING_FIELDS

    def get_queryset(self):
        qs = super(NestedMessageViewSet, self).get_queryset()
        if self.action == "mark_all_read":
            return qs.filter(alert_read=False)
        return super(NestedMessageViewSet, self).get_queryset()

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request, *args, **kwargs):
        # Update queryset using the client's latest known message as a cutoff for marking "all" as
        # read.  This defeats race conditions that the client doesn't know about.
        queryset = self.get_queryset()
        queryset.update(alert_read=True)

        self._post_to_websocket(request)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _post_to_websocket(self, request):
        # Post internally to private API to generate read receipts for client websockets
        # This will not happen for messages marked as read that were undelivered because of a large
        # backlog, since the client doesn't have a record of them anyway.
        server_type = settings.SERVER_TYPE
        http_prefix = "https://"
        if settings.SERVER_TYPE == settings.PRODUCTION_SERVER_TYPE:
            server_type = "axis"
        domain = server_type + ".pivotalenergy.net"

        if settings.SERVER_TYPE == settings.LOCALHOST_SERVER_TYPE:
            http_prefix = "http://"
            domain = "localhost:{port}".format(port=request.META.get("SERVER_PORT", "8000"))

        private_api_url = reverse(
            "apiv2:messaging_websocket-bulk-read",
            kwargs={
                "session_key": request.session.session_key,
            },
        )
        _ = requests.post(
            http_prefix + domain + private_api_url,
            headers={
                "Authorization": "Token " + Token.objects.get(user__username="websocket").key,
            },
        )

    @action(detail=False, methods=["post"])
    def pull(self, request, *args, **kwargs):
        mundane = ~Q(level="system")
        recent_system = Q(
            level="system", date_alerted__gte=timezone.now() - timezone.timedelta(days=7)
        )
        queryset = (
            self.get_queryset()
            .filter(mundane | recent_system, alert_read=False)
            .select_related("user")
            .order_by("id")
        )
        # Get Message_name List
        message_name_queryset = MessagingPreference.objects.filter(
            receive_notification=True, user=request.user
        ).values_list("message_name", flat=True)

        # Filter list.
        message_name_list = list(message_name_queryset)
        queryset = queryset.filter(modern_message__in=message_name_list)
        # Use built-in pagination to enforce a limit on the number of returned objects.
        # We don't expect the client to use any kind of specific page number, we just want to get
        # the leading head of results from page 1.

        page = self.paginate_queryset(queryset)
        if page is not None:
            objects = page
        else:
            objects = queryset
        serializer = self.get_serializer(objects, many=True)

        # Bake response, THEN update date_alerted field
        response = self.paginator.get_paginated_response(serializer.data)
        queryset = queryset.filter(date_alerted__isnull=True).update(date_alerted=timezone.now())

        return response

    @swagger_auto_schema(request_body=no_body, responses={"200": MessageCategorySerializer})
    @action(detail=False, methods=["get"], filter_backends=[], pagination_class=None)
    def categories(self, request, *args, **kwargs):
        user = User.objects.get(id=self.get_parents_query_dict()["user_id"])
        categories = get_preferences_report(user, trimmed=True).keys()
        serializer = MessageCategorySerializer(
            data=[{"value": c, "name": c.title()} for c in sorted(categories)], many=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=["patch"],
        request_body=BulkSelectByIdSerializer,
        manual_parameters=[
            openapi.Parameter(
                "all",
                openapi.IN_QUERY,
                description="Update all unread messages",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    @action(detail=False, methods=["patch"])
    def read_action(self, request, *args, **kwargs):
        serializer = BulkSelectByIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.request.query_params.get("all"):
            qs = self.get_queryset()
        else:
            qs = self.get_queryset().filter(id__in=serializer.data["ids"])
        updated_count = qs.update(alert_read=True)
        return Response(updated_count)


class NestedMessagingPreferenceViewSet(NestedViewSetMixin, viewsets.GenericViewSet):
    """
    Manage user preferences
    list:
        Get available message types


        Returns all registered messages types on AXIS available for user
    create:
         Override default message preferences


         Returns updated message preferences
    reset:
        Set all preferences to default


        Returns all registered messages types on AXIS available for user
    """

    model = MessagingPreference
    permission_classes = (NestedIsCurrentUserPermission,)
    queryset = model.objects.all()
    serializer_class = MessagePreferenceListSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        user_id = self.get_parents_query_dict().get("user_id", self.request.user.id)
        user = User.objects.get(id=user_id)
        existing_preferences = self.get_queryset().values(
            "message_name", "receive_notification", "receive_email"
        )
        preferences_data = []
        for modern_message in MESSAGE_REGISTRY.values():
            if (
                modern_message.company_types
                and user.company.company_type not in modern_message.company_types
            ):
                continue

            if (
                modern_message.company_slugs
                and user.company.slug not in modern_message.company_slugs
            ):
                continue

            pref = get_default_company_preference(self.request.user, message=modern_message)
            message_name = modern_message.__name__
            existing_preference = next(
                (item for item in existing_preferences if item["message_name"] == message_name),
                None,
            )

            data = {
                # Display info
                "required": modern_message.required,
                "verbose_name": modern_message.verbose_name,
                "description": modern_message.description,
                "sticky_alert": modern_message.sticky_alert,
                "unique": modern_message.unique,
                "level": modern_message.level,
                "company_admins_only": modern_message.company_admins_only,
                "company_types": modern_message.company_types,
                "company_slugs": modern_message.company_slugs,
                "companies_with_relationship": modern_message.companies_with_relationship,
                "companies_with_relationship_or_self": modern_message.companies_with_relationship_or_self,
                "category": modern_message.category,
                "message_name": modern_message.__name__,
                "receive_email": pref["receive_email"],
                "receive_notification": pref["receive_notification"],
            }

            if existing_preference:
                data["receive_email"] = existing_preference["receive_email"]
                data["receive_notification"] = existing_preference["receive_notification"]

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            preferences_data.append(data)

        return Response(preferences_data)

    @swagger_auto_schema(request_body=MessagePreferenceWritableSerializer)
    def create(self, request, *args, **kwargs):
        user_id = self.get_parents_query_dict().get("user_id", self.request.user.id)
        user = User.objects.get(id=user_id)
        serializer = MessagePreferenceWritableSerializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=False, methods=["delete"], filter_backends=[], pagination_class=None)
    def reset(self, request, *args, **kwargs):
        user = User.objects.get(id=self.get_parents_query_dict()["user_id"])
        MessagingPreference.objects.filter(user=user).delete()
        return self.list(request, *args, **kwargs)


class NestedDigestPreferenceViewSet(NestedViewSetMixin, viewsets.GenericViewSet):
    """
    list:
        Get digest preferences by user ID


        Returns Digest Preferences
    create:
         Override default digest preferences settings


         Returns Digest Preferences
    """

    model = DigestPreference
    permission_classes = (NestedIsCurrentUserPermission,)
    queryset = model.objects.all()
    serializer_class = DigestPreferenceSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        user_id = self.get_parents_query_dict().get("user_id", self.request.user.id)
        user = User.objects.get(id=user_id)
        try:
            digest_preference = user.digestpreference
        except DigestPreference.DoesNotExist:
            digest_preference = DigestPreference.objects.create(user=user)
            digest_preference.save()
        serializer = self.get_serializer(digest_preference)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_id = self.get_parents_query_dict().get("user_id", self.request.user.id)
        user = User.objects.get(id=user_id)
        serializer = DigestPreferenceSerializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
