import os
import logging

from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin

from datatableview.views import MultipleDatatableMixin

from axis.core.views.generic import AxisDatatableView, AxisExamineView
from axis.core.mixins import AuthenticationMixin
from .api import examine
from . import models
from . import datatables


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class WorkflowStatusListView(LoginRequiredMixin, AxisDatatableView):
    datatable_class = datatables.WorkflowStatusDatatable
    model = models.WorkflowStatus

    template_name = "base_list.html"

    def determine_workflow(self):
        if not hasattr(self, "_workflow"):
            self._workflow = models.Workflow.objects.get()  # FIXME
        return self._workflow

    def get_queryset(self):
        queryset = super(WorkflowStatusListView, self).get_queryset()
        queryset = queryset.filter_by_user(self.request.user)
        queryset = queryset.filter(certifiable_object__type=self.kwargs["type"])
        return queryset

    def get_add_url(self):
        default_url = reverse("certification:object:add", kwargs=self.kwargs)
        workflow = self.determine_workflow()
        config = workflow.get_config()
        return config.get_object_add_url(object_type=self.kwargs["type"], default=default_url)

    def get_datatable_kwargs(self):
        kwargs = super(WorkflowStatusListView, self).get_datatable_kwargs()
        kwargs["workflow"] = self.determine_workflow()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(WorkflowStatusListView, self).get_context_data(**kwargs)

        workflow = self.determine_workflow()
        config = workflow.get_config()
        object_type = self.kwargs["type"]
        context["verbose_name_plural"] = config.get_object_type_name_plural(object_type=object_type)

        return context


class CertifiableObjectListView(LoginRequiredMixin, AxisDatatableView):
    datatable_class = datatables.CertifiableObjectDatatable
    model = models.CertifiableObject

    template_name = "base_list.html"

    def determine_workflow(self):
        if not hasattr(self, "_workflow"):
            self._workflow = models.Workflow.objects.get()  # FIXME
        return self._workflow

    def get_queryset(self):
        queryset = super(CertifiableObjectListView, self).get_queryset()
        queryset = queryset.filter_by_user(self.request.user).filter(type=self.kwargs["type"])
        return queryset

    def get_add_url(self):
        default_url = reverse("certification:object:add", kwargs=self.kwargs)
        workflow = self.determine_workflow()
        config = workflow.get_config()
        return config.get_object_add_url(object_type=self.kwargs["type"], default=default_url)

    def get_datatable_kwargs(self):
        kwargs = super(CertifiableObjectListView, self).get_datatable_kwargs()
        kwargs["workflow"] = self.determine_workflow()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CertifiableObjectListView, self).get_context_data(**kwargs)

        workflow = self.determine_workflow()
        config = workflow.get_config()
        object_type = self.kwargs["type"]
        context["verbose_name_plural"] = config.get_object_type_name_plural(object_type=object_type)

        return context


class CertifiableObjectExamineView(LoginRequiredMixin, MultipleDatatableMixin, AxisExamineView):
    model = models.CertifiableObject
    template_name = "certification/certifiable_object_examine.html"

    datatable_classes = {
        "buildings": datatables.InlineWorkflowStatusDatatable,
    }

    def get_datatable_classes(self):
        # FIXME: Read object types dynamically
        datatable_classes = super(CertifiableObjectExamineView, self).get_datatable_classes()
        if self.kwargs["type"] == "building":
            del datatable_classes["buildings"]
        return datatable_classes

    def get_queryset(self):
        queryset = super(CertifiableObjectExamineView, self).get_queryset()
        queryset = queryset.filter_by_user(self.request.user).filter(type=self.kwargs["type"])
        return queryset

    def get_machinery(self):
        machineries = {}

        # FIXME: This is the big structural issue: We have no reference to the workflow the user is
        # about to use, so we can't easily obtain a reference.
        self.workflow = models.Workflow.objects.get()

        # Can't rely on self.object.type if the object is unsaved, so use this exclusively
        object_type = self.kwargs["type"]

        kwargs = {
            "create_new": self.create_new,
            "context": {
                "lightweight": True,
                "request": self.request,
                "type": object_type,
                "workflow_id": self.workflow.id,
            },
        }
        kwargs["context"].update(self.request.GET.dict())  # Used for implying form default values

        # CertifiableObject (primary)
        machinery = examine.CertifiableObjectExamineMachinery(instance=self.object, **kwargs)
        machineries[machinery.type_name_slug] = machinery
        self.primary_machinery = machinery

        # WorkflowStatuses
        self.config = self.workflow.get_config()
        if self.config.uses_workflow_status(object_type=object_type):
            queryset = (
                self.object.workflowstatus_set.filter_by_user(self.request.user)
                if self.object.pk
                else []
            )
            machinery_kwargs = kwargs.copy()
            machinery_kwargs["context"] = dict(
                kwargs["context"].copy(),
                **{
                    "max_regions": self.config.get_max_programs(object_type=object_type),
                    "certifiable_object": self.object.id,
                },
            )
            machinery = examine.WorkflowStatusExamineMachinery(objects=queryset, **machinery_kwargs)
            machineries[machinery.type_name_slug] = machinery

        return machineries

    def get_context_data(self, **kwargs):
        context = super(CertifiableObjectExamineView, self).get_context_data(**kwargs)

        object_type = self.kwargs["type"]
        context["program_tab_label"] = self.config.get_eep_program_tab_label(
            object_type=object_type
        )
        context["workflow"] = self.workflow
        context["verbose_name"] = self.config.get_object_type_name(object_type=object_type)

        return context

    # Satellite Datatables stuff
    # FIXME: Generalize for parent-child hierarchy
    def get_buildings_datatable_queryset(self):
        instance = self.get_object()
        if not instance:
            return models.WorkflowStatus.objects.none()
        queryset = models.WorkflowStatus.objects.filter_by_user(self.request.user).filter(
            certifiable_object__type="building"
        )
        queryset = queryset.filter(certifiable_object__parent=instance)
        return queryset


class CertifiableObjectGenerateView(LoginRequiredMixin, RedirectView):
    model = models.CertifiableObject
    permanent = False
    query_string = True

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.generate_certifiable_object(**kwargs)
        return super(CertifiableObjectGenerateView, self).dispatch(request, *args, **kwargs)

    def generate_certifiable_object(self, type, parent_id, workflow_id):
        user = self.request.user
        company = self.request.company
        try:
            workflow = models.Workflow.objects.filter_by_user(user).get(id=workflow_id)
            parent = models.CertifiableObject.objects.filter_by_user(user).get(id=parent_id)
            eep_program = parent.workflowstatus_set.filter_by_user(user).get().eep_program
        except ObjectDoesNotExist:
            raise Http404("Invalid creation context")

        config = workflow.get_config()
        if not config.supports_object_type(object_type=type):
            raise Http404("Unsupported object type for workflow.")

        # Build CertifiableObject
        object_name = "New {}".format(config.get_object_type_name(object_type=type))
        repr_setting = config.get_repr_setting(object_type=type, default=None)
        object_settings = {}
        if repr_setting:
            object_settings[repr_setting] = object_name
        certifiable_object = models.CertifiableObject.objects.create(
            **{
                "owner": company,
                "parent": parent,
                "type": type,
                "name": object_name,
                "settings": object_settings,
            }
        )

        # Build WorkflowStatus
        models.WorkflowStatus.objects.create(
            **{
                "owner": company,
                "workflow": workflow,
                "certifiable_object": certifiable_object,
                "eep_program": eep_program,
                "state": "initial",
            }
        )

        self.instance = certifiable_object

    def get_redirect_url(self, *args, **kwargs):
        return (
            reverse(
                "certification:object:view",
                kwargs={
                    "type": self.kwargs["type"],
                    "pk": self.instance.pk,
                },
            )
            + "?new=1"
        )
