"""forms.py: Django subdivision"""


import logging

from django import forms
from django_select2.forms import Select2Widget

from axis.community.models import Community
from axis.company.fields import BuilderOrganizationChoiceApiWidget
from axis.core.fields import ApiModelChoiceField
from axis.core.forms import DynamicGetOrCreateMixin
from axis.core.utils import set_help_text_from_model, set_verbose_name_from_model
from axis.geographic.fields import CityChoiceWidget
from .fields import UnattachedOrNewSubdivisionChoiceWidget
from .models import Subdivision

__author__ = "Steven Klass"
__date__ = "3/5/12 1:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SubdivisionForm(DynamicGetOrCreateMixin, forms.ModelForm):
    name = ApiModelChoiceField(
        widget=UnattachedOrNewSubdivisionChoiceWidget, help_text=None, required=True
    )

    builder_org = ApiModelChoiceField(widget=BuilderOrganizationChoiceApiWidget)

    community = forms.ModelChoiceField(queryset=Community.objects.none(), required=False)
    city = ApiModelChoiceField(widget=CityChoiceWidget, help_text=None, required=False)

    class Meta:
        model = Subdivision
        fields = (
            "name",
            "builder_org",
            "community",
            "city",
            "cross_roads",
            "builder_name",
            "geocode_response",
            "use_sampling",
            "use_metro_sampling",
            "address_override",
            "is_multi_family",
        )
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.company = user.company
        super(SubdivisionForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["city"].initial = self.instance.city_id

        queryset = self.company.relationships.get_communities(show_attached=True)
        self.fields["community"].queryset = queryset
        self.fields["community"].widget = Select2Widget(
            choices=[("", "--------")] + list(map(lambda o: (o.pk, str(o)), queryset))
        )

        # Transplant help_text for fields that we've overridden on this form
        for field_name in ["name", "builder_org", "community", "city"]:
            set_help_text_from_model(self, field_name)
            set_verbose_name_from_model(self, field_name)
