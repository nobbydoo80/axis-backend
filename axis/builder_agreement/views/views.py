"""views.py: Django builder_agreement"""


import datetime
import logging
from collections import defaultdict

import dateutil.parser
from django import forms
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from axis.builder_agreement import datatables
from axis.builder_agreement.forms import (
    BuilderAgreementStatusForm,
    BuilderAgreementCreateForm,
    BuilderAgreementUpdateForm,
    BuilderSubdivisionReportForm,
)
from axis.builder_agreement.models import BuilderAgreement
from axis.community.models import Community
from axis.company.models import Company
from axis.company.strings import COMPANY_TYPES
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    AxisExamineView,
    AxisCreateView,
    AxisUpdateView,
    AxisDeleteView,
    AxisDatatableView,
)
from axis.eep_program.models import EEPProgram
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.subdivision.models import Subdivision

__author__ = "Steven Klass"
__date__ = "3/2/12 1:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementMixin(AuthenticationMixin):
    """Calls ``filter_by_user`` on the model's default manager."""

    model = BuilderAgreement

    def get_queryset(self):
        return BuilderAgreement.objects.filter_by_user(user=self.request.user)


class BuilderAgreementListView(BuilderAgreementMixin, AxisDatatableView):
    permission_required = "builder_agreement.view_builderagreement"
    datatable_class = datatables.BuilderAgreementListDatatable

    def get_datatable_kwargs(self, **kwargs):
        data = super(BuilderAgreementListView, self).get_datatable_kwargs(**kwargs)
        data["company"] = self.request.company
        return data

    def get_queryset(self):
        """Limits objects to the user."""
        queryset = super(BuilderAgreementListView, self).get_queryset()
        queryset = queryset.select_related("company", "builder_org", "subdivision__community")
        return queryset


class BuilderAgreementDetailView(BuilderAgreementMixin, AxisExamineView):
    """Detail view of the Builder Agreement"""

    permission_required = "builder_agreement.view_builderagreement"
    template_name = "builder_agreement/builderagreement_examine.html"
    show_edit_button = True
    show_delete_button = True

    def get_machinery(self):
        machineries = {}

        builder_agreement = self.object
        kwargs = {}

        # Documents
        documents = []
        if not self.create_new:
            documents = builder_agreement.customer_documents.filter_by_user(
                self.request.user, include_public=True
            )
        machinery_class = customerdocument_machinery_factory(self.model)
        machinery = machinery_class(objects=documents, **kwargs)
        machineries["documents"] = machinery

        return machineries

    def get_context_data(self, **kwargs):
        """Adds ``can_delete`` and ``shared_documents`` to the context."""
        context = super(BuilderAgreementDetailView, self).get_context_data(**kwargs)
        company_type = self.request.user.company.company_type
        return context


class BuilderAgreementCreateView(BuilderAgreementMixin, AxisCreateView):
    """Create an EEP Builder Agreement."""

    permission_required = "builder_agreement.add_builderagreement"
    form_class = BuilderAgreementCreateForm

    def get_form(self, form_class=None):
        """Modifies the field attributes of the form."""
        form = super(BuilderAgreementCreateView, self).get_form(form_class)

        form.fields["company"].initial = self.request.user.company.id
        form.fields["company"].widget = forms.HiddenInput()

        builder_qs = Company.objects.filter_by_company(company=self.request.user.company)
        form.fields["builder_org"].queryset = builder_qs.filter(company_type="builder")

        subs_qs = Subdivision.objects.filter_by_company(
            company=self.request.user.company, show_attached=True
        )
        form.fields["subdivision"].queryset = subs_qs

        eep_progs_qs = EEPProgram.objects.filter(
            Q(
                Q(program_close_date__isnull=True)
                | Q(program_close_date__gte=datetime.datetime.today())
            ),
            owner=self.request.user.company,
        )

        form.fields["eep_programs"].queryset = eep_progs_qs.order_by("-name")

        return form

    def get_context_data(self, **kwargs):
        """Populates the ``action`` context variable as "Add"."""
        context = super(BuilderAgreementCreateView, self).get_context_data(**kwargs)
        context["action"] = "Add"
        return context


class BuilderAgreementUpdateView(BuilderAgreementMixin, AxisUpdateView):
    permission_required = "builder_agreement.change_builderagreement"
    form_class = BuilderAgreementUpdateForm

    def has_permission(self):
        return self.get_object().can_be_edited(self.request.user)

    def get_form(self, form_class=None):
        """Modifies the form field attributes."""
        form = super(BuilderAgreementUpdateView, self).get_form(form_class)

        current_pks = self.get_object().eep_programs.all().values_list("pk", flat=True)
        eep_progs_qs = EEPProgram.objects.filter(
            Q(pk__in=current_pks)
            | Q(
                Q(program_close_date__isnull=True)
                | Q(program_close_date__gte=datetime.datetime.today())
            ),
            owner=self.request.user.company,
        )

        form.fields["eep_programs"].queryset = eep_progs_qs.order_by("-name")
        return form

    def get_context_data(self, **kwargs):
        """Populates the ``update`` context variable as True"""
        context = super(BuilderAgreementUpdateView, self).get_context_data(**kwargs)
        context["update"] = True
        return context


class BuilderAgreementDeleteView(BuilderAgreementMixin, AxisDeleteView):
    permission_required = "builder_agreement.delete_builderagreement"
    success_url = reverse_lazy("builder_agreement:list")

    def has_permission(self):
        return self.get_object().can_be_deleted(self.request.user)

    def get_queryset(self):
        """Limit objects to the user."""
        return BuilderAgreement.objects.filter_by_user(user=self.request.user)


class BuilderAgreementMixin(object):
    def _get_datetime_from_string(self, date_string):
        if isinstance(date_string, (datetime.datetime, datetime.date)):
            return date_string
        elif isinstance(date_string, type(None)):
            return date_string
        if not len(date_string):
            return None
        try:
            return dateutil.parser.parse(date_string)
        except:
            log.error("Unable to parse %s", date_string)

    def apply_filters(self, queryset, user, kwargs):
        applied_filters = {}
        if kwargs.get("subdivision_id"):
            obj = kwargs.get("subdivision_id")
            obj_q = obj if isinstance(obj, list) else [obj]
            log.info("Filtering on Subdivision={}".format(obj_q))
            applied_filters["subdivision_id__in"] = obj_q
        if kwargs.get("builder_id"):
            obj = kwargs.get("builder_id")
            obj_q = obj if isinstance(obj, list) else [obj]
            log.info("Filtering on Builder={}".format(obj_q))
            applied_filters["builder_org_id__in"] = obj_q
        if kwargs.get("community_id"):
            obj = kwargs.get("community_id")
            obj_q = obj if isinstance(obj, list) else [obj]
            log.info("Filtering on Community={}".format(obj_q))
            applied_filters["subdivision__community_id__in"] = obj_q
        if kwargs.get("city_id"):
            obj = kwargs.get("city_id")
            obj_q = obj if isinstance(obj, list) else [obj]
            log.info("Filtering on City={}".format(obj_q))
            applied_filters["subdivision__city_id__in"] = obj_q

        object_ids = []
        if kwargs.get("rater_id") or kwargs.get("provider_id"):
            company_ids = []
            if kwargs.get("rater_id"):
                obj = kwargs.get("rater_id")
                obj_q = obj if isinstance(obj, list) else [obj]
                log.info("Filtering on Rater={}".format(obj_q))
                company_ids += obj_q
            if kwargs.get("provider_id"):
                obj = kwargs.get("provider_id")
                obj_q = obj if isinstance(obj, list) else [obj]
                log.info("Filtering on Provider={}".format(obj_q))
                company_ids += obj_q
            log.info("Filtering on Company={}".format(company_ids))
            companies = Company.objects.filter(id__in=company_ids)

            for company in companies:
                object_ids += list(
                    BuilderAgreement.objects.filter_by_company(company).values_list("id", flat=True)
                )

        if kwargs.get("hers_min") or kwargs.get("hers_max"):
            log.info(
                "Filtering on HERs Min={} HERs Max={}".format(
                    kwargs.get("hers_min"), kwargs.get("hers_max")
                )
            )
            obj_ids = BuilderAgreement.objects.filter_by_hers_score_for_user(
                user, kwargs.get("hers_min"), kwargs.get("hers_max")
            )
            obj_ids = list(obj_ids.values_list("id", flat=True))
            if not len(object_ids):
                object_ids = obj_ids
            else:
                object_ids = list(set(object_ids).intersection(set(obj_ids)))

        if len(object_ids):
            applied_filters["id__in"] = object_ids

        if kwargs.get("start_date"):
            start = self._get_datetime_from_string(kwargs.get("start_date"))
            log.info("Filtering on Start={}".format(start))
            applied_filters["start_date__gte"] = start

        if kwargs.get("end_date"):
            end = self._get_datetime_from_string(kwargs.get("end_date"))
            log.info("Filtering on Start={}".format(end))
            applied_filters["start_date__lte"] = end

        return queryset.filter(**applied_filters)

    def set_form_fields(self, form, user):
        _base = BuilderAgreement.objects.filter_by_user(user).select_related(
            "builder_org", "subdivision__commmunity", "subdivision__city"
        )

        choices = defaultdict(list)
        [
            choices[k].append(v)
            for k, v in Company.objects.filter_by_user(user).values_list("company_type", "id")
        ]
        for co_type in dict(COMPANY_TYPES).keys():
            _choices = choices.get(co_type, [])
            if co_type == "builder":
                _choices = _base.values_list("builder_org_id", flat=True)
            form.fields[co_type].queryset = Company.objects.filter(id__in=_choices)

        _choices = _base.values_list("subdivision_id", flat=True)
        _s_choices = Subdivision.objects.choice_items_from_instances(user=user, id__in=_choices)
        form.fields["subdivision"].choices = [("", "---------")] + _s_choices

        _choices = _base.values_list("subdivision__community_id", flat=True)
        _c_choices = Community.objects.choice_items_from_instances(user=user, id__in=_choices)
        form.fields["community"].choices = [("", "---------")] + _c_choices

        from axis.geographic.models import City

        _choices = _base.values_list("subdivision__city_id", flat=True)
        _city_choices = City.objects.choice_items_from_instances(user=user, id__in=_choices)
        form.fields["city"].choices = [("", "---------")] + _city_choices

        return form


class BuilderAgreementStatusListView(AuthenticationMixin, AxisDatatableView, BuilderAgreementMixin):
    model = BuilderAgreement

    permission_required = "builder_agreement.view_builderagreement"
    template_name = "builder_agreement/builder_agreement_status_list.html"
    datatable_class = datatables.BuilderAgreementStatusListDatatable

    select_related = [
        "subdivision",
        "subdivision__city",
        "subdivision__community",
    ]

    def get_queryset(self):
        """Apply filters requested by UI."""
        queryset = self.model.objects.filter_by_user(self.request.user).select_related(
            "subdivision__community"
        )
        kwargs = self.prevision_kwargs(**self.request.GET)
        return self.apply_filters(queryset, self.request.user, kwargs)

    def get_context_data(self, **kwargs):
        context = super(BuilderAgreementStatusListView, self).get_context_data(**kwargs)
        context["form"] = self.set_form_fields(BuilderAgreementStatusForm(), self.request.user)
        return context


class AsynchronousProcessedDocumentCreateBuilderSudivisionReport(
    AuthenticationMixin, AxisCreateView, BuilderAgreementMixin
):
    permission_required = "builder_agreement.view_builderagreement"
    model = AsynchronousProcessedDocument
    form_class = BuilderSubdivisionReportForm
    template_name = "filehandling/asynchronousprocesseddocument_form.html"

    show_cancel_button = False

    def get_context_data(self, **kwargs):
        """Add in any context data"""
        context = super(
            AsynchronousProcessedDocumentCreateBuilderSudivisionReport, self
        ).get_context_data(**kwargs)
        context["title"] = "Builder Information Report"
        return context

    def get_form(self, form_class=None):
        form = super(AsynchronousProcessedDocumentCreateBuilderSudivisionReport, self).get_form(
            form_class
        )
        form.fields["company"].initial = self.request.company
        form.fields["company"].queryset = Company.objects.filter(id=self.request.company.id)
        return self.set_form_fields(form, self.request.user)

    def form_valid(self, form):
        """Send this off for processing"""
        context = self.get_context_data()
        self.object = form.save(commit=False)
        self.object.download = True
        self.object.company = self.request.user.company
        self.object.save()
        task = form.cleaned_data["task_name"]
        log.info(task)

        kwargs = {"user_id": self.request.user.id, "result_object_id": self.object.id}
        for key, value in form.cleaned_data.items():
            if key in ["task", "task_name"]:
                continue
            if value:
                try:
                    kwargs["{}_id".format(key)] = int(value.id)
                except AttributeError:
                    try:
                        kwargs["{}_id".format(key)] = ",".join(
                            map(lambda x: str(x), value.values_list("id", flat=True))
                        )
                    except AttributeError:
                        if isinstance(value, datetime.date):
                            value = value.strftime("%m-%d-%Y")
                        kwargs[key] = value
        task_obj = task.apply_async(kwargs=kwargs, countdown=3)
        self.object.task_id = task_obj.task_id
        self.object.save()
        log.info("Assigning task %s id %s and kwargs %s", task, self.object.task_id, kwargs)
        return HttpResponseRedirect(self.get_success_url())
