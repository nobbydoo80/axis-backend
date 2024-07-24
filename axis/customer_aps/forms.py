"""forms.py: Django eep.forms"""


import logging

from django import forms
from django.utils.safestring import mark_safe

from django_select2.forms import Select2Widget
from localflavor.us.forms import USStateField

from axis.company.models import Company
from axis.filehandling.forms import AsynchronousProcessedDocumentForm
from axis.filehandling.models import AsynchronousProcessedDocument
import axis
from axis.home.models import Home
from axis.subdivision.models import Subdivision
from .models import APSHome, SMART_TSTAT_ELIGIBILITY, SMART_TSTAT_MODELS, APSSmartThermostatOption

__author__ = "Steven Klass"
__date__ = "1/30/12 8:05 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class UnattachedAPSHomeChoiceField(forms.ModelChoiceField):
    use_raw_address = False

    def label_from_instance(self, obj):
        return mark_safe(
            obj.get_home_address_display(
                include_lot_number=True,
                include_confirmed=True,
                include_city_state_zip=True,
                raw=self.use_raw_address,
            )
        )


class APSHomeManualMatchForm(forms.ModelForm):
    home = UnattachedAPSHomeChoiceField(
        queryset=Home.objects.none(), widget=Select2Widget, help_text="Axis Home", required=False
    )

    class Meta:
        model = APSHome
        fields = ["home"]

    def __init__(self, user, *args, **kwargs):
        super(APSHomeManualMatchForm, self).__init__(*args, **kwargs)
        if user.company.display_raw_addresses:
            self.fields["home"].use_raw_address = True


class APSHomeCoreModelForm(forms.ModelForm):
    """Baseline model form"""

    class Meta:
        model = APSHome
        exclude = ("latitude", "longitude", "confirmed_address", "address_override")
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }


class APSHomeModelForm(APSHomeCoreModelForm):
    """This is used in the views"""

    class Meta:
        model = APSHome
        fields = (
            "raw_lot_number",
            "raw_street_number",
            "raw_prefix",
            "raw_street_name",
            "raw_suffix",
            "raw_street_line_2",
            "raw_city",
            "raw_state",
            "raw_zip",
            "home",
            "geocode_response",
        )
        labels = {
            "raw_lot_number": "Lot Number",
            "raw_street_number": "Street Number",
            "raw_prefix": "Prefix",
            "raw_street_name": "Street Name",
            "raw_suffix": "Suffix",
            "raw_city": "City",
            "raw_state": "State",
            "raw_zip": "ZIP Code",
            "home": "Axis Home",
        }
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }


class APSHomeStringForm(APSHomeModelForm):
    """
    This is a form which accepts strings for foreign keys and will attempt to make it work.
    """

    lot_number = forms.CharField(max_length=16, required=False)
    street_line1 = forms.CharField(max_length=100, required=False)
    street_line2 = forms.CharField(max_length=100, required=False)
    zipcode = forms.CharField(max_length=15, required=False)

    premise_id = forms.CharField(required=True)
    raw_city = forms.CharField(required=True)
    raw_state = USStateField(required=True)
    raw_zip = forms.CharField(required=True)
    meterset_date = forms.DateField(required=True)

    class Meta:
        exclude = ("is_active", "aps_id")
        model = APSHome

    def clean_suffix(self):
        if self.cleaned_data.get("suffix") in ["TRL", "GLN"]:
            return self.cleaned_data.get("suffix")[0:2]
        self.cleaned_data.get("suffix")


class APSBulkHomeAsynchronousProcessedDocumentForm(AsynchronousProcessedDocumentForm):
    """This deals with uploading the document.. And our custom clean"""

    def clean_task_name(self):
        from .tasks import process_metersets_task

        log.info("APS Assignment of the task name")
        return process_metersets_task

    def clean(self):
        cleaned_data = super(APSBulkHomeAsynchronousProcessedDocumentForm, self).clean()
        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data


class APSSmartThermostatOptionsForm(forms.ModelForm):
    """Model form for subdivision APS thermostat options"""

    eligibility = forms.ChoiceField(choices=SMART_TSTAT_ELIGIBILITY)
    models = forms.MultipleChoiceField(
        choices=sorted(SMART_TSTAT_MODELS, key=lambda v_k: v_k[1].lower()), required=False
    )

    class Meta:
        """Meta options"""

        model = Subdivision
        fields = ("eligibility", "models")

    def __init__(self, *args, **kwargs):
        super(APSSmartThermostatOptionsForm, self).__init__(*args, **kwargs)
        try:
            if self.instance.pk and self.instance.aps_thermostat_option:
                self.fields["eligibility"].initial = self.instance.aps_thermostat_option.eligibility
                models = self.instance.aps_thermostat_option.models
                if not isinstance(models, set):
                    models = eval(models)
                self.fields["models"].initial = models
        except APSSmartThermostatOption.DoesNotExist:
            pass
