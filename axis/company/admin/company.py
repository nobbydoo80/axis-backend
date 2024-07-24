"""company.py: """

__author__ = "Artem Hruzd"
__date__ = "02/22/2023 00:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django import forms
from django.contrib import admin

from axis.company.models import Company
from axis.company.validators import validate_provider_id
from axis.geographic.admin import PlaceSaveMixin
from .company_access import CompanyAccessInlineAdmin


class GenericCompanyForm(forms.ModelForm):
    def __init__(self, *arg, **kwargs):
        instance = kwargs.get("instance")

        super(GenericCompanyForm, self).__init__(*arg, **kwargs)

        if instance and instance.company_type == "provider":
            self.fields["is_sample_eligible"] = forms.BooleanField(required=False)
            self.fields["is_sample_eligible"].initial = instance.is_sample_eligible
            self.fields["provider_id"] = forms.CharField(
                validators=[validate_provider_id], max_length=8, required=False
            )
            self.fields["provider_id"].initial = instance.provider_id
        if instance and instance.company_type != "provider":
            self.fields["is_sample_eligible"].disabled = True
            self.fields["provider_id"].disabled = True

        if instance and instance.company_type == "rater":
            self.fields["is_sample_eligible"] = forms.BooleanField(required=False)
            self.fields["is_sample_eligible"].initial = instance.is_sample_eligible
            self.fields["certification_number"] = forms.CharField(max_length=16, required=False)
            self.fields["certification_number"].initial = instance.certification_number
        if instance and instance.company_type != "rater":
            self.fields["is_sample_eligible"].disabled = True
            self.fields["certification_number"].disabled = True

        if instance and instance.company_type == "utility":
            self.fields["electricity_provider"] = forms.BooleanField(required=True)
            self.fields["electricity_provider"].initial = instance.electricity_provider
            self.fields["gas_provider"] = forms.BooleanField(required=True)
            self.fields["gas_provider"].initial = instance.gas_provider
            self.fields["water_provider"] = forms.BooleanField(required=True)
            self.fields["water_provider"].initial = instance.water_provider
        if instance and instance.company_type != "utility":
            self.fields["electricity_provider"] = forms.BooleanField(required=False)
            self.fields["gas_provider"] = forms.BooleanField(required=False)
            self.fields["water_provider"] = forms.BooleanField(required=False)
            self.fields["electricity_provider"].disabled = True
            self.fields["gas_provider"].disabled = True
            self.fields["water_provider"].disabled = True

        if instance and instance.company_type != "hvac":
            self.fields["hquito_accredited"] = forms.BooleanField(required=False)
            self.fields["hquito_accredited"].initial = instance.hquito_accredited

        if instance and instance.company_type != "hvac":
            self.fields["hquito_accredited"] = forms.BooleanField(required=False)
            self.fields["hquito_accredited"].disabled = True


@admin.register(Company)
class CompanyAdmin(PlaceSaveMixin, admin.ModelAdmin):
    ordering = [
        "name",
    ]
    search_fields = ["name", "city__name", "state"]
    readonly_fields = ("group",)
    filter_horizontal = ["counties", "countries"]
    list_display = (
        "name",
        "state",
        "is_customer",
        "is_active",
        "is_eep_sponsor",
    )
    list_filter = [
        "company_type",
    ]
    raw_id_fields = (
        "city",
        "place",
        "geocode_response",
        "shipping_geocode",
        "shipping_geocode_response",
    )
    form = GenericCompanyForm
    inlines = (CompanyAccessInlineAdmin,)
