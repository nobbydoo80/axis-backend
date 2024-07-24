"""Api V3 utils."""

from django.contrib.contenttypes.models import ContentType
from django_fsm import has_transition_perm, can_proceed
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from axis.core.api_v3.serializers import RecentlyViewedSerializer
from axis.core.models import RecentlyViewed

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 19:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


def _get_transition_viewset_method(field_name, transition_name):
    """
    Create a viewset method for the provided `transition_name`
    """

    def inner_func(self, request, pk=None, **kwargs):
        obj = self.get_object()
        transition_method = getattr(obj, transition_name)

        if not can_proceed(transition_method):
            raise PermissionDenied("You cannot move to this state")

        if not has_transition_perm(transition_method, request.user):
            raise PermissionDenied("You do not have permission to move to this state")

        # check if our transition_method have user param, then pass user object
        if "user" in transition_method.__code__.co_varnames:
            transition_method(user=self.request.user)
        else:
            transition_method()

        # Our object can be outdated, because of async tasks in transition method.
        # That's why we're updating only state field
        obj.save(
            update_fields=[
                field_name,
            ]
        )

        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    # rename inner_func to transition_name and make @action working correctly
    inner_func.__name__ = transition_name.lower()

    inner_func = swagger_auto_schema(request_body=no_body)(inner_func)
    return inner_func


def get_viewset_transition_action_mixin(model, field_name, exclude_transitions=None, **kwargs):
    """
    Find all transitions defined on `model`, then create a corresponding
    viewset action method for each and apply it to `Mixin`. Finally, return
    `Mixin`
    """
    instance = model()
    if exclude_transitions:
        exclude_transitions = set(exclude_transitions)
    else:
        exclude_transitions = set()

    transitions = getattr(instance, f"get_all_{field_name}_transitions")()
    transition_names = set(x.name for x in transitions)
    transition_names = transition_names - exclude_transitions

    actions = {}
    for transition_name in transition_names:
        actions[transition_name] = action(detail=True, methods=["post"], **kwargs)(
            _get_transition_viewset_method(field_name=field_name, transition_name=transition_name)
        )

    return type("TransitionMixin", (), actions)


class RecentlyViewedMixin:
    """
    Adds 2 extra actions to add Object to recently viewed list
    and to get this list
    """

    @property
    def model(self):
        raise NotImplementedError

    @swagger_auto_schema(
        methods=[
            "get",
        ],
        responses={"200": RecentlyViewedSerializer},
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                required=False,
                description="Fields to use when ordering " "the results: `updated_at`",
                type=openapi.TYPE_STRING,
                in_=openapi.IN_QUERY,
            ),
        ],
    )
    @action(
        methods=[
            "get",
        ],
        detail=False,
        serializer_class=RecentlyViewedSerializer,
        filter_backends=[],
    )
    def recently_viewed(self, request, *args, **kwargs):
        queryset = RecentlyViewed.objects.filter(
            user=request.user, content_type=ContentType.objects.get_for_model(self.model)
        )

        available_order_fields = ["updated_at", "-updated_at"]
        ordering = request.query_params.get("ordering", None)

        if ordering in available_order_fields:
            queryset = queryset.order_by(ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecentlyViewedSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RecentlyViewedSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=[
            "post",
        ],
        responses={"200": None},
        request_body=no_body,
    )
    @action(
        methods=[
            "post",
        ],
        detail=True,
        filter_backends=[],
    )
    def view(self, request, *args, **kwargs):
        RecentlyViewed.objects.view(instance=self.get_object(), by=request.user)
        return Response(status=status.HTTP_201_CREATED)
