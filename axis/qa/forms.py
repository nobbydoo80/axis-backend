"""forms.py: Django qa"""

__author__ = "Steven Klass"
__date__ = "12/20/13 6:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django import forms
from django.apps import apps

from django.contrib.auth import get_user_model
from axis.qa.models import QARequirement, QANote
from .models import QAStatus, ObservationType
from .state_machine import QAStateMachine
from . import strings
from axis.examine.forms import AjaxBase64FileFormMixin
from axis.filehandling.models import CustomerDocument

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class QAStatusForm(forms.ModelForm):
    new_state = forms.ChoiceField(choices=(), required=False, label="New Status")
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    observation_types = forms.ModelMultipleChoiceField(
        queryset=ObservationType.objects.none(), required=False, label="Add New Observations"
    )

    # note_document = forms.FileField(required=False, label='Note Document/Photo')

    # Fields we care about at different times in the Statuses life.
    field_map = {
        "create": (
            "requirement",
            "observation_types",
            "qa_designee",
            "hirl_verifier_points_reported",
            "hirl_verifier_points_awarded",
            "hirl_certification_level_awarded",
            "hirl_badges_awarded",
            "hirl_commercial_space_confirmed",
            "hirl_reviewer_wri_value_awarded",
            "hirl_water_sense_confirmed",
        ),
        "update": (
            "new_state",
            "note",
            "result",
            "observation_types",
            "qa_designee",
            "hirl_verifier_points_reported",
            "hirl_verifier_points_awarded",
            "hirl_certification_level_awarded",
            "hirl_badges_awarded",
            "hirl_commercial_space_confirmed",
            "hirl_reviewer_wri_value_awarded",
            "hirl_water_sense_confirmed",
        ),
    }

    class Meta:
        model = QAStatus
        fields = [
            "requirement",
            "result",
            "correction_types",
            "has_observations",
            "qa_designee",
            "has_failed",
            "new_state",
            "note",
            "observation_types",
            "hirl_verifier_points_reported",
            "hirl_verifier_points_awarded",
            "hirl_certification_level_awarded",
            "hirl_badges_awarded",
            "hirl_commercial_space_confirmed",
            "hirl_reviewer_wri_value_awarded",
            "hirl_water_sense_confirmed",
        ]
        labels = {"qa_designee": "QA Designee"}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        content_object = kwargs.pop("content_object")
        super(QAStatusForm, self).__init__(*args, **kwargs)

        self.setup_viewable_fields(user)
        self.setup_field_querysets(user, content_object)

        if self.instance.pk:
            self.fields[
                "new_state"
            ].choices = self.instance.get_possible_transition_choices_for_user(user)

            self.fields[
                "hirl_certification_level_awarded"
            ].choices = self.instance.get_hirl_certification_level_choices()

            if user.is_customer_hirl_company_member():
                self.fields["hirl_commercial_space_confirmed"] = forms.ChoiceField(
                    choices=[("false", "N/A"), ("true", "Confirmed")], initial="false"
                )
                self.fields["hirl_water_sense_confirmed"] = forms.ChoiceField(
                    choices=[("false", "N/A"), ("true", "Confirmed")], initial="false"
                )

            home_status = getattr(self.instance, "home_status", None)
            customer_hirl_project = None
            if home_status:
                customer_hirl_project = getattr(home_status, "customer_hirl_project", None)

            if home_status.eep_program.slug in [
                "ngbs-sf-whole-house-remodel-2020-new",
                "ngbs-mf-whole-house-remodel-2020-new",
                "ngbs-sf-whole-house-remodel-2015-new",
                "ngbs-mf-whole-house-remodel-2015-new",
                "ngbs-sf-whole-house-remodel-2012-new",
                "ngbs-mf-whole-house-remodel-2012-new",
            ] or (
                customer_hirl_project
                and (
                    customer_hirl_project.is_accessory_structure
                    or customer_hirl_project.is_accessory_dwelling_unit
                )
            ):
                del self.fields["hirl_reviewer_wri_value_awarded"]

            if home_status.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST:
                del self.fields["hirl_verifier_points_reported"]
                del self.fields["hirl_verifier_points_awarded"]
                del self.fields["hirl_certification_level_awarded"]
                del self.fields["hirl_badges_awarded"]
                del self.fields["hirl_commercial_space_confirmed"]
                self.fields["hirl_reviewer_wri_value_awarded"].required = True

            if home_status.eep_program.slug in customer_hirl_app.LAND_DEVELOPMENT_PROGRAM_LIST:
                del self.fields["hirl_badges_awarded"]
                del self.fields["hirl_commercial_space_confirmed"]
                del self.fields["hirl_reviewer_wri_value_awarded"]
                del self.fields["hirl_water_sense_confirmed"]

                if customer_hirl_project:
                    from axis.customer_hirl.models import HIRLProject

                    if (
                        customer_hirl_project.land_development_project_type
                        == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT
                    ):
                        del self.fields["hirl_verifier_points_reported"]
                        del self.fields["hirl_verifier_points_awarded"]

    def setup_viewable_fields(self, user):
        field_map = list(self.field_map["update" if self.instance.pk else "create"])

        for field in self.fields.keys():
            if field not in field_map:
                self.fields[field].widget = self.fields[field].hidden_widget()

        if user.company.company_type not in ["qa", "provider"] and not user.is_superuser:
            del self.fields["observation_types"]

    def setup_field_querysets(self, user, content_object):
        self.fields["requirement"].queryset = QARequirement.objects.none()
        if content_object and content_object.pk:
            self.fields["requirement"].queryset = QARequirement.objects.filter_for_add(
                content_object, user
            )

        # for field in ['home_status', 'owner']:
        #     self.fields[field].queryset = self.fields[field].queryset.none()

        if "observation_types" in self.fields:
            queryset = ObservationType.objects.filter_by_user(user)
            self.fields["observation_types"].choices = queryset.values_list("id", "name")

        if "qa_designee" in self.fields:
            if user.is_customer_hirl_company_member():
                self.fields["qa_designee"].queryset = User.objects.filter(
                    hirluserprofile__is_qa_designee=True, is_active=True
                )
            else:
                self.fields["qa_designee"].queryset = user.company.users.filter(is_active=True)

            if not self.instance.pk:
                self.initial["qa_designee"] = user

    def clean(self):
        cleaned_data = super(QAStatusForm, self).clean()

        new_state = cleaned_data.get("new_state")
        result = cleaned_data.get("result")
        note = cleaned_data.get("note")

        notes_required_transitions = [
            "in_progress_to_correction_required",
            "correction_required_to_correction_received",
            "correction_received_to_correction_required",
        ]

        to_complete_transitions = ["correction_received_to_complete", "in_progress_to_complete"]

        if new_state in notes_required_transitions:
            if note in ["", None]:
                description = QAStateMachine.transitions[new_state].description
                raise forms.ValidationError(
                    strings.MISSING_REQUIRED_NOTE.format(state_description=description)
                )

        if new_state in to_complete_transitions:
            if result in ["", None]:
                raise forms.ValidationError(strings.MISSING_RESULT)

        if result not in ["", None]:
            if new_state not in to_complete_transitions:
                raise forms.ValidationError(strings.INCORRECT_STATE_FOR_COMPLETE)

        return cleaned_data


class QANoteForm(forms.ModelForm):
    observations = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = QANote
        fields = ["qa_status", "note", "user", "content_type", "object_id", "last_update"]


class ObservationTypeForm(forms.ModelForm):
    class Meta:
        model = ObservationType
        fields = ("name",)


class StateTransitionForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none())
    new_state = forms.ChoiceField(choices=(), required=False)
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    class Meta:
        model = QAStatus
        exclude = ("home_status", "state")
        widgets = {
            "owner": forms.HiddenInput,
            "user": forms.HiddenInput,
        }

    def clean(self):
        cleaned_data = super(StateTransitionForm, self).clean()
        if cleaned_data.get("new_state") in [
            "in_progress_to_correction_required",
            "correction_required_to_correction_received",
            "correction_received_to_correction_required",
        ]:
            if cleaned_data.get("note") in ["", None]:
                description = QAStateMachine.transitions[cleaned_data["new_state"]].description
                raise forms.ValidationError(
                    strings.MISSING_REQUIRED_NOTE.format(state_description=description)
                )
        if cleaned_data.get("new_state") in [
            "correction_received_to_complete",
            "in_progress_to_complete",
        ]:
            if cleaned_data.get("result") in ["", None]:
                raise forms.ValidationError(strings.MISSING_RESULT)
        if cleaned_data.get("result") not in ["", None]:
            if cleaned_data.get("new_state") not in [
                "in_progress_to_complete",
                "correction_received_to_complete",
            ]:
                raise forms.ValidationError(strings.INCORRECT_STATE_FOR_COMPLETE)
        return cleaned_data


class QADocumentCustomerHIRLForm(AjaxBase64FileFormMixin.for_fields(["document"]), forms.ModelForm):
    class Meta:
        model = CustomerDocument
        fields = ("document", "description")

    def __init__(self, *args, **kwargs):
        """Accept extra kwargs `allow_multiple` and `raw_field_only`.

        NOTE: `raw_field_only` is an internal kwarg from the `AjaxBase64FileFormMixin` base, which
        drops all fields but `document_raw` for trivial form cleaning of that field in isolation.
        """

        allow_multiple = kwargs.pop("allow_multiple", False)
        raw_file_only = kwargs.get("raw_file_only")
        super(QADocumentCustomerHIRLForm, self).__init__(*args, **kwargs)

        # The document field will not exist when we're expecting only raw inputs.
        if not raw_file_only:
            self.fields["document"].widget.attrs["multiple"] = allow_multiple
