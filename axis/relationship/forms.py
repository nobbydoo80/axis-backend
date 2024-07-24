"""forms.py: Django relationship"""

import logging

from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget

from axis.company.models import (
    RaterOrganization,
    ProviderOrganization,
    EepOrganization,
    HvacOrganization,
    UtilityOrganization,
    QaOrganization,
    GeneralOrganization,
    BuilderOrganization,
    ArchitectOrganization,
    CommunityOwnerOrganization,
    DeveloperOrganization,
    Company,
)
from axis.core.utils import SELECT2_OPTIONS
from axis.home import strings as home_strings
from .models import Relationship

__author__ = "Steven Klass"
__date__ = "8/24/12 10:02 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RelationshipForm(forms.ModelForm):
    object = forms.IntegerField(label="Object ID")

    class Meta:
        fields = ()
        model = Relationship


class _BaseRelationshipsMixin(object):
    rater = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.RATER_COMPANY_TYPE),
        label=RaterOrganization._meta.verbose_name_plural,
        required=False,
    )
    provider = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.PROVIDER_COMPANY_TYPE),
        label=ProviderOrganization._meta.verbose_name_plural,
        required=False,
    )
    eep = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.EEP_COMPANY_TYPE),
        label=EepOrganization._meta.verbose_name_plural,
        required=False,
    )
    hvac = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.HVAC_COMPANY_TYPE),
        label=HvacOrganization._meta.verbose_name_plural,
        required=False,
    )
    utility = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE),
        label=UtilityOrganization._meta.verbose_name_plural,
        required=False,
    )
    qa = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.QA_COMPANY_TYPE),
        label=QaOrganization._meta.verbose_name_plural,
        required=False,
    )
    general = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.GENERAL_COMPANY_TYPE),
        label=GeneralOrganization._meta.verbose_name_plural,
        required=False,
    )


class _SplitUtilitiesMixin(object):
    """Removes ``utility_orgs`` and splits the utilities into separate fields."""

    rater = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.RATER_COMPANY_TYPE),
        label=RaterOrganization._meta.verbose_name_plural,
        required=False,
    )
    provider = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.PROVIDER_COMPANY_TYPE),
        label=ProviderOrganization._meta.verbose_name_plural,
        required=False,
    )
    eep = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.EEP_COMPANY_TYPE),
        label=EepOrganization._meta.verbose_name_plural,
        required=False,
    )
    hvac = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.HVAC_COMPANY_TYPE),
        label=HvacOrganization._meta.verbose_name_plural,
        required=False,
    )
    qa = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.QA_COMPANY_TYPE),
        label=QaOrganization._meta.verbose_name_plural,
        required=False,
    )
    general = forms.ModelMultipleChoiceField(
        queryset=Company.objects.filter(company_type=Company.GENERAL_COMPANY_TYPE),
        label=GeneralOrganization._meta.verbose_name_plural,
        required=False,
    )

    gas_utility_org = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE),
        required=False,
        help_text=home_strings.HOME_HELP_TEXT_UTILITY_COMPANIES,
        label="Gas Company",
    )
    electric_utility_org = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE),
        required=False,
        help_text=home_strings.HOME_HELP_TEXT_UTILITY_COMPANIES,
        label="Electric Company",
    )

    def __init__(self, *args, **kwargs):
        """Correctly initialize split utility fields"""
        super(_SplitUtilitiesMixin, self).__init__(*args, **kwargs)
        self.configure_fields()
        self.configure_initial()

    def configure_fields(self):
        queryset = Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE).filter_by_user(
            self.user, show_attached=True
        )
        electric_companies = queryset.filter(electricity_provider=True)
        gas_companies = queryset.filter(gas_provider=True)
        self.fields["gas_utility_org"].queryset = gas_companies
        self.fields["electric_utility_org"].queryset = electric_companies

        field = self.fields["gas_utility_org"]
        field.widget = Select2Widget(
            attrs=dict(SELECT2_OPTIONS, placeholder="Type to search"),
            choices=[("", "---------")] + list(map(lambda o: (o.pk, o), field.queryset)),
        )
        field = self.fields["electric_utility_org"]
        field.widget = Select2Widget(
            attrs=dict(SELECT2_OPTIONS, placeholder="Type to search"),
            choices=[("", "---------")] + list(map(lambda o: (o.pk, o), field.queryset)),
        )

    def configure_initial(self):
        # Duplicated from HomeForm, but splits utilities into separate types
        if self.instance.pk:
            orgs = self.instance.get_org_ids(use_suffixes=True, split_utilities=True)
            for org_type, value in orgs.items():
                self.fields[org_type].initial = value

            if "updated_construction_stage" in self.fields:
                current_stage = self.instance.get_current_stage(self.user)
                if current_stage:
                    self.fields["updated_construction_stage"].initial = current_stage.stage_id


def object_relationships_form_factory(Model, company_types=None):
    # We need to declare the extra company fields directly on the ModelForm class which specifies
    # the target Model.  Subclassing a generic piece doesn't work for some reason.
    class _BaseObjectRelationshipsForm(forms.ModelForm):
        class Meta:
            model = Model
            fields = ()  # We don't want any of the fields from the original model

        company_types = None  # If specified, this is a field limiter on what we've delcared here.

        # TODO: Implement a save function that correctly updates relationships on the instance

        builder = forms.ModelChoiceField(
            queryset=Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE),
            label=BuilderOrganization._meta.verbose_name,
            required=False,
        )
        rater = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.RATER_COMPANY_TYPE),
            label=RaterOrganization._meta.verbose_name_plural,
            required=False,
        )
        provider = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.PROVIDER_COMPANY_TYPE),
            label=ProviderOrganization._meta.verbose_name_plural,
            required=False,
        )
        eep = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.EEP_COMPANY_TYPE),
            label=EepOrganization._meta.verbose_name_plural,
            required=False,
        )
        hvac = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.HVAC_COMPANY_TYPE),
            label=HvacOrganization._meta.verbose_name_plural,
            required=False,
        )

        qa = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.QA_COMPANY_TYPE),
            label=QaOrganization._meta.verbose_name_plural,
            required=False,
        )
        general = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.GENERAL_COMPANY_TYPE),
            label=GeneralOrganization._meta.verbose_name_plural,
            required=False,
        )

        electric_utility = forms.ModelChoiceField(
            queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE),
            required=False,
            help_text=home_strings.HOME_HELP_TEXT_UTILITY_COMPANIES,
            label="Electric Company",
        )
        gas_utility = forms.ModelChoiceField(
            queryset=Company.objects.filter(company_type=Company.UTILITY_COMPANY_TYPE),
            required=False,
            help_text=home_strings.HOME_HELP_TEXT_UTILITY_COMPANIES,
            label="Gas Company",
        )
        architect = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.ARCHITECT_COMPANY_TYPE),
            label=ArchitectOrganization._meta.verbose_name_plural,
            required=False,
        )
        developer = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.DEVELOPER_COMPANY_TYPE),
            label=DeveloperOrganization._meta.verbose_name_plural,
            required=False,
        )
        communityowner = forms.ModelMultipleChoiceField(
            queryset=Company.objects.filter(company_type=Company.COMMUNITY_OWNER_COMPANY_TYPE),
            label=CommunityOwnerOrganization._meta.verbose_name_plural,
            required=False,
        )

        def __init__(self, user, *args, **kwargs):
            self.user = user
            self.company_types = kwargs.pop("company_types", None)
            super(_BaseObjectRelationshipsForm, self).__init__(*args, **kwargs)

            self.configure_fields()

        def configure_fields(self):
            """Remove fields where the user should have the required permission."""

            # The 'builder' item is a special case in that it is singular.  The split utilities are
            # the same but are being handled outside of this first loop.

            for name, field in list(self.fields.items()):
                # Remove types that weren't asked for by the page
                # This will probably happen because the underlying object has an FK to the excluded
                # type and will manage the relationship itself.
                if self.company_types and name not in self.company_types:
                    del self.fields[name]

                # Remove types that are outside of the user's permission area
                company_type = name
                if name.endswith("_utility"):
                    company_type = "utility"
                if not self.user.has_perm("company.view_%sorganization" % (company_type,)):
                    try:
                        del self.fields[name]
                    except KeyError:
                        log.warning(
                            "Missing field %r in object_relationships_form_factory",
                            name,
                        )
                        continue

                # Handle these later
                if company_type == "utility":
                    continue

                if self.instance.pk:
                    field.initial = self.instance.relationships.get_orgs(name, ids_only=True)
                    if name == "builder":
                        if len(field.initial):
                            field.initial = field.initial[0]
                        else:
                            field.initial = None
                field.queryset = field.queryset.filter_by_user(self.user, show_attached=True)

                if name != "builder":
                    field.widget = Select2MultipleWidget(
                        attrs=dict(SELECT2_OPTIONS, placeholder="Type to search"),
                        choices=map(lambda o: (o.pk, "{}".format(o)), field.queryset),
                    )

            queryset = Company.objects.filter(
                company_type=Company.UTILITY_COMPANY_TYPE
            ).filter_by_user(self.user, show_attached=True)
            electric_companies = queryset.filter(electricity_provider=True)
            gas_companies = queryset.filter(gas_provider=True)
            if "gas_utility" in self.fields:
                self.fields["gas_utility"].queryset = gas_companies
            if "electric_utility" in self.fields:
                self.fields["electric_utility"].queryset = electric_companies

            # field = self.fields['gas_utility_org']
            # field.widget = Select2Widget(
            #     attrs=dict(SELECT2_OPTIONS, placeholder="Type to search"),
            #     choices=[('', '---------')] + list(map(lambda o: (o.pk, o), field.queryset)))
            # field = self.fields['electric_utility_org']
            # field.widget = Select2Widget(
            #     attrs=dict(SELECT2_OPTIONS, placeholder="Type to search"),
            #     choices=[('', '---------')] + list(map(lambda o: (o.pk, o), field.queryset)))

    return type(
        str("%sRelationshipsForm" % (Model.__name__,)),
        (_BaseObjectRelationshipsForm,),
        {
            "company_types": company_types,
        },
    )
