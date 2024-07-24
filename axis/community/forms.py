"""forms.py: Django community"""


import logging

from django import forms

from axis.core.forms import DynamicGetOrCreateMixin
from axis.core.fields import ApiModelChoiceField
from axis.core.utils import set_help_text_from_model
from axis.geographic.fields import CityChoiceWidget
from .models import Community
from .fields import UnattachedOrNewCommunityChoiceWidget

__author__ = "Steven Klass"
__date__ = "3/5/12 1:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityForm(DynamicGetOrCreateMixin, forms.ModelForm):
    name = UnattachedOrNewCommunityChoiceWidget()
    city = ApiModelChoiceField(widget=CityChoiceWidget, required=True)

    class Meta:
        model = Community
        fields = (
            "name",
            "city",
            "cross_roads",
            "website",
            "geocode_response",
            "address_override",
            "is_multi_family",
        )
        labels = {
            "name": "Community Name",
            "city": "City/State/County",
            "cross_roads": "Crossroads",
        }
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super(CommunityForm, self).__init__(*args, **kwargs)

        # Transplant help_text for fields that we've overridden on this form
        for field_name in ["name", "city"]:
            set_help_text_from_model(self, field_name)

    def clean_cross_roads(self):
        return self.cleaned_data["cross_roads"].replace("/", " and ")

    def clean(self):
        """All we need to do is validate the address"""
        cleaned_data = super(CommunityForm, self).clean()

        if "city" in cleaned_data:
            if cleaned_data.get("county") is None:
                cleaned_data["county"] = cleaned_data["city"].county
                self.changed_data.append("county")
            if cleaned_data.get("state") is None and cleaned_data["city"].county:
                cleaned_data["state"] = cleaned_data["city"].county.state
                self.changed_data.append("state")
            if (
                cleaned_data.get("metro") is None
                and cleaned_data["city"].county
                and cleaned_data["city"].county.metro
            ):
                cleaned_data["metro"] = cleaned_data["city"].county.metro
                self.changed_data.append("metro")

        return cleaned_data
