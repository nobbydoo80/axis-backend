"""views.py: Django home"""

__author__ = "Steven Klass"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import json
import logging
import operator
import shutil
import tempfile
from collections import defaultdict, OrderedDict
from functools import reduce
from io import StringIO
from operator import itemgetter
from zipfile import ZipFile

import datatableview.helpers
import dateutil.parser

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.forms import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse, reverse_lazy
from django.utils import formats
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic import TemplateView, RedirectView, View, DetailView
from django.views.generic.edit import FormMixin

from axis.annotation.models import Annotation, Type
from axis.checklist.collection.collectors import get_user_role_for_homestatus
from axis.checklist.models import Answer
from axis.company.models import Company
from axis.company.strings import COMPANY_TYPES
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    AxisDatatableView,
    LegacyAxisDatatableView,
    AxisCreateView,
    AxisUpdateView,
    AxisConfirmView,
)
from axis.customer_eto.enumerations import ProjectTrackerSubmissionStatus
from axis.customer_eto.utils import ETO_REGIONS, get_zipcodes_for_eto_region_id
from axis.eep_program.models import EEPProgram
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.filehandling.views import AsynchronousProcessedDocumentCreateView
from axis.floorplan.models import Floorplan
from axis.geographic.models import Metro, City
from axis.home.datatables import HomeListDatatable, HomeStatusListDatatable
from axis.home.forms import (
    EEPPROGRAMHOMESTATUS_STATE_CHOICES,
    EEPPROGRAMHOMESTATUS_IPP_STATE_CHOICES,
    EEPPROGRAMHOMESTATUS_QASTATUS_CHOICES,
    EEPPROGRAMHOMESTATUS_QAREQUIREMENT_TYPES,
    HomeAsynchronousProcessedDocumentForm,
)
from axis.home.reports import BuiltGreenCertificate
from axis.home.tasks import certify_single_home, certify_sampleset
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.qa.models import QAStatus, QARequirement, ObservationType
from axis.relationship.models import Relationship
from axis.scheduling.models import TaskType, Task
from axis.subdivision.models import Subdivision
from axis.home.forms import (
    HomeCertifyForm,
    HomeLabelForm,
    HomeCertificationForm,
    HomeStatusFilterForm,
    HomeStatusReportForm,
    BulkHomeAsynchronousProcessedDocumentForm,
    ProviderDashboardFilterForm,
    HomePhotoForm,
)
from axis.home.models import Home, EEPProgramHomeStatus, HomePhoto
from axis.home.reports import HomeEnergyStarLabel, HomeCertificate
from axis.home.utils import write_home_program_reports

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class HomeListView(AuthenticationMixin, AxisDatatableView):
    """
    The list view for homes
    """

    permission_required = "home.view_home"
    datatable_class = HomeListDatatable

    # These are causing massive, massive slowdowns when we carelessly evaluate the full queryset.
    prefetch_related = [
        # 'eep_programs',
        # 'eep_programs__owner',
        # 'homestatuses__qastatus_set',
        # 'homestatuses__qastatus_set__requirement'
    ]
    select_related = [
        "subdivision",
        "subdivision__community",
    ]

    href = "<a href='{}'>{}</a>"

    def get_queryset(self):
        """
        Get the list of items for this view. In this case it's narrowed based on your company
        """

        # NOTE: user_eeps is used outside of the datatable kwargs, so compute it here so that
        # skipping precompute_hints() doesn't skip the creation of this variable.
        self._user_eeps = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        if (
            not self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            and self.request.GET.get("ajax") != "true"
        ):
            return Home.objects.none()

        if hasattr(self, "_queryset"):
            return self._queryset

        queryset = Home.objects.filter_by_user(user=self.request.user, show_attached=False)
        if self.kwargs.get("pk"):
            queryset = queryset.filter(subdivision__id=self.kwargs["pk"])

        queryset = (
            queryset.prefetch_related(*self.prefetch_related)
            .select_related(*self.select_related)
            .distinct()
        )
        self._queryset = queryset
        return self._queryset

    def precompute_hints(self):
        if not hasattr(self, "_home_stats"):
            eep_select_related = [
                "home",
                "floorplan",
                "eep_program",
                "eep_program__owner",
            ]
            self._user_eeps = EEPProgramHomeStatus.objects.filter_by_user(
                user=self.request.user
            ).select_related(*eep_select_related)

            self._home_stats = defaultdict(list)
            for stat in self._user_eeps:
                self._home_stats[stat.home.id].append(stat)

            # Question: Do we need these two queries to check?
            self._company_eep_programs = EEPProgram.objects.filter_by_company(
                self.request.user.company
            )
            self._user_floorplans = Floorplan.objects.filter_by_user(self.request.user)

            self._aps_metersets = []
            if self.request.user.company.slug == "aps":
                queryset = self.get_queryset()
                kwargs = {
                    "user": self.request.user,
                    "id__in": list(queryset.values_list("id", flat=True)),
                }
                self._aps_metersets = Home.objects.get_aps_ms_for_user_qs(**kwargs)

    def get_datatable_kwargs(self):
        kwargs = super(HomeListView, self).get_datatable_kwargs()

        kwargs["company"] = self.request.company

        # Send pre-baked queryset information
        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            self.precompute_hints()
            kwargs["hints"] = {
                "user_eeps": self._user_eeps,
                "home_stats": self._home_stats,
                "company_eep_programs": self._company_eep_programs,
                "user_floorplans": self._user_floorplans,
                "aps_metersets": self._aps_metersets,
            }

        return kwargs

    def get_datatable(self):
        datatable = super(HomeListView, self).get_datatable()

        use_aps_column = False
        try:
            if self.request.user.company.id == Company.objects.get(slug__iexact="aps").id:
                use_aps_column = True
        except Company.DoesNotExist:
            pass

        if not use_aps_column:
            del datatable.columns["ms_date"]

        # Drop the qa_states column if no qastatus items exist.
        if not self._user_eeps.filter(
            qastatus__isnull=False
        ).exists() or not self.request.user.has_perm("qa.view_qastatus"):
            del datatable.columns["qa_states"]

        return datatable

    def get_context_data(self, **kwargs):
        """
        Get all associated context data.
        :param kwargs: Optional kwargs
        """
        context = super(HomeListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        try:
            if company.id == Company.objects.get(name__iexact="aps").id:
                context["aps"] = True
        except Company.DoesNotExist:
            pass
        # Remove once no longer using legacy
        custom_home_ids = Home.objects.filter(is_custom_home=True).values_list("id", flat=True)
        custom_rels = Relationship.objects.filter_homes_for_company(company, show_attached=True)
        custom_rels = custom_rels.filter(is_owned=False, object_id__in=custom_home_ids)
        custom_rel_ids = custom_rels.values_list("object_id", flat=True)
        context["custom_home_relationships"] = Home.objects.filter(id__in=custom_rel_ids)

        return context


class BulkHomeAsynchronousProcessedDocumentCreateView(AsynchronousProcessedDocumentCreateView):
    """A way to upload a bunch of homes.."""

    permission_required = "home.add_home"
    form_class = BulkHomeAsynchronousProcessedDocumentForm

    def get_context_data(self, **kwargs):
        """Adds in all context data"""
        context = super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
        context["template"] = settings.STATIC_URL + "templates/BulkUpload.xlsx"
        context["title"] = "Bulk home upload"
        return context


class HomeAsynchronousProcessedDocumentCreateView(AsynchronousProcessedDocumentCreateView):
    """A way to upload a bunch of homes.."""

    permission_required = "home.add_home"
    form_class = HomeAsynchronousProcessedDocumentForm

    def get_context_data(self, **kwargs):
        """Adds in all context data"""
        context = super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
        # context['template'] = settings.STATIC_URL + 'templates/BulkUpload.xlsx'
        context["title"] = "Single home upload"
        return context


class SetStateView(AuthenticationMixin, AxisConfirmView):
    permission_required = "home.change_home"
    template_name = "home/eepprogramhomestatus_confirm_state_view_update.html"

    def confirm(self, request, *args, **kwargs):
        """Update the state for the ``EEPProgramHomeStatus``."""
        self.object.make_transition(self.kwargs.get("state"), user=request.user)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        """Filters objects by user company."""
        return EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)

    def get_cancel_url(self):
        """Go back to the associated ``Home``."""
        return self.object.home.get_absolute_url()

    def get_success_url(self):
        """Redirect to the associated ``Home``."""
        return self.object.home.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(SetStateView, self).get_context_data(**kwargs)
        self.object = self.get_object()
        context["next_state"] = "abandoned"
        if self.object.state == "abandoned":
            context["next_state"] = "pending_inspection"
        return context


class CertifyEEPHomeStatView(AuthenticationMixin, AxisUpdateView):
    """This is used to certify a home"""

    template_name = "home/home_certify.html"
    form_class = HomeCertifyForm

    def has_permission(self):
        # TODO: Expand on this to further protect tampered access to the page.
        # The QA perm should likely only allow you to view this if other conditions are met.
        # In circumstances where we don't show the user the button to get here, they can still hit
        # the url without a permission error.
        return self.request.user.has_perm("home.change_home") or self.request.user.has_perm(
            "qa.change_qastatus"
        )

    def get_queryset(self):
        return EEPProgramHomeStatus.objects.filter_by_user(self.request.user)

    def get_object(self):
        obj = super(CertifyEEPHomeStatView, self).get_object()
        self.sampleset = obj.get_sampleset()

        if obj.certification_date:
            if not self.sampleset:
                # Home with certification date should be stopped as long as it's solo
                raise Http404("Home is already certified.")
            else:
                # Try to find another home in the sampleset that isn't certified
                uncertified_items = self.sampleset.samplesethomestatus_set.current().uncertified()
                if uncertified_items:
                    obj = uncertified_items[0].home_status
                else:
                    raise Http404("Sampleset is already fully certified.")

        return obj

    def get_form_kwargs(self):
        """Send user company to form constructor."""
        kwargs = super(CertifyEEPHomeStatView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super(CertifyEEPHomeStatView, self).get_initial()
        cert_date = datetime.date.today()
        sampleset = self.object.get_sampleset()
        if sampleset:
            certified_items = sampleset.samplesethomestatus_set.current().certified()
            dates = list(
                filter(
                    None,
                    list(certified_items.values_list("home_status__certification_date", flat=True)),
                )
            )
            cert_date = dates[0] if dates else cert_date
        initial["certification_date"] = cert_date.strftime("%m/%d/%Y")
        return initial

    def form_invalid(self, form):
        log.info(form.errors)
        return super(CertifyEEPHomeStatView, self).form_invalid(form)

    def form_valid(self, form):
        """
        Starts ``certify_eep_program_form_home`` task function, which sets all answers to confirmed;
        no more retraction.
        """
        # NOTE: This could be moved to a method on the EEPProgramHomeStatus model, but it's unclear
        # at this stage how to promise the system that the method won't be called at inappropriate
        # times.  At present, keeping the logic here at least creates a requirement of explicit
        # intent to certify.

        if self.object not in form.cleaned_data.get("statuses"):
            self.object = form.cleaned_data.get("statuses")[0]

        home_stat = EEPProgramHomeStatus.objects.get(id=self.object.id)

        # NOTE: some sample homes come back saying they have no questions. Their completeness
        # cannot be updated. So we look to the parent of the sampleset to get information.
        sshs = home_stat.get_samplesethomestatus()
        sampleset = sshs.sampleset if sshs else None
        if sshs:
            if self.object.pct_complete < 99.9 and not sshs.is_test_home:
                for item in sampleset.samplesethomestatus_set.current().filter(is_test_home=True):
                    for stat in item.home_status.home.homestatuses.all():
                        if stat.pct_complete > self.object.pct_complete:
                            self.object.pct_complete = stat.pct_complete

        self.object.save()
        self.object.update_stats()

        kwargs = {
            "home_stat_id": home_stat.id,
            "user_id": self.request.user.id,
            "certification_date": form.cleaned_data["certification_date"],
        }
        # NOTE: We have stopped running the task asynchronously for single homestatuses
        if sampleset is None:
            certify_single_home(
                self.request.user, home_stat, form.cleaned_data["certification_date"]
            )
        else:
            certify_sampleset(self.request.user, sampleset, form.cleaned_data["certification_date"])

        cert_type = (
            "Certified" if home_stat.eep_program.slug != "neea-efficient-homes" else "Completed"
        )

        try:
            cert_date = formats.date_format(home_stat.certification_date, "SHORT_DATE_FORMAT")
        except AttributeError:
            if home_stat.certification_date is not None:
                log.error("Unable to figure out cert_date %s", home_stat.certification_date)
            cert_date = home_stat.certification_date

        context = {
            "home_url": home_stat.get_absolute_url(),
            "home": "{}".format(home_stat.home),
            "certifying_company": "{}".format(self.request.company),
            "certification_type": cert_type,
            "certification_date": cert_date,
        }

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """Return the the community list"""
        eep_stat = EEPProgramHomeStatus.objects.get(id=self.kwargs.get("pk"))
        return reverse("home:view", kwargs={"pk": eep_stat.home.pk})

    def get_context_data(self, **kwargs):
        context = super(CertifyEEPHomeStatView, self).get_context_data(**kwargs)

        context.update(
            {"sampleset": self.sampleset, "homes": [], "certified_homes": [], "certifiable": []}
        )
        if self.sampleset:
            context["homes"] = [
                sshs.home_status
                for sshs in self.sampleset.samplesethomestatus_set.current()
                .uncertified()
                .select_related("home_status__home")
            ]
            context["certified_homes"] = [
                sshs.home_status
                for sshs in self.sampleset.samplesethomestatus_set.current()
                .certified()
                .select_related("home_status__home")
            ]
            context["certifiable"] = [
                sshs.home_status.id
                for sshs in self.sampleset.samplesethomestatus_set.current()
                if sshs.home_status.get_simplified_status_for_user(self.request.user).can_certify
            ]
        else:
            obj = EEPProgramHomeStatus.objects.get(id=self.kwargs.get("pk"))
            status = obj.get_simplified_status_for_user(self.request.user)
            if status.can_certify:
                context["certifiable"] = [obj.id]
        return context


class EEPProgramHomeStatusListView(AuthenticationMixin, LegacyAxisDatatableView):
    """This will simply provide a list view for the Program Home Status"""

    permission_required = "home.view_home"
    template_name = "home/home_list.html"

    datatable_options = {
        "columns": [
            (
                "Address",
                [
                    "home__lot_number",
                    "home__street_line1",
                    "home__street_line2",
                    "home__city__name",
                    "home__state",
                    "home__zipcode",
                ],
            ),
            ("Subdivision/MF Project", "home__subdivision__name"),
            ("Floorplan", "floorplan__name"),
            ("Program", "eep_program__name"),
            ("Cert Date", "certification_date"),
            ("State", "state"),
        ],
    }

    select_related = [
        "home",
        "home__subdivision",
        "home__subdivision__community",
        "home__city",
        "floorplan",
        "eep_program",
    ]

    def get_queryset(self):
        qs = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        if self.kwargs.get("certified_only"):
            qs = qs.filter(certification_date__isnull=False)
        qs = qs.select_related(*self.select_related)
        return qs

    def get_column_Address_data(self, obj, *args, **kwargs):
        return obj.home.get_home_address_display(
            include_lot_number=True, company=self.request.company
        )

    def get_column_Subdivision_data(self, obj, *args, **kwargs):
        subdivision = obj.home.subdivision
        if subdivision:
            return datatableview.helpers.link_to_model(subdivision, text=subdivision.name)
        return ""

    def get_column_Floorplan_data(self, obj, *args, **kwargs):
        if obj.floorplan:
            return datatableview.helpers.link_to_model(obj.floorplan)
        return ""

    def get_column_EEP_Programs_data(self, obj, *args, **kwargs):
        return datatableview.helpers.link_to_model(obj.eep_program)

    def get_column_State_data(self, obj, *args, **kwargs):
        return obj.state_description

    def get_column_Cert_Date_data(self, obj, *args, **kwargs):
        try:
            return obj.certification_date.strftime("%m/%d/%Y")
        except AttributeError:
            return ""

    def get_add_url(self):
        return reverse("home:add")

    def get_context_data(self, **kwargs):
        context = super(EEPProgramHomeStatusListView, self).get_context_data(**kwargs)
        # Our generic base finds the EEPProgramHomeStatus model, but we're presenting the
        # information more like a list of Homes.
        context["verbose_name_plural"] = "Homes"
        context["can_add"] = Home.can_be_added(self.request.user)
        return context


class HomeEnergyStarLabelForm(EEPProgramHomeStatusListView, FormMixin):
    permission_required = "home.view_home"
    form_class = HomeLabelForm
    template_name = "home/estar_label_form.html"
    success_url = reverse_lazy("home:report:energy_star_certificate")

    def get_queryset(self):
        queryset = super(HomeEnergyStarLabelForm, self).get_queryset()
        estar_programs = [
            "aps-energy-star-v3",
            "aps-energy-star-v3-hers-60",
            "aps-energy-star-v3-2014",
            "aps-2015-audit",
            "neea-energy-star-v3",
            "neea-energy-star-v3-performance",
            "neea-performance-2015",
            "neea-prescriptive-2015",
            "energy-star-version-3-rev-07",
            "energy-star-version-3-rev-08",
            "energy-star-version-31-rev-05",
            "energy-star-version-31-rev-08",
            "ncbpa-epa-energy-star-v3-rev-08",
        ]
        queryset = (
            queryset.filter(eep_program__slug__in=estar_programs)
            .exclude(state="abandoned")
            .distinct()
        )

        if not hasattr(self, "_annotations"):
            annotations = queryset.filter(
                annotations__type__slug="last_estar_date",
                annotations__user__company_id=self.request.user.company.id,
            )
            self._annotations = annotations.values_list("id", "annotations__content")
        return queryset

    def has_permission(self):
        return self.request.user.has_perm("home.change_home")

    def post(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        form = self.get_form(self.form_class)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        try:
            kwargs["object_list"] = kwargs.get("object_list", self.object_list)
        except AttributeError:
            self.object_list = kwargs["object_list"] = self.get_queryset()
        kwargs["form"] = kwargs.get("form", self.get_form(self.form_class))
        context = super(HomeEnergyStarLabelForm, self).get_context_data(**kwargs)
        return context

    def get_initial(self):
        initial = super(HomeEnergyStarLabelForm, self).get_initial()
        initial["default_date"] = datetime.date.today().strftime("%Y-%m-%d")
        return initial

    def get_form(self, form_class=None):
        form = super(HomeEnergyStarLabelForm, self).get_form(form_class)
        form.fields["homes"].choices = [
            (x, x) for x in self.get_queryset().values_list("id", flat=True)
        ]
        form.fields["homes"].required = True
        return form

    def get_datatable_options(self):
        options = self.datatable_options.copy()
        options["columns"] = options["columns"][:]
        options["columns"].insert(0, ("select", None, "get_column_select_data"))
        options["columns"].insert(
            1, ("Last Printed", ["annotations__content"], "get_column_last_printed")
        )
        options["unsortable_columns"] = ["select", "Last Printed"]

        return options

    def get_column_select_data(self, obj, *args, **kwargs):
        return "<input data-id='{}' type='checkbox'>".format(obj.id)

    def get_column_last_printed(self, obj, *args, **kwargs):
        try:
            cert = dict(self._annotations).get(obj.id)
            return dateutil.parser.parse(cert).strftime("%m/%d/%Y")
        except (AttributeError, TypeError):
            return ""

    def update_last_printed_date(self, stats, slug="last_estar_date"):
        from axis.annotation.models import Type, Annotation
        from django.contrib.contenttypes.models import ContentType

        try:
            ann_type = Type.objects.get(slug=slug)
        except Type.DoesNotExist:
            log.error("Missing annotation - %s", slug)
            return
        else:
            ct = ContentType.objects.get_for_model(EEPProgramHomeStatus)
            for stat in stats:
                kw = dict(type=ann_type, content_type=ct, object_id=stat.id, user=self.request.user)
                ann, _c = Annotation.objects.get_or_create(**kw)
                ann.content = datetime.date.today()
                ann.save()

    def form_valid(self, form):
        filename = tempfile.NamedTemporaryFile()
        labels = HomeEnergyStarLabel(filename=filename)
        homes = EEPProgramHomeStatus.objects.filter(id__in=form.cleaned_data["homes"])
        labels.build(homes=homes, default_date=form.cleaned_data["default_date"])
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=axis_home_labels.pdf"
        response.write(filename.read())

        # Store the date this was printed..
        self.update_last_printed_date(homes, slug="last_estar_date")
        return response

    def form_invalid(self, form):
        log.warning(form.errors)
        return super(HomeEnergyStarLabelForm, self).form_invalid(form)


def _get_ref_NWESHCertificationReport():
    # home.export_data module import views, and the views brings in a report that wants export_data
    # stuff.  This is not the ideal place to fix a circular import, but the views are parent classes
    # over in the export_data module, so we can't fix it there.
    from axis.customer_neea.reports import NWESHCertificationReport

    return NWESHCertificationReport


class HomeCertificateForm(HomeEnergyStarLabelForm):
    """
    Prints a Home Certificate.
    If a company requires a custom certificate, put the Certificate Generator in the
    `custom_company_certificate_classes` dict mapped to the companies slug.
    Make a Corresponding '{company_slug}_USE_NEW_CERTIFICATE' flag in the settings files.
    """

    template_name = "home/certificate_form.html"
    form_class = HomeCertificationForm
    success_url = "/"

    datatable_options = {
        "columns": [
            (
                "Address",
                [
                    "home__lot_number",
                    "home__street_line1",
                    "home__street_line2",
                    "home__city__name",
                ],
            ),
            ("Subdivision/MF Project", "home__subdivision__name"),
            ("Floorplan", "floorplan__name"),
            ("Program", "eep_program__name"),
            ("Cert Date", "certification_date"),
            ("State", "state"),
        ],
    }

    custom_company_certificate_classes = {
        "neea": _get_ref_NWESHCertificationReport,
        "provider-home-builders-association-of-tri-cities": BuiltGreenCertificate,
    }
    custom_company_certificate_classes_program_exclusion = {
        "neea": ["utility-incentive-v1-single-family", "utility-incentive-v1-multifamily"]
    }

    def get_queryset(self, skip_annotations=False):
        queryset = super(HomeEnergyStarLabelForm, self).get_queryset()
        queryset = queryset.exclude(eep_program__owner__slug="eto")
        queryset = queryset.exclude(eep_program__slug="neea-efficient-homes")
        queryset = queryset.filter(state="complete", certification_date__isnull=False).distinct()
        queryset = queryset.select_related(
            "home", "home__subdivision", "home__city", "floorplan", "eep_program", "company"
        )
        if not hasattr(self, "_annotations"):
            annotations = queryset.filter(
                annotations__type__slug="last_cert_date",
                annotations__user__company_id=self.request.user.company.id,
            )
            self._annotations = annotations.values_list("id", "annotations__content")

        return queryset

    def has_permission(self):
        return self.request.user.has_perm("home.change_home")

    def get_form(self, form_class=None):
        """Get the form"""
        form = super(HomeEnergyStarLabelForm, self).get_form(form_class)
        homes_qs = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        if self.kwargs.get("certified_only"):
            homes_qs = homes_qs.filter(certification_date__isnull=False)

        form.fields["homes"].choices = [(x, x) for x in homes_qs.values_list("id", flat=True)]
        form.fields["homes"].required = True

        companies = (
            Company.objects.filter_by_user(self.request.user)
            .filter(company_type__in=["rater"])
            .values_list("id", flat=True)
        )
        companies = list(companies) + [self.request.user.company.id]
        users = User.objects.filter(company_id__in=companies)
        choices = [(x.id, "{} ({})".format(x.get_full_name(), x.company)) for x in users]
        form.fields["certifier"].choices = choices
        return form

    def form_valid(self, form):
        home_stats_by_program = defaultdict(list)
        home_stats = EEPProgramHomeStatus.objects.filter(id__in=form.cleaned_data["homes"])
        certifier = form.cleaned_data.get("certifier")

        for stat in home_stats:
            home_stats_by_program[stat.eep_program.slug].append(stat)

        if len(set(home_stats.values_list("eep_program__slug"))) > 1:
            response = self.generate_multiple_reports(home_stats, certifier)
        else:
            response = self.generate_single_report(home_stats, certifier)

        self.update_last_printed_date(home_stats, slug="last_cert_date")

        return response

    def get_certificate_printing_class(self, program):
        """
        Given a program will return the Certificate
        Printing class associated with that programs owner.
        If a flag in the settings file exists for this owner
        it 'must' be defined in the `custom_company_certificate_classes` dict.
        """
        if program.slug not in self.custom_company_certificate_classes_program_exclusion.get(
            program.owner.slug, []
        ):
            slug = program.owner.slug
            settings_string = "{}_USE_NEW_CERTIFICATE".format(slug.upper().replace("-", "_"))

            if getattr(settings, settings_string, False):
                report_class = self.custom_company_certificate_classes[slug]
                if callable(report_class):
                    report_class = report_class()
                return report_class

        return HomeCertificate

    def generate_single_report(self, home_stats, certifier):
        """Will return one pdf containing all the homes."""
        certificate_class = self.get_certificate_printing_class(home_stats[0].eep_program)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=axis_home_certificate.pdf"

        filename = tempfile.NamedTemporaryFile()

        labels = certificate_class(filename=filename)
        labels.build(home_stats=home_stats, certifier_id=certifier)

        response.write(filename.read())

        return response

    def generate_multiple_reports(self, home_stats, certifier):
        """Will Create one pdf for each program and package it in a nice zip file."""
        home_stats_by_program = defaultdict(list)

        for stat in home_stats:
            home_stats_by_program[stat.eep_program].append(stat)

        in_memory = StringIO()
        zip = ZipFile(in_memory, "a")

        for program, group in home_stats_by_program.items():
            filename = tempfile.NamedTemporaryFile()
            certificate_class = self.get_certificate_printing_class(program)

            labels = certificate_class(filename=filename)
            labels.build(home_stats=group, certifier_id=certifier)

            zip.writestr("axis_cert_{}.pdf".format(program.slug), filename.read())

        zip.close()

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=axis_certs.zip"

        in_memory.seek(0)
        response.write(in_memory.read())

        return response

    def get_column_Address_data(self, obj, *args, **kwargs):
        text = obj.home.get_home_address_display(
            include_lot_number=True, company=self.request.company
        )
        return datatableview.helpers.link_to_model(obj.home, text=text)

    def get_column_Subdivision_data(self, obj, *args, **kwargs):
        subdivision = obj.home.subdivision
        if subdivision:
            return datatableview.helpers.link_to_model(subdivision, text=subdivision.name)
        return "Custom Home"

    def get_column_Floorplan_data(self, obj, *args, **kwargs):
        if obj.floorplan:
            return datatableview.helpers.link_to_model(obj.floorplan)
        return "-"

    def get_column_EEP_Programs_data(self, obj, *args, **kwargs):
        if obj.eep_program:
            return datatableview.helpers.link_to_model(obj.eep_program)
        return "-"

    def get_column_State_data(self, obj, *args, **kwargs):
        return obj.state_description


class HomeChecklistreport(HomeCertificateForm):
    template_name = "home/checklist_report.html"

    single_homestatus_filename = "Program_Report.pdf"
    multi_homestatus_filename = "Program_Report_{street_line1}.pdf"
    multi_homestatus_zipname = "Program_Reports.zip"

    def has_permission(self):
        return self.request.user.has_perm("home.view_home")

    def get(self, request, *args, **kwargs):
        if "home_status" not in kwargs:
            return super(HomeChecklistreport, self).get(request, *args, **kwargs)
        home_status_qs = EEPProgramHomeStatus.objects.filter(id=kwargs["home_status"])
        if home_status_qs.count() == 0:
            raise Http404()
        return self.generate_report(home_status_qs)

    def form_valid(self, form):
        home_stats = EEPProgramHomeStatus.objects.filter(id__in=form.cleaned_data["homes"])
        return self.generate_report(home_stats)

    def generate_report(self, home_stats):
        if len(home_stats) > 1:
            content_type = "application/zip"
        else:
            content_type = "application/pdf"

        response = HttpResponse()
        filename, response_stream = write_home_program_reports(self.request.user, home_stats)
        response_stream.seek(0)
        shutil.copyfileobj(response_stream, response)

        response["Content-Type"] = content_type
        response["Content-Disposition"] = "attachment; filename={}".format(filename)

        return response

    def get_queryset(self):
        queryset = EEPProgramHomeStatus.objects.all()
        queryset = queryset.select_related(*self.select_related)
        return queryset

    def get_form(self, form_class=None):
        """Get the form"""
        form = super(HomeEnergyStarLabelForm, self).get_form(form_class)
        homes_qs = EEPProgramHomeStatus.objects.all()
        if self.request.user.company.company_type in ["rater", "provider"]:
            homes_qs = EEPProgramHomeStatus.objects.all()

        form.fields["homes"].choices = [(x, x) for x in homes_qs.values_list("id", flat=True)]
        form.fields["homes"].required = True
        return form

    def get_context_data(self, **kwargs):
        context = super(HomeChecklistreport, self).get_context_data(**kwargs)
        context["page_title"] = "Home Checklist Report"
        return context


class HomeStatusReportMixin(object):
    def get_base_queryset(self):
        return EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)

    def prevision_kwargs(self, **kwrgs):
        kwargs = {}
        for k, v in kwrgs.items():
            k = k[:-2] if k.endswith("[]") else k

            if v in ["", "undefined", [""], ["undefined"]]:
                v = None
            elif v in ["true", "on", ["true"], ["on"]]:
                v = True
            elif v in ["false", "off", ["false"], ["off"]]:
                v = False
            elif isinstance(v, (list, tuple)):
                if len(v) == 1:
                    v = v[0]
                else:
                    v = list(filter(None, v))

            if k not in kwargs:
                kwargs[k] = v
            else:
                if kwargs[k] is None:
                    kwargs[k] = v
                elif isinstance(kwargs[k], (list, tuple)):
                    v = [v] if not isinstance(v, list) else v
                    kwargs[k] += v
                else:
                    existing = [kwargs[k]] if not isinstance(kwargs[k], list) else kwargs[k]
                    v = [v] if not isinstance(v, list) else v
                    kwargs[k] = existing + v
        log.debug("*+" * 10)
        for k, v in kwargs.items():
            if v is None or k == "_":
                continue
            if len(k) > 1 and (k[0].lower() == k[0] and k[1].upper() == k[1]):
                if k != "sSearch":
                    continue
            log.debug("{}: {}".format(k, v))
        log.debug("*-" * 10)
        return kwargs

    def add_filter(self, label, value):
        if isinstance(value, (QuerySet, list)):
            value = " or ".join(["{}".format(x) for x in value])
        elif not isinstance(value, str):
            value = "{}".format(value)
        log.debug("Filtering on %s = %s", label, value)
        self.filters.append((label, value))

    def filter_by_task_type(self, task_type_ids=None, **kwargs):
        self.exclude["home__task__isnull"] = True
        self.filter["home__task__task_type_id__in"] = task_type_ids

        if kwargs.get("return_filters"):
            self.add_filter("Task Type", task_type_ids)

    def filter_by_task_assignee(self, task_assignee, **kwargs):
        self.exclude["home__task__isnull"] = True
        viewable_tasks = Task.objects.filter_by_user(self.request.user).values_list("id", flat=True)
        self.filter["home__task__id__in"] = list(viewable_tasks)
        self.filter["home__task__assignees__in"] = map(int, self._get_list_from_type(task_assignee))

        if kwargs.get("return_filters"):
            self.add_filter("Task Assignee", task_assignee)

    def filter_by_mode(self, mode=None, **kwargs):
        """Filter by datatable mode (implicit filters not represented in the sidebar)"""

        if mode == "projecttracker":
            if kwargs.get("return_filters"):
                self.add_filter("Mode", mode)

            # Filter version of EEPProgramHomeStatus.is_allowed_by_projecttracker()
            # Note that the 'completed' homestatus check is automatically included because of the
            # sidebar filter.
            self.q_filters.append(
                Q(eep_program__slug__startswith="eto", eep_program__is_qa_program=False)
            )

            # Only show programs that have an end_date >= 6 months.
            close_by = now() - datetime.timedelta(days=180)
            self.q_filters.append(
                (
                    Q(eep_program__program_end_date__gte=close_by)
                    | Q(eep_program__program_end_date__isnull=True)
                )
            )
            fail = ProjectTrackerSubmissionStatus.FAILURE
            no_previous_submission_or_fails = Q(
                Q(fasttracksubmission__submit_status__isnull=True)
                | Q(fasttracksubmission__submit_status="")
                | Q(fasttracksubmission__submit_status=fail)
                | Q(fasttracksubmission__solar_submit_status=fail),
                fasttracksubmission__eps_score__isnull=False,
                state="complete",
            )
            self.q_filters.append(no_previous_submission_or_fails)

    def filter_by_subdivision(self, subdivision_ids=None, **kwargs):
        """Filter by list of Subdivision ids."""
        if kwargs.get("return_filters"):
            objects = Subdivision.objects.filter(id__in=subdivision_ids)
            self.add_filter("Subdivision/MF Project", objects)

        self.filter["home__subdivision_id__in"] = subdivision_ids

    def filter_by_eep_program(self, eep_ids, **kwargs):
        """Filter by list of EEPProgram ids."""
        if kwargs.get("return_filters"):
            objects = EEPProgram.objects.filter(id__in=eep_ids)
            self.add_filter("Program", objects)
        self.filter["eep_program_id__in"] = eep_ids

    def filter_by_builder(self, builder_ids, **kwargs):
        """Filter by list of Company ids that are builders."""
        companies = Company.objects.filter(id__in=builder_ids)
        if kwargs["user"].company.company_type != "builder":
            home_qs = Home.objects.filter_by_multiple_companies(companies, show_attached=True)
            stat_qs = EEPProgramHomeStatus.objects.filter(home__in=home_qs)
        else:
            stat_qs = EEPProgramHomeStatus.objects.filter_by_multiple_companies(companies)

        self.filter["id__in"].append(list(stat_qs.values_list("id", flat=True)))

        if kwargs.get("return_filters"):
            self.add_filter("Builder", companies)

    def filter_by_company_type(self, company_type, pretty_name, **kwargs):
        lookup = "{}_id".format(company_type)
        value = kwargs.get(lookup, kwargs.get(company_type))
        if value:
            company_ids = self._get_list_from_type(value)
            companies = Company.objects.filter(id__in=company_ids)

            # At this point we are only looking at our stuff so this is pretty safe.
            home_ids = Home.objects.filter_by_multiple_companies(
                companies, show_attached=True
            ).values_list("id", flat=True)
            stat_ids = EEPProgramHomeStatus.objects.filter(home__in=list(home_ids)).values_list(
                "id", flat=True
            )

            self.filter["id__in"].append(list(stat_ids))

            if kwargs.get("return_filters"):
                self.add_filter(pretty_name, companies)

    def filter_by_location(self, **kwargs):
        us_state = kwargs.get("us_state")
        metro = kwargs.get("metro_id")
        city = kwargs.get("city_id")

        if city not in self.null_list:
            city_ids = self._get_list_from_type(city)
            self.filter["home__city_id__in"] = city_ids
            if kwargs.get("return_filters"):
                obj_name = ", ".join(
                    City.objects.filter(id__in=city_ids).values_list("name", flat=True)
                )
                self.add_filter("City", obj_name)

        if us_state not in self.null_list:
            us_states = self._get_list_from_type(us_state)
            self.filter["home__state__in"] = us_states
            if kwargs.get("return_filters"):
                self.add_filter("US State", ", ".join([x.upper() for x in us_states]))

        if metro not in self.null_list:
            metro_ids = self._get_list_from_type(metro)
            self.filter["home__metro_id__in"] = metro_ids
            if kwargs.get("return_filters"):
                obj_name = ", ".join(
                    Metro.objects.filter(id__in=metro_ids).values_list("name", flat=True)
                )
                self.add_filter("Metro", obj_name)

    def filter_by_eto_region(self, eto_region, **kwargs):
        try:
            eto_region = int(eto_region)
        except:
            return

        self.filter["home__zipcode__in"] = get_zipcodes_for_eto_region_id(eto_region)
        self.add_filter("ETO Region", ETO_REGIONS.get(eto_region))

    def filter_by_rating_type(self, rating_types=None, **kwargs):
        """
        state: 'confirmed'
            return items that have certification dates

        state: 'test'
            return homes that are marked as test homes in their sample set

        state: 'sampled'
            return homes that are not marked as test homes in their sample set
        """
        if kwargs.get("return_filters"):
            obj_name = ", ".join(rating_types)
            self.add_filter("Rating Type", obj_name)

        q_filters = []
        if "confirmed" in rating_types:
            q_filters.append(Q(samplesethomestatus__isnull=True))

        if "test" in rating_types:
            q_filters.append(Q(samplesethomestatus__is_test_home=True))

        if "sampled" in rating_types:
            q_filters.append(Q(samplesethomestatus__is_test_home=False))

        q = reduce(operator.or_, q_filters)
        self.q_filters.append(q)

    def filter_by_rater_user(self, rater_of_record_id, **kwargs):
        if rater_of_record_id == "-1":
            rater_of_record_id = None

        if rater_of_record_id:
            try:
                rater_of_record_id = int(rater_of_record_id)
            except:
                rater_of_record_id = False

        if rater_of_record_id is not False:  # Allow None
            self.filter["rater_of_record"] = rater_of_record_id

        if kwargs.get("return_filters"):
            rater_of_record = User.objects.get(id=rater_of_record_id)
            self.add_filter("Rater of Record", rater_of_record)

    def filter_by_certification(self, **kwargs):
        activity_start = self.get_start_date(kwargs.get("activity_start"))
        activity_stop = self.get_stop_date(kwargs.get("activity_stop"))

        self.filter["certification_date__isnull"] = False

        if activity_start:
            self.filter["certification_date__gte"] = activity_start

        if activity_stop:
            self.filter["certification_date__lte"] = activity_stop

        if kwargs.get("return_filters"):
            self.add_filter("State", self.eep_program_states["complete"])

    def filter_by_state(self, state=None, **kwargs):
        """
        state: '-1' (Not Certified)
            return items that are not in state 'complete'.

        state: '-2' (Not Certified (Not Abandoned))
            return items that are not in state 'complete' and not 'abandoned'.

        state: 'pending_inspection'
            return items that have not had any transitions yet,
             created in the date range.

        state: 'other' (else)
            if no dates provided:
                return items currently in that state.
            if dates provided:
                return items that were in the given state in the date range.
        """
        # NOTE: This does not run when state was 'complete'; see filter_by_certification() instead
        activity_start = self.get_start_date(kwargs.get("activity_start"))
        activity_stop = self.get_stop_date(kwargs.get("activity_stop"))

        state = self._get_one_from_type(state)

        if state == "-1":
            choices = list(dict(EEPProgramHomeStatus.get_state_choices()).keys())
            choices.remove("complete")
            self.filter["state__in"] = choices

        elif state == "-2":
            choices = list(dict(EEPProgramHomeStatus.get_state_choices()).keys())
            choices.remove("complete")
            choices.remove("abandoned")
            self.filter["state__in"] = choices

        elif state == "pending_inspection":
            self.filter["state"] = state
            if activity_start:
                self.filter["created_date__gte"] = activity_start
            if activity_stop:
                self.filter["created_date__lte"] = activity_stop

        else:
            if not activity_start or not activity_stop:
                self.filter["state"] = state
            else:
                StateLog = EEPProgramHomeStatus._state_log_model
                qs = StateLog.objects.filter(to_state=state)
                if activity_start:
                    qs = qs.filter(start_time__gte=activity_start)
                if activity_stop:
                    qs = qs.filter(start_time__lte=activity_stop)

                self.filter["id__in"].append(list(qs.values_list("on_id", flat=True)))

        if kwargs.get("return_filters"):
            self.add_filter("State", self.eep_program_states[state])

    def filter_by_ipp_state(self, ipp_state=None, certification_only=False, **kwargs):
        """
        state: '-2' (Not Received)
            return items that have no incentivepaymentstatus.

        state: '-1' (Not Paid)
            return items not in state 'complete'.

        state: 'other' (else)
            if no dates provided:
                return items currently in that state.
            if dates provided:
                return items that were in the given state in the date range.
        """
        activity_start = self.get_start_date(kwargs.get("activity_start"))
        activity_stop = self.get_stop_date(kwargs.get("activity_stop"))

        ipp_state = self._get_one_from_type(ipp_state)

        if ipp_state == "-2":
            self.filter["incentivepaymentstatus__isnull"] = True

        elif ipp_state == "-1":
            choices = list(dict(EEPPROGRAMHOMESTATUS_IPP_STATE_CHOICES()).keys())
            choices.remove("complete")
            self.filter["incentivepaymentstatus__isnull"] = False
            self.filter["incentivepaymentstatus__state__in"] = choices

        else:
            if certification_only or (activity_stop is None and activity_start is None):
                self.filter["incentivepaymentstatus__state"] = ipp_state
            else:
                StateLog = IncentivePaymentStatus._state_log_model
                qs = StateLog.objects.filter(to_state=ipp_state)
                if activity_start:
                    qs = qs.filter(start_time__gte=activity_start)
                if activity_stop:
                    qs = qs.filter(start_time__lte=activity_stop)
                self.filter["id__in"].append(list(qs.values_list("on__home_status__id", flat=True)))

        if kwargs.get("return_filters"):
            self.add_filter("Incentive Status", self.incentive_payment_states[ipp_state])

    def filter_by_qa_type(self, qatype, **kwargs):
        """
        state: anything
            return items that have a qaRequirement of type against it's EEP Program.
        """
        qatype = self._get_one_from_type(qatype)

        self.filter["qastatus__requirement__type"] = qatype

        if kwargs.get("return_filters"):
            self.add_filter("QA Type", self.qa_requirement_types[qatype])

    def filter_by_qa_status(self, qastatus=None, certification_only=False, **kwargs):
        """
        state: '-4' (Not in Progress)
            return items where QA does not exist, or is complete.

        state: '-3' (QA Addable)
            return items that have no qastatus but are eligible.

        state: '-2' (Does Not Exist)
            return items that have no qastatus.

        state: '-1' (Not Complete)
            return items not in state 'complete'.

        state: 'other' (else)
            if not dates provided:
                return items currently in that state.
            if date provided:
                return items that were in the given state in the date range.
        """
        activity_start = self.get_start_date(kwargs.get("activity_start"))
        activity_stop = self.get_stop_date(kwargs.get("activity_stop"))

        qastatus = self._get_one_from_type(qastatus)

        if qastatus == "-4":
            not_in_progress = Q(qastatus__isnull=True) | Q(qastatus__state="complete")
            self.q_filters.append(not_in_progress)

        elif qastatus == "-3":
            eeps = QARequirement.objects.filter_by_user(kwargs.get("user"))
            self.filter["eep_program__id__in"] = list(eeps.values_list("eep_program", flat=True))
            self.filter["qastatus__isnull"] = True

        elif qastatus == "-2":
            self.filter["qastatus__isnull"] = True

        elif qastatus == "-1":
            choices = list(dict(EEPPROGRAMHOMESTATUS_QASTATUS_CHOICES()).keys())
            choices.remove("complete")
            self.filter["qastatus__isnull"] = False
            self.filter["qastatus__state__in"] = choices

        else:
            if certification_only or (activity_stop is None and activity_start is None):
                self.filter["qastatus__state"] = qastatus
            else:
                StateLog = QAStatus._state_log_model
                qs = StateLog.objects.filter(to_state=qastatus)
                if activity_start:
                    qs = qs.filter(start_time__gte=activity_start)
                if activity_stop:
                    qs = qs.filter(start_time__lte=activity_stop)

                self.filter["id__in"].append(qs.values_list("on__home_status__id", flat=True))

        if kwargs.get("return_filters"):
            self.add_filter("QA Status", self.qa_status_states[qastatus])

    def filter_by_qa_observation(self, qaobservation, **kwargs):
        if qaobservation:
            if not isinstance(qaobservation, list):
                qaobservation = [qaobservation]
            qaobservation = map(int, qaobservation)
            self.filter["qastatus__correction_types__in"] = qaobservation

    def filter_by_qa_designee(self, qa_designee=None, qa_designee_id=None, **kwargs):
        if qa_designee:
            self.filter["qastatus__qa_designee"] = qa_designee
            if kwargs.get("return_filters"):
                self.add_filter("QA Designee", qa_designee)
        if qa_designee_id:
            self.filter["qastatus__qa_designee_id"] = qa_designee_id
            if kwargs.get("return_filters"):
                qa_designee = User.objects.get(id=qa_designee_id)
                self.add_filter("QA Designee", qa_designee)

    def filter_by_heat_source_status(self, heat_source, return_filters, **kwargs):
        """
        state: '-1' (Gas Heat Homes)
            return Homes that have some type of gas heat.

        state: '-2' (Heat Pump Homes)
            return Homes that have some type of a heat pump

        state: '-3' (other)
            return Homes that have some type of a other type of fuel

        state: slug (specific heat type)
            return Homes that have a specific type of fuel
        """
        # Convert to string in case it's -3, -2, -1 for consistency of lookups
        heat_source = str(heat_source)
        try:
            atypes = Type.objects.get(slug="heat-source").get_valid_multiplechoice_values()
        except Type.DoesNotExist:
            atypes = []
        answer_types = (
            Answer.objects.filter(question__slug="neea-heating_source")
            .values_list("answer", flat=True)
            .distinct()
        )

        answer_c = [(slugify(x), x) for x in answer_types]
        anns_c = [(slugify(x), x) for x in atypes]
        heat_sources = dict(set(answer_c + anns_c))

        def get_filter_presets(prefix):
            return {
                "-3": {
                    "filter": {
                        "{}__in".format(prefix): [
                            "Propane Oil or Wood",
                            "Other",
                            "Zonal Electric",
                            "N/A",
                            # neea-heating_source question answers
                            "Hydronic Radiant Electric Boiler",
                            "Hydronic Radiant Gas Boiler",
                            "Hydronic Radiant Heat Pump",
                        ]
                    },
                    "name": "Other Heat Homes",
                },
                "-2": {
                    "filter": {"{}__istartswith".format(prefix): "heat pump"},
                    "name": "Heat Pump Homes",
                },
                "-1": {
                    "filter": {"{}__istartswith".format(prefix): "gas"},
                    "name": "Gas Heat Homes",
                },
                "default": {
                    "filter": {
                        "{}__iexact".format(prefix): heat_sources.get(heat_source, heat_source)
                    },
                    "name": heat_sources.get(heat_source, heat_source),
                },
            }

        def annotation_filter(value):
            filter_presets = get_filter_presets("content")
            selection = filter_presets.get(value, filter_presets["default"])

            if return_filters:
                self.add_filter("Heat Source", selection["name"])
            log.debug("Filtering on Annotation %s", selection["name"])

            return (
                Annotation.objects.filter(type__slug="heat-source", **selection["filter"])
                .values_list("object_id", flat=True)
                .distinct()
            )

        def answer_filter(value):
            filter_presets = get_filter_presets("answer")
            selection = filter_presets.get(value, filter_presets["default"])

            if return_filters:
                self.add_filter("Heat Source", selection["name"])
            log.info("Filtering on Answer %r", selection)

            return (
                Answer.objects.filter(question__slug="neea-heating_source", **selection["filter"])
                .values_list("home__homestatuses__id", flat=True)
                .distinct()
            )

        annotation_id_list = list(annotation_filter(heat_source))
        answer_id_list = list(answer_filter(heat_source))
        self.filter["id__in"].append(set(annotation_id_list + answer_id_list))

    def filter_by_remrate_flavor(self, flavor, **kwargs):
        """
        state:  '-2' (Northwest OR Washington
            return items that have flavor or Northwest OR Washington

        state:  '-1' (None)
            return items that have Falsey value flavors.

        state: 'other' (else)
            return items that have that flavor
        """

        flavor = self._get_one_from_type(flavor)

        if flavor == "-2":
            query = Q(floorplan__remrate_target__flavor__icontains="northwest") | Q(
                floorplan__remrate_target__flavor__icontains="washington"
            )
            self.q_filters.append(query)

        elif flavor == "-1":
            query = Q(floorplan__remrate_target__flavor__isnull=True) | Q(
                floorplan__remrate_target__flavor=["", "None"]
            )
            self.q_filters.append(query)

        else:
            self.filter["floorplan__remrate_target__flavor__icontains"] = flavor

    def filter_by_meets_or_beats(self, value, **kwargs):
        value = self._get_one_from_type(value)

        self.filter["annotations__type__slug"] = "beat-annual-fuel-usage"
        self.filter["annotations__content__icontains"] = value

    def filter_by_paid_date(self, start_date, stop_date, **kwargs):
        start_date = self.get_start_date(start_date)
        stop_date = self.get_stop_date(stop_date)

        if start_date:
            self.filter["ippitem__incentive_distribution__paid_date__gte"] = start_date
            self.add_filter("Paid Date Start", start_date.strftime("%m/%d/%y"))

        if stop_date:
            self.filter["ippitem__incentive_distribution__paid_date__lte"] = stop_date
            self.add_filter("Paid Date Stop", stop_date.strftime("%m/%d/%y"))

    def filter_by_program_activity_date(self, start_date, stop_date, **kwargs):
        start_date = self.get_start_date(start_date)
        stop_date = self.get_stop_date(stop_date)

        self.filter["eep_program__is_qa_program"] = False

        if start_date:
            self.filter["created_date__gte"] = start_date
            self.add_filter("Program Activity Start", start_date.strftime("%m/%d/%y"))

        if stop_date:
            self.filter["created_date__lte"] = stop_date
            self.add_filter("Program Activity Stop", stop_date.strftime("%m/%d/%y"))

    def filter_by_program_certification_date(self, start_date, stop_date, **kwargs):
        start_date = self.get_start_date(start_date)
        stop_date = self.get_stop_date(stop_date)

        if start_date:
            self.filter["certification_date__gte"] = start_date
            self.add_filter("Certification Date Start", start_date.strftime("%m/%d/%y"))

        if stop_date:
            self.filter["certification_date__lte"] = stop_date
            self.add_filter("Certification Date Stop", stop_date.strftime("%m/%d/%y"))

    def filter_by_home_created_date(self, start_date, stop_date, **kwargs):
        start_date = self.get_start_date(start_date)
        stop_date = self.get_stop_date(stop_date)

        if start_date:
            self.filter["home__created_date__date__gte"] = start_date
            self.add_filter("Home Created Date Start", start_date.strftime("%m/%d/%y"))

        if stop_date:
            self.filter["home__created_date__date__lte"] = stop_date
            self.add_filter("Home Created Date Stop", stop_date.strftime("%m/%d/%y"))

    def extra_filters(self, **kwargs):
        """Hook for applying more filters before the final .distinct() happens."""
        pass

    def _get_datetime_from_string(self, date_string):
        if isinstance(date_string, (datetime.datetime, datetime.date)):
            return date_string
        elif isinstance(date_string, type(None)):
            return date_string
        elif isinstance(date_string, list):  # supplied twice by query params due to hard linking
            date_string = date_string[-1]  # first was just default, last is latest settting
        try:
            return dateutil.parser.parse(date_string).replace(tzinfo=datetime.timezone.utc)
        except:
            log.error("Unable to parse %s", date_string)

    def _get_list_from_type(self, value):
        if isinstance(value, str):
            if value[0] == "[":
                value = json.loads(value)
            else:
                value = value.split(",")
        elif not isinstance(value, list):
            value = [value]
        return value

    def _get_one_from_type(self, value):
        if isinstance(value, list) and len(value) > 0:
            return value[-1]
        return value

    def get_start_date(self, date_string):
        """get a datetime object from a date string."""
        return self._get_datetime_from_string(date_string)

    def get_stop_date(self, date_string):
        """
        Activity Stop dates are expected to be at the end of the day.
        Transform dates to the end of the day.

        12/31/2014 -> 12/31/2014 23:59:59
        """
        date = self._get_datetime_from_string(date_string)
        try:
            date += datetime.timedelta(hours=23, minutes=59, seconds=59)
        except TypeError:
            return date_string

        try:
            date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, 0).replace(
                tzinfo=date.tzinfo
            )
        except AttributeError:
            pass

        return date

    def get_external_qs_filters(self, queryset, user, return_filters=False, **kwargs):
        """
        Get the list of items for this view. In this case it's narrowed based on your company
        """
        self.q_filters = []
        self.filters = []

        self.filter = {"id__in": []}
        self.exclude = {"id__in": []}

        self.null_list = ["", "undefined", None]

        self.eep_program_states = dict(EEPPROGRAMHOMESTATUS_STATE_CHOICES())
        self.incentive_payment_states = dict(EEPPROGRAMHOMESTATUS_IPP_STATE_CHOICES())
        self.qa_status_states = dict(EEPPROGRAMHOMESTATUS_QASTATUS_CHOICES())
        self.qa_requirement_types = dict(EEPPROGRAMHOMESTATUS_QAREQUIREMENT_TYPES())
        self.qa_observation_types = dict(
            ObservationType.objects.filter_by_user(user).values_list("id", "name")
        )

        kwargs = self.prevision_kwargs(**kwargs)
        kwargs["return_filters"] = return_filters
        kwargs["user"] = user

        datatable_mode = kwargs.get("datatable")

        subdivision_ids = kwargs.get("subdivision_id", kwargs.get("subdivision"))
        eep_program_ids = kwargs.get("eep_program_id", kwargs.get("eep_program"))
        builder_ids = kwargs.get("builder_id", kwargs.get("builder"))
        rater_user_id = self._get_one_from_type(
            kwargs.get("rater_of_record_id", kwargs.get("rater_of_record"))
        )
        eto_region = self._get_one_from_type(kwargs.get("eto_region"))
        state = self._get_one_from_type(kwargs.get("state"))
        ipp_state = self._get_one_from_type(kwargs.get("ipp_state"))
        qa_type = self._get_one_from_type(kwargs.get("qatype"))
        qa_status = self._get_one_from_type(kwargs.get("qastatus"))
        qa_observation = kwargs.get("qaobservation")
        qa_designee = kwargs.get("qa_designee")
        qa_designee_id = kwargs.get("qa_designee_id")
        rating_type = kwargs.get("rating_type")
        heat_source = kwargs.get("heat_source")
        certification = kwargs.get("certification_only")
        remrate_flavor = kwargs.get("remrate_flavor")
        meet_or_beats = kwargs.get("meets_or_beats")
        paid_date_start = self._get_one_from_type(kwargs.get("paid_date_start"))
        paid_date_stop = self._get_one_from_type(kwargs.get("paid_date_stop"))
        program_activity_start = self._get_one_from_type(kwargs.get("program_activity_start"))
        program_activity_stop = self._get_one_from_type(kwargs.get("program_activity_stop"))
        certification_date_start = self._get_one_from_type(kwargs.get("certification_date_start"))
        certification_date_end = self._get_one_from_type(kwargs.get("certification_date_end"))
        home_created_date_start = self._get_one_from_type(kwargs.get("home_created_date_start"))
        home_created_date_end = self._get_one_from_type(kwargs.get("home_created_date_end"))
        task_type_ids = kwargs.get("task_type_id", kwargs.get("task_type"))
        task_assignee = self._get_one_from_type(kwargs.get("task_assignee"))

        exclude_ids = self._get_one_from_type(kwargs.get("exclude_ids"))
        if exclude_ids:
            exclude_ids = self._get_list_from_type(exclude_ids)
        if exclude_ids:
            self.exclude["id__in"].append(exclude_ids)

        self.filter_by_mode(datatable_mode)

        if subdivision_ids:
            self.filter_by_subdivision(self._get_list_from_type(subdivision_ids), **kwargs)

        if eep_program_ids:
            self.filter_by_eep_program(self._get_list_from_type(eep_program_ids), **kwargs)

        if builder_ids:
            self.filter_by_builder(self._get_list_from_type(builder_ids), **kwargs)

        for co_type, pretty_name in COMPANY_TYPES:
            if co_type == "builder":
                continue
            self.filter_by_company_type(co_type, pretty_name, **kwargs)

        if rater_user_id:
            self.filter_by_rater_user(**kwargs)

        if heat_source:
            self.filter_by_heat_source_status(**kwargs)

        # Filtering by home_status.state = 'complete' should be the
        # same as filtering by user defined certification date.
        if certification or state == "complete":
            self.filter_by_certification(**kwargs)
        else:
            if state:
                self.filter_by_state(**kwargs)

        if ipp_state:
            self.filter_by_ipp_state(**kwargs)
        if qa_type:
            self.filter_by_qa_type(**kwargs)
        if qa_status:
            self.filter_by_qa_status(**kwargs)
        if qa_observation:
            self.filter_by_qa_observation(**kwargs)
        if qa_designee or qa_designee_id:
            self.filter_by_qa_designee(**kwargs)

        self.filter_by_location(**kwargs)

        if eto_region:
            self.filter_by_eto_region(**kwargs)

        if rating_type:
            self.filter_by_rating_type(self._get_list_from_type(rating_type), **kwargs)

        if remrate_flavor:
            self.filter_by_remrate_flavor(remrate_flavor, **kwargs)

        if meet_or_beats:
            self.filter_by_meets_or_beats(meet_or_beats, **kwargs)

        if paid_date_start or paid_date_stop:
            self.filter_by_paid_date(paid_date_start, paid_date_stop, **kwargs)

        if program_activity_start or program_activity_stop:
            self.filter_by_program_activity_date(
                program_activity_start, program_activity_stop, **kwargs
            )

        if certification_date_start or certification_date_end:
            self.filter_by_program_certification_date(
                certification_date_start, certification_date_end, **kwargs
            )

        if home_created_date_start or home_created_date_end:
            self.filter_by_home_created_date(
                home_created_date_start, home_created_date_end, **kwargs
            )

        if task_type_ids:
            self.filter_by_task_type(self._get_list_from_type(task_type_ids), **kwargs)

        if task_assignee:
            self.filter_by_task_assignee(**kwargs)

        self.extra_filters(**kwargs)

        # These keys have to be initialized to lists because of the way we add filters.
        # So we remove them if they are empty at the end of the day.
        if not self.filter["id__in"]:
            del self.filter["id__in"]
        else:
            self.filter["id__in"] = set.intersection(*[set(x) for x in self.filter["id__in"]])
        if not self.exclude["id__in"]:
            del self.exclude["id__in"]
        else:
            self.exclude["id__in"] = set.intersection(*[set(x) for x in self.exclude["id__in"]])

        queryset = queryset.filter(*self.q_filters, **self.filter).exclude(**self.exclude)

        if not return_filters:
            return queryset.distinct()

        if kwargs.get("activity_start"):
            self.add_filter("Activity Start", kwargs.get("activity_start"))
        if kwargs.get("activity_stop"):
            self.add_filter("Activity Stop", kwargs.get("activity_stop"))
        if certification:
            self.add_filter("Filter on Certification Date", "Yes")
        if kwargs.get("retain_empty"):
            self.add_filter("Retain all columns", "Yes")
        if kwargs.get("search_bar"):
            self.add_filter("Search Term", '"{}"'.format(kwargs.get("search_bar")))

        return queryset.distinct(), self.filters


class HomeStatusReportFormFieldSetupMixin(object):
    form_class = None

    def get_context_data(self, **kwargs):
        context = super(HomeStatusReportFormFieldSetupMixin, self).get_context_data(**kwargs)
        user = self.request.user

        has_paid_dates = (
            EEPProgramHomeStatus.objects.filter_by_user(user)
            .exclude(ippitem__incentive_distribution__paid_date=None)
            .exists()
        )
        form_kwargs = {
            "user": user,
            "add_payment_date_filters": has_paid_dates,
            "available_company_ids": list(
                self.get_base_queryset()
                .values_list("home__relationships__company__id", flat=True)
                .distinct()
            ),
        }
        context["filter_form"] = self.form_class(self.request.GET.copy(), **form_kwargs)

        setup_args = [context["filter_form"], user, context]

        self.setup_company_type_fields(*setup_args, **kwargs)
        self.setup_subdivision_field(*setup_args, **kwargs)
        self.setup_eep_program_field(*setup_args, **kwargs)
        self.setup_rater_user_field(*setup_args, **kwargs)
        self.setup_city_field(*setup_args, **kwargs)
        self.setup_us_states_field(*setup_args, **kwargs)
        self.setup_metro_field(*setup_args, **kwargs)
        self.setup_ipp_state_field(*setup_args, **kwargs)
        self.setup_qa_type_field(*setup_args, **kwargs)
        self.setup_qa_state_field(*setup_args, **kwargs)
        self.setup_qa_observation_field(*setup_args, **kwargs)
        self.setup_activity_fields(*setup_args, **kwargs)
        self.setup_state_field(*setup_args, **kwargs)
        self.setup_rating_type_field(*setup_args, **kwargs)
        self.setup_heat_source_field(*setup_args, **kwargs)
        self.setup_task_type_field(*setup_args, **kwargs)
        self.setup_task_assignee_field(*setup_args, **kwargs)

        return context

    def setup_company_type_fields(self, form, user, context, **kwargs):
        company_info = (
            self.get_base_queryset()
            .values_list(
                "home__relationships__company__id",
                "home__relationships__company__name",
                "home__relationships__company__company_type",
            )
            .order_by("home__relationships__company__name")
            .distinct()
        )

        # Previous order_by() ensures stable ordering for this loop, too
        breakdown = defaultdict(list)
        for pk, name, company_type in company_info:
            breakdown[company_type].append((pk, name))

        for co_type in dict(COMPANY_TYPES).keys():
            field = form.fields[co_type]
            field.choices = breakdown.get(co_type, [])

            show_field = all([len(field.choices) > 1, co_type != user.company.company_type])
            context["show_{}".format(co_type)] = show_field

            if not show_field:
                field.widget = field.hidden_widget()

    def setup_subdivision_field(self, form, user, context, **kwargs):
        field = form.fields["subdivision"]
        field.queryset = Subdivision.objects.filter_by_user(user).select_related("community")

    def setup_eep_program_field(self, form, user, context, **kwargs):
        field = form.fields["eep_program"]
        field.queryset = EEPProgram.objects.filter_by_user(user, ignore_dates=True).filter(
            id__in=self.qs.values_list("eep_program", flat=True)
        )

    def setup_rater_user_field(self, form, user, context, **kwargs):
        field = form.fields["rater_of_record"]

        user_ids = list(
            EEPProgramHomeStatus.objects.filter_by_user(user).values_list(
                "rater_of_record", flat=True
            )
        )
        users = (
            User.objects.filter(id__in=user_ids)
            .values("id", "first_name", "last_name", "company__name")
            .order_by("company__name")
        )

        user_repr_string = "{first_name} {last_name}"
        if user.is_superuser:
            user_repr_string = "[{id}] {first_name} {last_name}"

        choices = OrderedDict()
        for data in users:
            group_key = data["company__name"]
            choices.setdefault(group_key, [])
            choices[group_key].append((data["id"], user_repr_string.format(**data)))
        field.choices = [("", "---------"), ("-1", "Unassigned")] + list(choices.items())

    def setup_city_field(self, form, user, context, **kwargs):
        field = form.fields["city"]

        cities = list(self.qs.values_list("home__city_id", flat=True).distinct())
        field.queryset = City.objects.filter(id__in=cities).order_by("name")
        show_field = context["show_us_cities"] = len(cities) > 1

        if not show_field:
            field.widget = field.hidden_widget()

    def setup_us_states_field(self, form, user, context, **kwargs):
        field = form.fields["us_state"]

        states = self.qs.order_by("home__state").values_list("home__state", flat=True).distinct()
        if states and states[0] is None:
            states = states[1:]
        field.choices = [(name, name) for name in states]
        field.label = "US State"
        show_field = len(states) > 1

        if not show_field:
            field.widget = field.hidden_widget()

    def setup_metro_field(self, form, user, context, **kwargs):
        field = form.fields["metro"]

        metros = self.qs.values_list("home__metro_id", flat=True).distinct()
        field.queryset = Metro.objects.filter(id__in=metros)
        show_field = context["show_metro"] = len(metros) > 1

        if not show_field:
            field.widget = field.hidden_widget()

    def setup_ipp_state_field(self, form, user, context, **kwargs):
        field = form.fields["ipp_state"]

        show_field = context["show_ipp"] = self.qs.filter(
            incentivepaymentstatus__state__isnull=False
        ).exists()

        if not show_field:
            field.widget = field.hidden_widget()

    def setup_qa_type_field(self, form, user, context, **kwargs):
        field = form.fields["qatype"]

        show_field = all(
            [
                user.has_perm("qa.view_qastatus"),
                getattr(self, "show_qa", False) or context["show_qa"],
            ]
        )

        if show_field:
            choices = list(
                set(
                    QAStatus.objects.filter_by_user(user).values_list(
                        "requirement__type", flat=True
                    )
                )
            )
            valid_choices = [x for x in QARequirement.QA_REQUIREMENT_TYPES if x[0] in choices]
            field.choices = [("", "---------")] + valid_choices
            show_field = len(choices) > 1

        if not show_field:
            field.widget = field.hidden_widget()

    def setup_qa_state_field(self, form, user, context, **kwargs):
        field = form.fields["qastatus"]

        show_field = all(
            [
                user.has_perm("qa.view_qastatus"),
                getattr(self, "show_qa", False) or context["show_qa"],
            ]
        )
        if show_field:
            show_field = QAStatus.objects.filter_by_user(user).count() > 0
            if user.company.company_type not in ["provider", "qa"] and not user.is_superuser:
                choices = [x for x in field.choices if x[0] != "-3"]
                field.choices = choices
        if not show_field:
            field.widget = field.hidden_widget()

    def setup_qa_observation_field(self, form, user, context, **kwargs):
        field = form.fields["qaobservation"]
        field.queryset = ObservationType.objects.filter_by_user(user)

        show_field = all(
            [
                user.has_perm("qa.view_qastatus"),
                getattr(self, "show_qa", False) or context["show_qa"],
            ]
        )
        if show_field:
            show_field = field.queryset.exists()
        if not show_field:
            field.widget = field.hidden_widget()

    def setup_activity_fields(self, form, user, context, **kwargs):
        form.fields["activity_start"].widget.attrs["size"] = 9
        form.fields["activity_stop"].widget.attrs["size"] = 9

    def setup_state_field(self, form, user, context, **kwargs):
        field = form.fields["state"]

        field.label = "Project Status"

        # If they arrive to this page with a filter in the GET params, we want to respect that.
        if not form.data.get("state"):
            if user.is_superuser:
                form.data["state"] = "-2"
            elif user.company.company_type in ["rater", "provider", "hvac"]:
                form.data["state"] = "-1"

    def setup_rating_type_field(self, form, user, context, **kwargs):
        context["show_rating_type"] = True

    def setup_heat_source_field(self, form, user, context, **kwargs):
        field = form.fields["heat_source"]

        if kwargs.get("show_heat_sources"):
            try:
                atypes = Type.objects.get(slug="heat-source").get_valid_multiplechoice_values()
            except Type.DoesNotExist:
                atypes = []

            answer_types = (
                Answer.objects.filter(question__slug="neea-heating_source")
                .values_list("answer", flat=True)
                .distinct()
            )

            answer_c = [(slugify(x), x) for x in answer_types]
            anns_c = [(slugify(x), x) for x in atypes]
            choices = list(set(answer_c + anns_c))

            if len(choices):
                from axis.home.forms import HEAT_SOURCE_CHOICES

                field.choices = HEAT_SOURCE_CHOICES + sorted(choices)
            else:
                context["show_heat_sources"] = False
                field.widget = field.hidden_widget()
        else:
            context["show_heat_sources"] = False
            field.widget = field.hidden_widget()

    def setup_task_type_field(self, form, user, context, **kwargs):
        field = form.fields["task_type"]
        field.queryset = TaskType.objects.filter_by_user(user)

    def setup_task_assignee_field(self, form, user, context, **kwargs):
        field = form.fields["task_assignee"]
        if user and user.company_id:
            users = User.objects.filter(company_id=user.company_id)
        else:
            users = User.objects.none()
        field.queryset = users


class HomeStatusView(
    AuthenticationMixin,
    HomeStatusReportMixin,
    HomeStatusReportFormFieldSetupMixin,
    AxisDatatableView,
):
    """This will simply provide a list view for the Program Home Status"""

    form_class = HomeStatusFilterForm
    permission_required = "home.view_home"
    template_name = "home/home_stats.html"
    show_add_button = False
    show_qa = True

    datatable_class = HomeStatusListDatatable

    select_related = [
        "eep_program__owner",
        "floorplan__owner",
        "home__city",
        "home__subdivision",
        "home__subdivision__community",
        "incentivepaymentstatus",
    ]

    href = '<a href"{}">{}</a>'

    def get_flattened_query_params(self):
        """Flattens the GET querydict into a simple dict, and ensure desired lists are present."""
        query_params = self.request.GET.dict()  # Ignore shadowed duplicate keys!

        # Any multiple-choice fields will serialize in datatables with a '[]' suffix, so ensure we
        # take the full list of such values and not just the last one (as QueryDict does when we
        # flatten it with ``.dict()``)
        for k in query_params:
            if k.endswith("[]"):
                query_params[k] = self.request.GET.getlist(k)

        return query_params

    def get_queryset(self):
        qs = self.get_base_queryset()
        if not hasattr(self, "qs"):
            self.qs = qs

        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            query_params = self.get_flattened_query_params()
            qs = self.get_external_qs_filters(qs, user=self.request.user, **query_params)
            qs = qs.select_related(*self.select_related)
            return qs.distinct()
        else:
            return EEPProgramHomeStatus.objects.none()

    def get_datatable_kwargs(self):
        kwargs = super(HomeStatusView, self).get_datatable_kwargs()

        kwargs["company"] = self.request.company
        kwargs["user"] = self.request.user

        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            kwargs["hints"] = self.precompute_hints(user=kwargs["user"], company=kwargs["company"])

        return kwargs

    def precompute_hints(self, user, company):
        return {}

    def get_context_data(self, **kwargs):
        context = super(HomeStatusView, self).get_context_data(**kwargs)

        if (
            context["filter_form"]
            .fields["eep_program"]
            .queryset.filter(owner__slug__iexact="neea")
            .exists()
        ):
            context["show_generate_report"] = True

        # Push initial GET parameters to the datatable url
        context["datatable"].url = context["datatable"].url + "?" + self.request.GET.urlencode()

        from axis.home.forms import HomeStatusExportFieldsForm

        context["export_fields_form"] = HomeStatusExportFieldsForm()
        return context


class ProviderDashboardView(
    AuthenticationMixin,
    HomeStatusReportMixin,
    HomeStatusReportFormFieldSetupMixin,
    LegacyAxisDatatableView,
):
    model = EEPProgramHomeStatus
    form_class = ProviderDashboardFilterForm
    template_name = "home/provider_dashboard.html"
    show_add_button = False
    show_qa = True

    datatable_options = {
        "columns": [
            ("Select", None, "get_column_Select_data"),
            (
                "Address",
                [
                    "home__street_line1",
                    "home__street_line2",
                    "home__state",
                    "home__zipcode",
                    "home__city__name",
                    "home__lot_number",
                ],
                "get_column_Address_data",
            ),
            ("Rating Company", "company__name", "get_column_Rating_Company_data"),
            ("Program", "eep_program__name", "get_column_Program_data"),
            ("Rating Type", None, "get_column_Rating_Type_data"),
            ("Project Status", "state_description", "get_column_Home_Status_data"),
            ("Checklist Status", "pct_complete", "get_column_Checklist_Status_data"),
            (
                "REM/Rate Data",
                [
                    "floorplan__remrate_target__rating_number",
                    "floorplan__remrate_target__simulation_date",
                    "floorplan__remrate_target__version",
                ],
                "get_column_RemRate_Data_data",
            ),
            ("REM/Rate File", "floorplan__remrate_data_file", "get_column_RemRate_File_data"),
            # ('Meets or Beats', None, 'get_column_Meets_or_Beats_data'),
            ("Home Notes", None, "get_column_Home_Notes_data"),
            ("Additional Documentation", None, "get_column_Additional_Documentation_data"),
        ]
    }

    select_related = [
        "home",
        "eep_program",
        "company",
        "floorplan",
        "floorplan__remrate_target",
        "floorplan__remrate_target__building",
    ]

    prefetch_related = [
        "samplesethomestatus_set",
        "samplesethomestatus_set__sampleset",
        "home__customer_documents",
    ]

    href = "<a href='{url}' target='_blank'>{text}</a>"
    href_no_target = "<a href='{url}' target='_blank'>{text}</a>"

    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        return (
            self.request.user.company.company_type == "provider"
            or self.request.user.company.eep_programs_can_certify.exists()
        )

    def get_filtered_by_user_queryset(self):
        # Needed for setting up the filter options.
        if not hasattr(self, "qs"):
            user = self.request.user
            self.qs = EEPProgramHomeStatus.objects.filter_by_user(user=user)
            if not user.is_superuser and user.company.company_type != "provider":
                # Am I acting like a provider
                self.qs = self.qs.filter(eep_program__certifiable_by=user.company)
        return self.qs

    def _get_queryset(self, **kwargs):
        qs = self.get_filtered_by_user_queryset()
        qs, filters = self.get_external_qs_filters(
            qs, self.request.user, return_filters=True, **kwargs
        )
        qs = qs.select_related(*self.select_related).prefetch_related(*self.prefetch_related)
        log.debug("Count: {} KW: {}".format(qs.distinct().count(), kwargs))
        return qs.distinct()

    def get_queryset(self):
        self.get_filtered_by_user_queryset()

        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            qs = self._get_queryset(**self.request.GET)

            if not hasattr(self, "_samplesets"):
                from axis.sampleset.models import SampleSetHomeStatus

                ss = SampleSetHomeStatus.objects.filter(is_active=True).select_related(
                    "sampleset", "home_status"
                )
                self._samplesets = {obj.home_status.id: obj.sampleset for obj in ss}

            if not hasattr(self, "_notes"):
                from django.contrib.contenttypes.models import ContentType

                ct = ContentType.objects.get_for_model(self.model)
                notes = Annotation.objects.filter(
                    type__slug="note", content_type=ct
                ).select_related("user")
                self._notes = defaultdict(list)

                for note in notes:
                    self._notes[note.object_id].append(note)

                self._notes = dict(self._notes)
            return qs.distinct()
        else:
            return EEPProgramHomeStatus.objects.none()

    def get_extra_record_data(self, obj):
        if hasattr(obj, "fasttracksubmission"):
            can_be_submitted = obj.fasttracksubmission.can_be_sent_to_fastrack()
        else:
            can_be_submitted = False
        return {
            "projecttracker_submit_available": can_be_submitted,
        }

    def get_context_data(self, **kwargs):
        context = super(ProviderDashboardView, self).get_context_data(**kwargs)

        form = context["filter_form"]
        # Set the initial filter options
        form.data["state"] = "certification_pending"

        context["quick_links"] = self.process_quick_links(self.get_quick_links())

        if self.request.user.is_superuser:
            context["qa_active"] = True
        else:
            qa_requirements = QARequirement.objects.filter(
                qa_company=self.request.user.company, type="program_review"
            )
            context["qa_active"] = qa_requirements.count() > 0

        show_fasttrack_mode = False
        if self.request.company.slug in ["peci"] or self.request.user.is_superuser:
            show_fasttrack_mode = True
        context["show_fasttrack_mode"] = show_fasttrack_mode

        return context

    def make_quick_link(self, name, **filter_kwargs):
        exclude_from = filter_kwargs.pop("exclude_from", None)

        quick_link = {
            "slug": slugify(name),
            "name": name,
            "filter_kwargs": filter_kwargs,
            # Overridden later.
            "count": "",
        }

        if exclude_from:
            quick_link["exclude_from"] = exclude_from

        return quick_link

    def process_quick_links(self, quick_links):
        quick_links = {link["name"]: link for link in quick_links}

        for link in quick_links.values():
            exclude_from = link.get("exclude_from", None)

            if exclude_from:
                exclude_from_target = quick_links.get(exclude_from)

                if exclude_from_target:
                    exclude_ids = list(
                        self._get_queryset(**link["filter_kwargs"]).values_list("id", flat=True)
                    )
                    if not quick_links[exclude_from]["filter_kwargs"].get("exclude_ids"):
                        quick_links[exclude_from]["filter_kwargs"]["exclude_ids"] = []

                    quick_links[exclude_from]["filter_kwargs"]["exclude_ids"].extend(exclude_ids)

        for link in iter(quick_links.values()):
            if link["filter_kwargs"].get("exclude_ids"):
                link["filter_kwargs"]["exclude_ids"] = list(
                    map(int, link["filter_kwargs"]["exclude_ids"])
                )

            # Ugly but needed as when this gets received on front side it will be a list.
            filter_kwargs = link["filter_kwargs"].copy()
            if filter_kwargs.get("exclude_ids"):
                filter_kwargs["exclude_ids"] = "%r" % link["filter_kwargs"]["exclude_ids"]
            link["count"] = self._get_queryset(**filter_kwargs).count()

        return list(quick_links.values())

    def get_quick_links(self):
        # Ensures this method always has self.qs available
        self.get_filtered_by_user_queryset()

        if hasattr(self, "_quick_links"):
            return self._quick_links

        links = []

        in_use = self.qs.exclude(state__in=["complete", "abandoned"])
        in_use = list(set(in_use.values_list("eep_program_id", flat=True)))
        programs = EEPProgram.objects.filter_by_user(self.request.user).filter(id__in=in_use)

        common_filters = {
            "state": "certification_pending",
            "qastatus": "-4",
            "exclude_from": "Ready",
        }
        performance_filters = {
            "remrate_flavor": "-2",
            "meets_or_beats": "yes",
        }

        link = self.make_quick_link("Ready", state="certification_pending", qastatus="-4")
        links.append(link)

        for item in (
            programs.exclude(slug__endswith="-qa").order_by("name").values("id", "name", "slug")
        ):
            links.append(
                self.make_quick_link(
                    name="Ready: ({})".format(item["name"]),
                    **dict(
                        common_filters,
                        eep_program_id=[int(item["id"])],
                        **(performance_filters if "performance" in item["slug"] else {}),
                    ),
                )
            )

        if programs.filter(slug__endswith="-qa").exists():
            link = self.make_quick_link(
                "QA Correction Received",
                qastatus="correction_received",
                exclude_from="Ready",
            )
            links.append(link)
            link = self.make_quick_link(
                "QA Correction Required",
                qastatus="correction_required",
                exclude_from="Ready",
            )
            links.append(link)

        self._quick_links = links
        return self._quick_links

    def get_column_Select_data(self, obj, *args, **kwargs):
        return "<input type='checkbox' />"

    def get_column_Address_data(self, obj, *args, **kwargs):
        text = obj.home.get_home_address_display(
            include_lot_number=True, include_confirmed=True, company=self.request.company
        )
        return self.href.format(url=obj.home.get_absolute_url(), text=text)

    def get_column_Rating_Company_data(self, obj, *args, **kwargs):
        return self.href.format(url=obj.company.get_absolute_url(), text=obj.company)

    def get_column_Program_data(self, obj, *args, **kwargs):
        return self.href.format(url=obj.eep_program.get_absolute_url(), text=obj.eep_program)

    def get_column_Rating_Type_data(self, obj, *args, **kwargs):
        sampleset = self._samplesets.get(obj.id, False)
        text = obj.get_rating_type()

        if sampleset:
            return self.href.format(url=sampleset.get_absolute_url(), text=text)

        return text

    def get_column_Home_Status_data(self, obj, *args, **kwargs):
        return obj.get_state_display()

    def get_column_Checklist_Status_data(self, obj, *args, **kwargs):
        url = obj.home.get_absolute_url() + "#/tabs/checklist"
        return self.href.format(url=url, text=int(obj.pct_complete))

    def get_column_RemRate_Data_data(self, obj, *args, **kwargs):
        try:
            link = self.href.format(
                url=obj.floorplan.remrate_target.get_absolute_url(),
                text=obj.floorplan.remrate_target,
            )
            # label = "<i class='fa fa-download'></i> RemXML.xml"
            # link += "<br />" + self.href_no_target.format(url=obj.floorplan.remrate_data_sim_xml_url(), text=label)
            return link
        except (ValueError, AttributeError):
            return "-"

    def get_column_RemRate_File_data(self, obj, *args, **kwargs):
        try:
            text = "<i class='fa fa-cloud-download'></i> {}".format(
                obj.floorplan.remrate_data_filename()
            )
            link = self.href_no_target.format(url=obj.floorplan.remrate_data_file.url, text=text)
            # label = "<i class='fa fa-download'></i> {}".format(os.path.splitext(obj.floorplan.remrate_data_filename())[0] + ".xml")
            # link += "<br />" + self.href_no_target.format(url=obj.floorplan.remrate_data_blg_xml_url(), text=label)
            return link
        except (ValueError, AttributeError):
            return "-"

    def get_column_Home_Notes_data(self, obj, *args, **kwargs):
        try:
            annotations = self._notes[obj.id]
        except KeyError:
            return "-"
        else:
            parts = []
            button = """
            <button class='btn btn-default btn-xs' type='button' data-toggle='popover'
            data-trigger='click' data-title='Annotations' data-html='true' data-placement='left'
            data-content='{content}'>Read All</button>
            """
            blockquote = """
                <blockquote>
                    <small>{date} - {first}. {last}</small>
                    <p>{content}<p>
                </blockquote>
            """
            annotation_string = "[{first}. {last}] [{date}] {content}"

            for annotation in annotations:
                parts.append(
                    {
                        "first": annotation.user.first_name[0],
                        "last": annotation.user.last_name,
                        "content": annotation.content,
                        "date": annotation.last_update.strftime("%m/%d/%y"),
                        "date_object": annotation.last_update,
                    }
                )

            parts = sorted(parts, key=itemgetter("date_object"), reverse=True)

            if len(parts) == 1:
                return annotation_string.format(**parts[0])

            blockquotes = []
            for part in parts:
                blockquotes.append(format_html(blockquote, **part))

            first_annotation = truncatewords_html(annotation_string.format(**parts[0]), 12)
            show_all = button.format(content=" ".join(blockquotes))
            return "{} {}".format(first_annotation, show_all)

    def get_column_Additional_Documentation_data(self, obj, *args, **kwargs):
        if obj.home.customer_documents.count() > 0:
            url = "{}#/tabs/documents".format(obj.home.get_absolute_url())
            return self.href.format(url=url, text="Yes")
        else:
            return "-"


class AsynchronousProcessedDocumentCreateHomeStatusXLS(AuthenticationMixin, AxisCreateView):
    permission_required = "home.view_home"
    model = AsynchronousProcessedDocument
    form_class = HomeStatusReportForm
    template_name = "filehandling/asynchronousprocesseddocument_form.html"

    show_cancel_button = False

    def get_context_data(self, **kwargs):
        """Add in any context data"""
        context = super(AsynchronousProcessedDocumentCreateHomeStatusXLS, self).get_context_data(
            **kwargs
        )
        context["title"] = "Project Report"
        return context

    def get_form(self, form_class=None):
        # FIXME: This is an awful copy-paste of an outdated version of the same code above... :(
        form = super(AsynchronousProcessedDocumentCreateHomeStatusXLS, self).get_form(form_class)

        user = self.request.user

        company_info = (
            EEPProgramHomeStatus.objects.filter_by_user(user)
            .values_list(
                "home__relationships__company__id",
                "home__relationships__company__name",
                "home__relationships__company__company_type",
            )
            .order_by("home__relationships__company__name")
            .distinct()
        )

        # Previous order_by() ensures stable ordering for this loop, too
        breakdown = defaultdict(list)
        for pk, name, company_type in company_info:
            breakdown[company_type].append(pk)

        for co_type in dict(COMPANY_TYPES).keys():
            field = form.fields[co_type]
            choices = breakdown.get(co_type, [])
            field.queryset = Company.objects.filter(id__in=choices)

        _s_qs = Subdivision.objects.filter_by_user(user)
        form.fields["subdivision"].queryset = _s_qs
        _e_qs = EEPProgramHomeStatus.objects.filter_by_user(user).values_list("eep_program")
        _e_qs = EEPProgram.objects.filter_by_user(user, ignore_dates=True).filter(id__in=_e_qs)
        form.fields["eep_program"].queryset = _e_qs
        _base = EEPProgramHomeStatus.objects.filter_by_user(user)
        _states = list(set(_base.values_list("home__state", flat=True)))
        _states = [("", "---------")] + [(y, y) for y in _states]
        form.fields["us_state"].choices = _states
        _city = [x for x in list(set(_base.values_list("home__city_id", flat=True))) if x]
        _city_qs = City.objects.filter(id__in=_city)
        form.fields["city"].queryset = _city_qs
        _mets = [x for x in list(set(_base.values_list("home__metro_id", flat=True))) if x]
        _met_qs = Metro.objects.filter(id__in=_mets)
        form.fields["metro"].queryset = _met_qs
        if len(_mets) <= 1:
            form.fields["metro"].widget = HiddenInput()

        qs = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        anns = Annotation.objects.filter(
            type__slug="heat-source", object_id__in=qs.values_list("id", flat=True)
        )
        anns_c = [
            (slugify(x), x) for x in sorted(list(set(anns.values_list("content", flat=True))))
        ]
        if len(anns_c):
            base = [
                ("-1", "Gas Heat Homes *"),
                ("-2", "Heat Pump Homes *"),
                ("-3", "Other Heat Homes *"),
            ]
            form.fields["heat_source"].choices = [("", "---------")] + anns_c + base
        else:
            base = [
                ("-1", "Gas Heat Homes *"),
                ("-2", "Heat Pump Homes *"),
                ("-3", "Other Heat Homes *"),
            ]
            form.fields["heat_source"].choices = [("", "---------")] + base

        return form

    def form_invalid(self, form):
        log.warning("Error: %s", form.errors)
        return super(AsynchronousProcessedDocumentCreateHomeStatusXLS, self).form_invalid(form)

    def form_valid(self, form):
        """Send this off for processing"""
        context = self.get_context_data()
        self.object = form.save(commit=False)
        self.object.download = True
        self.object.company = self.request.user.company
        self.object.save()
        task = form.cleaned_data["task_name"]

        kwargs = {"user_id": self.request.user.id, "result_object_id": self.object.id}
        for key, value in form.cleaned_data.items():
            if key == "task_name":
                continue
            if value:
                id_key = "{}_id".format(key)
                if isinstance(value, QuerySet):
                    kwargs[id_key] = ",".join(map(str, value.values_list("id", flat=True)))
                elif isinstance(value, Model):
                    kwargs[id_key] = value.id
                elif isinstance(value, datetime.date):
                    kwargs[key] = value.strftime("%m-%d-%Y")
                else:
                    kwargs[key] = value

        kwargs["id_list"] = self.request.POST.getlist("homes") or None

        task_obj = task.apply_async(kwargs=kwargs, countdown=3)
        self.object.task_id = task_obj.task_id
        self.object.save()
        log.info("Assigning task %s id %s and kwargs %s", task, self.object.task_id, kwargs)
        return HttpResponseRedirect(self.get_success_url())


class BulkHomeProgramReportCreateView(AuthenticationMixin, AxisCreateView):
    permission_required = "home.view_home"
    model = AsynchronousProcessedDocument
    template_name = "filehandling/asynchronousprocesseddocument_form.html"

    # Allow form_valid without any input
    # This is less dumb than making an entire empty form class that validates and returns a
    # task function reference overridden on the 'task_name' field.
    fields = ()

    show_cancel_button = False

    def form_valid(self, form):
        from ..tasks import export_home_program_report_task

        task = export_home_program_report_task

        self.object = form.save(commit=False)
        self.object.download = True
        self.object.company = self.request.user.company
        self.object.save()

        id_list = self.request.POST.getlist("homes")
        filter_info = []
        if not id_list:
            view = ProviderDashboardView()
            self.request.GET = self.request.POST
            self.request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            view.request = self.request
            datatable = view.get_datatable()
            datatable.configure()
            id_list = list(datatable.object_list.values_list("id", flat=True))
            filter_info = view.filters

        kwargs = {
            "user_id": self.request.user.id,
            "result_object_id": self.object.id,
            "homestatus_ids": id_list,
            "filter_info": filter_info,  # UI-friendly hints only
        }

        task_obj = task.apply_async(kwargs=kwargs, countdown=3)
        self.object.task_id = task_obj.task_id
        self.object.save()
        log.info("Assigning task %s id %s and kwargs %s", task, self.object.task_id, kwargs)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Add in any context data"""
        context = super(BulkHomeProgramReportCreateView, self).get_context_data(**kwargs)
        context["title"] = "Home Program Report"
        return context


class UpdateStatsView(TemplateView):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateStatsView, self).dispatch(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        return reverse("home:view", kwargs={"pk": kwargs.get("pk")})

    def get(self, request, *args, **kwargs):
        from ..tasks import update_home_states, update_home_stats

        stat = EEPProgramHomeStatus.objects.get(id=kwargs["pk"])
        stat.validate_references()
        if (stat.state != "complete" or stat.pct_complete < 100) or request.user.is_superuser:
            update_home_stats(eepprogramhomestatus_id=kwargs["pk"])
            update_home_states(eepprogramhomestatus_id=kwargs["pk"])
            stat = EEPProgramHomeStatus.objects.get(id=kwargs["pk"])
            messages.success(request, "Successfully recalculated stats for {}".format(stat))
        else:
            messages.error(request, "Unable to recalculate stats for {}".format(stat))

        return HttpResponseRedirect(self.get_redirect_url(pk=stat.home.id))


class BypassRoughQAActionView(AuthenticationMixin, DetailView):
    """
    Allow NGBS users to skip Rough QA for HIRLProject and update home status to next state
    """

    model = EEPProgramHomeStatus

    def has_permission(self):
        home_status = self.get_object()
        if (
            home_status.eep_program.slug in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            and home_status.state
            in [
                EEPProgramHomeStatus.PENDING_INSPECTION_STATE,
                EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_PROJECT_DATA,
                EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE,
            ]
            and (
                self.request.user.is_superuser
                or self.request.user.is_customer_hirl_company_member()
            )
        ):
            return True
        return False

    def get(self, request, *args, **kwargs):
        from ..tasks import update_home_states

        home_status = self.get_object()
        home_status.customer_hirl_project.is_require_rough_inspection = False
        home_status.customer_hirl_project.save()

        update_home_states(eepprogramhomestatus_id=home_status.id)
        url = reverse("home:view", kwargs={"pk": home_status.home.pk})
        return HttpResponseRedirect(url)


class HomeRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        try:
            home = EEPProgramHomeStatus.objects.get(id=kwargs.get("pk")).home
            return home.get_absolute_url()
        except EEPProgramHomeStatus.DoesNotExist:
            raise Http404()


class HomeReportView(AuthenticationMixin, AxisCreateView):
    permission_required = "home.view_home"
    template_name = "home/eepprogramhomestatus_list.html"

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        # Use this in conjunction with the url kwarg for 'home_status' (instead of a form
        # submission)
        if "home_status" in kwargs:
            try:
                home_status = EEPProgramHomeStatus.objects.filter_by_user(self.request.user).get(
                    id=kwargs["home_status"]
                )
            except EEPProgramHomeStatus.DoesNotExist:
                raise Http404()

            rater_program = home_status.eep_program.get_rater_program()
            qa_program = rater_program.get_qa_program()
            qa_home_status = home_status.home.homestatuses.filter(eep_program=qa_program).first()

            user_role = get_user_role_for_homestatus(home_status, request.user)
            if user_role == "qa" and qa_home_status and qa_home_status.collection_request_id:
                home_status = qa_home_status

            # Direct requests to download a qa program generates the rater template, because legacy
            # did not previously allow for that except in one case, where we tried generating it by
            # referencing the rater home_status for the populated content.  Upload handled the
            # resulting role detection and behavioral switch to qa.
            elif home_status.eep_program.is_qa_program:
                home_status = home_status.home.homestatuses.get(eep_program=rater_program)
            return self.generate_report(home_status=home_status)
        elif "home" in kwargs:
            try:
                home = Home.objects.filter_by_user(self.request.user).get(id=kwargs["home"])
            except Home.DoesNotExist:
                raise Http404()
            return self.generate_report(home=home)
        elif "eep_program" in kwargs:
            try:
                eep_programs = EEPProgram.objects.filter_by_user(
                    self.request.user, visible_for_use=True
                )
                eep_program = eep_programs.get(id=kwargs["eep_program"])
            except EEPProgram.DoesNotExist:
                raise Http404()
            return self.generate_report(eep_program=eep_program)

        raise Http404()

    def generate_report(self, home_status=None, home=None, eep_program=None):
        """If more than one home_stat is selected, give them back in a zip file"""

        from axis.home.single_home_checklist import SingleHomeChecklist

        user = self.request.user
        company = user.company

        if home_status:
            eep_program = home_status.eep_program

        single_home = SingleHomeChecklist(user=self.request.user, company=self.request.user.company)

        if home_status:  # check before eep_program since we overwrite eep_program when this is set
            workbook = single_home.write(home_status_id=home_status.id, return_workbook=True)
            label = "Axis-Home-{}".format(home_status.home.id)
            label += "-QA" if home_status.eep_program.is_qa_program else ""
        elif home:
            workbook = single_home.write(home_id=home.id, return_workbook=True)
            label = "Axis-Home-{}".format(home.id)
        elif eep_program:
            workbook = single_home.write(program_id=eep_program.id, return_workbook=True)
            label = "Axis-Program-{}".format(eep_program.slug)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename={}.xlsx".format(label)
        workbook.save(response)
        return response


class HomePhotoView(View):
    def get(self, request, *args, **kwargs):
        try:
            home = Home.objects.filter_by_user(user=request.user).get(pk=kwargs.get("pk"))
        except Home.DoesNotExist:
            raise Http404()
        return render(
            self.request,
            "home/home_photo_upload.html",
            {"home": home, "home_photos": home.homephoto_set.order_by("-created_at")},
        )

    def post(self, request, *args, **kwargs):
        try:
            home = Home.objects.filter_by_user(user=request.user).get(pk=kwargs.get("pk"))
        except Home.DoesNotExist:
            raise Http404()
        form = HomePhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            home_photo = form.save(commit=False)
            home_photo.home = home
            home_photo.save()
            data = {
                "is_valid": True,
                "id": home_photo.id,
                "name": home_photo.file.name,
                "url": home_photo.file.url,
                "is_primary": home_photo.is_primary,
            }
        else:
            data = {"is_valid": False}
        return JsonResponse(data)


class HomePhotoDetailView(View):
    def post(self, request, *args, **kwargs):
        try:
            home = Home.objects.filter_by_user(user=request.user).get(pk=kwargs.get("pk"))

            home_photo = HomePhoto.objects.get(home=home, pk=kwargs.get("photo_pk"))
        except (Home.DoesNotExist, HomePhoto.DoesNotExist):
            raise Http404()
        form = HomePhotoForm(self.request.POST, self.request.FILES, instance=home_photo)
        if form.is_valid():
            home_photo.save()
            data = {
                "is_valid": True,
                "id": home_photo.id,
                "name": home_photo.file.name,
                "url": home_photo.file.url,
                "is_primary": home_photo.is_primary,
            }
        else:
            data = {"is_valid": False}
        return JsonResponse(data)

    def delete(self, request, *args, **kwargs):
        """
        Delete home photo and returns is_primary photo if exists
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            home = Home.objects.filter_by_user(user=request.user).get(pk=kwargs.get("pk"))

            HomePhoto.objects.get(home=home, pk=kwargs.get("photo_pk")).delete()
        except (Home.DoesNotExist, HomePhoto.DoesNotExist):
            raise Http404()

        home_photo = HomePhoto.objects.filter(home=home, is_primary=True).first()
        data = {}
        if home_photo:
            data = {
                "is_valid": True,
                "id": home_photo.id,
                "name": home_photo.file.name,
                "url": home_photo.file.url,
                "is_primary": home_photo.is_primary,
            }
        return JsonResponse(data)
