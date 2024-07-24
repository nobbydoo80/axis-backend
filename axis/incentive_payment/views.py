"""views.py: Django incentive_payment"""

import datetime
import json
import logging
import os
import io
import tempfile
import time
from collections import defaultdict
from operator import itemgetter

import datatableview.helpers
import dateutil.parser

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse, reverse_lazy
from django.utils.html import format_html
from django.utils.timezone import now
from django.views.generic import UpdateView, TemplateView
from django.views.generic.edit import BaseFormView, FormView
from django_states.exceptions import TransitionCannotStart

from axis.annotation.models import Type, Annotation
from axis.builder_agreement.models import BuilderAgreement
from axis.company.models import Company
from axis.core.models import RecentlyViewed
from axis.core.mixins import AuthenticationMixin
from axis.core.utils import collect_nested_object_list
from axis.core.views.generic import LegacyAxisDatatableView, AxisDetailView, AxisDeleteView
from axis.customer_aps.reports import CheckRequest
from axis.customer_aps.models import APSSmartThermostatOption
from axis.relationship.models import Relationship
from . import strings
from .forms import (
    IncentiveDistributionForm,
    IncentivePaymentStatusForm,
    IncentivePaymentStatusAnnotationForm,
    IncentiveDistributionUpdateForm,
)
from .models import IncentiveDistribution, IPPItem, IncentivePaymentStatus
from .reports import CheckDetail

__author__ = "Steven Klass"
__date__ = "3/16/12 1:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
customer_neea_app = apps.get_app_config("customer_neea")


class IncentiveDistributionCreateMixin(object):
    """
    Mixin for creation of Incentive Distribution views so we can
    have a regular view and an ajax view.
    Inherited by: IncentiveDistributionCreateView, AjaxNewForm
    """

    def get_form(self, form_class=None):
        form = super(IncentiveDistributionCreateMixin, self).get_form(form_class)
        queryset = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        queryset = queryset.filter(state="ipp_payment_automatic_requirements")
        self._id_list = queryset.values_list("id", flat=True)
        form.fields["stats"].choices = [(x, x) for x in self._id_list]

        _builders = IncentivePaymentStatus.objects.choice_builder_items_for_user(
            user=self.request.user, id__in=self._id_list
        )
        customer_qs = Company.objects.filter(id__in=[x[0] for x in _builders])
        form.fields["customer"].queryset = customer_qs

        form.fields["check_requested_date"].initial = now().strftime("%Y-%m-%d")
        return form

    def form_invalid(self, form):
        log.warning(form.errors)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            error = {"id": form.cleaned_data["stats"], "url": form.errors}
            response = {"error": error}
            return HttpResponse(json.dumps(response), content_type="application/json")
        return super(IncentiveDistributionCreateMixin, self).form_invalid(form)

    def get_success_url(self):
        return reverse("incentive_payment:view", kwargs={"pk": self.object.id})

    def form_valid(self, form):
        """
        FOR STEVE:
        the client side can handle 3 types of responses: success, info, error.
        success: id, url
        info:    id, message, url
        error:   id, message, url

        What determines each one of these is what I'm unsure of. If better information can be sent
        back for the user to interact with, I'll support it on the client side.
        """
        success = {}
        info = {}
        errors = {}
        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            and self.request.POST.get("validate")
            and self.request.POST["validate"] == "true"
        ):
            for stat in form.cleaned_data["stats"]:
                ipp_stat = IncentivePaymentStatus.objects.get(id=int(stat))
                url = ipp_stat.home_status.home.get_absolute_url()
                home_href = "<a target='_blank' href='{url}'>{home}</a>".format(
                    url=url, home=ipp_stat.home_status.home
                )
                info["id"] = ipp_stat.id
                info["url"] = home_href
                response = {"info": info}
                return HttpResponse(json.dumps(response), content_type="application/json")
        self.object = form.save(commit=False)
        self.object.total = 0
        self.object.company = self.request.user.company
        self.object.check_to_name = self.object.customer.name
        self.object.check_requested = True
        self.object.status = 1
        self.object.save()
        raters = []
        stat_ids = [int(x) for x in form.cleaned_data.get("stats", [])]
        ipp_stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)
        for ipp_stat in ipp_stats.all():
            home_stat = ipp_stat.home_status
            price = home_stat.get_builder_incentive()
            IPPItem.objects.create(
                home_status=home_stat, cost=price, incentive_distribution=self.object
            )
            if home_stat.company not in raters and home_stat.get_rater_incentive() > 0:
                raters.append(home_stat.company)
            ipp_stat.make_transition("pending_payment_requirements", user=self.request.user)
        self.object.save()

        if not self.object.rater_incentives.count():
            data = form.cleaned_data.copy()
            del data["stats"]
            del data["rater_incentives"]
            for rater in raters:
                data.update(
                    {
                        "customer": rater,
                        "check_to_name": rater.name,
                        "company": self.request.user.company,
                        "check_requested": True,
                        "status": 1,
                        "total": 0,
                    }
                )
                rater_object = IncentiveDistribution.objects.create(**data)
                rater_object.save()
                for ipp_stat in ipp_stats.all():
                    home_stat = ipp_stat.home_status
                    if home_stat.company != rater:
                        continue
                    if home_stat.get_rater_incentive() < 0.01:
                        continue
                    IPPItem.objects.create(
                        home_status=home_stat,
                        cost=home_stat.get_rater_incentive(),
                        incentive_distribution=rater_object,
                    )
                rater_object.total = rater_object.total_cost()
                rater_object.save()
                self.object.rater_incentives.add(rater_object)
        self.object.save()
        msg = 'Successfully created {}. &emsp; <a target="_blank" href="{}">Add another</a>'
        ajax_msg = 'Successfully created <a target="_blank" href="{}">{}</a>.'
        messages.success(self.request, msg.format(self.object, reverse("incentive_payment:add")))
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            success["id"] = self.object.id
            success["url"] = ajax_msg.format(self.object.get_absolute_url(), self.object)
            response = {}
            if len(success):
                response["success"] = success
            if len(info):
                response["info"] = info
            return HttpResponse(json.dumps(response), content_type="application/json")
        return HttpResponseRedirect(self.get_success_url())


class IncentivePaymentPendingAnnotationMixin(object):
    """
    Mixin for Pending Requests form to allow for regular view and ajax view of form.
    Inherited by: IncentivePaymentPendingAnnotationList, AjaxPendingForm
    """

    def get_form(self, form_class=None):
        form = super(IncentivePaymentPendingAnnotationMixin, self).get_form(form_class)
        if not hasattr(self, "_id_list"):
            queryset = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
            self._id_list = queryset.values_list("id", flat=True)
        form.fields["stats"].choices = [(x, x) for x in self._id_list]
        return form

    def form_invalid(self, form):
        log.warning(form.errors)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            response = {"progress": self.request.POST["progress"], "error": form.errors}
            return HttpResponse(json.dumps(response), content_type="application/json")
        return super(IncentivePaymentPendingAnnotationMixin, self).form_invalid(form)

    def get_success_url(self):
        if self.kwargs.get("state"):
            return reverse("incentive_payment:returned")
        return reverse("incentive_payment:pending")

    def _state_transitions(self, name):
        data = {
            "ipp_payment_requirements": "pending_requirements",
            "ipp_payment_failed_requirements": "failed_requirements",
            "resubmit-failed": "corrected_requirements",
            "payment_pending": "pending_requirements",
            "ipp_failed_restart": "corrected_requirements",
            "start": "reset_prior_approved",
        }
        return data[name]

    def form_valid(self, form):
        """Simply update the status and send messages"""
        success = {}
        info = {}
        errors = {}
        # if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
        #     for stat in form.cleaned_data['stats']:
        #         ipp_stat = IncentivePaymentStatus.objects.get(id=int(stat))
        #         url = ipp_stat.home_status.home.get_absolute_url()
        #         home_href = "<a href='{url}'>{home}</a>".format(
        #             url=url, home=ipp_stat.home_status.home)
        #         response = {'progress': self.request.POST['progress']}
        #         if int(self.request.POST['number']) % 3 == 0:
        #             print("SUCCESS")
        #             response['success'] = {
        #                 'id': ipp_stat.id,
        #                 'url': home_href
        #             }
        #         else:
        #             if int(self.request.POST['number']) % 2 == 0:
        #                 print("INFO")
        #                 response['info'] = {
        #                     'id': ipp_stat.id,
        #                     'message': "We have some information on this home",
        #                     'url': home_href
        #                 }
        #             else:
        #                 print("ERROR")
        #                 response['error'] = {
        #                     'id': ipp_stat.id,
        #                     'message': "There is something wrong",
        #                     'url': home_href
        #                 }
        #         return HttpResponse(json.dumps(response), content_type="application/json")

        cleaned_data = form.cleaned_data
        info = {}
        success = {}
        for stat in cleaned_data["stats"]:
            ipp_stat = IncentivePaymentStatus.objects.get(id=int(stat))
            if cleaned_data.get("new_state") not in [None, ""]:
                url = ipp_stat.home_status.home.get_absolute_url()
                home_href = "<a target='_blank' href='{url}'>{home}</a>".format(
                    url=url, home=ipp_stat.home_status.home
                )
                try:
                    ipp_stat.make_transition(
                        self._state_transitions(cleaned_data["new_state"]), user=self.request.user
                    )
                    success["id"] = ipp_stat.id
                    success["url"] = home_href
                except TransitionCannotStart:
                    states = dict(IncentivePaymentStatus.get_state_choices())
                    to_state = states.get(cleaned_data["new_state"])
                    msg = strings.UNABLE_TO_TRANSITION_HOME
                    msg = msg.format(
                        home_url=home_href, ostate=ipp_stat.get_state_display(), tstate=to_state
                    )
                    messages.warning(self.request, msg)
                    info["id"] = ipp_stat.id
                    info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                        ostate=ipp_stat.get_state_display(), tstate=to_state
                    )
                    info["url"] = home_href
            if cleaned_data["annotation"]:
                a_type, _ = Type.objects.get_or_create(
                    slug="{}-ipp-status-note".format(ipp_stat.owner.slug),
                    defaults=dict(name="{}-ipp-status-note".format(ipp_stat.owner.slug)),
                )
                Annotation.objects.create(
                    type=a_type,
                    content=cleaned_data["annotation"],
                    content_type=ContentType.objects.get_for_model(ipp_stat),
                    object_id=ipp_stat.id,
                    user=self.request.user,
                )

        if cleaned_data["new_state"] in ["ipp_payment_failed_requirements"]:
            IncentivePaymentStatus.objects.send_notification_failure_message(
                self.request.user.company, id__in=[int(x) for x in cleaned_data["stats"]]
            )
        if cleaned_data["new_state"] in ["resubmit-failed"]:
            IncentivePaymentStatus.objects.send_notification_corrected_message(
                self.request.user.company, id__in=[int(x) for x in cleaned_data["stats"]]
            )
        if cleaned_data["new_state"] in ["ipp_payment_requirements"]:
            IncentivePaymentStatus.objects.send_notification_approved_message(
                self.request.user.company, id__in=[int(x) for x in cleaned_data["stats"]]
            )

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            response = {"progress": self.request.POST["progress"]}
            if len(success):
                response["success"] = success
            if len(info):
                response["info"] = info

            return HttpResponse(json.dumps(response), content_type="application/json")
        return HttpResponseRedirect(self.get_success_url())


class IncentiveDistributionListView(AuthenticationMixin, LegacyAxisDatatableView):
    """List view for what has started / completed and incentive distribution"""

    permission_required = "incentive_payment.view_incentivedistribution"
    template_name = "incentive_payment/incentive_payment_list.html"

    datatable_options = {
        "columns": [
            ("Invoice Number", "invoice_number"),
            ("Customer", "customer__name", datatableview.helpers.link_to_model),
            ("Check Req", "check_requested", datatableview.helpers.make_boolean_checkmark),
            ("Check Req Date", "check_requested_date"),
            ("Is Paid", "is_paid", datatableview.helpers.make_boolean_checkmark),
            ("Paid Date", "paid_date"),
            ("Check No", "check_number"),
            ("Total", "total", datatableview.helpers.format("${:,.2f}", cast=float)),
        ],
    }
    select_related = ["customer"]

    def get_queryset(self):
        """Filter by user"""
        queryset = IncentiveDistribution.objects.filter_by_user(user=self.request.user)
        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            return self.get_external_qs_filters(queryset)
        return IncentiveDistribution.objects.none()

    def filter_by_customer(self, request):
        _company_ids = [request.GET.get(key) for key in ["builder_id", "provider_id"]]
        company_ids = list(filter(None, _company_ids))

        if company_ids:
            return {"customer_id__in": company_ids}

        return {}

    def filter_by_date(self, request):
        activity_start = request.GET.get("activity_start")
        activity_stop = request.GET.get("activity_stop")

        kwargs = {}

        if activity_start:
            kwargs["paid_date__gte"] = dateutil.parser.parse(activity_start)

        if activity_stop:
            kwargs["paid_date__lte"] = dateutil.parser.parse(activity_stop) + datetime.timedelta(
                days=1
            )

        return kwargs

    def get_external_qs_filters(self, queryset):
        filter_kwargs = self.filter_by_customer(self.request)
        filter_kwargs.update(self.filter_by_date(self.request))
        return queryset.filter(**filter_kwargs).select_related(*self.select_related)

    def get_column_Invoice_Number_data(self, obj, *args, **kwargs):
        """Provide the invoice number
        :param instance: instance
        """
        url = "<a href='{url}' target='_blank' data-toggle='tooltip' data-original-title='{tooltip}'>{text}</a>"
        return url.format(
            url=obj.get_absolute_url(), tooltip=obj.customer.name, text=obj.invoice_number
        )

        return datatableview.helpers.link_to_model(obj, text=obj.invoice_number)

    def get_form(self):
        form = IncentivePaymentStatusForm()

        builders, subdivisions, providers, eep_programs = IncentivePaymentPendingList(
            request=self.request
        ).get_query_form_choices()

        def get_choices(choices_list):
            return [("", "---------")] + choices_list

        form.fields["builder"].choices = get_choices(builders)
        form.fields["subdivision"].choices = get_choices(subdivisions)
        form.fields["eep_program"].choices = get_choices(eep_programs)
        form.fields["provider"].choices = get_choices(providers)
        form.fields["state"].initial = "pending"
        form.fields["activity_start"].widget.attrs["size"] = 9
        form.fields["activity_stop"].widget.attrs["size"] = 9
        form.fields["activity_start"].label = "Paid Date Start"
        form.fields["activity_stop"].label = "Paid Date End"

        return form

    def get_context_data(self, **kwargs):
        context = super(IncentiveDistributionListView, self).get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context


class IncentiveDistributionDetailView(AuthenticationMixin, AxisDetailView):
    """Detail view for an incentive distribution"""

    permission_required = "incentive_payment.view_incentivedistribution"

    def get_queryset(self):
        """Get the list of items for this view."""
        return IncentiveDistribution.objects.filter_by_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Get the context data"""
        data = super(IncentiveDistributionDetailView, self).get_context_data(**kwargs)
        data["date"] = now()
        if self.object.rater_incentives.count() and self.object.check_number:
            raters = []
            for rater in self.object.rater_incentives.all():
                if not rater.check_number:
                    raters.append(rater.customer.name)
            if len(raters) and self.request.user.company.id == self.object.company.id:
                msg = "You must also update the raters {} with the check_numbers"
                messages.warning(self.request, msg.format(", ".join(raters)))
        else:
            # no rater_incentive entries or program rater incentives, but related to the invoice
            rater_names = self.object.ippitem_set.values_list(
                "home_status__company__name", flat=True
            )
            data["rater_names"] = list(sorted(set(rater_names)))

        view = IncentiveDistributionIPPItems()
        view.request = self.request
        datatable = view.get_datatable()
        datatable.url = reverse("incentive_payment:ipp_items", kwargs={"pk": self.object.id})
        data["datatable"] = datatable

        RecentlyViewed.objects.view(instance=self.object, by=self.request.user)
        return data


class IncentivePaymentPendingList(AuthenticationMixin, LegacyAxisDatatableView):
    """This is the Pending List"""

    model = IncentivePaymentStatus
    permission_required = "incentive_payment.view_incentivedistribution"
    template_name = "incentive_payment/incentive_payment_status_list.html"

    datatable_options = {
        "columns": [
            ("Axis ID", "home_status_home_id"),
            (
                "Address",
                [
                    "home_status__home__street_line1",
                    "home_status__home__street_line2",
                    "home_status__home__lot_number",
                ],
            ),
            # ('EEP', 'home_status__eep_program__name'),
            ("Subdivision", "home_status__home__subdivision__name"),
            ("Program", "home_status__eep_program__name"),
            ("Meter Set", "home_status__home__apshome__meterset_date"),
            ("Cert Date", "home_status__certification_date"),
            (
                "Smart Thermostat",
                "home_status__home__subdivision__aps_thermostat_option__eligibility",
                "get_column_smart_thermostat_options_data",
            ),
            (
                "Simulation",
                [
                    "home_status__floorplan__remrate_target__energystar__energy_star_v3_pv_score",
                    "ekotrope_houseplan__analysis__data",  # ['hersScore']
                ],
                "get_column_Simulation_data",
            ),
            ("Annotation", "annotation__value"),
            ("Last Activity", "last_update", "get_column_Last_Activity_data"),
            ("Builder", "relationships__company__name", "get_column_Builder_data"),
            ("Provider", "home_status__company__name"),
        ],
        "ordering": ["-last_update", "home_status__certification_date"],
        "search_fields": ["home_status__home__subdivision__community__name"],
    }

    select_related = [
        "home_status__company",
        "home_status__eep_program",
        "home_status__floorplan",
        "home_status__floorplan__ekotrope_houseplan__analysis",
        "home_status__floorplan__remrate_target__energystar",
        "home_status__home",
        "home_status__home__apshome",
        "home_status__home__geocode_response",
        "home_status__home__geocode_response__geocode",
        "home_status__home__subdivision",
        "home_status__home__subdivision__community",
        "home_status__home__subdivision__builder_org",
        # 'home_status__home__history__history_user',
    ]
    prefetch_related = [
        # 'annotations__user',
        "home_status__home__relationships",
        "home_status__home__subdivision__floorplanapproval_set",
        "home_status__floorplan__floorplanapproval_set",
    ]

    defer = [
        "home_status__floorplan__component_serialization",
        "home_status__floorplan__simulation_result",
        "home_status__floorplan__ekotrope_houseplan__analysis__data",
        "home_status__home__geocode_response__place",
        "home_status__eep_program__workflow_default_settings",
    ]

    DEBUG = False

    def dispatch(self, request, *args, **kwargs):
        response = super(IncentivePaymentPendingList, self).dispatch(request, *args, **kwargs)
        if self.DEBUG:
            self.get_ajax(self.request, self.args, self.kwargs)
        return response

    def get_queryset(self):
        """Get the list of items for this view."""
        queryset = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        # only make these needed things if the queryset has not already been evaluated
        if not hasattr(self, "_id_list") or not hasattr(self, "_eep_program_choices"):
            self._id_list = list(queryset.values_list("id", flat=True))
            self._eep_program_choices = queryset.values_list(
                "home_status__eep_program_id", "home_status__eep_program__name"
            )
        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
            or self.DEBUG
        ):
            return self.get_external_qs_filters(queryset)
        return IncentivePaymentStatus.objects.none()

    def get_external_qs_filters(self, queryset):
        """This applies a number of filters to the queryset"""
        null_dict = [None, "", "undefined"]
        filtered_queryset = False
        if self.request.GET.get("subdivision_id") not in null_dict:
            log.info("Filtering on Subdivision=%s", self.request.GET["subdivision_id"])
            filtered_queryset = True
            queryset = queryset.filter_by_subdivision_id(
                id__in=self._id_list, subdivision_id=self.request.GET["subdivision_id"]
            )

        if self.request.GET.get("provider_id") not in null_dict:
            log.info("Filtering on Provider=%s", self.request.GET["provider_id"])
            filtered_queryset = True
            queryset = queryset.filter_by_provider_id(
                id__in=self._id_list, provider_id=self.request.GET["provider_id"]
            )

        if self.request.GET.get("eep_program_id") not in null_dict:
            log.info("Filtering on Program=%s", self.request.GET["eep_program_id"])
            filtered_queryset = True
            queryset = queryset.filter(
                id__in=self._id_list,
                home_status__eep_program_id=int(self.request.GET["eep_program_id"]),
            )

        if self.request.GET.get("builder_id") not in null_dict:
            log.info("Filtering on Builder=%s", self.request.GET["builder_id"])
            filtered_queryset = True
            queryset = queryset.filter_by_company_id(
                id__in=self._id_list, company_id=int(self.request.GET["builder_id"])
            )

        if self.request.GET.get("state") not in null_dict:
            log.info("Filtering on State=%s", self.request.GET["state"])
            filtered_queryset = True
            queryset = queryset.filter(state=self.request.GET["state"])

        if self.request.GET.get("activity_start") not in null_dict:
            log.info("Filtering on Activity Start=%s", self.request.GET["activity_start"])
            try:
                activity_start = dateutil.parser.parse(self.request.GET["activity_start"]).replace(
                    tzinfo=datetime.timezone.utc
                )

                filtered_queryset = True
                queryset = queryset.filter(
                    Q(last_update__gte=activity_start)
                    | Q(state_history__start_time__gte=activity_start)
                )
            except ValueError:
                log.error("Unable to parse start - %s", self.request.GET["activity_start"])

        if self.request.GET.get("activity_stop") not in null_dict:
            log.info("Filtering on Activity Stop=%s", self.request.GET["activity_stop"])
            try:
                activity_stop = dateutil.parser.parse(self.request.GET["activity_stop"]).replace(
                    tzinfo=datetime.timezone.utc
                )

                filtered_queryset = True
                queryset = queryset.filter(
                    Q(last_update__lte=activity_stop)
                    | Q(state_history__start_time__lte=activity_stop)
                )
            except ValueError:
                log.error("Unable to parse stop - %s", self.request.GET["activity_stop"])

        if not filtered_queryset:
            return queryset.none()

        # grab all the related stuff after the queryset has possibly changed
        queryset = queryset.prefetch_related(*self.prefetch_related)
        queryset = queryset.select_related(*self.select_related)
        queryset = queryset.defer(*self.defer)

        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            self.prefetch_home_relationships_names(queryset)
            self.prefetch_floorplan_data(queryset)

        return queryset

    def prefetch_home_relationships_names(self, queryset):
        """Pulls the home relationships.  Also grabs the homestatus.company as _company"""
        if getattr(self, "relationships", None) is not None:
            return self.relationships

        start = time.time()
        home_ids = list(queryset.values_list("home_status__home__id", flat=True))
        relationships = Relationship.objects.filter(
            object_id__in=home_ids, content_type__app_label="home"
        )
        desired = "object_id", "company__company_type", "company__name"
        _rels = relationships.values_list(*desired)
        self.relationships = defaultdict(defaultdict)
        for home_id, company_type, company_name in _rels:
            self.relationships[home_id][company_type] = company_name

        desired = "home_status__home__id", "home_status__company__name"
        for home_id, company_name in queryset.values_list(*desired):
            self.relationships[home_id]["_company"] = company_name

        from axis.home.models import Home

        history = Home.history.model
        desired = "id", "history_user__company__name"
        qs = history.objects.filter(id__in=home_ids).values_list(*desired)
        for home_id, company_name in qs.order_by("history_id"):
            self.relationships[home_id]["_originator"] = company_name

        for home_id, data in self.relationships.items():
            if "_originator" not in data:
                self.relationships[home_id]["_originator"] = "Administrator"
        log.debug("Completed %s in %.2fs", "prefetch_home_relationships_names", time.time() - start)

    def prefetch_floorplan_data(self, queryset):
        """This will prefetch a full set of floorplan / simulation data"""
        if getattr(self, "_floorplan_data", None) is not None:
            return self._floorplan_data
        start = time.time()
        desired = (
            "home_status__floorplan_id",
            "home_status__floorplan__remrate_target_id",
            "home_status__floorplan__ekotrope_houseplan_id",
            "home_status__floorplan__remrate_data_file",
            "home_status__floorplan__remrate_target__energystar__energy_star_v3p2_pv_score",
            "home_status__floorplan__remrate_target__energystar__energy_star_v3p1_pv_score",
            "home_status__floorplan__remrate_target__energystar__energy_star_v3_pv_score",
            "home_status__floorplan__remrate_target__energystar__energy_star_v2p5_pv_score",
            "home_status__floorplan__remrate_target__hers__score",
            "home_status__floorplan__remrate_target__energystar__passes_energy_star_v3",
            "home_status__floorplan__ekotrope_houseplan__analysis__data",
            "home_status__floorplan__floorplanapproval__is_approved",
            "home_status__eep_program__require_model_file",
            "home_status__eep_program__require_rem_data",
            "home_status__eep_program__require_ekotrope_data",
            "home_status__eep_program__max_hers_score",
            "home_status__eep_program__min_hers_score",
            "home_status__eep_program__owner__slug",
        )

        qs = queryset.values_list(*desired).distinct()
        self._floorplan_data = defaultdict(defaultdict)
        for item in qs.all():
            (
                fp_id,
                rr_id,
                ek_id,
                mdl_file,
                rr_3p2,
                rr_3p1,
                rr_3,
                rr_2p5,
                rr_hers,
                rr_pass_v3,
                eko_data,
                fp_approved,
                req_model,
                req_rr,
                req_eko,
                max_hers,
                min_hers,
                owner,
            ) = item

            errors, warnings = [], []

            try:
                rr_hers = list(filter(None, (rr_hers)))
            except TypeError:
                rr_hers = None

            eko_key = "hersScore"
            passing_v3 = None

            if owner == "aps":
                rr_hers = list(filter(None, (rr_3p2, rr_3p1, rr_3, rr_2p5)))
                eko_key = "hersScoreNoPv"

            if rr_hers:
                hers_score = rr_hers[0]
                url = reverse("floorplan:input:remrate", kwargs={"pk": rr_id})
                passing_v3 = rr_pass_v3
            else:
                try:
                    hers_score = eko_data.get(eko_key)
                except (TypeError, AttributeError):
                    hers_score = -1.0
                    url = "#"
                else:
                    url = reverse("floorplan:input:ekotrope", kwargs={"pk": ek_id})
                    compliances = eko_data.get("compliance", [])
                    comp = next((x for x in compliances if x.get("code") == "EnergyStarV3"), {})
                    passing_v3 = comp.get("complianceStatus") == "Pass"

            if req_model and mdl_file is None:
                errors.append("Missing REM/Rate data file")
            if req_rr and rr_id is None:
                errors.append("Missing REM/Rate data")
            if req_eko and ek_id is None:
                errors.append("Missing Ekotrope data")
            if max_hers and hers_score > max_hers:
                errors.append("HERs score greater than {}".format(max_hers))
            if min_hers and hers_score < min_hers:
                errors.append("HERs score less than {}".format(min_hers))
            if hers_score == -1.0:
                errors.append("Missing HERs score")
            if not passing_v3:
                errors.append("Simulation does not pass ENERGY STAR V3 Requirements")

            if owner == "aps" and not fp_approved:
                warnings.append("Floorplan is not active")

            source = "remrate" if rr_id else None
            source = "ekotrope" if ek_id and source is None else source

            data = {
                "hers_score": hers_score,
                "url": url,
                "source": source,
                "errors": errors,
                "warnings": warnings,
            }

            # if fp_id in self._floorplan_data:
            #     print('OLD: %s' % self._floorplan_data[fp_id])
            #     print('NEW: %s' % data)

            self._floorplan_data[fp_id] = {
                "url": reverse("floorplan:view", kwargs={"pk": fp_id}),
                "hers_score": hers_score,
                "simulation_url": url,
                "source": source,
                "errors": errors,
                "warnings": warnings,
            }
        log.debug("Completed %s in %.2fs", "prefetch_floorplan_data", time.time() - start)

    def get_datatable_options(self):
        """Returns the DatatableOptions object for this view's configuration."""
        options = self.datatable_options.copy()
        options["columns"] = options["columns"][:]

        hidden_columns = []

        if not self.request.user.is_superuser:
            hidden_columns.append("Builder")

        if self.request.company.slug != "aps":
            for name in ["Meter Set", "Bldr Agrmnt", "Simulation", "Provider"]:
                for i, column in list(enumerate(options["columns"])):
                    if column[0] == name:
                        options["columns"].pop(i)
        elif self.request.user.is_superuser:
            hidden_columns.append("Provider")

        if self.request.company.slug not in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS:
            for name in ["Axis ID"]:
                for i, column in list(enumerate(options["columns"])):
                    if column[0] == name:
                        options["columns"].pop(i)

        options["hidden_columns"] = hidden_columns

        return options

    def get_column_Address_data(self, obj, **kwargs):
        """Provide the home address
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        home = obj.home_status.home

        text = home.get_home_address_display(include_confirmed=True, company=self.request.company)

        builder = self.relationships[obj.home_status.home_id].get("builder")
        originator = self.relationships[obj.home_status.home_id].get("_originator")
        tooltip = "{} - {}".format(originator, builder)

        url = "<a href='{url}' target='_blank' data-toggle='tooltip' data-original-title='Created by: {tooltip}'>{text}</a>"
        return url.format(url=home.get_absolute_url(), tooltip=tooltip, text=text)

    def get_column_Subdivision_data(self, obj, **kwargs):
        """Provide the subdivision data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        if obj.home_status.home.subdivision:
            if obj.home_status.home.subdivision.community:
                url = "<a href='{url}' target='_blank' data-toggle='tooltip' data-original-title='Community: {tooltip}'>{text}</a>"
                subdivision = obj.home_status.home.subdivision
                community = subdivision.community
                url = url.format(
                    url=subdivision.get_absolute_url(), tooltip=community, text=subdivision
                )
                return url

            return datatableview.helpers.link_to_model(obj.home_status.home.subdivision)
        else:
            return "Custom"

    def get_column_Axis_ID_data(self, obj, **kwargs):
        return obj.home_status.home.id

    def get_column_Program_data(self, obj, **kwargs):
        """Provide the Program
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        return datatableview.helpers.link_to_model(obj.home_status.eep_program)

    def get_column_Meter_Set_data(self, obj, **kwargs):
        """Provide the MeterSet data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        error = "<div class='error label label-danger' data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        warning = "<div class='warning label label-warning' data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        href = "<a target='_blank' href='{}'>{}</a>"
        if hasattr(obj.home_status.home, "apshome"):
            try:
                url = href.format(
                    reverse(
                        "aps_homes_detail_view", kwargs={"pk": obj.home_status.home.apshome.id}
                    ),
                    obj.home_status.home.apshome.meterset_date.strftime("%m/%d/%y"),
                )
                if (
                    datetime.date.today() - obj.home_status.home.apshome.meterset_date
                    >= datetime.timedelta(days=365)
                ):
                    return warning.format("Meterset is over a year old", url)
                return url
            except AttributeError:
                return error.format(
                    "Missing Meterset or it's wrong", "<i class='fa fa-exclamation'></i>&nbspNo"
                )
        # QUESTION: Are we only supporting this column for aps homes
        else:
            return error.format("Missing Meterset", "<i class='fa fa-exclamation'></i>&nbspNo")

    def get_column_Cert_Date_data(self, obj, **kwargs):
        """Provide the certification data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        error = "<div class='error label label-danger' data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        warning = "<div class='warning label label-warning' data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        certification_date = obj.home_status.certification_date
        if not certification_date:
            msg = "Missing certification date."
            return error.format(msg, "<i class='fa fa-exclamation'></i>&nbspNo")

        try:
            delta_days = abs(
                (
                    obj.home_status.home.apshome.meterset_date - obj.home_status.certification_date
                ).days
            )
            if delta_days > 275:
                msg = "Certification date to meterset window is greater than 275 days."
                return error.format(msg, certification_date.strftime("%m/%d/%y"))
            if delta_days > 180:
                msg = "Certification date to meterset window is greater than 180 days."
                return warning.format(msg, certification_date.strftime("%m/%d/%y"))
        except AttributeError:
            pass

        return certification_date.strftime("%m/%d/%y")

    def Xget_column_Simulation_data(self, obj, **kwargs):
        """Provide the RemRate/Ekotrope Data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        # TODO: show which issue is causing the 'NO' error in the tooltip.
        error = "<div class='error label label-danger' data-html='true' data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        warning = "<div class='warning label label-warning' data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"

        error_class = "error label label-danger"
        href = "<a target='_blank' class='{}' href='{}'>{}</a>"
        div = "<div class='{}'>{}</div>"
        eep = obj.home_status.eep_program
        if obj.home_status.floorplan:
            floorplan_id = obj.home_status.floorplan_id
            ekotrope_id = obj.home_status.floorplan.ekotrope_houseplan_id
            target_id = obj.home_status.floorplan.remrate_target_id
            data_file = obj.home_status.floorplan.remrate_data_file
            try:
                hers_score = int(
                    obj.home_status.floorplan.get_hers_score_for_program(
                        obj.home_status.eep_program
                    )
                )
            except (ObjectDoesNotExist, AttributeError, TypeError):
                hers_score = False
            climate_zone = obj.home_status.home.climate_zone.zone
        else:
            target_id = False
            data_file = False
            ekotrope_id = False
            hers_score = False
            floorplan_id = False
            climate_zone = None

        if not eep.require_input_data:
            if target_id:
                url = reverse("floorplan:input:remrate", kwargs={"pk": target_id})
                return href.format(error_class, url, "OK")
            if ekotrope_id:
                url = reverse("floorplan:input:ekotrope", kwargs={"pk": ekotrope_id})
                return href.format(error_class, url, "OK")
            return "<div>OK</div>"

        if not hers_score:
            hers_score = -1.0
        errors = []
        warnings = []

        if eep.require_model_file and data_file is None:
            errors.append("Missing REM/Rate data file")
        if eep.require_rem_data and target_id is None:
            errors.append("Missing REM/Rate data")
        if eep.require_ekotrope_data and ekotrope_id is None:
            errors.append("Missing Ekotrope data")
        if eep.max_hers_score and hers_score > eep.max_hers_score:
            errors.append("HERs score greater than {}".format(eep.max_hers_score))
        if eep.min_hers_score and hers_score < eep.min_hers_score:
            errors.append("HERs score less than {}".format(eep.max_hers_score))
        if hers_score == -1.0:
            errors.append("Missing HERs score")

        if floorplan_id and eep.owner.slug == "aps":
            # The home and floorplan subdivisions should reconcile already by this point, and this
            # is the only appropriate subdivision reference if/when APS starts assigning floorplans
            # to multiple subdivisions (each with their own approval setting).
            subdivision = obj.home_status.home.subdivision
            approval_status = obj.home_status.floorplan.get_approved_status(subdivision=subdivision)
            if not approval_status.is_approved:
                warnings.append("Floorplan is not active")
            if not obj.home_status.floorplan.simulation_passes_energy_star_v3:
                errors.append("Simulation does not pass ENERGY STAR V3 Requirements")

        if errors or warnings:
            href = "<a target='_blank' style='color: white' href='{}'><u>{}</u></a>"

        messages = errors + warnings

        if errors:
            msg = "<br>".join(messages)
            text = hers_score if hers_score else "No"
            if target_id:
                url = reverse("floorplan:input:remrate", kwargs={"pk": target_id})
                tag = href.format(url, text)
                return error.format(msg, tag)
            elif ekotrope_id:
                url = reverse("floorplan:input:ekotrope", kwargs={"pk": ekotrope_id})
                tag = href.format(url, text)
                return error.format(msg, tag)
            return error.format(msg, "<i class='fa fa-exclamation'></i>&nbspNo")
        elif warnings:
            msg = "<br>".join(messages)
            url = reverse("floorplan:view", kwargs={"pk": floorplan_id})
            tag = href.format(url, hers_score if hers_score else "No")
            return warning.format(msg, tag)

        error_class = ""
        text = hers_score if hers_score else "Yes"
        if target_id:
            url = reverse("floorplan:input:remrate", kwargs={"pk": target_id})
            return href.format(error_class, url, text)
        elif ekotrope_id:
            url = reverse("floorplan:input:ekotrope", kwargs={"pk": ekotrope_id})
            return href.format(error_class, url, text)
        return div.format(error_class, "-")

    def get_column_Simulation_data(self, obj, **kwargs):
        """Pull the simulation data"""
        floorplan_id = obj.home_status.floorplan_id

        data = self._floorplan_data.get(floorplan_id, {})

        errors, warnings = data.get("errors", []), data.get("warnings", [])
        hers_score, simulation_type = data.get("hers_score", -1), data.get("simulation", "N/A")
        url, sim_url = data.get("url", "#"), data.get("simulation_url", "#")

        error = (
            "<div class='error label label-danger' data-html='true' "
            "data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        )
        warning = (
            "<div class='warning label label-warning' "
            "data-toggle='tooltip' data-placement='top' title='{}'>{}</div>"
        )
        href = "<a target='_blank' class='{}' href='{}'>{}</a>"
        div = "<div class='{}'>{}</div>"

        messages = errors + warnings
        if messages:
            href = "<a target='_blank' style='color: white' href='{}'><u>{}</u></a>"

        if errors:
            msg = "<br>".join(messages)
            text = hers_score if hers_score else "No"

            if simulation_type == "remrate":
                return error.format(msg, href.format(sim_url, text))
            elif simulation_type == "ekotrope":
                return error.format(msg, href.format(sim_url, text))
            return error.format(msg, "<i class='fa fa-exclamation'></i>&nbspNo")
        elif warnings:
            msg = "<br>".join(messages)
            tag = href.format(url, hers_score if hers_score else "No")
            return warning.format(msg, tag)

        error_class = ""
        text = hers_score if hers_score else "Yes"
        if simulation_type == "remrate":
            return href.format(error_class, sim_url, text)
        elif simulation_type == "ekotrope":
            return href.format(error_class, sim_url, text)
        return div.format(error_class, "-")

    def get_column_Builder_data(self, obj, **kwargs):
        """Provide the builder"""
        # How can we prefetch this?
        builder = self.relationships[obj.home_status.home_id]["builder"]
        span = (
            "<span data-toggle='tooltip' "
            "data-original-title='Subdivision: {tooltip}'>{text}</span>"
        )
        if obj.home_status.home.subdivision_id:
            tooltip = obj.home_status.home.subdivision.name
        else:
            tooltip = "Custom"
        return span.format(text=builder, tooltip=tooltip)

    def get_column_provider_data(self, obj, **kwargs):
        """Pull the provider out"""
        return self.relationships[obj.home_status.home_id]["provider"]

    def get_column_smart_thermostat_options_data(self, obj, **kwargs):
        fake_obj = APSSmartThermostatOption(eligibility=kwargs["rich_value"])
        return fake_obj.get_eligibility_display() or "N/A"

    def get_column_Last_Activity_data(self, obj, **kwargs):
        """Provide the last activity
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        return obj.last_update.strftime("%m/%d/%y")

    def get_column_Annotation_data(self, obj, **kwargs):
        """Provide the annotation data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        annotation_strings = []
        blockquotes = []
        parts = []
        button = """<button class="btn btn-default btn-xs" type="button" data-toggle="popover"
        data-trigger="click" data-title="Annotations" data-html="true" data-placement="left"
        data-content="{}">Read All</button>"""
        blockquote = """
            <blockquote>
                <small>{date} - {first}. {last}</small>
                <p>{content}</p>
            </blockquote>
        """
        annotation_string = "[{first}. {last}][{date}] {content}"

        tz = self.request.user.timezone_preference

        for annotation in obj.annotations.all():
            first = annotation.user.first_name
            last = annotation.user.last_name
            last_update = annotation.last_update.astimezone(tz)
            content = annotation.content
            if not annotation.id:
                continue
            else:
                if first and last:
                    part = {
                        "date_object": last_update,
                        "date": last_update.strftime("%m/%d/%y"),
                        "first": first[0],
                        "last": last,
                        "content": content,
                    }
                    parts.append(part)
        parts = sorted(parts, key=itemgetter("date_object"), reverse=True)
        for part in parts:
            blockquotes.append(format_html(blockquote, **part))
            annotation_strings.append(format_html(annotation_string, **part))
        if len(blockquotes) > 1:
            return "{} {}".format(
                truncatewords_html(annotation_strings[0], 12), button.format("".join(blockquotes))
            )
        if annotation_strings:
            return annotation_strings[0]
        return "-"

    def get_query_form_choices(self):
        if not hasattr(self, "_id_list") or not hasattr(self, "_eep_program_choices"):
            self.get_queryset()
        builders = IncentivePaymentStatus.objects.choice_builder_items_for_user(
            user=self.request.user, id__in=self._id_list
        )
        subdivisions = IncentivePaymentStatus.objects.choice_subdivision_items_for_user(
            user=self.request.user, id__in=self._id_list
        )
        providers = IncentivePaymentStatus.objects.choice_provider_items_for_user(
            user=self.request.user, id__in=self._id_list
        )
        eep_programs = sorted(list(set(self._eep_program_choices)), key=itemgetter(1))

        return builders, subdivisions, providers, eep_programs

    def get_context_data(self, **kwargs):
        """Get the context data"""
        context = super(IncentivePaymentPendingList, self).get_context_data(**kwargs)

        # Sets up the form.
        context["query_form"] = IncentivePaymentStatusForm()

        builders, subdivisions, providers, eep_programs = self.get_query_form_choices()

        context["query_form"].fields["builder"].choices = [("", "---------")] + builders
        context["query_form"].fields["subdivision"].choices = [("", "---------")] + subdivisions
        context["query_form"].fields["eep_program"].choices = [("", "---------")] + eep_programs
        context["query_form"].fields["provider"].choices = [("", "---------")] + providers
        context["query_form"].fields["state"].initial = "pending"
        context["query_form"].fields["activity_start"].widget.attrs["size"] = 9
        context["query_form"].fields["activity_stop"].widget.attrs["size"] = 9
        return context


class IncentivePaymentPendingAnnotationList(
    IncentivePaymentPendingList, IncentivePaymentPendingAnnotationMixin, BaseFormView
):
    form_class = IncentivePaymentStatusAnnotationForm
    permission_required = "incentive_payment.change_incentivepaymentstatus"

    def get_datatable_options(self):
        options = super(IncentivePaymentPendingAnnotationList, self).get_datatable_options()
        options = options.copy()  # Not strictly necessary in this situation, but good for clarity
        options["columns"] = options["columns"][:]
        options["columns"].insert(0, ("select", None, "get_column_select_data"))

        if self.request.company.slug in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS:
            for i, column_info in enumerate(options["columns"][:]):
                if column_info[0] == "Annotation":
                    options["columns"][i:i] = [
                        (
                            "Builder Incentive",
                            "home_status__standardprotocolcalculator__builder_incentive",
                        ),
                        (
                            "Pct Improvement",
                            "home_status__standardprotocolcalculator__percent_improvement",
                        ),
                    ]
                    break

        return options

    def get_column_select_data(self, obj, *args, **kwargs):
        """Remove all traces of builder agreement"""
        return "<input data-id='{}' data-builder-agreement-id='{}' type='checkbox'>".format(
            obj.id, "none"
        )

    def get_column_Builder_Incentive_data(self, obj, **kwargs):
        """Provide the certification data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        calculator = obj.home_status.standardprotocolcalculator_set.first()
        if calculator and calculator.builder_incentive:
            return "${:.02f}".format(calculator.builder_incentive)

    def get_column_Pct_Improvement_data(self, obj, **kwargs):
        """Provide the certification data
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        calculator = obj.home_status.standardprotocolcalculator_set.first()
        if calculator and calculator.percent_improvement:
            return "{:.2f} %".format(100 * calculator.percent_improvement)

    def get_context_data(self, **kwargs):
        if not kwargs.get("object_list"):
            datatable = self.get_datatable()
            datatable.populate_records()
            kwargs["object_list"] = datatable._records
        self.object_list = kwargs["object_list"]
        context = super(IncentivePaymentPendingAnnotationList, self).get_context_data(**kwargs)
        initial = self.kwargs.get("state") if self.kwargs.get("state") else "start"
        context["query_form"].fields["state"].initial = initial
        context["form"] = self.get_form(self.form_class)
        context["form"].action = reverse("incentive_payment:pending")
        context["title"] = "Received"

        if self.request.user.company.slug in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS:
            context["only_approve"] = True
        return context


class IncentivePaymentRejectedAnnotationList(IncentivePaymentPendingAnnotationList):
    permission_required = "home.add_home"

    datatable_options = {
        "columns": [
            (
                "Address",
                [
                    "home_status__home__lot_number",
                    "home_status__home__street_line1",
                    "home_status__home__street_line2",
                ],
            ),
            ("Program", "home_status__eep_program__name"),
            ("REM/Rate", None, "get_column_Simulation_data"),
            ("Annotation", "annotation__value"),
            ("Last Activity", "last_update", "get_column_Last_Activity_data"),
            ("Builder", "relationships__company__name", "get_column_Builder_data"),
            ("Provider", "home_status__company__name", "get_column_provider_data"),
        ],
        "ordering": ["-last_update", "home_status__certification_date"],
    }
    prefetch_related = [
        "annotations__user",
        "home_status__home__relationships",
        "home_status__home__subdivision__builderagreement_set",
        "home_status__home__subdivision__floorplanapproval_set",
    ]

    def get_queryset(self):
        """Get the list of items for this view."""
        queryset = IncentivePaymentStatus.objects.filter_by_user(
            self.request.user, state="ipp_payment_failed_requirements"
        )
        self._id_list = list(queryset.values_list("id", flat=True))
        self._eep_program_choices = queryset.values_list(
            "home_status__eep_program_id", "home_status__eep_program__name"
        )
        return self.get_external_qs_filters(queryset)

    def get_context_data(self, **kwargs):
        context = super(IncentivePaymentRejectedAnnotationList, self).get_context_data(**kwargs)
        context["title"] = "Rejected"
        context["query_form"].fields["state"].initial = "ipp_payment_failed_requirements"
        context["form"].action = reverse("incentive_payment:failures")
        return context

    def get_success_url(self):
        return reverse("incentive_payment:failures")

    def get_form(self, form_class=None):
        """Get a form"""
        form = super(IncentivePaymentRejectedAnnotationList, self).get_form(form_class)
        form.fields["new_state"].choices = [("", "---------"), ("resubmit-failed", "Re-Submit")]
        return form

    def get_column_Address_data(self, obj, **kwargs):
        """Provide the home address
        :param obj: axis.incentive_payment.models.IncentivePaymentStatus"""
        home = obj.home_status.home

        text = home.get_home_address_display(include_confirmed=True, company=self.request.company)

        # company_name = self.historical_home[obj.home_status.home.id]
        company_name = home.history.values_list("history_user__company__name", flat=True).last()
        if not company_name:
            company_name = "Administrator"

        builder = obj.home_status.home.get_builder()
        tooltip = "{} - {}".format(company_name, builder)

        url = "<a href='{url}' target='_blank' data-toggle='tooltip' data-original-title='Created by: {tooltip}'>{text}</a>"
        if self.request.user.company.id == obj.home_status.company.id:
            _url = reverse("home:view", kwargs={"pk": home.id})
            url += (
                "&nbsp;<a href='{edit}' target='_blank'><i class='fa "
                "fa-pencil-square-o'></i></a>".format(edit=_url)
            )
        return url.format(url=home.get_absolute_url(), tooltip=tooltip, text=text)


class IncentiveDistributionCreateView(
    IncentivePaymentPendingList, IncentiveDistributionCreateMixin, BaseFormView
):
    permission_required = "incentive_payment.add_incentivedistribution"
    template_name = "incentive_payment/incentivedistribution_form.html"
    form_class = IncentiveDistributionForm

    def get_queryset(self):
        """Get the list of items for this view."""
        queryset = super(IncentiveDistributionCreateView, self).get_queryset()
        queryset = queryset.filter(
            state__in=[
                "ipp_payment_automatic_requirements",
            ]
        )
        return self.get_external_qs_filters(queryset)

    def get_context_data(self, **kwargs):
        if not kwargs.get("object_list"):
            datatable = self.get_datatable()
            datatable.populate_records()
            kwargs["object_list"] = datatable._records
        self.object_list = kwargs["object_list"]
        context = super(IncentiveDistributionCreateView, self).get_context_data(**kwargs)
        context["form"] = self.get_form(self.form_class)
        context["title"] = "Approved for Payment"
        return context


class IncentiveDistributionIPPItems(LoginRequiredMixin, LegacyAxisDatatableView):
    """This is used for the detail / update views of a specific distribution"""

    datatable_options = {
        "columns": [
            (
                "Address",
                [
                    "home_status__home__lot_number",
                    "home_status__home__street_line1",
                    "home_status__home__street_line2",
                ],
            ),
            ("Subdivision", "home_status__home__subdivision__name"),
            ("EEP", "home_status__eep_program__name", datatableview.helpers.link_to_model),
            ("Cost", "cost", datatableview.helpers.format("${:,.2f}", cast=float)),
        ],
    }

    def get_queryset(self):
        if not self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return IPPItem.objects.none()
        return IPPItem.objects.filter(incentive_distribution__pk=self.kwargs.get("pk"))

    def get_column_Address_data(self, obj, *args, **kwargs):
        return datatableview.helpers.link_to_model(obj.home_status.home, text=obj.home_status.home)

    def get_column_Subdivision_data(self, obj, *args, **kwargs):
        if obj.home_status.home.subdivision:
            return datatableview.helpers.link_to_model(
                obj.home_status.home.subdivision, text=kwargs["default_value"]
            )
        return "Custom Home"


class IncentiveDistributionUpdateView(AuthenticationMixin, UpdateView):
    """List Out the invoices via Ajax"""

    permission_required = "incentive_payment.add_incentivedistribution"
    template_name = "incentive_payment/incentivedistribution_update_form.html"
    form_class = IncentiveDistributionUpdateForm

    def get_queryset(self):
        """Get the list of items for this view."""
        return IncentiveDistribution.objects.filter_by_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(IncentiveDistributionUpdateView, self).get_context_data(**kwargs)
        context["update"] = True
        context["can_delete"] = self.object.can_be_deleted(self.request.user)
        context[
            "confirmation_message"
        ] = strings.INVENTIVE_DISTRIBUTION_CUSTOMER_CHANGED_CONFIRMATION

        view = IncentiveDistributionIPPItems()
        view.request = self.request
        datatable = view.get_datatable()
        datatable.url = reverse("incentive_payment:ipp_items", kwargs={"pk": self.object.id})
        context["datatable"] = datatable
        return context

    def get_form(self, form_class=None):
        """Get the form"""
        form = super(IncentiveDistributionUpdateView, self).get_form(form_class)

        c_qs = Company.objects.filter_by_user(self.request.user)
        form.fields["customer"].queryset = c_qs
        form.fields["customer"].required = True
        form.fields["customer"].initial = self.object.customer.id

        form.fields["check_number"].widget.attrs["size"] = 9

        if self.object.paid_date:
            form.fields["check_requested_date"].editable = False
            form.fields["check_requested_date"].widget = HiddenInput()
            if not self.object.parent_incentive_distributions.count():
                form.fields["comment"].required = True
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.request.user.company
        self.object.check_to_name = self.object.customer.name
        if self.object.check_requested_date:
            self.object.check_requested = True
            self.object.status = 1
        if self.object.paid_date:
            self.object.is_paid = True
            self.object.status = 2
            ipp_stat_ids = self.object.ippitem_set.values_list("home_status", flat=True)
            ipp_stats = IncentivePaymentStatus.objects.filter(home_status_id__in=ipp_stat_ids)
            for ipp_stat in ipp_stats.all():
                if ipp_stat.state != "complete":
                    ipp_stat.make_transition("pending_complete", user=self.request.user)
        self.object.save()
        for ipp in self.object.rater_incentives.all():
            ipp.check_requested = self.object.check_requested
            ipp.check_requested_date = self.object.check_requested_date
            ipp.save()
        return HttpResponseRedirect(self.get_success_url())


# ========================= Delete View =================================


class IncentiveDistributionDeleteView(AuthenticationMixin, AxisDeleteView):
    """List Out the invoices via Ajax"""

    permission_required = "incentive_payment.delete_incentivedistribution"
    success_url = reverse_lazy("incentive_payment:list")

    def has_permission(self):
        return self.get_object().can_be_deleted(self.request.user)

    def get_queryset(self):
        """Narrow this based on your company"""
        return IncentiveDistribution.objects.filter_by_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(IncentiveDistributionDeleteView, self).get_context_data(**kwargs)

        ids = [self.object.id] + list(
            self.object.rater_incentives.all().values_list("id", flat=True)
        )
        objects = IncentiveDistribution.objects.filter(id__in=ids)
        context["deleted_objects"] = collect_nested_object_list(objects)
        return context

    def post(self, *args, **kwargs):
        ipp = self.get_object()
        stat_ids = ipp.ippitem_set.all()
        stat_ids = list(stat_ids.values_list("home_status", flat=True))

        for rater_incentive in ipp.rater_incentives.all():
            rater_incentive.delete()

        ret_value = self.delete(*args, **kwargs)

        for ipp_stat in IncentivePaymentStatus.objects.filter(home_status__in=stat_ids):
            ipp_stat.make_transition("distribution_delete_reset", user=self.request.user)

        return ret_value


class IncentiveDistributionDetailPrintView(IncentiveDistributionDetailView):
    def get_template_names(self):
        slug = self.request.user.company.slug
        return [
            os.path.join("incentive_payment", "print_{}_invoice.htm").format(slug),
        ]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        with tempfile.NamedTemporaryFile() as filename:
            check_request = CheckRequest(filename=filename)
            check_request.build(invoice=self.object)

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename={}.pdf".format(
                self.object.invoice_number[:8]
            )
            response.write(filename.read())
        return response


class IPPItemDistributionListDetailPrintView(AuthenticationMixin, TemplateView):
    """List the Detail View"""

    permission_required = "incentive_payment.view_incentivedistribution"

    def get_queryset(self):
        """Narrow this based on your company"""
        return IPPItem.objects.filter(incentive_distribution__pk=self.kwargs.get("pk"))

    def get_template_names(self):
        slug = self.request.user.company.slug
        return [os.path.join("incentive_payment", "print_{}_detail.html").format(slug)]

    def get_context_data(self, **kwargs):
        context = super(IPPItemDistributionListDetailPrintView, self).get_context_data(**kwargs)

        subdivisions = {}
        for item in self.get_queryset():
            context["incentive_distribution"] = item.incentive_distribution
            subdivision = "Custom Home"
            if item.home_status.home.subdivision:
                subdivision = item.home_status.home.subdivision
            if subdivision not in subdivisions:
                subdivisions[subdivision] = {
                    "homes": [],
                    "totals": {"paid": 0, "total": 0, "remaining": 0},
                }
            subdivisions[subdivision]["homes"].append(item)

        ipp = IncentiveDistribution.objects.get(id=self.kwargs.get("pk"))
        for subdivision, data in subdivisions.items():
            try:
                builder_agreement = BuilderAgreement.objects.get(subdivision=subdivision)
                data["totals"]["paid"] = builder_agreement.lots_paid
            except ValueError:
                try:
                    builder_agreement = BuilderAgreement.objects.get(
                        builder_org=ipp.customer, subdivision__isnull=True
                    )
                    data["totals"]["paid"] = builder_agreement.lots_paid
                except BuilderAgreement.DoesNotExist:
                    data["totals"]["no_builder_agreement"] = True
            except BuilderAgreement.DoesNotExist:
                data["totals"]["no_builder_agreement"] = True

        context["subdivisions"] = subdivisions
        return context

    def get(self, request, *args, **kwargs):
        self.object = IncentiveDistribution.objects.get(pk=self.kwargs.get("pk"))
        context = self.get_context_data(object=self.object)
        filename = tempfile.NamedTemporaryFile(delete=False)

        title = "Check Detail<br />"
        if self.request.user.company.name == "APS":
            title = "APS ENERGY STAR Homes Program - Check Detail<br />"
        check_request = CheckDetail(filename=filename)
        check_request.build(
            invoice=self.object,
            data=context["subdivisions"],
            company=self.request.user.company,
            title=title,
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename={}.pdf".format(
            self.object.invoice_number[:8]
        )
        filename.close()
        with io.open(filename.name, "rb") as f:
            response.write(f.read())
        os.unlink(filename.name)
        return response


# class IncentiveDistributionReport(FormView):
#     form_class = IncentiveDistributionReportForm
#     template_name = "incentive_payment/incentivedistribution_report.html"
#
#     @method_decorator(login_required)
#     @method_decorator(permission_required_with_403('incentive_payment.view_incentivedistribution'))
#     def dispatch(self, *args, **kwargs):
#         """Ensure we have access"""
#         return super(IncentiveDistributionReport, self).dispatch(*args, **kwargs)
#
#     def get_form(self, form_class):
#         """Get the form"""
#         form = super(IncentiveDistributionReport,self).get_form(form_class)
#         company = self.request.user.company
#         form.fields['eep_program'].queryset = EEPProgram.objects.filter_by_company(company=company)
#         form.fields['start_date'].widget.attrs['size'] = 9
#         form.fields['end_date'].widget.attrs['size'] = 9
#         return form


# ========================= AJAX Goodness =================================


class ControlCenterView(IncentivePaymentPendingList):
    template_name = "incentive_payment/control_center/control_center.html"
    show_add_button = False

    def get_datatable_options(self):
        options = super(ControlCenterView, self).get_datatable_options()
        options = options.copy()  # Not strictly necessary in this situation, but good for clarity
        options["columns"] = options["columns"][:]
        options["columns"].insert(0, ("select", None, "get_column_select_data"))
        return options

    def get_column_select_data(self, obj, *args, **kwargs):
        return "<input data-id='{}' type='checkbox'>".format(obj.id)

    def get_context_data(self, **kwargs):
        context = super(ControlCenterView, self).get_context_data(**kwargs)
        context["query_form"].fields["state"].initial = "start"

        builder_dict = {}
        for id, total, paid in BuilderAgreement.objects.filter_by_user(
            self.request.user
        ).values_list("id", "total_lots", "lots_paid"):
            try:
                builder_dict[int(id)] = int(total - paid)
            except TypeError:
                builder_dict[int(id)] = 1e9  # We didn't define one so we can't exceed it.

        show_received_approved_tables = IncentivePaymentStatus.objects.filter(
            home_status__eep_program__owner=self.request.user.company
        ).exists()

        # Get counts
        counts = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        pending_count = counts.filter(state="start").count()
        corrections_received = counts.filter(state="ipp_failed_restart").count()
        corrections_required = counts.filter(state="ipp_payment_failed_requirements").count()
        approved_count = counts.filter(state="ipp_payment_automatic_requirements").count()

        # Set counts
        if show_received_approved_tables:
            context["total_count"] = (
                pending_count + corrections_received + corrections_required + approved_count
            )
        else:
            context["total_count"] = corrections_required
        context["pending_count"] = pending_count
        context["corrections_received"] = corrections_received
        context["corrections_required"] = corrections_required
        context["approved_count"] = approved_count

        # set other context variables
        context["builder_dict"] = builder_dict
        context["show_received_approved_tables"] = show_received_approved_tables
        # context['rejected_count'] = counts.filter(state='ipp_payment_failed_requirements').count()
        # context['incentives_count'] = IncentiveDistribution.objects.filter_by_user(
        #     user=self.request.user).count()
        return context


class AjaxPendingForm(LoginRequiredMixin, IncentivePaymentPendingAnnotationMixin, FormView):
    template_name = "incentive_payment/control_center/pending_form.html"
    form_class = IncentivePaymentStatusAnnotationForm

    def get_form(self, form_class=None):
        return super(AjaxPendingForm, self).get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super(AjaxPendingForm, self).get_context_data(**kwargs)
        context["form"].action = reverse("incentive_payment:pending_form")
        return context


class AjaxNewForm(LoginRequiredMixin, IncentiveDistributionCreateMixin, FormView):
    template_name = "incentive_payment/control_center/new_form.html"
    form_class = IncentiveDistributionForm

    def get_form(self, form_class=None):
        return super(AjaxNewForm, self).get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super(AjaxNewForm, self).get_context_data(**kwargs)
        context["form"].action = reverse("incentive_payment:new_form")
        return context


class IncentivePaymentPendingDatatable(IncentivePaymentPendingAnnotationList):
    def get(self, request, *args, **kwargs):
        if request.GET.get("skeleton") == "true" and request.GET["skeleton"] == "true":
            datatable = self.get_datatable()
            if request.GET.get("table") == "pending":
                datatable.options["result_counter_id"] = "pending_count"
            if request.GET.get("table") == "review":
                datatable.options["result_counter_id"] = "corrections_count"
            if request.GET.get("table") == "new":
                datatable.options["result_counter_id"] = "approved_count"
            return HttpResponse("{}".format(datatable))
        return super(IncentivePaymentPendingDatatable, self).get(request, *args, **kwargs)


class IncentivePaymentRejectedDatatable(IncentivePaymentRejectedAnnotationList):
    def get(self, request, *args, **kwargs):
        if request.GET.get("skeleton") == "true" and request.GET["skeleton"] == "true":
            datatable = self.get_datatable()
            datatable._meta["result_counter_id"] = "rejected_count"
            return HttpResponse("{}".format(datatable))
        return super(IncentivePaymentRejectedDatatable, self).get(request, *args, **kwargs)


class IncentiveDistributionDatatable(IncentiveDistributionListView):
    def get(self, request, *args, **kwargs):
        if request.GET.get("skeleton") == "true" and request.GET["skeleton"] == "true":
            datatable = self.get_datatable()
            datatable._meta["result_counter_id"] = "incentive_distribution_count"
            return HttpResponse("{}".format(datatable))
        return super(IncentiveDistributionDatatable, self).get(request, *args, **kwargs)
