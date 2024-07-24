"""forms.py: Django floorplan"""
import datetime
import logging
from functools import lru_cache

from django import forms
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django_select2.forms import Select2Widget

from axis.company.models import Company
from axis.core.fields import ApiModelChoiceField
from axis.ekotrope.fields import UnattachedProjectChoiceWidget
from axis.ekotrope.models import HousePlan
from axis.examine.forms import AjaxBase64FileFormMixin
from axis.remrate_data.fields import UnattachedSimulationChoiceWidget
from axis.subdivision.fields import SubdivisionChoiceWidget
from axis.subdivision.models import THERMOSTAT_CHOICES
from . import strings
from .fields import FloorplanChoiceWidget
from .models import Floorplan

__author__ = "Steven Klass"
__date__ = "3/3/12 5:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HomeStatusFloorplanForm(
    AjaxBase64FileFormMixin.for_fields(["remrate_data_file"]), forms.ModelForm
):
    """Home Status Floorplan Form"""

    # remrate_data_file stuff for "raw_file_only" setting
    valid_content_types = ["application/blg"]

    # Add-existing mode

    # Non-db field for tracking what the user wants to do about associating floorplans to the object
    existing_floorplan = ApiModelChoiceField(
        widget=FloorplanChoiceWidget, required=False, label="Floorplan"
    )

    # Add-ekotrope mode
    ekotrope_project = ApiModelChoiceField(widget=UnattachedProjectChoiceWidget, required=False)
    ekotrope_houseplan = forms.ModelChoiceField(queryset=HousePlan.objects.none(), required=False)

    # Normal mode
    name = forms.CharField(max_length=64)  # required=True so slug generation works
    remrate_target = ApiModelChoiceField(
        widget=UnattachedSimulationChoiceWidget,
        required=False,
        help_text="Enter name, development or builder name.",
    )

    # Helper attribute
    # This is poked into the form externally, after it is instantiated.  Sending extra data to
    # the constructor isn't easy because of the way the runtime-generated FormSet handles the
    # instantiation.
    _owner = None

    class Meta:
        """Meta"""

        model = Floorplan
        fields = [
            "type",
            "remrate_target",
            "name",
            "number",
            "square_footage",
            "remrate_target",
            "remrate_data_file",
            "comment",
            "ekotrope_project",
            "ekotrope_houseplan",
        ]
        labels = {
            "remrate_target": "REM/Rate™ Data",
            "remrate_data_file": "REM/Rate™ File",
            "type": "Rating Type",
        }
        widgets = {
            "is_custom_home": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        mode = kwargs.pop("mode", None)
        keep_remrate_fields = kwargs.pop("keep_remrate_fields", False)
        super(HomeStatusFloorplanForm, self).__init__(*args, **kwargs)

        # raw mode doesn't need anything for other field configuration, so return now
        if self.raw_file_only:
            return

        # These need to not trigger validation errors if not provided, since the user will be able
        # to supply a target "existing" floorplan from a <select> element and we'll shortcut the
        # process.
        self.fields["square_footage"].required = False
        self.fields["number"].required = False
        # self.fields['name'].required = False

        try:
            label_dict = self.Meta.labels
        except AttributeError:
            label_dict = {}

        for fld, lbl in label_dict.items():
            self.fields[fld].label = lbl

        del_keys = []
        if user and user.company.company_type not in ["rater", "provider"]:
            if not keep_remrate_fields and not user.is_superuser:
                del_keys += ["remrate_target", "remrate_data_file"]

        if mode == "ekotrope":
            del_keys += ["remrate_target", "remrate_data_file"]
        elif mode == "remrate" or not hasattr(user, "ekotropeauthdetails"):
            del_keys += ["ekotrope_project", "ekotrope_houseplan"]

        for key in del_keys:
            try:
                del self.fields[key]
            except KeyError:
                pass

    def clean(self):
        """Add in some nice data"""
        cleaned_data = super(HomeStatusFloorplanForm, self).clean()

        # If nothing has changed, please leave.
        if not len(self.changed_data):
            return cleaned_data

        # This is a false alarm, given the way is_custom_home is a field (it really shouldn't be)
        if len(self.changed_data) == 1 and "is_custom_home" in self.changed_data:
            return cleaned_data

        # If the floorplan picker is filled out, we shouldn't try to clean all of the fields.
        existing_floorplan = cleaned_data.get("existing_floorplan")
        if existing_floorplan:
            return cleaned_data

        project = cleaned_data.get("ekotrope_houseplan")
        houseplan = cleaned_data.get("ekotrope_houseplan")
        if project and houseplan:
            cleaned_data["ekotrope_houseplan"] = houseplan

        # See class-level comment about _owner
        owner = self._owner if self._owner else cleaned_data.get("owner")
        existing = Floorplan.objects.filter_by_company(company=owner)

        if self.initial.get("id"):
            existing = existing.exclude(id=self.initial["id"])
        if self.instance and self.instance.pk:
            existing = existing.exclude(id=self.instance.pk)

        if cleaned_data.get("name"):
            if existing.filter(name__iexact=cleaned_data["name"]).count():
                raise forms.ValidationError(
                    "Please provide a different name as '{}' already exists".format(
                        cleaned_data["name"]
                    )
                )

        if cleaned_data.get("number"):
            if existing.filter(number__iexact=cleaned_data.get("number")).count():
                raise forms.ValidationError(
                    "Please provide a different number as '{}' already exists".format(
                        cleaned_data["number"]
                    )
                )

        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Returns the target "existing floorplan" if specified, otherwise creates/updates an instance.
        """
        existing_floorplan = self.cleaned_data.get("existing_floorplan")
        if existing_floorplan:
            self.instance = existing_floorplan
            return existing_floorplan
        return super(HomeStatusFloorplanForm, self).save(*args, **kwargs)

    @property
    def changed_data(self):
        """Removes certain fields from the "changed_data" detection mechanism."""
        changed_data = super(HomeStatusFloorplanForm, self).changed_data
        for skip_field in ["is_custom_home"]:
            if skip_field in changed_data:
                changed_data.remove(skip_field)
        return changed_data


class FloorplanApprovalForm(forms.ModelForm):
    """Sets the Floorplan Approval and Thermostats"""

    is_approved = forms.BooleanField(
        required=False, label="Is Active", help_text=strings.FLOORPLAN_FORM_IS_REVIEWED
    )
    thermostat_qty = forms.ChoiceField(
        required=False,
        label="Qty Thermostats",
        choices=THERMOSTAT_CHOICES,
        widget=Select2Widget,
        help_text=strings.FLOORPLAN_FORM_THERMOSTAT_QTY,
    )

    class Meta:
        """Meta Options"""

        model = Floorplan
        fields = ("is_approved", "thermostat_qty")

    def __init__(self, *args, **kwargs):
        super(FloorplanApprovalForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            status = self.instance.get_approved_status()
            self.fields["is_approved"].initial = status.is_approved
            self.fields["thermostat_qty"].initial = status.thermostat_qty


class FloorplanRemrateForm(
    AjaxBase64FileFormMixin.for_fields(["remrate_data_file"]), forms.ModelForm
):
    remrate_target = ApiModelChoiceField(
        widget=UnattachedSimulationChoiceWidget,
        required=False,
        label="REM/Rate™ Data",
        help_text="Enter name, development or builder name.",
    )

    class Meta(object):
        """Meta Options"""

        model = Floorplan
        fields = ("id", "remrate_target", "remrate_data_file")

    def __init__(self, *args, **kwargs):
        super(FloorplanRemrateForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            if self.instance.is_restricted:
                self.fields["remrate_target"].widget.attrs["disabled"] = True
                self.fields["remrate_data_file"].widget.attrs["disabled"] = True
                if "remrate_data_file_raw" in self.fields:
                    self.fields["remrate_data_file_raw"].widget.attrs["disabled"] = True
                    self.fields["remrate_data_file_raw_name"].widget.attrs["disabled"] = True


class FloorplanEkotropeForm(forms.ModelForm):
    """Floorplan Ekotrope Form"""

    ekotrope_project = ApiModelChoiceField(
        widget=UnattachedProjectChoiceWidget,
        required=False,
        help_text="Enter an Ekotrope Project name or id.",
    )
    ekotrope_houseplan = forms.ModelChoiceField(
        queryset=HousePlan.objects.none(),
        required=False,
        help_text="Enter an Ekotrope HousePlan name or id.",
    )

    class Meta(object):
        """Meta Options"""

        model = Floorplan
        fields = ("id", "ekotrope_houseplan")

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")

        super(FloorplanEkotropeForm, self).__init__(*args, **kwargs)

        # Arrange for a request-powered queryset for ekotrope_project
        project_field = self.fields["ekotrope_project"]
        project_viewset = project_field.widget.viewset_class(request=request)
        project_field.queryset = project_viewset.get_queryset()

        if self.instance:
            houseplan = self.instance.ekotrope_houseplan
            if houseplan:
                # self.fields['ekotrope_project'].initial = houseplan.project
                self.fields["ekotrope_houseplan"].queryset = houseplan.project.houseplan_set.all()
