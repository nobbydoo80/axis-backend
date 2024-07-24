"""forms.py: Django geographic"""


import logging

from django import forms

from axis.core.fields import ApiModelChoiceField
from .models import City
from .fields import CountyChoiceWidget
from .strings import PLACE_ENTITY_CHOICES

__author__ = "Steven Klass"
__date__ = "3/2/12 4:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CityForm(forms.ModelForm):
    county = ApiModelChoiceField(widget=CountyChoiceWidget, help_text=None, required=True)

    class Meta:
        model = City
        fields = (
            "name",
            "county",
            "land_area_meters",
            "water_area_meters",
            "latitude",
            "longitude",
        )

    def clean(self):
        data = self.cleaned_data
        if "county" in data and "name" not in self.initial:
            existing = City.objects.filter(name__iexact=data["name"], county=data["county"])
            if existing.count():
                raise forms.ValidationError(
                    "%s already exists in %s; \n"
                    "You may just need to add %s county to your company's "
                    "supported counties (Edit Company)"
                    % (data["name"], data["county"], data["county"])
                )

        re_geocode_keys = ["county", "latitude", "longitude"]
        if len(set(re_geocode_keys).intersection(set(self.changed_data))):
            if data["latitude"] != 0:
                data["latitude"] = 0
                if "latitude" not in self.changed_data:
                    self.changed_data.append("latitude")
            if data["longitude"] != 0:
                data["longitude"] = 0
                if "longitude" not in self.changed_data:
                    self.changed_data.append("longitude")
        return data
