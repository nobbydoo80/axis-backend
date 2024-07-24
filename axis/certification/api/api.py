import logging

from django.http.response import Http404

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from axis.examine.api.restframework import ExamineViewSetAPIMixin
from ..utils import get_progress_analysis
from ..exceptions import MissingSettingError
from .. import models
from . import serializers


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Main
class CertifiableObjectViewSet(viewsets.ModelViewSet):
    model = models.CertifiableObject
    serializer_class = serializers.CertifiableObjectSerializer

    url_basename = "certifiableobject"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self._validate_request_objects()

        return super(CertifiableObjectViewSet, self).dispatch(request, *args, **kwargs)

    def _validate_request_objects(self):
        """Raises 404 when dynamic workflow and object types are outside expected values."""
        try:
            workflow_id = int(self.kwargs["workflow_pk"])
        except:
            raise Http404()
        workflow = (
            models.Workflow.objects.filter_by_user(self.request.user).filter(pk=workflow_id).first()
        )
        if not workflow:
            raise Http404("Invalid workflow for user")

        config = workflow.get_config()
        try:
            config.get_object_type_spec(object_type=self.kwargs["type"])
        except MissingSettingError as e:
            raise Http404("Workflow does not support object type '%s'" % (self.kwargs["type"],))

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(self.request.user)
        queryset = queryset.filter(
            **{
                "type": self.kwargs["type"],
                "workflowstatus__workflow_id": self.kwargs["workflow_pk"],
            }
        )
        return queryset

    def get_serializer_context(self):
        context = super(CertifiableObjectViewSet, self).get_serializer_context()
        context["type"] = self.kwargs["type"]
        return context


class WorkflowStatusViewSet(viewsets.ModelViewSet):
    model = models.WorkflowStatus
    serializer_class = serializers.WorkflowStatusSerializer

    url_basename = "workflowstatus"

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(self.request.user)
        queryset = queryset.filter(
            **{
                "certifiable_object_id": self.kwargs["certifiable_object_pk"],
                "certifiable_object__type": self.kwargs["type"],
                "workflow_id": self.kwargs["workflow_pk"],
            }
        )
        return queryset

    def get_serializer_context(self):
        context = super(WorkflowStatusViewSet, self).get_serializer_context()
        context["type"] = self.kwargs["type"]
        return context


# Examine viewsets
class CertifiableObjectExamineViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = models.CertifiableObject
    serializer_class = serializers.CertifiableObjectSerializer

    # Hint for api urls we will register
    url_basename = "certifiableobject"

    def get_queryset(self):
        return self.model.objects.filter_by_user(self.request.user)

    def get_examine_machinery_class(self, raise_exception=True):
        from .examine import CertifiableObjectExamineMachinery

        return CertifiableObjectExamineMachinery

    def get_serializer_context(self):
        context = super(CertifiableObjectExamineViewSet, self).get_serializer_context()
        context.update(self.request.query_params.dict())
        return context


class WorkflowStatusExamineViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = models.WorkflowStatus
    serializer_class = serializers.WorkflowStatusSerializer

    # Hint for api urls we will register
    url_basename = "workflowstatus"

    def get_queryset(self):
        queryset = self.model.objects.filter_by_user(self.request.user)

        # Scope by possible specific CertifiableObject
        parent_pk = self.kwargs.get("parent_pk")
        if parent_pk:
            queryset = queryset.filter(certifiable_object=parent_pk)

        return queryset

    def get_examine_machinery_class(self, raise_exception=True):
        from .examine import WorkflowStatusExamineMachinery

        return WorkflowStatusExamineMachinery

    def get_serializer_context(self):
        context = super(WorkflowStatusExamineViewSet, self).get_serializer_context()
        context.update(self.request.query_params.dict())
        return context

    @action(detail=True, methods=["patch"])
    def transition(self, request, **kwargs):
        workflow_status = self.get_object()

        serializer = serializers.WorkflowStatusStateChangeSerializer(
            **{
                "instance": workflow_status,
                "data": request.data,
                "context": {"request": self.request},
            }
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def progress(self, request, *args, **kwargs):
        obj = self.get_object()
        data = obj.get_progress_analysis(
            user=request.user, as_list=True, skip_certification_check=True
        )
        return Response(data)
