""" Superuser-only views.  Make sure all dispatch() methods are decorated!  """

__author__ = "Autumn Valenta"
__date__ = "07-14-14  2:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import json
import logging
import re
import subprocess
from operator import itemgetter

import datatableview.helpers
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from axis.core.utils import values_to_dict
from .generic import LegacyAxisDatatableView
from .. import forms, AxisSystemMessage

log = logging.getLogger(__name__)
User = get_user_model()


class SuperUserMixin(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(SuperUserMixin, self).dispatch(request, *args, **kwargs)


class DumpRequestHeadersView(SuperUserMixin, TemplateView):
    """Dumps HTTP_* entries from request.META as plaintext."""

    template_name = "debug/dump_headers.txt"

    def render_to_response(self, context, **response_kwargs):
        response_kwargs["content_type"] = "text/plain"
        return super(DumpRequestHeadersView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(DumpRequestHeadersView, self).get_context_data(**kwargs)
        headers = (
            # Convert HTTP_* META items to Title-Case
            (k[5:].title().replace("_", "-"), v)
            for k, v in self.request.META.items()
            if k.startswith("HTTP_")
        )
        headers = sorted(headers, key=itemgetter(0))
        context["headers"] = headers
        return context


class DumpRecentLogView(SuperUserMixin, TemplateView):
    """Tails the current server log for specific types of messages."""

    template_name = "debug/dump_log.html"

    default_lines = 50

    def get_lines(self):
        n = self.request.GET.get("n", self.default_lines)
        try:
            n = int(n)
        except:
            n = self.default_lines
        return "{}".format(n)

    def get_log_data(self):
        path = settings.LOGGING["handlers"]["logfile"]["filename"]
        lines = self.get_lines()
        process = subprocess.Popen(["tail", "-n", lines, path], stdout=subprocess.PIPE)  # nosec
        return process.communicate()[0]

    def get_log_file_length(self):
        path = settings.LOGGING["handlers"]["logfile"]["filename"]
        process = subprocess.Popen(["wc", "-l", path], stdout=subprocess.PIPE)  # nosec
        return int(process.communicate()[0].split()[0])

    def get_context_data(self, **kwargs):
        context = super(DumpRecentLogView, self).get_context_data(**kwargs)
        lines = self.get_log_data().split("\n")
        classifications = {
            "ERROR": "danger",
            "DEBUG": "default",
            "CRITICAL": "danger",
        }
        data = []
        for line in lines:
            match = re.search(r"\] (?P<level>[A-Z]+) \[", line)
            if match:
                level = match.group("level")
            else:
                level = "UNKNOWN"
            classification = classifications.get(level, level.lower())
            data.append((level, classification, line))

        n_lines = self.get_lines()
        context.update(
            {
                "data": data,
                "lines": n_lines,
                "offset_range": range(1, self.get_log_file_length() - int(n_lines) + 1),
            }
        )
        return context


class BaseQueryView(SuperUserMixin, TemplateView):
    template_name = "debug/query.html"


class ExceptionTestView(SuperUserMixin, TemplateView):
    template_name = "debug/dump_log.html"

    def get(self, request, *args, **kwargs):
        raise IOError("Exception Test Raised an error")


class ModelHistoryView(SuperUserMixin, LegacyAxisDatatableView):
    model = None
    template_name = "base_list.html"

    datatable_options = {
        "ordering": ("-history_id",),
    }

    show_add_button = False

    def get(self, *args, **kwargs):
        if self.model is None:
            return HttpResponseBadRequest("No model label given.")
        self.model_label = self.model
        self.original_model = apps.get_model(*self.model_label.split("."))
        self.model = self.original_model.history.model
        return super(ModelHistoryView, self).get(*args, **kwargs)

    def _get_datatable_options(self):
        first_call = not hasattr(self, "_datatable_options")
        options = super(ModelHistoryView, self)._get_datatable_options()

        if first_call:
            columns = options["columns"][:-4]
            columns[1:1] = options["columns"][-4:]
            options["columns"] = [("unicode", None, "get_column_unicode_data")] + columns
        return options

    def preload_record_data(self, instance):
        return self.original_model.objects.get(id=instance.id)

    def get_column_unicode_data(self, instance, real_object, *args, **kwargs):
        return datatableview.helpers.link_to_model(real_object)

    def get_column_history_user_data(self, instance, *args, **kwargs):
        if instance.history_user:
            return datatableview.helpers.link_to_model(instance.history_user)
        return ""


class SystemMessengerView(SuperUserMixin, FormView):
    template_name = "core/system_messenger.html"
    form_class = forms.SystemMessengerForm
    success_url = reverse_lazy("system_messenger")

    initial = {
        "level": "system",
        "sticky_alert": True,
        "cc": True,
    }

    def form_valid(self, form):
        recipients_list = [{"company": company} for company in form.cleaned_data["companies"]]
        if form.cleaned_data["cc"]:
            recipients_list.append({"user": self.request.user})

        for recipient_info in recipients_list:
            msg = AxisSystemMessage()
            msg.title = form.cleaned_data["title"] or ""
            msg.content = form.cleaned_data["content"] or ""
            msg.send(
                **recipient_info,
            )

        messages.success(
            self.request,
            "Bombs away, {}!  {} companies have been messaged!".format(
                *(
                    self.request.user.first_name,
                    len(form.cleaned_data["companies"]),
                )
            ),
        )

        # Redirect
        return super(SystemMessengerView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SystemMessengerView, self).get_context_data(**kwargs)

        from axis.company.models import Company

        values = list(Company.objects.values("id", "company_type", "name"))
        info = values_to_dict(values, "company_type", value_as_list=True)
        context["companies_info"] = json.dumps(info)

        return context
