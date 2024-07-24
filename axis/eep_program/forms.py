"""forms.py: Django eep_program"""


import logging
from decimal import Decimal

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import ModelForm

from axis.core.widgets import BigSelectMultiple
from axis.company.models import Company
from .models import EEPProgram
from axis.checklist.models import CheckList
from axis.annotation.models import Type

__author__ = "Steven Klass"
__date__ = "3/2/12 11:28 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ModelMultipleChoiceSlugField(forms.ModelMultipleChoiceField):
    """Customizes forms.ModelMultipleChoiceField"""

    def label_from_instance(self, obj):
        """Formatting label"""
        return "({}) {}".format(obj.slug, "{}".format(obj) or "-")


class EEPProgramForm(ModelForm):
    """Abstract for modifying Company"""

    sponsor = forms.ModelChoiceField(queryset=Company.objects.none())
    certifiable_by = forms.ModelMultipleChoiceField(queryset=Company.objects.none())
    required_checklists = forms.ModelMultipleChoiceField(
        queryset=CheckList.objects.none(), widget=BigSelectMultiple
    )
    required_annotation_types = ModelMultipleChoiceSlugField(
        queryset=Type.objects.none(), widget=BigSelectMultiple
    )

    class Meta:
        model = EEPProgram
        exclude = ("slug", "metrics")

    def __init__(self, user, *args, **kwargs):
        super(EEPProgramForm, self).__init__(*args, **kwargs)

        self.fields["sponsor"].queryset = self._get_sponsor_queryset(user)
        self.fields["required_checklists"].queryset = self._get_required_checklists_queryset(
            user.company
        )
        self.fields[
            "required_annotation_types"
        ].queryset = self._get_required_annotation_types_queryset(user)
        self.fields["certifiable_by"].queryset = self._get_certifiable_by_queryset(user.company)
        self.fields["comment"].widget.attrs["rows"] = 3
        self.fields["opt_in"].required = False

        if not self.instance.pk:
            if user.company.is_eep_sponsor:
                # self.fields['sponsor'].widget = self.fields['sponsor'].hidden_widget()
                self.fields["sponsor"].initial = user.company
        else:
            self.fields["opt_in"].widget.attrs["disabled"] = True
            self.fields["sponsor"].initial = self.instance.owner.id

    def _get_sponsor_queryset(self, user):
        """Gets sponsor field queryset"""
        comp_ids = list(
            EEPProgram.objects.filter_potential_sponsors_for_user(user).values_list("id", flat=True)
        )
        if self.instance and self.instance.pk:
            comp_ids.append(self.instance.owner.id)
        else:
            comp_ids.append(user.company.id)
        return Company.objects.filter(id__in=comp_ids)

    @staticmethod
    def _get_required_checklists_queryset(company):
        """Gets required_checklists field queryset"""
        return CheckList.objects.filter_by_company(company)

    @staticmethod
    def _get_required_annotation_types_queryset(user):
        """Gets required_annotation_types field queryset"""
        return Type.objects.filter_by_user(user)

    @staticmethod
    def _get_certifiable_by_queryset(company):
        """Gets certifiable_by field queryset"""
        return Company.objects.filter_by_company(company, include_self=True)

    def clean_per_point_adder(self):
        """Cleans per_point_adder attr"""
        data = self.cleaned_data.get("per_point_adder")
        return data if data is not None else Decimal(0.0)

    def clean_builder_incentive_dollar_value(self):
        """Cleans builder_incentive_dollar_value attr"""
        data = self.cleaned_data.get("builder_incentive_dollar_value", "0.0")
        return data if data is not None else Decimal(0.0)

    def clean_rater_incentive_dollar_value(self):
        """Cleans rater_incentive_dollar_value attr"""
        data = self.cleaned_data.get("rater_incentive_dollar_value", "0.0")
        return data if data is not None else Decimal(0.0)

    def clean(self):  # noqa: MC0001
        """Validate the checklist"""
        data = self.cleaned_data

        if data.get("program_visibility_date") and not data.get("program_start_date"):
            raise forms.ValidationError("You must have a start date with a program visibility date")

        if data.get("program_visibility_date") and data.get("program_start_date"):
            if data["program_visibility_date"] > data["program_start_date"]:
                raise forms.ValidationError(
                    "You cannot have a program visibility date after it starts."
                )

        if data.get("program_close_date") and data.get("program_start_date"):
            if data["program_close_date"] < data["program_start_date"]:
                raise forms.ValidationError(
                    "You cannot have a program closed date before it starts."
                )

        if data.get("program_close_date") and data.get("program_end_date"):
            if data["program_end_date"] < data["program_close_date"]:
                raise forms.ValidationError("You cannot have a program end before it closes.")

        if data.get("program_end_date") and data.get("program_start_date"):
            if data["program_end_date"] < data["program_start_date"]:
                raise forms.ValidationError("You cannot have a program end date before it starts.")

        if data.get("min_hers_score") and data.get("max_hers_score"):
            if data["max_hers_score"] < data["min_hers_score"]:
                raise forms.ValidationError(
                    "Max HERs  Score needs to be more than the Min HERs Score"
                )

        # if not data['is_legacy'] and 'required_checklists' not in data:
        #     raise forms.ValidationError, "Only Legacy Programs do not require a checklist"
        if not data["is_legacy"] and "required_checklists" in data:
            for checklist in data["required_checklists"]:
                if not checklist.public:
                    if checklist.group != data["sponsor"].group:
                        raise forms.ValidationError(
                            "This checklist is not owned by the sponsor and is not public.  "
                            "It must be public to attach to this sponsor."
                        )

        if data.get("per_point_adder") and not data.get("require_rem_data"):
            raise forms.ValidationError(
                "You must also select Requre Rem Data if you use a the Per-Point Adder"
            )

        # If we are adding an entry make sure it doesn't exist.
        if not self.initial.get("id"):
            try:
                EEPProgram.objects.get(name__iexact=data.get("name"))
                err = "{} already exists - You will need to use a different program name.".format(
                    data.get("name", "none")
                )
                raise forms.ValidationError(err)
            except ObjectDoesNotExist:
                pass

        return data
