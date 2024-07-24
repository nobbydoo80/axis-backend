"""forms.py: Django incentive_payment"""


import logging
import datetime

from django import forms

from django_select2.forms import Select2Widget

from axis.core.fields import ApiModelChoiceField
from axis.company.fields import BuilderOrganizationChoiceApiWidget
from axis.eep_program.models import EEPProgram
from axis.home.models import Home, EEPProgramHomeStatus
from axis.subdivision.models import Subdivision
from .models import IncentiveDistribution, IncentivePaymentStatus
from .strings import *

__author__ = "Steven Klass"
__date__ = "3/16/12 1:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IncentiveDistributionUpdateForm(forms.ModelForm):
    """This is the basic form for updates.  The differences is the exclusion of stats"""

    class Meta:
        model = IncentiveDistribution

        # omg, just pick one, they don't work together, so expected behavior is ambiguous here.
        include = (
            "customer",
            "check_requested_date",
            "paid_date",
            "check_number",
            "total",
            "comment",
        )
        exclude = ("status", "company", "check_to_name", "invoice_number")

    def clean(self):
        data = super(IncentiveDistributionUpdateForm, self).clean()

        if data.get("paid_date") and not data.get("check_number"):
            raise forms.ValidationError(ERROR_NO_CHECK_NUMBER)

        if data.get("check_number") and not data.get("paid_date"):
            raise forms.ValidationError(ERROR_NO_PAID_DATE)

        if data.get("check_requested_date") and data.get("paid_date"):
            if data.get("paid_date") < data.get("check_requested_date"):
                raise forms.ValidationError(ERROR_PAID_DATE_BEFORE_CHECK_REQUEST_DATE)

        if data.get("check_requested_date"):
            delta = datetime.date.today() + datetime.timedelta(days=3)
            if data.get("check_requested_date") > delta:
                raise forms.ValidationError(ERROR_DATE_IN_FUTURE)

        if data.get("paid_date"):
            delta = datetime.date.today() + datetime.timedelta(days=3)
            if data.get("paid_date") > delta:
                raise forms.ValidationError(ERROR_DATE_IN_FUTURE)
        if data.get("check_number"):
            existing = IncentiveDistribution.objects.filter(check_number=data.get("check_number"))
            if hasattr(self.instance, "company"):
                existing = existing.filter(company=self.instance.company)
            if getattr(self.instance, "pk", None) is not None:
                existing = existing.exclude(id=self.instance.pk)
            if existing.count():
                msg = ERROR_CHECK_NUMBER_ALREADY_EXISTS.format(
                    ",".join(existing.values_list("invoice_number", flat=True))
                )
                raise forms.ValidationError(msg)
        if data.get("total") and data["total"] != self.instance.total and not data["comment"]:
            raise forms.ValidationError("If you change the total a comment must be added")
        return data


class IncentiveDistributionForm(IncentiveDistributionUpdateForm):
    """This is the Incentive Distribution Form"""

    stats = forms.MultipleChoiceField()

    class Meta:
        model = IncentiveDistribution

        # omg, just pick one, they don't work together, so expected behavior is ambiguous here.
        include = ("customer", "check_requested_date", "paid_date", "check_number", "comment")
        exclude = ("status", "company", "check_to_name", "total", "invoice_number")

    def clean(self):
        data = super(IncentiveDistributionForm, self).clean()

        if not data.get("stats"):
            raise forms.ValidationError(ERROR_NO_HOMES_SUPPLIED)

        # A home status can only show up once for a builder..
        stat_ids = [int(x) for x in data.get("stats", [])]
        stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)
        homes = Home.objects.filter(id__in=[x.home_status.home_id for x in stats.all()])
        builder = data.get("customer", None)
        company_type = None
        if builder and builder.company_type == "builder":
            company_type = "builder"
            builder = builder.name
            for home in homes:
                if builder is None:
                    builder = home.get_builder().name
                if home.get_builder().name != builder:
                    raise forms.ValidationError(
                        ERROR_MULTIPLE_BUILDERS.format(builder, home.get_builder().name)
                    )
        if company_type != "builder":
            return data

        return data


class IncentivePaymentStatusRevertForm(forms.Form):
    stats = forms.MultipleChoiceField()
    annotation = forms.CharField(max_length=500)

    def clean_stats(self):
        data = self.cleaned_data["stats"]
        stats = IncentivePaymentStatus.objects.filter(id__in=data)

        for stat in stats:
            if stat.state not in ["payment_pending", "ipp_payment_automatic_requirements"]:
                raise forms.ValidationError(
                    UNABLE_TO_REVERT_HOME_NO_HOME.format(ostate=stat.get_state_display())
                )

        return data


class IncentivePaymentStatusUndoForm(forms.Form):
    stats = forms.MultipleChoiceField()
    annotation = forms.CharField(max_length=500)
    old_state = forms.CharField(max_length=20)

    def clean_stats(self):
        data = self.cleaned_data["stats"]
        stats = IncentivePaymentStatus.objects.filter(id__in=data)

        for stat in stats:
            if stat.state != "ipp_payment_failed_requirements":
                raise forms.ValidationError(
                    UNABLE_TO_REVERT_HOME_NO_HOME.format(ostate=stat.get_state_display())
                )

        return data


class IncentiveDistributionReportForm(forms.Form):
    """The first complicated form"""

    builder_org = ApiModelChoiceField(
        widget=BuilderOrganizationChoiceApiWidget, help_text=None, required=False
    )
    subdivision = forms.ModelChoiceField(
        queryset=Subdivision.objects.all(), widget=Select2Widget, help_text=None, required=False
    )
    eep_program = forms.ModelMultipleChoiceField(queryset=EEPProgram.objects.none(), required=False)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def clean(self):
        data = self.cleaned_data
        if not data.get("builder_org") and not data.get("subdivision"):
            raise forms.ValidationError(ERROR_NO_BUILDER_ORG_OR_SUBDIVISION)

        if data.get("builder_org") and data.get("subdivision"):
            if data["subdivision"].builder_org != data.get("builder_org"):
                err = ERROR_BUILDER_ORG_DOES_NOT_REPRESENT_SUBDIVISION
                raise forms.ValidationError(
                    err.format(
                        data.get("builder_org"),
                        data.get("subdivision"),
                        data.get("subdivision").builder_org,
                    )
                )

        if data.get("start_date") and data.get("start_date") > datetime.date.today():
            raise forms.ValidationError(ERROR_START_END_DATE_IN_FUTURE)

        if data.get("end_date") and data.get("end_date") > datetime.date.today():
            raise forms.ValidationError(ERROR_START_END_DATE_IN_FUTURE)

        if (
            data.get("end_date")
            and data.get("start_date")
            and data.get("end_date") < data.get("start_date")
        ):
            raise forms.ValidationError(ERROR_END_DATE_BEFORE_START_DATE)

        return data


class IncentivePaymentStatusForm(forms.Form):
    """Incentive Payment Filter"""

    builder = forms.ChoiceField(choices=[("", "---------")], required=False)
    subdivision = forms.ChoiceField(choices=[("", "---------")], required=False)
    eep_program = forms.ChoiceField(choices=[("", "---------")], required=False, label="Program")
    provider = forms.ChoiceField(choices=[("", "---------")], required=False)
    all_choices = IncentivePaymentStatus.get_state_choices()
    choices = [("", "---------")]
    choices += [
        x
        for x in all_choices
        if x[0] not in ["complete", "payment_pending", "ipp_payment_requirements"]
    ]
    state = forms.ChoiceField(choices=choices, required=False, initial="pending")
    activity_start = forms.DateField(required=False)
    activity_stop = forms.DateField(required=False)


class IncentivePaymentStatusAnnotationForm(forms.Form):
    """Allows you to quickly add annotations"""

    all_choices = IncentivePaymentStatus.get_state_choices()
    # This filtering is done dynamically on the client..
    choices = [("", "---------")] + all_choices
    new_state = state = forms.ChoiceField(choices=choices, required=False)
    annotation = forms.CharField(required=False, widget=forms.Textarea())
    stats = forms.MultipleChoiceField()

    def clean(self):
        data = self.cleaned_data
        if data["new_state"] in [
            "ipp_payment_failed_requirements",
            "start",
            "resubmit-failed",
        ]:
            if data["annotation"] in ["", None]:
                raise forms.ValidationError(ERROR_NO_ANNOTATION)
        return data
