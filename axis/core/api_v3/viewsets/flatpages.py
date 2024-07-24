"""news.py: """

__author__ = "Artem Hruzd"
__date__ = "11/16/2020 11:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.utils.functional import cached_property
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission
from axis.core.models import AxisFlatPage
from rest_framework.permissions import AllowAny
from axis.core.api_v3.serializers import AxisFlatPageSerializer
from axis.core.api_v3.filters import AxisOrderingFilter, AxisFilterBackend
from axis.customer_hirl.api_v3.permissions import HIRLCompanyMemberPermission

customer_hirl_app = apps.get_app_config("customer_hirl")


class FlatpageViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Represents Static pages content that are also using as news
    list:
        Return all static pages


        Static pages list
    news:
        Return only news static pages


        News list
    """

    model = AxisFlatPage
    serializer_class = AxisFlatPageSerializer
    filter_backends = [AxisFilterBackend, AxisOrderingFilter]
    queryset = AxisFlatPage.objects.all()
    ordering_fields = ["created_at", "order"]
    ordering = ["order", "-created_at"]

    def get_queryset(self):
        qs = super(FlatpageViewSet, self).get_queryset()
        if self.action == "news":
            return qs.filter(url__icontains="-news/")
        if self.action == "builder_central_page":
            return qs
        return qs.filter_by_user(user=self.request.user)

    @cached_property
    def permission_classes(self):
        if self.action in ["update", "partial_update"]:
            return (IsAdminUserOrSuperUserPermission | HIRLCompanyMemberPermission,)
        return (AllowAny,)

    @action(detail=False)
    def news(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    @action(detail=False)
    def verifier_resources_page(self, request, *args, **kwargs):
        instance = get_object_or_404(
            self.get_queryset(), **{"url": customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL}
        )
        self.check_object_permissions(self.request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, url_path=r"verifier_resources_page/(?P<year>[0-9]+)")
    def verifier_resources_page_by_year(self, request, year, *args, **kwargs):
        instance = get_object_or_404(
            self.get_queryset(),
            **{"url": f"{customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL}{year}/"},
        )
        self.check_object_permissions(self.request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False)
    def builder_central_page(self, request, *args, **kwargs):
        instance = get_object_or_404(
            self.get_queryset(), **{"url": customer_hirl_app.BUILDER_CENTRAL_PAGE_URL}
        )
        self.check_object_permissions(self.request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
