"""views.py: Django filehandling"""

import json
from collections import defaultdict

import datatableview
import datatableview.helpers
from celery.result import EagerResult
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import formats

from axis.company.models import Company
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisCreateView, LegacyAxisDatatableView, AxisDetailView
from axis.filehandling.forms import (
    AsynchronousProcessedDocumentForm,
    TestAsynchronousProcessedDocumentForm,
)
from .models import *

__author__ = "Gaurav Kapoor"
__date__ = "3/27/12 2:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Gaurav Kapoor",
    "Steven Klass",
]

log = logging.getLogger(__name__)


def colored_state(state):
    color = TASK_STATE_COLORS.get(state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)


class AsynchronousProcessedDocumentListView(AuthenticationMixin, LegacyAxisDatatableView):
    model = AsynchronousProcessedDocument
    permission_required = "filehandling.view_asynchronousprocesseddocument"
    show_add_button = False

    datatable_options = {
        "columns": [
            ("Document", ["document"], "get_column_document_data"),
            ("State", ["state"], "get_column_state_data"),
            ("Created Date", "created_date", "get_column_created_date_data"),
            ("Modified Date", "modified_date", "get_column_modified_date_data"),
            ("Company", ["company__name"], "get_column_company_data"),
        ],
        "ordering": ["-modified_date"],
    }

    def get_queryset(self):
        """Narrow this based on your company"""
        return AsynchronousProcessedDocument.objects.filter_by_user(user=self.request.user)

    def get_datatable_options(self):
        options = self.datatable_options.copy()
        options["columns"] = options["columns"][:]

        if not self.request.user.is_superuser:
            options["columns"].pop(4)
        return options

    def get_column_document_data(self, obj, *args, **kwargs):
        text = obj.filename()
        if text is None or len(text) == 0:
            text = "Document {}".format(obj.id)
        return datatableview.helpers.link_to_model(obj, text=text)

    def get_column_state_data(self, obj, *args, **kwargs):
        return colored_state(obj.get_state())

    def get_column_created_date_data(self, obj, *args, **kwargs):
        tz = self.request.user.timezone_preference
        dts = obj.created_date.astimezone(tz)
        return formats.date_format(dts, "SHORT_DATETIME_FORMAT")

    def get_column_modified_date_data(self, obj, *args, **kwargs):
        tz = self.request.user.timezone_preference
        dts = obj.modified_date.astimezone(tz)
        return formats.date_format(dts, "SHORT_DATETIME_FORMAT")

    def get_column_company_data(self, obj, *args, **kwargs):
        return datatableview.helpers.link_to_model(obj.company)


class AsynchronousProcessedDocumentCreateView(AuthenticationMixin, AxisCreateView):
    model = AsynchronousProcessedDocument
    form_class = AsynchronousProcessedDocumentForm
    permission_required = "filehandling.add_asynchronousprocesseddocument"

    def get_context_data(self, **kwargs):
        context = super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
        context["title"] = "Processed Document Upload"
        return context

    def get_form(self, form_class=None):
        form = super(AsynchronousProcessedDocumentCreateView, self).get_form(form_class)
        company_qs = Company.objects.filter(id=self.request.user.company.id)
        form.fields["company"].queryset = company_qs
        form.fields["company"].initial = self.request.user.company
        return form

    def get_task_kwargs(self, form):
        kwargs = self.kwargs.copy()
        kwargs.update(
            dict(
                company_id=self.object.company.id,
                user_id=self.request.user.id,
                result_object_id=self.object.id,
            )
        )

        for key, value in form.cleaned_data.items():
            if key in ["company", "document", "task_name"]:
                continue
            if key not in kwargs.keys():
                if not isinstance(value, (str, int, float)):
                    log.error(
                        "Filehandling not able to handle key %s:%s for " "result_id %s",
                        key,
                        value,
                        self.object.id,
                    )
                    continue
                kwargs[key] = value
        return kwargs

    def form_valid(self, form):
        """Send this off for processing"""

        self.object = form.save(commit=False)
        self.object.company = self.request.user.company

        task = form.cleaned_data["task_name"]

        self.object.task_name = task.name
        self.object.save()

        kwargs = self.get_task_kwargs(form)

        results = task.apply_async(kwargs=kwargs)

        if isinstance(results, EagerResult):
            self.object = AsynchronousProcessedDocument.objects.get(id=self.object.id)
            log.debug("ALWAYS EAGER - Result Received %s", results._state)
            t_result = self.object.result if isinstance(self.object.result, dict) else dict()
            t_result["traceback"] = results._traceback
            t_result["result"] = results._result
            self.object.task_id = results.id
            self.object.result = t_result
            self.object.final_status = results._state
            if isinstance(t_result, dict) and len(t_result.get("errors", [])):
                self.object.final_status = "FAILURE"
            self.object.save()
        else:
            log.debug("Celery task %s dispatched", results.task_id)
            self.object.task_id = results.task_id
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_cancel_url(self):
        return reverse("async_document_list")


class AsynchronousProcessedDocumentDetailView(AuthenticationMixin, AxisDetailView):
    permission_required = "filehandling.view_asynchronousprocesseddocument"
    show_delete_button = False
    show_edit_button = False
    auto_download = False

    def get(self, context, **kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            result = self.get_serialized_data()
            return HttpResponse(json.dumps(result), content_type="application/json")

        if self.auto_download:
            return HttpResponseRedirect(self.get_object().document.url)

        return super(AsynchronousProcessedDocumentDetailView, self).get(context, **kwargs)

    def get_row_logs(self, key, value):
        has_errors = value.pop("has_errors")
        return {"row": key, "logs": value, "has_errors": has_errors}

    def split_by_minute(self, chronological):
        temp = defaultdict(list)
        for string in chronological:
            split = string.index("]") + 1
            key = string[:split]
            message = string[split:]
            temp[key].append(message)
        return temp

    def get_queryset(self):
        return AsynchronousProcessedDocument.objects.filter_by_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(AsynchronousProcessedDocumentDetailView, self).get_context_data(**kwargs)
        self.object.update_results()
        context["task"] = self.object.task_id
        context["state"] = colored_state(self.object.get_state())
        context["exception"] = self.object.get_exception()
        context["complete"] = False
        if self.object.final_status in ["SUCCESS", "FAILURE"]:
            context["complete"] = True
        return context

    def get_serialized_data(self):
        """A quick way to update the status"""

        complete = False
        object = self.get_object()

        try:
            latest = object.result["latest"]
            if isinstance(latest, logging.LogRecord):
                latest = latest.getMessage()
        except (KeyError, TypeError):
            latest = ""

        object.update_results()
        state = object.get_state()
        if object.final_status in ["SUCCESS", "FAILURE"]:
            complete = True

        if settings.CELERY_TASK_ALWAYS_EAGER:
            _result = "Result NOT available when CELERY_TASK_ALWAYS_EAGER"
        else:
            try:
                _result = AsyncResult(object.task_id).result
            except (RuntimeError, ValueError) as err:
                _result = f"{err}"

        valid_types = (str, dict, int, float, list, tuple, set)
        result = _result if isinstance(_result, valid_types) else f"{_result}"
        result = "" if _result is None else result

        data = {
            "complete": complete,
            "state": colored_state(state),
            "latest": latest,
            "result": result,
        }
        return data


class TestAsynchronousProcessedDocument(AsynchronousProcessedDocumentCreateView):
    """This deals with uploading the document.. And our custom clean"""

    form_class = TestAsynchronousProcessedDocumentForm

    def get_context_data(self, **kwargs):
        context = super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
        context["title"] = "Test File Upload"
        return context
