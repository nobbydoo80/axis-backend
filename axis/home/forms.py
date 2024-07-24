"""forms.py: Django home"""

__author__ = "Steven Klass"
__date__ = "3/5/12 1:35 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import datetime
import logging
from collections import OrderedDict

from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_select2.forms import Select2MultipleWidget, Select2Widget
from localflavor.us.us_states import US_STATES

from axis.certification.utils import get_owner_swap_queryset
from axis.checklist.models import Answer
from axis.community.models import Community
from axis.company.models import Company, BuilderOrganization
from axis.company.strings import COMPANY_TYPES
from axis.core.fields import ApiModelChoiceField
from axis.customer_eto.utils import ETO_REGIONS
from axis.eep_program.models import EEPProgram
from axis.filehandling.forms import AsynchronousProcessedDocumentForm
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.floorplan.models import Floorplan
from axis.geographic.fields import CityChoiceWidget
from axis.geographic.models import Metro, City
from axis.geographic.utils.legacy import denormalize_related_references_dict
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.qa.models import QAStatus, ObservationType, QARequirement
from axis.qa.state_machine import QAStateMachine
from axis.relationship.models import Relationship
from axis.sampleset.models import SampleSet
from axis.scheduling.models import ConstructionStage, TaskType
from axis.subdivision.models import Subdivision
from axis.customer_hirl.models import HIRLProject
from . import strings
from .models import Home, EEPProgramHomeStatus, HomePhoto
from axis.invoicing.models import InvoiceItemGroup, InvoiceItem

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")

BLANK_CHOICE = ("", "---------")

RATING_NAMES = [
    ("confirmed", "Confirmed Rating"),
    ("test", "Sampled Test House"),
    ("sampled", "Sampled House"),
]

REMRATE_FLAVORS = [
    BLANK_CHOICE,
    ("-1", "None"),
    ("rate", "Rate"),
    ("northwest", "Northwest"),
    ("washington", "Washington"),
    ("-2", "Northwest or Washington"),
]

MEETS_OR_BEATS = [BLANK_CHOICE, ("no", "No"), ("yes", "Yes")]

ACTIVITY_TYPE_CHOICES = [("any", "Any Activity"), ("certification", "Certification")]

HEAT_SOURCE_CHOICES = [
    BLANK_CHOICE,
    ("-1", "Gas Heat Homes *"),
    ("-2", "Heat Pump Homes *"),
    ("-3", "Other Heat Homes *"),
]

EXPORT_CHOICES = [
    ("home", "Project"),
    ("subdivision", "Subdivision/MF Development"),
    ("community", "Community"),
    ("relationships", "Associations"),
    ("eep_program", "Program"),
    ("floorplan", "Floorplan"),
    ("sampleset", "Sampleset"),
    ("simulation", "Simulation"),
    ("hes_data", "HES Data"),
    ("ngbs_data", "NGBS Data"),
    ("annotations", "Annotations"),
    ("checklist_answers", "Checklist Answers"),
    ("ipp", "Incentives"),
    ("invoicing", "Invoicing"),
    ("qa", "QA"),
    ("customer_aps", "APS Data"),
]

SIMULATION_TYPE_CHOICES = [("basic", "Simulation Basic"), ("advanced", "Simulation Advanced")]


def EEPPROGRAMHOMESTATUS_STATE_CHOICES():
    negate_states = [("-1", "Not Certified"), ("-2", "Not Certified (exclude abandoned)")]
    states = list(EEPProgramHomeStatus.get_state_choices())
    return [BLANK_CHOICE] + states + negate_states


def EEPPROGRAMHOMESTATUS_IPP_STATE_CHOICES():
    negate_states = [("-1", "Not Paid"), ("-2", "Not Received")]
    trim_ipp = [
        x for x in IncentivePaymentStatus.get_state_choices() if x[0] != "ipp_payment_requirements"
    ]
    return [BLANK_CHOICE] + trim_ipp + negate_states


def EEPPROGRAMHOMESTATUS_QASTATUS_CHOICES():
    negate_states = [
        ("-1", "Not Complete"),
        ("-2", "Does Not Exist"),
        ("-3", "QA Addable"),
        ("-4", "Not In Progress"),
    ]
    choices = [(key, value.description) for key, value in QAStateMachine.states.items()]
    return [BLANK_CHOICE] + choices + negate_states


def EEPPROGRAMHOMESTATUS_QAREQUIREMENT_TYPES():
    return [BLANK_CHOICE] + list(QARequirement.QA_REQUIREMENT_TYPES)


class HomeForm(forms.ModelForm):
    city = ApiModelChoiceField(
        widget=CityChoiceWidget, required=True, help_text=strings.HOME_HELP_TEXT_CITY
    )
    subdivision = forms.ModelChoiceField(
        queryset=Subdivision.objects.all(),
        widget=Select2Widget,
        required=False,
        help_text=strings.HOME_HELP_TEXT_SUBDIVISION,
    )
    updated_construction_stage = forms.ModelChoiceField(
        required=False, queryset=ConstructionStage.objects.filter(is_public=True)
    )

    class Meta:
        model = Home
        fields = (
            "lot_number",
            "street_line1",
            "street_line2",
            "is_multi_family",
            "city",
            "zipcode",
            "subdivision",
            "address_override",
            "geocode_response",
        )
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }

    def __init__(
        self,
        user,
        restricted_by_ipp=False,
        restricted_by_sampling=False,
        restricted_by_homestatus_state=False,
        *args,
        **kwargs,
    ):
        super(HomeForm, self).__init__(*args, **kwargs)
        self.user = user
        self.restricted_by_ipp = restricted_by_ipp
        self.restricted_by_sampling = restricted_by_sampling
        self.restricted_by_homestatus_state = restricted_by_homestatus_state
        self.configure_fields()

    def configure_fields(self):
        queryset = Subdivision.objects.filter_by_user(self.user).select_related("community")
        self.fields["subdivision"].queryset = queryset
        if not self.user.is_superuser:
            if self.restricted_by_ipp:
                for field in self.Meta.fields:
                    self.fields[field].widget.attrs["disabled"] = True
            if self.restricted_by_sampling:
                self.fields["subdivision"].widget.attrs["disabled"] = True
            if self.restricted_by_homestatus_state:
                # Note that if this is true, current logic also makes 'restricted_by_ipp' also true
                pass

        # Several fields are auto-inspected as required=False because we allow them blank=True
        self.fields["street_line1"].required = True


class HomeBLGCreationForm(forms.ModelForm):
    blg_file_raw_name = forms.CharField(widget=forms.HiddenInput, required=False)
    blg_file_raw = forms.CharField(widget=forms.HiddenInput, required=False)
    blg_file = forms.FileField(required=False)

    class Meta:
        model = Home
        fields = ("blg_file", "blg_file_raw", "blg_file_raw_name")


class HomeStatusForm(forms.ModelForm):
    requires_floorplan = None  # Helper attribute

    class Meta:
        model = EEPProgramHomeStatus
        fields = ("eep_program",)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(HomeStatusForm, self).__init__(*args, **kwargs)

        company_swap_candiates = get_owner_swap_queryset(user, include_self=True)
        if company_swap_candiates and company_swap_candiates.count() > 1:
            self.fields["company"] = forms.ModelChoiceField(
                queryset=company_swap_candiates,
                label="Program owner",
                help_text=strings.PROGRAM_HELP_OWNER,
            )
            if not self.instance.pk:
                self.fields["company"].initial = user.company.id

        if user.is_superuser or user.company.company_type in ("rater", "provider"):
            # This queryset is likely not correct if user is a provider, but their company is going
            # to appear autoselected in the 'company' field override anyway, so it's at least
            # consistent with the rest of the form until they make a change.
            default_users_queryset = user.company.users.all().only_active()
            self.fields["rater_of_record"] = forms.ModelChoiceField(
                queryset=default_users_queryset,
                help_text=strings.EEP_PROGRAM_HOME_STATUS_FORM_RATER_OF_RECORD,
            )
            self.fields["energy_modeler"] = forms.ModelChoiceField(
                queryset=default_users_queryset, help_text=""
            )
            self.fields["field_inspectors"] = forms.ModelMultipleChoiceField(
                queryset=default_users_queryset, help_text=""
            )

        self.configure_field_querysets(user)

        # Show customer HIRL only specific fields
        if self.instance and self.instance.pk and self.instance.eep_program:
            if self.instance.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS:
                if getattr(self.instance, "customer_hirl_project", None):
                    self.fields = {}
                    registration_user_company = (
                        self.instance.customer_hirl_project.registration.registration_user.company
                    )
                    if registration_user_company:
                        self.fields["customer_hirl_rough_verifier"] = forms.ModelChoiceField(
                            label="Rough Verifier",
                            queryset=registration_user_company.users.all(),
                            required=False,
                        )
                        self.fields["customer_hirl_final_verifier"] = forms.ModelChoiceField(
                            label="Final Verifier",
                            queryset=registration_user_company.users.all(),
                            required=False,
                        )

    def configure_field_querysets(self, user):
        eep_programs = EEPProgram.objects.filter_active_for_home_status_creation_by_user(
            user, is_qa_program=False, visible_for_use=True
        )
        eep_program_ids = list(eep_programs.values_list("id", flat=True))

        if self.instance.pk:
            # If QA has started on a home, we cannot allow the user to change the program out from
            # under us.  We can only allow the user to change the program to ones the QA company
            # has a Requirement for, and which conforms to company presence requirements on the
            # home's relationships.
            qa_statuses = self.instance.qastatus_set.filter(
                requirement__eep_program=self.instance.eep_program
            )
            company_hints = self.instance.home.relationships.all().get_orgs(ids_only=True)
            for qa_status in qa_statuses:
                qa_user = qa_status.owner.users.first()
                # We only want requirements of the same type as the original
                possible_qa_requirements = QARequirement.objects.filter_by_user(
                    qa_user, company_hints=company_hints
                ).filter(type=qa_status.requirement.type)

                addable_eep_program_ids = list(
                    possible_qa_requirements.values_list("eep_program__id", flat=True)
                )
                # Only show programs current user has access to AND active qa has a requirement for.
                eep_program_ids = list(
                    set(eep_program_ids).intersection(set(addable_eep_program_ids))
                )

            if self.instance.eep_program and self.instance.eep_program.id not in eep_program_ids:
                eep_program_ids.append(self.instance.eep_program.id)

            self.requires_floorplan = self.instance.eep_program.requires_floorplan()
            if "rater_of_record" in self.fields:
                self.fields[
                    "rater_of_record"
                ].queryset = self.instance.company.users.all().only_active()

        queryset = EEPProgram.objects.filter(id__in=eep_program_ids).order_by_customer_status()
        self.fields["eep_program"].queryset = queryset


class XLSHomeForm(HomeForm):
    """Specialized for XLS processing in a full bound form.clean() and form.save() cycle."""

    # This was the old HomeCoreModelForm, but this new name should make it clearer what its role is
    # now that the Examine mechanics have taken over the non-bulk pages.

    class Meta:
        model = Home
        exclude = (
            "construction_stage",
            "subdivision",
            "documents",
            "users",
            "modified_date",
            "eep_programs",
            "latitude",
            "longitude",
            "confirmed_address",
            "address_override",
        )
        labels = {
            "street_line1": "Street Address",
            "street_line2": "Unit number if applicable",
            "city": "City/State",
        }
        widgets = {
            # Hidden because we handle it with geocode JavaScript/AJAX.
            "geocode_response": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super(XLSHomeForm, self).__init__(*args, **kwargs)
        self.fields["street_line1"].required = True

    def clean_lot_number(self):
        lot_number = self.cleaned_data["lot_number"]
        if isinstance(lot_number, str):
            lot_number = lot_number.strip()
        return lot_number

    def clean_street_line2(self):
        street_line2 = self.cleaned_data["street_line2"]
        if not street_line2 or street_line2.strip() == "":
            return None
        return street_line2.strip()

    def clean(self):
        """Verify and confirm the address"""
        cleaned_data = self.cleaned_data

        # To make easier the task of detecting duplicates via existing logic, we will denormalize
        # the fields in the cleaned_data now, even though this is part of the on-save code for the
        # placedmodel base.
        denormalize_related_references_dict(cleaned_data)

        similar = self.Meta.model.objects.filter_similar(
            **{
                "street_line1": cleaned_data["street_line1"],
                "street_line2": cleaned_data["street_line2"],
                "city": cleaned_data.get("city", self.instance.city),
                "state": cleaned_data.get("state", self.instance.state),
                "zipcode": cleaned_data.get("zipcode", self.instance.zipcode),
                "geocode_response": cleaned_data.get("geocode_response"),
            }
        )
        if self.instance.id:
            similar = similar.exclude(id=self.instance.id)

        # Raise an error if any similar instances should trigger an alert to the frontend.
        if similar.count():
            addr = [
                cleaned_data["street_line1"],
                cleaned_data["street_line2"],
                cleaned_data.get("city", self.instance.city).name,
            ]
            if cleaned_data.get("geocode_response"):
                place = cleaned_data.get("geocode_response").get_normalized_fields(
                    return_city_as_string=True
                )
                addr = [place.get("street_line1"), place.get("street_line2"), place.get("city")]
            _similar = "<ul>"
            for _id in similar.values_list("id", flat=True):
                url = reverse("home:view", kwargs={"pk": _id})
                _similar += (
                    '<li><a href="{url}" target="_blank">{addr} (Lot: {lot})</a></li>'.format(
                        url=url, lot=cleaned_data["lot_number"], addr=", ".join(filter(None, addr))
                    )
                )
            _similar += "</ul>"

            if not cleaned_data["street_line2"]:
                if similar.filter(
                    (Q(street_line2__isnull=True) | Q(street_line2="")),
                    lot_number__iexact=cleaned_data["lot_number"],
                    street_line1__iexact=cleaned_data["street_line1"],
                    state=cleaned_data["state"],
                    zipcode=cleaned_data["zipcode"],
                ).count():
                    err = (
                        "A home with a matching Lot number '{}' and Street "
                        "Line 1 '{}'already exists.<br /> {}".format(
                            cleaned_data["lot_number"], cleaned_data["street_line1"], _similar
                        )
                    )

                    raise forms.ValidationError(mark_safe(err))
            else:
                if similar.filter(
                    lot_number__iexact=cleaned_data["lot_number"],
                    street_line1__iexact=cleaned_data["street_line1"],
                    street_line2__iexact=cleaned_data["street_line2"],
                    state=cleaned_data["state"],
                    zipcode=cleaned_data["zipcode"],
                ).count():
                    err = (
                        "A home with a matching Street Line 1 '{}' and "
                        "Street Line 2 '{}'already exists.<br /> {}".format(
                            cleaned_data["street_line1"], cleaned_data["street_line2"], _similar
                        )
                    )
                    raise forms.ValidationError(mark_safe(err))

            if cleaned_data.get("is_multi_family") and similar.filter(is_multi_family=True):
                pass
            else:
                if cleaned_data.get("is_multi_family"):
                    err = "A home at this address already exists but is not multi-family.<br /> {}".format(
                        _similar
                    )
                else:
                    err = "A home at this address already exists.<br /> {}".format(_similar)
                raise forms.ValidationError(mark_safe(err))

        return cleaned_data


class HomeCertifyForm(forms.ModelForm):
    certification_date = forms.DateField(required=True)

    class Meta:
        model = EEPProgramHomeStatus
        fields = ("certification_date",)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(HomeCertifyForm, self).__init__(*args, **kwargs)

    def clean_certification_date(self):
        certification_date = self.cleaned_data["certification_date"]

        if certification_date > datetime.date.today() + datetime.timedelta(days=1):
            raise forms.ValidationError("Homes may not certify more than 1 day in advance.")

        return certification_date

    def clean(self):
        cleaned_data = self.cleaned_data

        if self.user.company.id != self.instance.company.id:
            if self.user.company not in self.instance.company.relationships.get_companies():
                msg = """{company} does not have a relationship with {user}. This home was not certified."""
                log.error(msg.format(company=self.instance.company, user=self.user.company))
                raise forms.ValidationError(
                    msg.format(company=self.instance.company, user=self.user.company)
                )

        statuses = [self.instance]
        sampleset_membership = self.instance.get_samplesethomestatus()
        if sampleset_membership:
            sampleset_homes = sampleset_membership.sampleset.samplesethomestatus_set.current()
            statuses += [x.home_status for x in sampleset_homes]
        statuses = list(set(statuses))

        from axis.home.utils import HomeCertification

        cert_date = cleaned_data["certification_date"]

        issues = []
        can_certify = []
        for stat in statuses:
            certify = HomeCertification(self.user, stat, cert_date, fail_fast=True, log=log)

            if certify.already_certified:
                continue

            verified = certify.verify()
            can_certify.append(verified)

            if not verified:
                issues += certify.errors

        if not all(can_certify):
            if sampleset_membership:
                issues.insert(0, "Unable to certify any program in the sampleset")
            raise forms.ValidationError(issues)

        cleaned_data["statuses"] = statuses
        cleaned_data["warnings"] = issues
        return cleaned_data


class BulkHomeAsynchronousProcessedDocumentForm(AsynchronousProcessedDocumentForm):
    """This deals with uploading the document.. And our custom clean"""

    def clean_task_name(self):
        log.info("Home Assignment of the task name")
        from axis.checklist.tasks import bulk_checklist_process

        return bulk_checklist_process

    def clean(self):
        cleaned_data = super(AsynchronousProcessedDocumentForm, self).clean()
        cleaned_data["task_name"] = self.clean_task_name()
        cleaned_data["only_bulk_home_processing"] = True
        return cleaned_data


class HomeAsynchronousProcessedDocumentForm(AsynchronousProcessedDocumentForm):
    def clean_task_name(self):
        from axis.home.tasks import home_upload_process

        return home_upload_process

    def clean(self):
        cleaned_data = super(AsynchronousProcessedDocumentForm, self).clean()
        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data


class HomeStatusRaterForm(forms.Form):
    builder_org = forms.ModelChoiceField(queryset=Company.objects.none(), required=False)
    subdivision = forms.ModelChoiceField(queryset=Subdivision.objects.none(), required=False)


class HomeLabelForm(forms.Form):
    """Home Label Form used for printing labels"""

    homes = forms.MultipleChoiceField()
    default_date = forms.DateField(required=False)


class HomeCertificationForm(forms.Form):
    """Home Label Form used for printing certificates"""

    homes = forms.MultipleChoiceField()
    certifier = forms.ChoiceField(choices=[], required=False)


class HomeStatusFilterForm(forms.Form):
    """This is the home status filter"""

    # NOTE: Querysets need to be .all() if GET param filtering is expected to work.  If .none() is
    # used instead, the form will end up showing the right stuff by the time it's rendered, but it
    # will also show a validation error about the GET value not being a valid choice.
    subdivision = forms.ModelMultipleChoiceField(
        queryset=Subdivision.objects.none(), required=False, label="Subdivision/MF Development"
    )
    eep_program = forms.ModelMultipleChoiceField(
        queryset=EEPProgram.objects.all(), required=False, label="Program"
    )
    rater_of_record = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label="Rater of Record"
    )
    city = forms.ModelMultipleChoiceField(queryset=City.objects.none(), required=False)
    metro = forms.ModelMultipleChoiceField(queryset=Metro.objects.none(), required=False)
    eto_region = forms.ChoiceField(
        choices=[BLANK_CHOICE] + [(k, v) for k, v in ETO_REGIONS.items()],
        required=False,
        label="ETO Region",
    )
    us_state = forms.MultipleChoiceField(choices=US_STATES, required=False)
    rating_type = forms.ChoiceField(choices=RATING_NAMES, required=False)
    state = forms.ChoiceField(choices=EEPPROGRAMHOMESTATUS_STATE_CHOICES(), required=False)
    trim_ipp = [
        x for x in IncentivePaymentStatus.get_state_choices() if x[0] != "ipp_payment_requirements"
    ]
    ipp_state = forms.ChoiceField(
        choices=EEPPROGRAMHOMESTATUS_IPP_STATE_CHOICES(), required=False, label="Incentive Status"
    )
    qatype = forms.ChoiceField(
        choices=EEPPROGRAMHOMESTATUS_QAREQUIREMENT_TYPES(), required=False, label="QA Type"
    )
    qastatus = forms.ChoiceField(
        choices=EEPPROGRAMHOMESTATUS_QASTATUS_CHOICES(), required=False, label="QA Status"
    )
    qaobservation = forms.ModelMultipleChoiceField(
        queryset=ObservationType.objects.none(), required=False, label="QA Observations"
    )
    activity_date = forms.DateField(required=False)
    activity_type = forms.ChoiceField(choices=ACTIVITY_TYPE_CHOICES, required=False)
    activity_start = forms.DateField(required=False, label="Period Start")
    activity_stop = forms.DateField(required=False, label="Period End")
    certification_only = forms.BooleanField(
        required=False, label="Filter on certification date only"
    )
    program_activity_start = forms.DateField(required=False, label="Program Activity Start")
    program_activity_stop = forms.DateField(required=False, label="Program Activity End")

    certification_date_start = forms.DateField(required=False, label="Certification Date Start")
    certification_date_end = forms.DateField(required=False, label="Certification Date End")

    home_created_date_start = forms.DateField(required=False, label="Home Created Date Start")
    home_created_date_end = forms.DateField(required=False, label="Home Created Date End")

    task_type = forms.ModelMultipleChoiceField(queryset=TaskType.objects.none(), required=False)
    task_assignee = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    qa_designee = forms.ModelChoiceField(
        queryset=User.objects.none(), required=False, label="QA Designee"
    )

    paid_date_start = forms.DateField(required=False, label="Paid Date Start")
    paid_date_stop = forms.DateField(required=False, label="Paid Date End")

    heat_source = forms.ChoiceField(choices=HEAT_SOURCE_CHOICES, required=False, label="Heat Type")

    export_fields = forms.MultipleChoiceField(
        choices=EXPORT_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        initial=[choice[0] for choice in EXPORT_CHOICES],
    )
    search_bar = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    exclude_ids = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, data, *args, **kwargs):
        user = kwargs.pop("user", None)
        self.available_company_ids = kwargs.pop("available_company_ids", [])
        add_payment_date_filters = kwargs.pop("add_payment_date_filters", False)

        # If keys are provided blank in the querydict, multiselect2 fields really hate that.
        # Blank keys come from the dashboard having no value set on a field (which is valid).
        pop_blanks = ["us_state"] + list(dict(COMPANY_TYPES).keys())
        for pop_name in pop_blanks:
            if pop_name in data and not data[pop_name]:
                data.pop(pop_name)

        super(HomeStatusFilterForm, self).__init__(data, *args, **kwargs)

        self.init_multiselect_fields()
        self.init_company_fields()

        if user and user.company_id:
            self.fields["task_assignee"].queryset = User.objects.filter(company_id=user.company_id)

        if user and user.company_id:
            if user.is_customer_hirl_company_member():
                self.fields["qa_designee"].queryset = User.objects.filter(
                    company_id=user.company_id, hirluserprofile__is_qa_designee=True
                )
            else:
                self.fields["qa_designee"].queryset = User.objects.filter(
                    company_id=user.company_id
                )

        if user and not user.is_superuser:
            self.init_export_fields(user)

        if not add_payment_date_filters:
            del self.fields["paid_date_start"]
            del self.fields["paid_date_stop"]

        can_see_eto_region = user.company.slug in ("eto", "peci", "csg-qa") or user.is_superuser
        if not can_see_eto_region:
            del self.fields["eto_region"]

    def init_multiselect_fields(self):
        select_fields = [
            "subdivision",
            "eep_program",
            "metro",
            "city",
            "us_state",
            "rating_type",
            "qaobservation",
            "task_type",
        ]

        for field_name in select_fields:
            field = self.fields[field_name]
            if hasattr(field, "queryset"):
                choices = map(lambda o: (o.pk, o), list(field.queryset))
            else:
                choices = field.choices
            field.widget = Select2MultipleWidget(choices=choices)
            if (field_name + "_id") in self.data:
                self.data[field_name] = self.data[field_name + "_id"]

    def init_company_fields(self):
        available_company_queryset = Company.objects.filter(id__in=self.available_company_ids)
        for co_type, label in dict(COMPANY_TYPES).items():
            company_queryset = available_company_queryset.filter(company_type=co_type)
            field = forms.ModelMultipleChoiceField(
                queryset=company_queryset, required=False, label=label
            )
            choices = map(lambda o: (o.pk, o), field.queryset)
            field.widget = Select2MultipleWidget(choices=choices)

            self.fields[co_type] = field

    def init_export_fields(self, user):
        company_slug = "customer_{slug}".format(slug=user.company.slug)
        choices = [
            (name, label)
            for name, label in EXPORT_CHOICES
            if (name == company_slug or not name.startswith("customer"))
        ]
        self.fields["export_fields"].choices = choices
        self.fields["export_fields"].initial = [
            "home",
            "subdivision",
            "community",
            "relationships",
            "eep_program",
            "floorplan",
        ]


class ProviderDashboardFilterForm(HomeStatusFilterForm):
    """Filter class for the Provider dashboard."""

    remrate_flavor = forms.ChoiceField(choices=REMRATE_FLAVORS, required=False)
    meets_or_beats = forms.ChoiceField(choices=MEETS_OR_BEATS, required=False)


class NEEAUtilityFilterForm(HomeStatusFilterForm):
    has_bpa_association = forms.ChoiceField(
        label="BPA Affiliation",
        choices=(
            BLANK_CHOICE,
            ("false", "No"),
            ("true", "Yes"),
        ),
        required=False,
    )


class HomeStatusReportForm(forms.ModelForm):
    """Form used for the Home Status XLS Report"""

    subdivision = forms.ModelMultipleChoiceField(
        queryset=Subdivision.objects.none(), required=False
    )
    eep_program = forms.ModelMultipleChoiceField(
        queryset=EEPProgram.objects.none(), required=False, label="Program"
    )
    rater_of_record = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label="Rater of Record"
    )
    city = forms.ModelMultipleChoiceField(queryset=City.objects.none(), required=False)
    metro = forms.ModelMultipleChoiceField(queryset=Metro.objects.none(), required=False)
    eto_region = forms.ChoiceField(
        choices=[("", "---------")] + [(k, v) for k, v in ETO_REGIONS.items()],
        required=False,
        label="ETO Region",
    )
    us_state = forms.MultipleChoiceField(choices=US_STATES, required=False)
    rating_type = forms.ChoiceField(choices=RATING_NAMES, required=False)
    state = forms.ChoiceField(choices=EEPPROGRAMHOMESTATUS_STATE_CHOICES(), required=False)
    ipp_state = forms.ChoiceField(
        choices=EEPPROGRAMHOMESTATUS_IPP_STATE_CHOICES(), required=False, label="Incentive Status"
    )
    qatype = forms.ChoiceField(
        choices=EEPPROGRAMHOMESTATUS_QAREQUIREMENT_TYPES(), required=False, label="QA Type"
    )
    qastatus = forms.ChoiceField(
        choices=EEPPROGRAMHOMESTATUS_QASTATUS_CHOICES(), required=False, label="QA Status"
    )
    qa_designee = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label="QA Designee"
    )
    activity_date = forms.DateField(required=False)
    company = forms.ModelMultipleChoiceField(queryset=Company.objects.none(), required=False)
    activity_type = forms.ChoiceField(choices=ACTIVITY_TYPE_CHOICES, required=False)
    activity_start = forms.DateField(required=False)
    activity_stop = forms.DateField(required=False)
    certification_only = forms.BooleanField(
        required=False, label="Filter on certification date only"
    )
    program_activity_start = forms.DateField(required=False, label="Program Activity Start")
    program_activity_stop = forms.DateField(required=False, label="Program Activity End")

    qaobservation = forms.ModelMultipleChoiceField(
        queryset=ObservationType.objects.none(), required=False, label="QA Observations"
    )
    paid_date_start = forms.DateField(required=False, label="Paid Date Start")
    paid_date_stop = forms.DateField(required=False, label="Paid Date End")

    heat_source = forms.ChoiceField(choices=HEAT_SOURCE_CHOICES, required=False)

    search_bar = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())

    # -----------------------------------------------------------------------------------------------
    home_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False, initial=True)
    subdivision_field = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False, initial=True
    )
    community_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False, initial=True)
    relationships_field = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False, initial=True
    )
    eep_program_field = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False, initial=True
    )
    ipp_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    invoicing_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    floorplan_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False, initial=True)
    simulation_field = forms.ChoiceField(
        choices=SIMULATION_TYPE_CHOICES, widget=forms.RadioSelect(), required=False, initial="basic"
    )
    hes_field = forms.BooleanField(widget=forms.CheckboxInput(), label="HES Data", required=False)
    sampleset_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    annotations_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    checklist_answers_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    qa_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    customer_aps_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    customer_eto_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    customer_hirl_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    retain_empty_field = forms.BooleanField(widget=forms.CheckboxInput(), required=False)

    class Meta:
        model = AsynchronousProcessedDocument
        fields = ("task_name",)

    def __init__(self, *args, **kwargs):
        super(HomeStatusReportForm, self).__init__(*args, **kwargs)
        for co_type, label in dict(COMPANY_TYPES).items():
            self.fields[co_type] = forms.ModelMultipleChoiceField(
                queryset=Company.objects.none(), required=False, label=label
            )

        # -------------------------------------------------------------------------------------------
        self.checkbox_fields = OrderedDict(
            [
                ("home_field", "home"),
                ("subdivision_field", "subdivision"),
                ("community_field", "community"),
                ("relationships_field", "relationships"),
                ("eep_program_field", "eep_program"),
                ("floorplan_field", "floorplan"),
                ("sampleset_field", "sampleset"),
                ("simulation_field", "simulation"),
                ("hes_field", "hes_data"),
                ("annotations_field", "annotations"),
                ("checklist_answers_field", "checklist_answers"),
                ("ipp_field", "ipp"),
                ("invoicing_field", "invoicing"),
                ("qa_field", "qa"),
                ("customer_aps_field", "customer_aps"),
                ("customer_eto_field", "customer_eto"),
                ("customer_hirl_field", "ngbs_data"),
                ("retain_empty_field", "retain_empty"),
            ]
        )

        for field, name in self.checkbox_fields.items():
            self.fields[field].widget.attrs["type"] = "checkbox"

        self.fields["simulation_field"].widget.attrs["type"] = "radio"

    def clean_task_name(self):
        """This is the task name"""
        from .tasks import export_home_data

        return export_home_data

    def clean(self):
        """Validate the dates"""
        cleaned_data = super(HomeStatusReportForm, self).clean()

        cleaned_data["export_fields"] = []
        for field, name in self.checkbox_fields.items():
            if field in cleaned_data and cleaned_data[field]:
                if name == "simulation":
                    name = "{}_{}".format(name, cleaned_data[field])
                cleaned_data["export_fields"].append(name)
            if field == "home":
                cleaned_data["export_fields"].append("status")

        cleaned_data["task_name"] = self.clean_task_name()
        return cleaned_data


class HomeStatusExportFieldsForm(forms.Form):
    home_field = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=True, label="Project Data", required=False
    )
    subdivision_field = forms.BooleanField(
        widget=forms.CheckboxInput(),
        initial=True,
        label="Subdivision/MF Development",
        required=False,
    )
    community_field = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=True, label="Community Data", required=False
    )
    relationships_field = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=True, label="Company Association Data", required=False
    )
    eep_program_field = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=True, label="Program Data", required=False
    )
    ipp_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="Incentive Payment Data", required=False
    )
    invoicing_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="Invoicing Data", required=False
    )
    floorplan_field = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=True, label="Floorplan Data", required=False
    )
    simulation_field = forms.ChoiceField(
        choices=SIMULATION_TYPE_CHOICES, widget=forms.RadioSelect(), initial="basic", required=False
    )
    hes_field = forms.BooleanField(widget=forms.CheckboxInput(), label="HES Data", required=False)
    sampleset_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="Sampleset Data", required=False
    )
    annotations_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="Annotation Data", required=False
    )
    checklist_answers_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="Checklist Answer Data", required=False
    )
    qa_field = forms.BooleanField(widget=forms.CheckboxInput(), label="QA Data", required=False)
    customer_aps_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="APS Data", required=False
    )
    customer_eto_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="ETO Data", required=False
    )
    customer_hirl_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="NGBS Data", required=False
    )
    retain_empty_field = forms.BooleanField(
        widget=forms.CheckboxInput(), label="Retain Empty Columns", required=False
    )

    def __init__(self, *args, **kwargs):
        super(HomeStatusExportFieldsForm, self).__init__(*args, **kwargs)
        checkbox_fields = [
            "home_field",
            "subdivision_field",
            "community_field",
            "relationships_field",
            "eep_program_field",
            "floorplan_field",
            "simulation_field",
            "hes_field",
            "sampleset_field",
            "annotations_field",
            "checklist_answers_field",
            "retain_empty_field",
            "ipp_field",
            "invoicing_field",
            "qa_field",
            "customer_aps_field",
            "customer_eto_field",
            "customer_hirl_field",
        ]

        for field in checkbox_fields:
            self.fields[field].widget.attrs["type"] = "checkbox"

        self.fields["simulation_field"].widget.attrs["type"] = "radio"

    def get_excluded_fields(self, user, exclude_fields=False):
        # TODO: This backwards logic is hard to amend when new conditions come along...
        exclude = []

        if not Home.objects.filter_by_user(user).count() > 0:
            exclude.append("home_field")

        if not Subdivision.objects.filter_by_user(user).count() > 0:
            exclude.append("subdivision_field")

        if not Community.objects.filter_by_user(user).count() > 0:
            exclude.append("community_field")

        if not Relationship.objects.filter_by_user(user).count() > 0:
            exclude.append("relationships_field")

        if not EEPProgram.objects.filter_by_user(user).count() > 0:
            exclude.append("eep_program_field")

        if not Floorplan.objects.filter_by_user(user).count() > 0:
            exclude.append("floorplan_field")

        n_remrate_items = EEPProgramHomeStatus.objects.filter_by_user(
            user, floorplan__remrate_target__isnull=False
        ).count()
        n_ekotrope_items = EEPProgramHomeStatus.objects.filter_by_user(
            user, floorplan__ekotrope_houseplan__isnull=False
        ).count()
        if not n_remrate_items and not n_ekotrope_items:  # simulation field
            # TODO: how do we want to grab this?
            # TODO: Figure out what ^^that^^ means
            exclude.append("simulation_field")

        n_hes_items = EEPProgramHomeStatus.objects.filter_by_user(
            user, hes_score_statuses__isnull=False
        ).count()
        if not n_hes_items:  # hes
            exclude.append("hes_field")

        if not SampleSet.objects.filter_by_user(user).count() > 0:
            exclude.append("sampleset_field")

        # TODO:  This doesn't work because of how relationships span.
        # if not Type.objects.filter_by_user(user).count() > 0:
        #     exclude.append('annotations_field')

        if not Answer.objects.filter_by_user(user).count() > 0:
            exclude.append("checklist_answers_field")

        allow_ipp_export = any(
            [
                user.company.slug == "neea",  # They don't get filter_by_user() results, so override
                user.company.sponsors.filter(slug="neea").exists(),
            ]
        )
        if (
            not allow_ipp_export
            and not IncentivePaymentStatus.objects.filter_by_user(user).count() > 0
        ):
            exclude.append("ipp_field")

        always_allow_qa_export = any(
            [
                user.company.slug == "neea",  # They don't get filter_by_user() results, so override
                user.company.company_type == "utility",
            ]
        )
        if not always_allow_qa_export and not QAStatus.objects.filter_by_user(user).count() > 0:
            exclude.append("qa_field")

        company_slug = user.company.slug

        company_sponsors_slugs = user.company.sponsors.values_list("slug", flat=True)

        if "aps" not in company_slug and not user.is_superuser:
            exclude.append("customer_aps_field")

        if (
            "eto" not in company_slug
            and "eto" not in company_sponsors_slugs
            and not user.is_superuser
        ):
            exclude.append("customer_eto_field")

        if (
            customer_hirl_app.CUSTOMER_SLUG != company_slug
            and customer_hirl_app.CUSTOMER_SLUG not in company_sponsors_slugs
            and not user.is_superuser
        ):
            exclude.append("customer_hirl_field")

        if exclude_fields:
            for field in exclude:
                del self.fields[field]

        return exclude


class HomePhotoForm(forms.ModelForm):
    class Meta:
        model = HomePhoto
        fields = ("file", "is_primary")


# Forms specific to the Examine workflow
class HomeUsersForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        help_text=strings.HOME_HELP_TEXT_USERS,
        required=False,
        queryset=User.objects.none(),
        widget=Select2MultipleWidget,
    )

    class Meta:
        model = Home
        fields = ("users",)

    def __init__(self, user, *args, **kwargs):
        super(HomeUsersForm, self).__init__(*args, **kwargs)
        self.fields["users"].queryset = User.objects.filter_by_user(user)


class HomeStatusHIRLSingleFamilyProjectForm(forms.ModelForm):
    class Meta:
        model = HIRLProject
        fields = (
            "accessory_structure_description",
            "accessory_dwelling_unit_description",
            "green_energy_badges",
            "hud_disaster_case_number",
            "is_require_rough_inspection",
            "is_require_water_sense_certification",
            "is_require_wri_certification",
        )

    def __init__(self, *args, **kwargs):
        eep_program_slug = kwargs.pop("eep_program_slug", None)
        is_accessory_structure = kwargs.pop("is_accessory_structure", False)
        is_accessory_dwelling_unit = kwargs.pop("is_accessory_dwelling_unit", False)
        super(HomeStatusHIRLSingleFamilyProjectForm, self).__init__(*args, **kwargs)

        if is_accessory_structure:
            fields_to_remove = [
                "accessory_dwelling_unit_description",
                "green_energy_badges",
                "hud_disaster_case_number",
                "is_require_rough_inspection",
                "is_require_water_sense_certification",
            ]
        elif is_accessory_dwelling_unit:
            fields_to_remove = [
                "accessory_structure_description",
            ]
        else:
            fields_to_remove = [
                "accessory_structure_description",
                "accessory_dwelling_unit_description",
            ]

            if eep_program_slug not in customer_hirl_app.WATER_SENSE_PROGRAM_LIST:
                fields_to_remove.append("is_require_water_sense_certification")

            if eep_program_slug not in customer_hirl_app.REQUIRE_ROUGH_INSPECTION_PROGRAM_LIST:
                fields_to_remove.append("is_require_rough_inspection")

            if eep_program_slug not in customer_hirl_app.WRI_SEEKING_PROGRAM_LIST:
                fields_to_remove.append("is_require_wri_certification")

            filtered_badges = self.fields["green_energy_badges"].queryset.filter_by_eep_program(
                slug=eep_program_slug
            )
            self.fields["green_energy_badges"].queryset = filtered_badges

        for field_name in fields_to_remove:
            del self.fields[field_name]


class HomeStatusHIRLMultiFamilyProjectForm(forms.ModelForm):
    is_include_commercial_space = forms.BooleanField(label="Include Commercial Space")

    def __init__(self, *args, **kwargs):
        eep_program_slug = kwargs.pop("eep_program_slug", None)
        is_accessory_structure = kwargs.pop("is_accessory_structure", False)
        is_include_commercial_space = kwargs.pop("is_include_commercial_space", False)
        is_accessory_dwelling_unit = kwargs.pop("is_accessory_dwelling_unit", False)
        super(HomeStatusHIRLMultiFamilyProjectForm, self).__init__(*args, **kwargs)

        if is_accessory_structure:
            fields_to_remove = [
                "is_accessory_structure",
                "is_accessory_dwelling_unit",
                "hud_disaster_case_number",
                "green_energy_badges",
                "building_number",
                "is_include_commercial_space",
                "commercial_space_type",
                "total_commercial_space",
                "story_count",
                "number_of_units",
                "is_require_water_sense_certification",
                "is_require_rough_inspection",
            ]
        elif is_accessory_dwelling_unit:
            fields_to_remove = [
                "is_accessory_structure",
                "is_accessory_dwelling_unit",
                "hud_disaster_case_number",
                "green_energy_badges",
                "building_number",
                "is_include_commercial_space",
                "commercial_space_type",
                "total_commercial_space",
                "story_count",
                "number_of_units",
                "is_require_water_sense_certification",
                "is_require_rough_inspection",
            ]
        elif is_include_commercial_space:
            fields_to_remove = [
                "is_accessory_structure",
                "accessory_structure_description",
                "is_accessory_dwelling_unit",
                "accessory_dwelling_unit_description",
                "green_energy_badges",
                "is_include_commercial_space",
                "is_require_water_sense_certification",
                "is_require_rough_inspection",
                "story_count",
                "number_of_units",
            ]
        else:
            fields_to_remove = [
                "is_accessory_structure",
                "accessory_structure_description",
                "is_include_commercial_space",
                "commercial_space_type",
                "total_commercial_space",
            ]

            if eep_program_slug not in customer_hirl_app.WATER_SENSE_PROGRAM_LIST:
                fields_to_remove.append("is_require_water_sense_certification")

            if eep_program_slug not in customer_hirl_app.REQUIRE_ROUGH_INSPECTION_PROGRAM_LIST:
                fields_to_remove.append("is_require_rough_inspection")

            if eep_program_slug not in customer_hirl_app.WRI_SEEKING_PROGRAM_LIST:
                fields_to_remove.append("is_require_wri_certification")

            filtered_badges = self.fields["green_energy_badges"].queryset.filter_by_eep_program(
                slug=eep_program_slug
            )
            self.fields["green_energy_badges"].queryset = filtered_badges

        for field_name in fields_to_remove:
            del self.fields[field_name]

    class Meta:
        model = HIRLProject
        fields = (
            "is_accessory_structure",
            "accessory_structure_description",
            "is_accessory_dwelling_unit",
            "accessory_dwelling_unit_description",
            "hud_disaster_case_number",
            "green_energy_badges",
            "building_number",
            "is_include_commercial_space",
            "commercial_space_type",
            "total_commercial_space",
            "story_count",
            "number_of_units",
            "is_require_water_sense_certification",
            "is_require_rough_inspection",
            "is_require_wri_certification",
        )


class HomeStatusHIRLLandDevelopmentProjectForm(forms.ModelForm):
    class Meta:
        model = HIRLProject
        fields = ("number_of_lots",)


class HIRLInvoiceItemGroupForm(forms.ModelForm):
    class Meta:
        model = InvoiceItemGroup
        fields = ()


class HIRLInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ("name", "cost")
