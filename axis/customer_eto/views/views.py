"""views.py: Django customer_eto"""

import json
import logging

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView

import datatableview.helpers
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import LegacyAxisDatatableView, AxisUpdateView
from axis.customer_appraisal_institute.forms import GreenEnergyEfficientAddendumForm
from axis.customer_eto.calculator.eps import EPSCalculator
from axis.customer_eto.calculator.eps.utils import get_eto_calculation_completed_form
from axis.customer_eto.tasks import eps_report_task
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.filehandling.views import AsynchronousProcessedDocumentCreateView
from axis.home.forms import HomeStatusFilterForm
from axis.home.models import EEPProgramHomeStatus
from axis.home.views.views import HomeStatusReportMixin
from axis.subdivision.models import Subdivision
from ..api_v3.viewsets.eps_report import get_eps_report
from ..forms import (
    EPSCalculatorForm,
    EPSCalculatorBasicForm,
    EPSPaymentUpdateForm,
    WashingtonCodeCreditProcessedDocumentForm,
)
from axis.customer_eto.tasks.washington_code_credit import WashingtonCodeCreditBulkReportTask
from ..models import FastTrackSubmission
from axis.eep_program.models import EEPProgram

__author__ = "Steven Klass"
__date__ = "9/4/13 10:20 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
customer_eto_app = apps.get_app_config("customer_eto")


class EPSHomesListView(AuthenticationMixin, HomeStatusReportMixin, LegacyAxisDatatableView):
    """This will simply provide a list view for the Program Home Status"""

    permission_required = "home.view_home"
    template_name = "home/eepprogramhomestatus_list.html"

    datatable_options = {
        "columns": [
            ("Address", ["home__lot_number", "home__street_line1", "home__street_line2"]),
            ("Subdivision", "home__subdivision__name"),
            ("Floorplan", "floorplan__name"),
            ("Program", "eep_program__name"),
            ("State", "state"),
        ],
    }

    select_related = [
        "home",
        "home__subdivision",
        "eep_program",
        "floorplan",
    ]

    def get_queryset(self):
        queryset = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        queryset = queryset.filter(certification_date__isnull=False)
        queryset = queryset.select_related(*self.select_related)
        queryset = self.get_external_qs_filters(queryset, self.request.user, **self.request.GET)

        return queryset.distinct()

    def get_column_Address_data(self, obj, *args, **kwargs):
        text = obj.home.get_home_address_display(
            include_confirmed=True, company=self.request.company
        )
        return datatableview.helpers.link_to_model(obj.home, text=text)

    def get_column_Subdivision_data(self, obj, *args, **kwargs):
        try:
            sub = obj.home.subdivision
        except Subdivision.DoesNotExist:
            return "Custom"
        else:
            try:
                name = "{}{}{}".format(
                    sub.name,
                    " at {}".format(sub.community) if sub.community else "",
                    " ({})".format(sub.builder_name) if sub.builder_name else "",
                )
                return "<a href='{}'>{}</a>".format(sub.get_absolute_url(), name)
            except AttributeError:
                return "Custom"

    def get_column_Floorplan_data(self, obj, *args, **kwargs):
        if obj.floorplan:
            return "<a href='{}'>{}</a>".format(
                obj.floorplan.get_absolute_url(), obj.floorplan.name
            )
        return ""

    def get_column_EEP_Program_data(self, obj, *args, **kwargs):
        if obj.eep_program:
            return "<a href='{}'>{}</a>".format(
                obj.eep_program.get_absolute_url(), obj.eep_program.name
            )
        return ""

    def get_column_State_data(self, obj, *args, **kwargs):
        return obj.state_description


class EPSReportView(EPSHomesListView, FormView):
    """Inherits the datatable from the above List view, but adds some form workflow."""

    permission_required = "home.view_home"
    form_class = GreenEnergyEfficientAddendumForm
    template_name = "customer_eto/eps_report.html"
    success_url = reverse_lazy("home")
    show_add_button = False

    datatable_options = {
        "columns": [
            ("Select", None, "get_column_Select_data"),
            ("Address", ["home__lot_number", "home__street_line1", "home__street_line2"]),
            ("Subdivision", "home__subdivision__name"),
            ("Floorplan", "floorplan__name"),
            ("Program", "eep_program__name"),
            ("State", "state"),
        ],
        "unsortable_columns": [
            "Select",
        ],
    }

    def get(self, request, *args, **kwargs):
        # Use this in conjunction with the url kwarg for 'home_status' (instead of a form
        # submission)
        if "home_status" not in kwargs:
            return super(EPSReportView, self).get(request, *args, **kwargs)
        try:
            EEPProgramHomeStatus.objects.get(id=kwargs["home_status"])
            home_status = EEPProgramHomeStatus.objects.filter(id=kwargs["home_status"])
        except EEPProgramHomeStatus.DoesNotExist:
            raise Http404()
        return self.generate_report(home_status)

    def get_queryset(self):
        qs = super(EPSReportView, self).get_queryset()
        return qs.filter(eep_program__owner__slug="eto", state="complete")

    def get_column_Select_data(self, obj, *args, **kwargs):
        return "<input type='checkbox' />"

    def generate_report(self, home_stats):
        """If more than one home_stat is selected, give them back in a zip file"""
        if home_stats.count() > 1:
            eep_program_home_status_ids = list(home_stats.values_list("id", flat=True))
            asynchronous_process_document = AsynchronousProcessedDocument(
                download=True, company=self.request.user.company
            )
            asynchronous_process_document.save()

            eps_report_task.delay(
                asynchronous_process_document_id=asynchronous_process_document.id,
                eep_program_home_status_ids=eep_program_home_status_ids,
                user_id=self.request.user.id,
            )
            return HttpResponseRedirect(asynchronous_process_document.get_absolute_url())
        return get_eps_report(home_stats.get().pk, self.request.user)

    def get_form_kwargs(self):
        kwargs = super(EPSReportView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_invalid(self, form):
        log.warning(form.errors)
        return super(EPSReportView, self).form_invalid(form)

    def form_valid(self, form):
        """Generates the PDF document for the submitted ID list."""
        home_stats = EEPProgramHomeStatus.objects.filter(id__in=form.cleaned_data["homes"])
        wcc_report_requested = all(
            x == "washington-code-credit"
            for x in home_stats.values_list("eep_program__slug", flat=True)
        )
        if wcc_report_requested:
            return self.generate_wcc_report(home_stats)

        return self.generate_report(home_stats)

    def get_context_data(self, **kwargs):
        # This is a necessary evil born from the weird inheritance structure of this view.
        # The get() method of a ListView normally adds object_list to the context kwargs, but the
        # FormView.post() doesn't do such a thing, and so this method's chain of super() calls
        # results in the ListView getting confused about why the 'object_list' isn't there.
        if "object_list" not in kwargs:
            self.object_list = kwargs["object_list"] = self.get_queryset()
        context = super(EPSReportView, self).get_context_data(**kwargs)
        context["form"] = self.get_form(self.form_class)
        context["filter_form"] = HomeStatusFilterForm(
            self.request.GET, user=self.request.user, initial={"certification_only": True}
        )
        self.setup_filter_form(context["filter_form"])
        return context

    def get_visible_filter_fields(self):
        return [
            "eep_program",
            "subdivision",
            "builder",
            "rater",
            "activity_start",
            "activity_stop",
            "certification_date_start",
            "certification_date_end",
        ]

    def setup_filter_form(self, form):
        visible_fields = self.get_visible_filter_fields()
        for field in form.fields.keys():
            if field not in visible_fields:
                form.fields[field].widget = form.fields[field].hidden_widget()

        if not hasattr(self, "_related_companies"):
            self._related_companies = (
                EEPProgramHomeStatus.objects.filter_by_user_for_list_of_companies_by_types(
                    self.request.user
                )
            )

        self.setup_subdivision_field(form)
        self.setup_builder_field(form)
        self.setup_rater_field(form)
        self.setup_eep_program_field(form)

    def setup_subdivision_field(self, form):
        field = form.fields["subdivision"]
        field.queryset = Subdivision.objects.filter_by_user(self.request.user).select_related(
            "community"
        )

    def setup_eep_program_field(self, form):
        field = form.fields["eep_program"]
        field.queryset = EEPProgram.objects.filter(owner__slug="eto")

    def setup_builder_field(self, form):
        field = form.fields["builder"]
        field.choices = self._related_companies.get("builder", [])

    def setup_rater_field(self, form):
        field = form.fields["rater"]

        if self.request.company.company_type == "rater":
            field.widget = field.hidden_widget()
        else:
            field.choices = self._related_companies.get("rater", [])

    def generate_wcc_report(self, home_status):
        home_status_ids = list(home_status.values_list("id", flat=True))
        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=self.request.user.company
        )
        asynchronous_process_document.save()

        WashingtonCodeCreditBulkReportTask.apply_async(
            [asynchronous_process_document.id, home_status_ids, self.request.user.id]
        )

        return HttpResponseRedirect(asynchronous_process_document.get_absolute_url())


class EPSCalculatorFormView(AuthenticationMixin, FormView):
    permission_required = "home.change_home"
    template_name = "customer_eto/eps_calculator.html"
    form_class = EPSCalculatorForm

    def get(self, request, *args, **kwargs):
        if "home_status" in self.request.GET:
            home_status = EEPProgramHomeStatus.objects.get(id=self.request.GET["home_status"])
            form = get_eto_calculation_completed_form(home_status)
            if form.is_valid():
                return self.form_valid(form)
        return super(EPSCalculatorFormView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        data = super(EPSCalculatorFormView, self).get_form_kwargs()
        data["company"] = self.request.user.company

        if self.request.user.is_superuser:
            if "home_status" in self.request.POST:
                home_status = EEPProgramHomeStatus.objects.get(id=self.request.POST["home_status"])
                data["company"] = home_status.company

        return data

    def calculate(self, home_status, **kwargs):
        include_text_report = kwargs.pop("include_text_report", False)

        if isinstance(home_status, (int, str)):
            home_status = EEPProgramHomeStatus.objects.get(id=int(home_status))
        calculator = EPSCalculator(**kwargs)
        return calculator.report_data(include_formated_data=include_text_report)

    def form_invalid(self, form):
        log.warning(form.errors)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HttpResponseBadRequest(json.dumps(form.errors), content_type="application/json")
        return super(EPSCalculatorFormView, self).form_invalid(form)

    def form_valid(self, form):
        self.home_status = getattr(form, "home_status", None)
        results = self.calculate(self.home_status, include_text_report=True, **form.cleaned_data)

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            if self.home_status:
                results.update(
                    {
                        "download_url": reverse(
                            "eto:download", kwargs={"home_status": self.home_status}
                        ),
                    }
                )
            return HttpResponse(json.dumps(results), content_type="application/json")
        return self.render_to_response(self.get_context_data(form=form, results=results))

    def get_context_data(self, **kwargs):
        context = super(EPSCalculatorFormView, self).get_context_data(**kwargs)
        context["hide_admin_table"] = not self.request.user.is_superuser
        mode = kwargs.get("mode", self.kwargs.get("mode", "original"))
        context["mode"] = mode.lower() if mode.lower() == "swwa" else "original"
        context["mode_text"] = "Southwest Washington" if mode.lower() == "swwa" else "Oregon"
        context["state_abbreviation"] = "WA" if context["mode"] == "swwa" else "OR"
        context["enable_inputs"] = True
        return context


class EPSCalculatorBasicFormView(EPSCalculatorFormView):
    permission_required = "home.change_home"
    template_name = "customer_eto/eps_calculator.html"
    form_class = EPSCalculatorBasicForm

    def get_context_data(self, **kwargs):
        context = super(EPSCalculatorBasicFormView, self).get_context_data(**kwargs)
        context["show_full_form"] = True
        context["hide_admin_table"] = True
        context["enable_inputs"] = True
        return context


class PaymentAdjustView(AuthenticationMixin, AxisUpdateView):
    permission_required = "customer_eto.change_fasttracksubmission"
    template_name = "customer_eto/payment_update.html"
    form_class = EPSPaymentUpdateForm
    model = FastTrackSubmission

    def has_permission(self):
        return self.get_object().can_payment_be_updated(self.request.user)

    def get_queryset(self):
        return self.model.objects.filter(home_status__state="complete")

    def get_form_kwargs(self):
        kwargs = super(PaymentAdjustView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            home_status = EEPProgramHomeStatus.objects.get(id=self.kwargs["home_status"])
        except EEPProgramHomeStatus.DoesNotExist:
            raise Http404()

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get(home_status=home_status)
        except queryset.model.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query"
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def get_success_url(self):
        try:
            home_status = EEPProgramHomeStatus.objects.get(id=self.kwargs["home_status"])
        except EEPProgramHomeStatus.DoesNotExist:
            raise Http404()
        return home_status.get_absolute_url()

    def add_success_message(self, form):
        if form.instance.project_id or form.instance.solar_project_id:
            ids = []
            if form.instance.project_id:
                ids.append(f"ENH ID: {form.instance.project_id}")
            if form.instance.solar_project_id:
                ids.append(f"SLE ID: {form.instance.solar_project_id}")
            messages.warning(
                self.request,
                f"Project Tracker {'and '.join(ids)} appear to have been submitted to "
                f"FastTrack. You will need to resubmit as the incentives have changed.",
            )
        messages.success(
            self.request, "Updated payment info for Project ID %s" % form.instance.project_id
        )


class WashingtonCodeCreditProcessedDocumentCreateView(AsynchronousProcessedDocumentCreateView):
    """Washington Code Credit Program Home Upload"""

    permission_required = "home.add_home"
    form_class = WashingtonCodeCreditProcessedDocumentForm

    def get_context_data(self, **kwargs):
        """Adds in all context data"""
        context = super(AsynchronousProcessedDocumentCreateView, self).get_context_data(**kwargs)
        context["template"] = settings.STATIC_URL + "templates/washington_code_credit.xlsm"
        context["title"] = "Washington Code Credit Upload"
        return context
