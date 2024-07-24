"""forms.py: Django company"""

__author__ = "Steven Klass"
__date__ = "3/2/12 2:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import re
from itertools import chain

from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Q, Count

import axis.company.fields  # Absolute import for explicit and tidy getatter() calls
from axis.core.fields import ApiModelChoiceField
from axis.core.forms import DynamicGetOrCreateMixin
from axis.core.utils import PHONE_DIGITS_RE
from axis.core.widgets import BigSelectMultiple
from axis.eep_program.models import EEPProgram
from axis.equipment.models import Equipment
from axis.examine.forms import AjaxBase64FileFormMixin
from axis.geocoder.models import Geocode
from axis.geographic.fields import UnrestrictedCityChoiceWidget
from axis.geographic.models import City, County, Country
from . import strings
from .fields import (
    UnattachedRaterOrganizationChoiceApiWidget,
    UnattachedBuilderOrganizationChoiceApiWidget,
    UnattachedProviderOrganizationChoiceApiWidget,
    UnattachedEepOrganizationChoiceApiWidget,
    UnattachedQaOrganizationChoiceApiWidget,
    UnattachedUtilityOrganizationChoiceApiWidget,
    UnattachedGeneralOrganizationChoiceApiWidget,
    UnattachedHvacOrganizationChoiceApiWidget,
    UnattachedArchitectOrganizationChoiceApiWidget,
    UnattachedDeveloperOrganizationChoiceApiWidget,
    UnattachedCommunityOwnerOrganizationChoiceApiWidget,
)
from .models import (
    Company,
    HQUITO_CHOICES,
    AltName,
    COMPANY_MODELS_MAP,
    Contact,
    SponsorPreferences,
)
from .utils import can_edit_hquito_status


customer_hirl_app = apps.get_app_config("customer_hirl")

log = logging.getLogger(__name__)
User = get_user_model()


ZIPCODE_RE = re.compile(r"^\d{5}(?:-\d{4})?$")
COMPANY_FIELD_EXCLUDES = (
    "group",
    "state",
    "sponsors",
    "company_type",
    "is_eep_sponsor",
    "logo",
    "latitude",
    "longitude",
    "confirmed_address",
    "address_override",
    "slug",
)
COMPANY_STRING_FIELD_EXCLUDES = (
    "group",
    "state",
    "is_customer",
    "sponsors",
    "is_eep_sponsor",
    "logo",
    "slug",
)


class CompanyBaseForm(forms.ModelForm):
    """Base Form for companies"""

    def __init__(self, is_limited=False, *args, **kwargs):
        super(CompanyBaseForm, self).__init__(*args, **kwargs)
        pretty_name = self._meta.model.get_company_type_pretty_name()
        self.fields["name"].label = "{} Name".format(pretty_name)
        self.fields["street_line1"].label = "Street Address"
        self.fields["zipcode"].label = "ZIP Code"
        self.fields["description"].widget.attrs = {"class": "input-block-level", "rows": 5}
        self.fields["description"].help_text = "HTML will be accepted"

        self._is_limited = is_limited
        if is_limited:
            for field_name in [
                "name",
                "street_line1",
                "street_line2",
                "city",
                "zipcode",
                "office_phone",
                "default_email",
            ]:
                self.fields[field_name].widget.attrs = {"readonly": "readonly"}

    def clean_office_phone(self):
        """Tries to normalize a phone number using ``company.utils.PHONE_DIGITS_RE``."""
        if self._is_limited:
            return self.instance.office_phone
        office_phone = None
        if self.cleaned_data.get("office_phone"):
            m = PHONE_DIGITS_RE.search(self.cleaned_data.get("office_phone"))
            if m:
                office_phone = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
        return office_phone

    def clean_is_active(self):
        """Defaults ``is_active`` to True if it's not sent."""
        return self.cleaned_data.get("is_active", True)

    def clean_company_type(self):
        return self._meta.model.COMPANY_TYPE

    def clean_name(self):
        if self._is_limited:
            return self.instance.name
        return self.cleaned_data["name"]

    def clean_street_line1(self):
        if self._is_limited:
            return self.instance.street_line1
        return self.cleaned_data["street_line1"]

    def clean_street_line2(self):
        if self._is_limited:
            return self.instance.street_line2
        return self.cleaned_data["street_line2"]

    def clean_city(self):
        if self._is_limited:
            return self.instance.city
        return self.cleaned_data["city"]

    def clean_zipcode(self):
        if self._is_limited:
            return self.instance.zipcode
        zipcode = self.cleaned_data["zipcode"]
        if zipcode is None or not ZIPCODE_RE.search(zipcode.strip()):
            raise forms.ValidationError("Enter a ZIP Code in the format XXXXX or XXXXX-XXXX.")
        return zipcode.strip()

    def clean_default_email(self):
        if self._is_limited:
            return self.instance.default_email
        return self.cleaned_data["default_email"]

    def clean_certification_number(self):
        if self.cleaned_data["certification_number"].strip() == "":
            return None
        return self.cleaned_data["certification_number"]

    def clean_provider_id(self):
        if self.cleaned_data["provider_id"].strip() == "":
            return None
        return self.cleaned_data["provider_id"]

    def clean(self):
        """Geocodes street address, identifies city, and verifies that company name is unique."""
        cleaned_data = super(CompanyBaseForm, self).clean()

        required_keys_for_clean = {"zipcode", "city", "name", "office_phone", "street_line1"}
        if required_keys_for_clean - set(cleaned_data.keys()):
            return cleaned_data

        # We need to make sure that all admins are also actual users. This is
        # used to determine what company you work for.
        cleaned_data["users"] = list(
            chain(cleaned_data.get("users", []), cleaned_data.get("admins", []))
        )

        lookup = dict(
            street_line1=cleaned_data.get("street_line1"),
            street_line2=cleaned_data.get("street_line2"),
            city=cleaned_data.get("city"),
            state=cleaned_data.get("state"),
            zipcode=cleaned_data.get("zipcode"),
        )

        geolocation_matches = Geocode.objects.get_matches(**lookup)

        if len(geolocation_matches) == 1:
            match = geolocation_matches[0]
            geocoded_data = match.get_normalized_fields()
            values = [
                "street_line1",
                "street_line2",
                "state",
                "zipcode",
                "confirmed_address",
                "latitude",
                "longitude",
            ]
            cleaned_data.update({k: geocoded_data.get(k, None) for k in values})
            cleaned_data["geocode_response"] = match
            _city = cleaned_data["city"]
            cleaned_data["city"] = geocoded_data.get("city") if geocoded_data.get("city") else None
            if not cleaned_data["city"]:
                if isinstance(_city, str):
                    _city, _ = City.objects.get_or_create_by_string(
                        _city, state=cleaned_data["state"]
                    )
                cleaned_data["city"] = _city
        else:
            # Can't make a positive match on a single geocoded result
            cleaned_data["confirmed_address"] = False
            addr = "{street_line1} {street_line2} {city}, {state} {zipcode}".format(**lookup)
            log.warning("%s - Address provided was not confirmed - %s", "CompanyBaseForm", addr)

            if not isinstance(cleaned_data.get("city"), City):
                cleaned_data["city"], _cc = City.objects.get_or_create_by_string(
                    name=cleaned_data.get("city"), state=cleaned_data.get("state")
                )
                if _cc:
                    log.warning("Created city - %s", cleaned_data["city"])

        query_string = Q(
            street_line1=cleaned_data["street_line1"],
            street_line2=cleaned_data["street_line2"],
            city=cleaned_data["city"],
            state=cleaned_data["city"].county.state if cleaned_data["city"].county else None,
            zipcode=cleaned_data["zipcode"],
        )
        query_string |= Q(office_phone=cleaned_data["office_phone"])

        similar = self.Meta.model.objects.filter(query_string, name__iexact=cleaned_data["name"])

        if self.instance.pk:
            similar = similar.exclude(id=self.instance.id)

        if similar.count():
            model_name = self.Meta.model._meta.verbose_name
            if similar.filter(name__iexact=cleaned_data.get("name")).count():
                err = "A {model} already exists with the name '{name}'".format(
                    model=model_name, name=cleaned_data["name"]
                )
                raise forms.ValidationError(err)
            if similar.filter(office_phone=cleaned_data.get("office_phone")).count():
                err = "This phone number already bound to another company"
                log.warning(err)
            err = "A %s at this address already exists."
            log.warning(err, model_name)

        return cleaned_data


class CompanyForm(DynamicGetOrCreateMixin, forms.ModelForm):
    """Abstract for modifying Company."""

    city = ApiModelChoiceField(
        widget=UnrestrictedCityChoiceWidget,
        required=True,
        help_text=strings.SUBDIVISION_HELP_TEXT_CITY,
    )
    street_line1 = forms.CharField(
        max_length=100, required=True, help_text=strings.SUBDIVISION_HELP_TEXT_STREET_LINE1
    )
    default_email = forms.EmailField(
        required=True, help_text=strings.SUBDIVISION_HELP_TEXT_DEFAULT_EMAIL
    )

    # Situational fields that are ignored if company_type is wrong for what they represent
    hquito_accredited = forms.BooleanField(
        widget=forms.Select(choices=HQUITO_CHOICES), required=False, label="H-QUITO Accredited"
    )
    electricity_provider = forms.BooleanField(required=False)
    gas_provider = forms.BooleanField(required=False)
    water_provider = forms.BooleanField(required=False)
    office_phone = forms.CharField(required=True)

    class Meta(object):
        model = Company
        fields = (
            "name",
            "street_line1",
            "street_line2",
            "home_page",
            "office_phone",
            "zipcode",
            "description",
            "geocode_response",
            "address_override",
            "city",
            "default_email",
            # Situational fields
            "hquito_accredited",
            "electricity_provider",
            "gas_provider",
            "water_provider",
            # superuser fields
            "is_customer",
            "is_active",
            "is_public",
        )
        labels = {
            "city": "City/State/County",
            "home_page": "Website",
            "office_phone": "Phone Number",
        }
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }
        help_texts = {
            "name": strings.SUBDIVISION_HELP_TEXT_NAME,
        }

    def __init__(self, *args, **kwargs):
        """Adds type-specific UnattachedOrNew field for the 'name' field."""
        company_type = kwargs.pop("company_type", None)
        is_limited = kwargs.pop("is_limited", False)
        user = kwargs.pop("user")

        super(CompanyForm, self).__init__(*args, **kwargs)

        if not self.instance.pk and "data" not in kwargs:
            company_api_field_name = "UnattachedOrNew{}OrganizationChoiceApiWidget".format(
                company_type.capitalize()
            )
            company_api_field = getattr(axis.company.fields, company_api_field_name)
            self.fields["name"] = company_api_field()
            self.fields["name"].help_text = None
            self.fields["name"].required = True

        is_users_company = user.is_superuser or (
            self.instance and self.instance.id == user.company.id
        )

        pretty_name = self._meta.model.get_company_type_pretty_name()
        self.fields["name"].label = "{} Name".format(pretty_name)
        self.fields["street_line1"].label = "Street Address"
        self.fields["zipcode"].label = "ZIP Code"

        if is_limited:
            field_list_to_limit_editing = [
                "name",
                "street_line1",
                "street_line2",
                "city",
                "zipcode",
                "office_phone",
                "default_email",
            ]

            # If HI is a sponsor and there are other sponsors,
            # we need to enforce the most restrictive condition
            only_customer_hirl_can_edit_identity_fields_restriction_exists = (
                SponsorPreferences.objects.filter(
                    sponsored_company=self.instance,
                    sponsor__slug=customer_hirl_app.CUSTOMER_SLUG,
                    can_edit_identity_fields=False,
                )
                .annotate(
                    count_can_edit_identity_fields=Count(
                        "can_edit_identity_fields", filter=Q(can_edit_identity_fields=False)
                    )
                )
                .filter(count_can_edit_identity_fields=1)
                .exists()
            )

            if self.instance and only_customer_hirl_can_edit_identity_fields_restriction_exists:
                field_list_to_limit_editing = [
                    "name",
                ]

            for field_name in field_list_to_limit_editing:
                self.fields[field_name].widget.attrs = {"disabled": "disabled"}

        pretty_name = COMPANY_MODELS_MAP[company_type].get_company_type_pretty_name()
        if not self.instance.pk and "data" not in kwargs:
            field_name = "UnattachedOrNew{}OrganizationChoiceApiWidget".format(
                company_type.capitalize()
            )
            Widget = getattr(axis.company.fields, field_name)
            self.fields["name"] = ApiModelChoiceField(
                widget=Widget, label="{} Company Name".format(pretty_name)
            )
        else:
            self.fields["name"].label = "{} Company Name".format(pretty_name)

        if not user.is_superuser:
            del self.fields["is_customer"]
            del self.fields["is_active"]

            if not is_users_company:
                del self.fields["is_public"]

        company_type = self.instance.company_type or company_type
        can_edit_hquito = can_edit_hquito_status(user, self.instance, company_type)
        if can_edit_hquito:
            if hasattr(self.instance, "hvacorganization"):
                self.fields["hquito_accredited"].initial = self.instance.hquito_accredited
        else:
            del self.fields["hquito_accredited"]


class CompanyEEPProgramsForm(forms.ModelForm):
    eep_programs = forms.ModelMultipleChoiceField(
        required=False, queryset=EEPProgram.objects.none(), widget=BigSelectMultiple
    )

    class Meta:
        model = Company
        fields = ("eep_programs",)

    def __init__(self, user, *args, **kwargs):
        super(CompanyEEPProgramsForm, self).__init__(*args, **kwargs)
        company = kwargs.get("instance")
        if company:
            self.fields["eep_programs"].queryset = EEPProgram.objects.filter_by_company(company)


class CompanyCountiesForm(forms.ModelForm):
    counties = forms.ModelMultipleChoiceField(
        required=False, queryset=County.objects.none(), widget=BigSelectMultiple
    )

    class Meta:
        model = Company
        fields = ("counties",)

    def __init__(self, *args, **kwargs):
        super(CompanyCountiesForm, self).__init__(*args, **kwargs)
        field = self.fields["counties"]
        field.choices = ((o.pk, field.label_from_instance(o)) for o in County.objects.all())


class CompanyCountriesForm(forms.ModelForm):
    countries = forms.ModelMultipleChoiceField(
        required=False, queryset=Country.objects.none(), widget=BigSelectMultiple
    )

    class Meta:
        model = Company
        fields = ("countries",)

    def __init__(self, *args, **kwargs):
        super(CompanyCountriesForm, self).__init__(*args, **kwargs)
        field = self.fields["countries"]
        field.choices = ((o.pk, field.label_from_instance(o)) for o in Country.objects.all())


class CompanyEquipmentForm(
    AjaxBase64FileFormMixin.for_fields(["calibration_documentation"]), forms.ModelForm
):
    assignees = forms.ModelMultipleChoiceField(required=False, queryset=User.objects.none())
    calibration_documentation = forms.FileField(required=True)

    class Meta:
        model = Equipment
        exclude = ("owner_company", "sponsors", "expired_equipment")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(CompanyEquipmentForm, self).__init__(*args, **kwargs)
        if user and self.fields.get("assignees"):
            self.fields["assignees"].queryset = user.company.users.all()


class AltNameForm(forms.ModelForm):
    class Meta:
        model = AltName
        fields = ("name",)


class CompanyDescriptionForm(AjaxBase64FileFormMixin.for_fields(["logo"]), forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "description",
            "auto_add_direct_relationships",
            "display_raw_addresses",
            "inspection_grade_type",
            "logo",
        )
        labels = {"display_raw_addresses": "Show addresses as-entered"}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(CompanyDescriptionForm, self).__init__(*args, **kwargs)

        is_users_company = user.is_superuser or (self.instance.pk == user.company.id)

        if self.instance.pk:
            if (
                not self.instance.auto_add_direct_relationships and self.instance.is_eep_sponsor
            ) or user.company.pk != self.instance.pk:
                # our mixing delete all fields that is not related to image fields
                if not user.is_superuser and not self.raw_file_only:
                    del self.fields["auto_add_direct_relationships"]

                    if not is_users_company and not self.raw_file_only:
                        del self.fields["display_raw_addresses"]


class CompanyCOIForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("worker_compensation_insurance",)


class ContactForm(forms.ModelForm):
    is_company = forms.BooleanField(label="Company")

    class Meta:
        model = Contact
        fields = (
            "first_name",
            "last_name",
            "description",
            "phone",
            "email",
            "street_line1",
            "street_line2",
            "city",
            "zipcode",
            "is_company",
        )
        labels = {
            "street_line2": "Unit number",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        type = kwargs.pop("type", "person")

        super(ContactForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["is_company"].initial = self.instance.type == "company"
        self.fields["city"].queryset = City.objects.filter_by_user(user)
        self.fields["zipcode"].required = False
        self.fields["phone"].required = False

        if type == "company" or (self.instance.pk and self.instance.type == "company"):
            self.fields["first_name"].label = "Company Name"


class CompanyStringForm(CompanyBaseForm):
    """String-based form for companies.  Adds fields to cleaned_data based on inputs."""

    city = forms.CharField(max_length=64)
    county = forms.CharField(max_length=64, required=False)
    state = forms.CharField(max_length=20)

    def clean(self):
        """Verify and confirm the address."""
        cleaned_data = super(CompanyStringForm, self).clean()

        if self.instance:
            for key in self.cleaned_data.keys():
                if key in self.changed_data:
                    if getattr(self.instance, key) == cleaned_data.get(key):
                        self.changed_data.pop(self.changed_data.index(key))

        return cleaned_data


class BuilderCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES


class BuilderStringForm(CompanyStringForm):
    class Meta:
        model = Company
        exclude = COMPANY_STRING_FIELD_EXCLUDES


class ProviderCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES
        labels = {
            "provider_id": "Provider ID",
        }


class ProviderStringForm(CompanyStringForm):
    class Meta:
        model = Company
        exclude = COMPANY_STRING_FIELD_EXCLUDES


class RaterCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES


class RaterStringForm(CompanyStringForm):
    class Meta:
        model = Company
        exclude = COMPANY_STRING_FIELD_EXCLUDES


class EepCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES


class HvacCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES

    def __init__(self, *args, **kwargs):
        super(HvacCompanyForm, self).__init__(*args, **kwargs)
        self.fields["hquito_accredited"].label = "H-QUITO Accredited"
        self.fields["hquito_accredited"].choices = HQUITO_CHOICES


class UtilityCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES


class QaCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES


class GeneralCompanyForm(CompanyForm):
    class Meta(CompanyForm.Meta):
        model = Company
        exclude = COMPANY_FIELD_EXCLUDES


# Specialized forms for extended fields
class ProviderFieldsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("provider_id", "auto_submit_to_registry")


class RaterFieldsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("certification_number",)


# Forms that target unattached organizations only
class AddExistingRaterForm(forms.Form):
    object = ApiModelChoiceField(widget=UnattachedRaterOrganizationChoiceApiWidget, help_text=None)


class AddExistingProviderForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedProviderOrganizationChoiceApiWidget, help_text=None
    )


class AddExistingBuilderForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedBuilderOrganizationChoiceApiWidget, help_text=None
    )


class AddExistingEepForm(forms.Form):
    object = ApiModelChoiceField(widget=UnattachedEepOrganizationChoiceApiWidget, help_text=None)


class AddExistingHvacForm(forms.Form):
    object = ApiModelChoiceField(widget=UnattachedHvacOrganizationChoiceApiWidget, help_text=None)


class AddExistingGeneralForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedGeneralOrganizationChoiceApiWidget, help_text=None
    )


class AddExistingUtilityForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedUtilityOrganizationChoiceApiWidget, help_text=None
    )


class AddExistingQaForm(forms.Form):
    object = ApiModelChoiceField(widget=UnattachedQaOrganizationChoiceApiWidget, help_text=None)


class AddExistingArchitectForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedArchitectOrganizationChoiceApiWidget, help_text=None
    )


class AddExistingDeveloperForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedDeveloperOrganizationChoiceApiWidget, help_text=None
    )


# Communityowner we can't capitalize owner without updating examine code
class AddExistingCommunityownerForm(forms.Form):
    object = ApiModelChoiceField(
        widget=UnattachedCommunityOwnerOrganizationChoiceApiWidget, help_text=None
    )


class SponsorPreferencesForm(forms.ModelForm):
    """Changes labels for friendly UI presentation."""

    # Dummy field for display column purposes.  Surprisingly, this was the best way.
    sponsored_company_name = forms.CharField(label="Sponsored Company", required=False)

    can_edit_profile = forms.BooleanField(label="Allow profile modifications", required=False)
    can_edit_identity_fields = forms.BooleanField(
        label="Unlock name, address, phone, and email fields", required=False
    )
    notify_sponsor_on_update = forms.BooleanField(
        label="Subscribe to profile update notifications", required=False
    )

    class Meta:
        model = Company.sponsors.through
        fields = (
            "sponsored_company_name",
            "can_edit_profile",
            "can_edit_identity_fields",
            "notify_sponsor_on_update",
        )


class CompanyShippingAddressForm(forms.ModelForm):
    shipping_geocode_street_line1 = forms.CharField(
        max_length=100, label="Address Line 1", required=True
    )
    shipping_geocode_street_line2 = forms.CharField(
        max_length=100, label="Address Line 2", required=False
    )
    shipping_geocode_zipcode = forms.CharField(max_length=15, label="ZIP Code", required=True)
    shipping_geocode_city = ApiModelChoiceField(
        widget=UnrestrictedCityChoiceWidget, required=True, label="City"
    )

    class Meta:
        model = Company
        fields = ()
