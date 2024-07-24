"""views.py: Django qa"""


import json
import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    AxisListView,
    AxisCreateView,
    AxisUpdateView,
    AxisDeleteView,
    AxisDetailView,
    AjaxableResponseMixin,
)
from axis.qa import messages
from axis.qa.forms import StateTransitionForm
from axis.qa.models import QAStatus, QANote
from axis.qa.utils import (
    get_content_object_data_for_qa_messages,
    get_qa_message_context,
)

__author__ = "Steven Klass"
__date__ = "12/20/13 6:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class QAListView(AxisListView):
    model = QAStatus


class QADetailView(AxisDetailView):
    model = QAStatus


class QACreateView(AxisCreateView):
    model = QAStatus


class QAUpdateView(AxisUpdateView):
    model = QAStatus


class QADeleteView(AxisDeleteView):
    model = QAStatus


class SetStateView(AuthenticationMixin, AjaxableResponseMixin, AxisUpdateView):
    form_class = StateTransitionForm
    success_message = None
    # permission_required = 'qa.change_qastatus'
    template_name = "qa/qastate_form.html"

    def get_template_names(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            self.template_name_suffix = "_ajax{}".format(self.template_name_suffix)
            return [
                (
                    "{}/{}{}.html".format(
                        self.object._meta.app_label,
                        self.object._meta.object_name.lower(),
                        self.template_name_suffix,
                    )
                )
            ]
        return super(SetStateView, self).get_template_names()

    def get_queryset(self):
        """Filters objects by user company."""
        return QAStatus.objects.filter_by_user(user=self.request.user)

    def get_form(self, form_class=None):
        form = super(SetStateView, self).get_form(form_class)
        choices = self.object.get_possible_transition_choices_for_user(self.request.user)
        form.fields["new_state"].choices = choices
        if not (len(choices)):
            form.fields["new_state"].widget = forms.HiddenInput()
        if self.object.state in ["correction_required", "complete"]:
            form.fields["result"].widget = forms.HiddenInput()
            form.fields["note"].label = "Add Note"
            form.fields["note"].required = True
        if self.request.user.company.id != self.object.owner.id:
            form.fields["result"].widget = forms.HiddenInput()
            form.fields["note"].required = True
        form.fields["user"].queryset = User.objects.filter(id=self.request.user.id)
        form.fields["user"].initial = self.request.user
        form.fields["user"].widget = forms.HiddenInput()
        return form

    def get_success_url(self):
        """Redirect to the associated ``Home``."""
        return self.object.home_status.home.get_absolute_url()

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        note = cleaned_data.pop("note", None)
        new_state = cleaned_data.pop("new_state")
        if new_state:
            self.object.make_transition(new_state)
            msg, target = None, None
            if new_state in [
                "in_progress_to_correction_required",
                "correction_received_to_correction_required",
            ]:
                # Send message to rater
                target = self.object.home_status.company
                msg = messages.QaCorrectionRequiredMessage()
            if new_state == "correction_required_to_correction_received":
                # Send message to QA Company
                target = self.object.owner
                msg = messages.QaCorrectionReceivedMessage()
            if msg:
                qa_message_data = get_content_object_data_for_qa_messages(self.object)
                context = get_qa_message_context(self.object, qa_message_data)
                msg(url=context["action_url"]).send(context=context, company=target)

        if cleaned_data.get("result"):
            form.save()
        if note:
            ct = ContentType.objects.get_for_model(self.object.home_status)
            ct_id = self.object.home_status.id
            QANote.objects.create(
                qa_status=self.object,
                note=note,
                user=self.request.user,
                content_type=ct,
                object_id=ct_id,
            )
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
        return HttpResponseRedirect(self.get_success_url())
