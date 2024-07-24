__author__ = "Artem Hruzd"
__date__ = "01/03/2020 21:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.company.models import Company
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter
from axis.core.api_v3.permissions import IsAdminUserOrSuperUserPermission
from .filters import RelationshipFilter
from .serializers import RelationshipSerializer
from ..models import Relationship


class RelationshipViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Relationship management endpoints.
    retrieve:
        Return a Relationship instance.
    list:
        Return all Relationship objects
    create:
        Create a relationship between two objects
    delete:
        Delete a Relationship.
    attach:
        Attach/Detach relationship
    show:
        Show/Hide relationship
    lock:
        Lock/Unlock relationship
    """

    permission_classes = [
        IsAuthenticated,
    ]
    model = Relationship
    queryset = model.objects.all()
    serializer_class = RelationshipSerializer

    filterset_class = RelationshipFilter
    ordering_fields = [
        "id",
        "object_id",
        "company__name",
    ]
    ordering = ("-id",)

    def get_permissions(self):
        self.permission_classes = (IsAuthenticated,)
        if self.action in ["destroy"]:
            self.permission_classes = (IsAdminUserOrSuperUserPermission,)

        return super(RelationshipViewSet, self).get_permissions()

    @swagger_auto_schema(
        methods=["post"],
        request_body=no_body,
        operation_description="Set flag `is_attached` to True for relationship",
    )
    @swagger_auto_schema(
        methods=["delete"],
        request_body=no_body,
        operation_description="Set flag `is_attached` to False for relationship",
    )
    @action(detail=True, methods=["post", "delete"])
    def attach(self, request, **kwargs):
        relationship = self.get_object()
        relationship.is_attached = request.method == "POST"
        relationship.save()
        serializer = self.get_serializer(instance=relationship)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=["post"],
        request_body=no_body,
        operation_description="Set flag `is_viewable` and `is_reportable` "
        "to True for relationship",
    )
    @swagger_auto_schema(
        methods=["delete"],
        request_body=no_body,
        operation_description="Set flag `is_viewable` and `is_reportable` "
        "to False for relationship",
    )
    @action(detail=True, methods=["post", "delete"])
    def show(self, request, **kwargs):
        relationship = self.get_object()
        relationship.is_viewable = request.method == "POST"
        relationship.is_reporable = request.method == "POST"
        relationship.save()
        serializer = self.get_serializer(instance=relationship)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=["post"],
        request_body=no_body,
        operation_description="Set flag `is_owned` " "to True for relationship",
    )
    @swagger_auto_schema(
        methods=["delete"],
        request_body=no_body,
        operation_description="Set flag `is_owned` " "to False for relationship",
    )
    @action(detail=True, methods=["post", "delete"])
    def lock(self, request, **kwargs):
        relationship = self.get_object()
        relationship.is_owned = request.method == "POST"
        relationship.save()
        serializer = self.get_serializer(instance=relationship)
        return Response(serializer.data)


class NestedRelationshipViewSet(
    NestedViewSetMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Nested Relationship management endpoints.
    list:
        Return all Relationship objects
    create:
        Create a relationship between two objects or
        return existing `Relationship` if already exists
    delete:
        Delete relationship between two objects
    """

    permission_classes = [
        IsAuthenticated,
    ]
    model = Relationship
    queryset = model.objects.all()
    serializer_class = RelationshipSerializer

    filterset_class = RelationshipFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = [
        "company__name",
    ]
    ordering_fields = [
        "id",
        "object_id",
        "company__name",
    ]
    ordering = ("-id",)

    @property
    def ct_model(self):
        """
        Use to define Model class that we want to connect
        object_id handled by NestedViewSetMixin
        """
        raise NotImplementedError

    def get_queryset(self):
        return (
            super(NestedRelationshipViewSet, self)
            .get_queryset()
            .filter(content_type=ContentType.objects.get_for_model(self.ct_model))
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        object_id = self.get_parents_query_dict().get("object_id")
        company = serializer.validated_data.get("company")
        content_type = ContentType.objects.get_for_model(self.ct_model)
        relationship = Relationship.objects.filter(
            object_id=object_id, company=company, content_type=content_type
        ).first()
        if relationship:
            serializer = self.get_serializer(instance=relationship, data=request.data)
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer.save(object_id=object_id, company=company, content_type=content_type)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        detail=False,
        methods=[
            "delete",
        ],
    )
    def remove(self, request, *args, **kwargs):
        object_id = self.get_parents_query_dict().get("object_id")
        obj = self.ct_model.objects.get(id=object_id)

        if isinstance(obj, Company):
            content_types = ContentType.objects.get_for_models(self.ct_model, Company)
        else:
            content_types = ContentType.objects.get_for_models(self.ct_model)

        Relationship.objects.filter(
            object_id=object_id,
            company=self.request.user.company,
            content_type__in=content_types.values(),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NestedRelationshipByCompanyTypeViewSet(NestedRelationshipViewSet):
    """
    Nested Relationship management endpoints.
    list:
        Return all Relationship objects
    create:
        Create a relationship between two objects
    builder:
        Get or Create builder relationship


        Create builder relationship for object
    """

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change Builder Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def builder_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.BUILDER_COMPANY_TYPE
        )

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change Rater Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def rater_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.RATER_COMPANY_TYPE
        )

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change General Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def general_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.GENERAL_COMPANY_TYPE
        )

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change HVAC Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def hvac_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.HVAC_COMPANY_TYPE
        )

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change EEP Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def eep_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.EEP_COMPANY_TYPE
        )

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change QA Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def qa_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.QA_COMPANY_TYPE
        )

    @swagger_auto_schema(
        methods=["post"],
        request_body=RelationshipSerializer,
        operation_description="Change Utility Organization relationship",
    )
    @action(
        detail=False,
        methods=[
            "get",
            "post",
        ],
    )
    def utility_organization(self, request, **kwargs):
        return self.relationship_by_company_type(
            request=request, company_type=Company.UTILITY_COMPANY_TYPE
        )

    def relationship_by_company_type(self, request, company_type):
        if request.method == "GET":
            try:
                relationship = self.get_queryset().filter(company__company_type=company_type).get()
            except self.model.DoesNotExist:
                raise Http404
            serializer = self.get_serializer(instance=relationship)
            return Response(serializer.data)

        with transaction.atomic():
            relationship = self.get_queryset().filter(company__company_type=company_type)
            if relationship:
                relationship.delete()
            if not request.data.get("company"):
                return Response(status=status.HTTP_204_NO_CONTENT)

            serializer = RelationshipSerializer(
                data=request.data, context={"request": self.request}
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            relationship = serializer.instance
            headers = self.get_success_headers(serializer.data)
            serializer = self.get_serializer(instance=relationship.company)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
