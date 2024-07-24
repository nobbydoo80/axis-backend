"""views.py: Django core views"""

__author__ = "Steven Klass"
__date__ = "2011/08/04 15:21:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

import datetime
import hashlib
import inspect
import json
import logging
import operator
import os
import re
from functools import reduce

import datatableview.helpers
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models import Q, Value
from django.db.models.functions import ExtractYear, Concat
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone, formats
from django.utils.timezone import now
from django.views.generic import TemplateView, FormView, UpdateView, RedirectView
from django_select2.views import AutoResponseView
from simulation.enumerations import SourceType, SimulationStatus
from simulation.models import Simulation
from tensor_registration.forms import TensorAuthenticationForm

from axis.community.models import Community
from axis.company.models import Company
from axis.core.messages import TensorCompanyAdminUserApprovalMessage
from axis.core.models import AxisFlatPage
from axis.core.views.generic import AxisExamineView
from axis.customer_hirl.models import HIRLUserProfile, HIRLProject
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.floorplan.models import Floorplan
from axis.home.models import Home, EEPProgramHomeStatus
from axis.invoicing.models import Invoice
from axis.sampleset.models import SampleSet
from axis.subdivision.models import Subdivision
from .generic import LegacyAxisDatatableView
from .machineries import (
    UserExamineMachinery,
    UserTrainingExamineMachinery,
    UserAccreditationExamineMachinery,
    UserCertificationMetricExamineMachinery,
    UserInspectionGradeExamineMachinery,
    HIRLUserProfileExamineMachinery,
)
from axis.core.fields import AxisJSONEncoder
from axis.core.forms import ContactForm, CustomTensorApproveUserForm
from axis.core.messages import TensorCompanyApprovalMessage, TensorUserApprovalMessage
from axis.core.mixins import AuthenticationMixin
from axis.core.simple_history_utils import get_revision_delta
from axis.company.strings import COMPANY_TYPES
from ...scheduling.models import Task
from ...scheduling.views import TaskUserMachinery

User = get_user_model()

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
user_management_app = apps.get_app_config("user_management")


class AjaxLoginView(FormView):
    """Logs a user in from an ajax call"""

    form_class = TensorAuthenticationForm
    http_method_names = ["post"]

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponse(json.dumps({"status": 1}), content_type="application/json")

    def form_invalid(self, form):
        return HttpResponseBadRequest(
            json.dumps({"status": 0, "errors": form.errors}), content_type="application/json"
        )


class ApproveTensorAccount(LoginRequiredMixin, UpdateView):
    template_name = "tensor_registration/admin/approve_tensor_user_form.html"
    form_class = CustomTensorApproveUserForm
    success_url = reverse_lazy("admin:core_user_changelist")
    success_url_for_company_admin = reverse_lazy("home")
    model = User

    def get_form_kwargs(self):
        kwargs = super(ApproveTensorAccount, self).get_form_kwargs()
        kwargs["user"] = self.object
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(
            self.request, messages.INFO, "{} successfully" " approved".format(self.object)
        )
        self.send_approve_notification()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_approved:
            messages.add_message(
                self.request, messages.INFO, "{} already approved".format(self.object)
            )
            return HttpResponseRedirect(self.success_url_for_company_admin)

        # In case that new user has a company approve him and
        # redirect to success_url_for_company_admin url
        if self.object.company:
            if (
                self.request.user.is_company_admin
                and self.request.user.company == self.object.company
            ) or self.request.user.is_superuser:
                self.object.is_approved = True
                self.object.save()
                self.send_approve_notification()
            return HttpResponseRedirect(self.success_url_for_company_admin)

        if not self.request.user.is_superuser:
            raise PermissionDenied()
        return super(ApproveTensorAccount, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied()
        return super(ApproveTensorAccount, self).post(request, *args, **kwargs)

    def get_email_context(self):
        """
        Build the template context used for the confirmation email.
        """
        scheme = "https" if self.request.is_secure() else "http"
        return {
            "scheme": scheme,
            "user": self.object,
            "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
            "site": get_current_site(self.request),
        }

    def send_approve_notification(self):
        """
        Send for approved user notification that he can successfully log in
        """
        axis_login_url = self.request.build_absolute_uri(reverse("auth:login"))
        TensorCompanyApprovalMessage().send(
            user=self.object,
            context={
                "user_fullname": f"{self.object.first_name} {self.object.last_name}",
                "user_email": self.object.email,
                "approval_user": self.object,
                "request": self.request,
                "axis_login_url": axis_login_url,
            },
        )
        if self.object.is_company_admin:
            # Let the other admins know
            users = User.objects.filter(
                Q(company=self.object.company, is_company_admin=True)
                | Q(company__slug="pivotal-energy-solutions", is_staff=True)
            ).exclude(id=self.request.user.id)
            if users.count():
                TensorCompanyAdminUserApprovalMessage().send(
                    users=users,
                    context={
                        "company_name": self.object.company,
                        "company_url": self.object.company.get_absolute_url(),
                        "user_fullname": f"{self.object.first_name} {self.object.last_name}",
                        "user_email": self.object.email,
                    },
                )
        else:
            # Let the other admins know
            users = User.objects.filter(company=self.object.company, is_company_admin=True).exclude(
                id=self.request.user.id
            )
            if users.count():
                TensorUserApprovalMessage().send(
                    users=users,
                    context={
                        "company_name": self.object.company,
                        "user_fullname": f"{self.object.first_name} {self.object.last_name}",
                        "user_email": self.object.email,
                    },
                )


class NewsListView(TemplateView):
    template_name = "core/news.html"

    def get_cached_flat_page_news_data(self, query_type="all", limit=25):
        """A cached version of a flat_page data"""
        if query_type not in ["all", "public", "product", "info"]:
            return []

        cache_key = hashlib.sha1("flat_pages__{}".format(query_type).encode("utf-8")).hexdigest()
        flat_pages = cache.get(cache_key, {})
        if flat_pages:
            return flat_pages[:limit]

        query = {"url__icontains": "-news/"}
        if query_type == "public":
            query = {"url__istartswith": "/public-news/"}
        elif query_type == "product":
            query = {"url": "/products/"}
        elif query_type == "info":
            query = {"url": "/info/"}
        flat_pages = AxisFlatPage.objects.filter(**query).order_by(
            "-created_at",
        )
        cache.set(cache_key, flat_pages, 300)
        return flat_pages[:limit]

    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context["form"] = context["q"] = None
        context["limit"] = 5
        if self.request.user.is_authenticated:
            context["news"] = self.get_cached_flat_page_news_data(query_type="all")
        else:
            context["news"] = self.get_cached_flat_page_news_data(query_type="public")
        return context


class ContactView(FormView):
    form_class = ContactForm
    template_name = "core/contact_form.html"

    def form_valid(self, form):
        form.send()
        messages.success(self.request, "Your message was sent successfully! Thank you.")
        return super(ContactView, self).form_valid(form)

    def get_success_url(self):
        return reverse("contact_success")


class ContactSuccessView(TemplateView):
    template_name = "core/contact_success.html"


class EnableBetaView(AuthenticationMixin, RedirectView):
    def has_permission(self):
        return self.request.user.is_superuser or self.request.user.is_impersonate

    def get_redirect_url(self, *args, **kwargs):
        pk = self.request.user.pk
        if self.request.user.is_impersonate:
            pk = self.request.impersonator.pk
        user = User.objects.get(pk=pk)
        user.show_beta = not user.show_beta
        user.save()
        return self.request.META.get("HTTP_REFERER", "/")


class ProfileListView(AuthenticationMixin, LegacyAxisDatatableView):
    model = User
    template_name = "profiles/profile_list.html"
    show_add_button = False

    is_public = False  # set in urlconf for public variant of the view

    datatable_options = {
        "columns": [
            ("Name", ["user__first_name, user__last_name"], datatableview.helpers.link_to_model),
            ("Role", ["title"]),
            ("Company", "company__name"),
            ("Phone Number", ["work_phone"]),
        ],
    }

    def has_permission(self):
        if self.request.user.is_superuser or self.is_public:
            return True
        return self.request.user.has_perm("core.view_user")

    def get_queryset(self):
        if self.is_public:
            return self.model.objects.filter_by_user(self.request.user).filter(is_public=True)
        return self.model.objects.filter_by_user(self.request.user)

    def get_column_Company_data(self, user, *args, **kwargs):
        if user.company:
            return datatableview.helpers.link_to_model(user.company, *args, **kwargs)
        return None


class UserExamineView(AuthenticationMixin, AxisExamineView):
    model = User
    queryset = model.objects.all().select_related("hes_credentials").select_related("hirlrateruser")
    template_name = "user/user_examine.html"
    show_edit_button = True

    def has_permission(self):
        user = self.get_object()
        return (
            self.request.user.is_superuser
            or self.request.user == user
            or self.request.company.id == user.company_id
            or self.request.user.company.has_mutual_relationship(user.company)
        )

    @property
    def accreditations(self):
        """
        Available accreditation queryset for user
        :return: Accreditation queryset
        """
        user = self.get_object()
        accreditations = user.accreditations.all()

        if self.request.user.is_superuser:
            return accreditations
        if user == self.request.user:
            return accreditations
        if user != self.request.user and (
            user.company == self.request.user.company and self.request.user.is_company_admin
        ):
            return accreditations

        if self.request.user.company.company_type == "qa":
            return accreditations

        accreditations = accreditations.filter(Q(approver__company=self.request.user.company))
        return accreditations

    @property
    def certification_metrics(self):
        """
        Available EEPProgramHomeStatus queryset for user
        :return: EEPProgramHomeStatus queryset
        """
        user = self.get_object()
        certification_metrics = EEPProgramHomeStatus.objects.filter(rater_of_record=user)
        if (
            not self.request.user.is_superuser
            and user != self.request.user
            and self.request.user.company.slug
            not in user_management_app.CERTIFICATION_METRIC_APPLICABLE_COMPANIES_SLUGS
        ):
            certification_metrics = certification_metrics.filter(
                eep_program__in=self.request.user.company.eepprogram_set.all(),
            )
        return certification_metrics

    @property
    def inspection_gradings(self):
        """
        Available inspection grading queryset for user
        :return: InspectionGrading queryset
        """
        user = self.get_object()
        inspection_gradings = user.inspectiongrade_set.all()
        if (
            not self.request.user.is_superuser
            and user != self.request.user
            and (user.company != self.request.user.company and user.is_company_admin)
        ):
            inspection_gradings = inspection_gradings.filter(
                Q(approver__company=self.request.user.company)
            )
        return inspection_gradings

    @property
    def training_years(self):
        """
        Years based on training queryset in reverse order.
        Always contains at least current year
        :return: list of integers
        """
        user = self.get_object()
        training_years = [
            timezone.now().year,
        ]
        training_years += (
            user.training_set.all()
            .annotate(year=ExtractYear("training_date"))
            .exclude(year=None)
            .distinct()
            .values_list("year", flat=True)
        )
        return sorted(set(training_years), reverse=True)

    @property
    def accreditation_years(self):
        """
        Years based on accreditation queryset in reverse order.
        Always contains at least current year
        :return: list of integers
        """
        accreditation_years = [
            timezone.now().year,
        ]
        accreditation_years += (
            self.accreditations.annotate(year=ExtractYear("date_last"))
            .exclude(year=None)
            .distinct()
            .values_list("year", flat=True)
        )
        return sorted(set(accreditation_years), reverse=True)

    @property
    def certification_metric_years(self):
        """
        Years based on certification metrics queryset in reverse order.
        Always contains at least current year
        :return: list of integers
        """
        certification_metric_years = [
            timezone.now().year,
        ]
        certification_metric_years += (
            self.certification_metrics.annotate(year=ExtractYear("certification_date"))
            .exclude(year=None)
            .distinct()
            .values_list("year", flat=True)
        )
        return sorted(set(certification_metric_years), reverse=True)

    @property
    def inspection_grade_years(self):
        """
        Years based on inspection grades queryset in reverse order.
        Always contains at least current year
        :return: list of integers
        """
        inspection_grade_years = [
            timezone.now().year,
        ]
        inspection_grade_years += (
            self.inspection_gradings.annotate(year=ExtractYear("graded_date"))
            .distinct()
            .values_list("year", flat=True)
        )
        return sorted(set(inspection_grade_years), reverse=True)

    def get_machinery(self):
        user = self.get_object()

        machineries = {}
        kwargs = {
            "create_new": True,
            "context": {
                "request": self.request,
            },
        }

        machinery = UserExamineMachinery(
            instance=user,
            **{
                "create_new": False,
                "context": {
                    "request": self.request,
                },
            },
        )
        machineries[machinery.type_name_slug] = machinery
        self.primary_machinery = machinery

        hirl_user_profile, created = HIRLUserProfile.objects.get_or_create(user=user)
        machinery = HIRLUserProfileExamineMachinery(
            instance=hirl_user_profile, context={"request": self.request, "user": user}
        )
        machineries[machinery.type_name_slug] = machinery

        for training_year in self.training_years:
            trainings = user.training_set.filter(
                training_date__year=training_year
            ).prefetch_related("statuses")
            machinery = UserTrainingExamineMachinery(
                objects=trainings, context={"request": self.request, "user": user}
            )
            machineries["{}_{}".format(machinery.type_name_slug, training_year)] = machinery

        for accreditation_year in self.accreditation_years:
            # add Accreditations without date_last to current year
            if accreditation_year == timezone.now().year:
                accreditations = self.accreditations.filter(
                    Q(date_last__year=accreditation_year) | Q(date_last=None)
                )
            else:
                accreditations = self.accreditations.filter(date_last__year=accreditation_year)

            accreditations = accreditations.distinct()
            machinery = UserAccreditationExamineMachinery(
                objects=accreditations, context={"request": self.request, "user": user}
            )
            machineries["{}_{}".format(machinery.type_name_slug, accreditation_year)] = machinery

        for certification_metric_year in self.certification_metric_years:
            # This can create a lot of region objects that hurts DFR throttle API and create performance issues
            # limit query to 5 items
            machinery = UserCertificationMetricExamineMachinery(
                objects=self.certification_metrics.filter(
                    certification_date__year=certification_metric_year
                )[:5],
                **kwargs,
            )
            machineries[
                "{}_{}".format(machinery.type_name_slug, certification_metric_year)
            ] = machinery

        for inspection_grading_year in self.inspection_grade_years:
            # avoid spamming requests by showing latest 5 records per year
            grades = self.inspection_gradings.filter(graded_date__year=inspection_grading_year)[:5]
            machinery = UserInspectionGradeExamineMachinery(
                objects=grades,
                context={"request": self.request, "user": user},
            )
            machineries[
                "{}_{}".format(machinery.type_name_slug, inspection_grading_year)
            ] = machinery

        machinery = TaskUserMachinery(
            objects=Task.objects.filter_by_user(user=self.request.user).filter(
                assignees__in=[
                    user,
                ]
            ),
            context={"request": self.request, "user": user},
        )
        machineries[machinery.type_name_slug] = machinery

        return machineries

    def get_context_data(self, **kwargs):
        user = self.get_object()
        context = super(UserExamineView, self).get_context_data(**kwargs)
        context["profile_user"] = user
        context["training_years"] = self.training_years
        context["accreditation_years"] = self.accreditation_years
        context["certification_metric_years"] = self.certification_metric_years
        context["inspection_grade_years"] = self.inspection_grade_years

        context["show_training"] = (
            self.request.user.is_superuser
            or user.company == self.request.user.company
            or self.request.user.company.slug
            in user_management_app.TRAINING_APPLICABLE_COMPANIES_SLUGS
        )

        context["show_accreditation"] = (
            self.request.user.is_superuser
            or user.company.company_type in ["rater", "provider"]
            or self.request.user.company.slug
            in user_management_app.ACCREDITATION_APPLICABLE_COMPANIES_SLUGS
        )

        context["show_certification_metric"] = (
            self.request.user.is_superuser
            or user.company == self.request.user.company
            or self.request.user.company.slug
            in user_management_app.CERTIFICATION_METRIC_APPLICABLE_COMPANIES_SLUGS
        )

        context["show_inspection_grade"] = (
            self.request.user.is_superuser
            or user.company == self.request.user.company
            or self.request.user.company.slug
            in user_management_app.INSPECTION_GRADE_APPLICABLE_COMPANIES_SLUGS
            or (
                user.company.company_type == "rater"
                and user.company != self.request.user.company
                and self.request.user.company.company_type == "qa"
            )
        )

        context["show_hirl_settings"] = (
            self.request.user.is_customer_hirl_company_member()
            or self.request.user.is_superuser
            or self.request.user.is_sponsored_by_company(customer_hirl_app.CUSTOMER_SLUG)
        )
        context["show_hirl_rater_settings"] = (
            self.request.user.is_customer_hirl_company_member()
            or self.request.user.is_superuser
            or self.request.user.is_sponsored_by_company(customer_hirl_app.CUSTOMER_SLUG)
        )

        if (
            user.is_company_type_member(Company.RATER_COMPANY_TYPE)
            and (
                self.request.user.is_customer_hirl_company_member()
                or self.request.user.is_superuser
            )
            and getattr(user, "hirlrateruser", None)
        ):
            context["hirl_rater_user_internal_id"] = user.hirlrateruser.hirl_id
        return context


class SearchListView(LoginRequiredMixin, TemplateView):
    """Calls ``filter_by_user`` on the model's default manager

    TODO: Rewrite this ugly template
    """

    template_name = "core/search_results.html"

    def get(self, context, **kwargs):
        if "q" not in self.request.GET:
            messages.warning(self.request, "You must input something to search on.")
            return HttpResponseRedirect(reverse("home"))

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.get_ajax()

        return super(SearchListView, self).get(context, **kwargs)

    def get_ajax(self):
        """Return the serialized data"""
        object_list = self.get_queryset()
        num_items = len(object_list)

        data = {
            "data": object_list,
            "recordsTotal": num_items,
            "recordsFiltered": num_items,
        }
        return HttpResponse(AxisJSONEncoder().encode(data), content_type="application/json")

    def get_queryset(self):
        """The search QuerySet"""

        search_query = self.request.GET.get("q", "").strip()
        filter_query = self.request.GET.get("search[value]", "").lower().strip()

        if not (search_query or filter_query):
            return []

        valid_types = dict.fromkeys(
            [
                "user",
                "company",
                "community",
                "subdivision",
                "home",
                "community",
                "sampleset",
                "floorplan",
                "simulation",
                "document",
            ],
            True,
        )
        valid_types.update(
            {
                "hirl_project": self.request.user.is_customer_hirl_company_member()
                or self.request.user.is_superuser,
                "invoice": self.request.user.is_customer_hirl_company_member()
                or self.request.user.is_superuser,
            }
        )

        # Split type specifier (including whitespace to keep terms propertly "strip()"'d)
        type_search = None
        if ":" in search_query:
            type_search, search_query = re.split(r"\s*:\s*", search_query, 1)

            # Complain about a bad type only if it came from the major search input
            if not valid_types.get(type_search):
                msg = "Invalid type '{}'. Valid <type>: searches are one of '{}'".format(
                    type_search, ", ".join(valid_types)
                )
                messages.warning(self.request, msg)
                # valid_types = {}

        elif ":" in filter_query:
            type_search, filter_query = re.split(r"\s*:\s*", filter_query, 1)

        log.debug("Type: {} Q: {} Search: {}".format(type_search, search_query, filter_query))

        # Restrict search to type (only if valid/meets boolean condition)
        if valid_types.get(type_search):
            valid_types = {type_search: True}

        data = []
        full_query = search_query + " " + filter_query
        terms = set(full_query.split())
        for valid_type in valid_types:
            f = getattr(self, "get_{}_values".format(valid_type))
            data.extend(
                f(
                    **{
                        "terms": terms,
                        "search_query": search_query,
                        "filter_query": filter_query,
                        "full_query": full_query,
                    }
                )
            )
            log.debug("%s %ss returned with search = %s", len(data), valid_type, search_query)

        # This needs to live here so that the initial response via get() can catch it
        if not self.request.headers.get("x-requested-with") == "XMLHttpRequest" and len(data) > 200:
            href = "<a href='{}'>Advanced Search</a>".format(reverse("search:search"))
            err = (
                "More that 200 items returned - Please use {} to narrow your "
                "results {} items matched your search of {}".format(href, len(data), search_query)
            )
            messages.warning(self.request, err)

        return data

    def build_results(self, object_list, **kwargs):
        return [self.build_result(obj, **kwargs) for obj in object_list]

    def build_result(self, obj, get_type=None, get_href=None, get_text=None, get_url=None):
        if get_type:
            type = get_type(obj)
        else:
            type = obj.__class__.__name__

        if get_href:
            href = get_href(obj)  # Should include appropriate {}-style formatting names
        else:
            href = '<a href="{url}">{text}</a>'

        if get_url:
            url = get_url(obj)
        else:
            url = obj.get_absolute_url()

        if get_text:
            text = get_text(obj)
        else:
            text = "{}".format(obj)

        item = href.format(
            **{
                "obj": obj,
                "url": url,
                "text": text,
            }
        )

        return (type, item, obj.pk)

    def _get_values(
        self, model, terms, fields, extra_q=None, extra_queryset=None, annotations=None, **kwargs
    ):
        """
        :param model: Django Model class
        :param terms: set of terms to search
        :param fields: list of fields to search
        :param extra_q: extra queryset params will add with AND condition
        :param extra_queryset: extra queryset to union with result
        :param annotations: annotation fields
        :param kwargs: extra params for build_results
        :return: list
        """
        queryset = model.objects.filter_by_user(self.request.user)

        if terms:
            filters = dict.fromkeys(fields)
            for path in fields:
                path_q = reduce(operator.and_, [Q(**{path: term}) for term in terms])
                filters[path] = path_q
            q = reduce(operator.or_, filters.values())

            id_values = []
            for term in terms:
                try:
                    id_values.append(int(term))
                except (ValueError, TypeError):
                    pass

            if id_values:
                q |= Q(pk__in=id_values)

            if extra_q:
                q &= extra_q

            if annotations:
                queryset = queryset.annotate(**annotations)

            queryset = queryset.filter(q).distinct()

            if extra_queryset:
                queryset = queryset.union(extra_queryset)

        return self.build_results(queryset, **kwargs)

    def get_company_values(self, terms, **kwargs):
        def get_type(obj):
            return dict(COMPANY_TYPES).get(obj.company_type)

        return self._get_values(
            Company,
            terms,
            ["name__icontains", "altname__name__icontains"],
            **{
                "get_type": lambda obj: get_type(obj),
            },
        )

    def get_community_values(self, terms, **kwargs):
        return self._get_values(Community, terms, ["name__icontains"])

    def get_subdivision_values(self, terms, full_query, **kwargs):
        fields = ["builder_name__icontains", "name__icontains"]

        # Try to handle the "X at Y" format to extend search to the community name
        q = None
        re_at_community = re.search(r"(.*)(?:\sat\s|\s?@\s?)(.*)", full_query)
        if re_at_community:
            q = Q(
                **{
                    "name__icontains": re_at_community.group(1).strip(),
                    "community__name__icontains": re_at_community.group(2).strip(),
                }
            )

        return self._get_values(
            Subdivision,
            terms,
            fields,
            **{
                "get_type": lambda obj: "Subdivision/MF Development",
                "extra_q": q,
            },
        )

    def get_floorplan_values(self, terms, **kwargs):
        return self._get_values(Floorplan, terms, ["name__icontains", "number__icontains"])

    def get_hirl_project_values(self, terms, **kwargs):
        fields = [
            "id__icontains",
            "registration__id__icontains",
            "h_number__icontains",
            "hirllegacycertification__hirl_id__icontains",
            "hirllegacycertification__hirl_project_id__icontains",
            "home_status__home__lot_number__icontains",
            "home_status__home__street_line1__icontains",
            "home_status__home__city__name__icontains",
            "home_status__home__zipcode__icontains",
            "home_status__home__geocode_response__geocode__raw_street_line1__icontains",
            "home_status__customer_hirl_project__home_address_geocode__raw_street_line1__icontains",
            "home_status__customer_hirl_project__home_address_geocode__raw_street_line2__icontains",
            "home_status__customer_hirl_project__home_address_geocode__raw_city__name__icontains",
            "home_status__customer_hirl_project__home_address_geocode__raw_zipcode__icontains",
            "home_status__customer_hirl_project__home_address_geocode__raw_address__icontains",
        ]

        def get_text(hirl_project):
            text = f"Project ID: {str(hirl_project.id)}"
            legacy_certification = hirl_project.hirllegacycertification_set.first()
            if legacy_certification:
                text = (
                    f"Project ID: {str(hirl_project.id)} | "
                    f"NGBS Legacy Project ID: {legacy_certification.hirl_project_id}"
                )
            return text

        def get_href(hirl_project):
            url = hirl_project.get_absolute_url()
            if getattr(hirl_project, "home_status", None):
                url = hirl_project.home_status.get_absolute_url()
            text = get_text(hirl_project)

            return f"<a href='{url}'>{text}</a>"

        return self._get_values(
            HIRLProject,
            terms,
            fields,
            **{
                "get_type": lambda obj: "NGBS Project",
                "get_text": lambda obj: get_text(obj),
                "get_href": get_href,
            },
        )

    def get_invoice_values(self, terms, **kwargs):
        fields = [
            "id__icontains",
            "invoiceitemgroup__home_status__customer_hirl_project__id__icontains",
            "invoiceitemgroup__home_status__customer_hirl_project__h_number__icontains",
            "invoiceitemgroup__home_status__customer_hirl_project__hirllegacycertification__hirl_id__icontains",
            "invoiceitemgroup__home_status__customer_hirl_project__hirllegacycertification__hirl_project_id__icontains",
        ]

        inv_term = next(iter(terms), None)
        extra_queryset = Invoice.objects.search_by_case_insensitive_id(value=inv_term)

        return self._get_values(
            Invoice,
            terms,
            fields,
            extra_queryset=extra_queryset,
            **{
                "get_text": lambda obj: f"Invoice ID: {obj.id}",
            },
        )

    def get_simulation_values(self, terms, **kwargs):
        fields = [
            "name__icontains",
        ]

        def get_type(obj):
            return obj.get_source_type_display()

        def get_text(obj):
            return obj.as_string()

        def get_url(obj):
            try:
                if obj.source_type == SourceType.REMRATE_SQL:
                    return reverse("floorplan:input:remrate", kwargs={"pk": obj.source.source.pk})
                elif obj.source_type == SourceType.EKOTROPE:
                    pk = obj.source.source.houseplan_set.get().pk
                    return reverse(
                        "floorplan:input:ekotrope",
                        kwargs={"pk": pk},
                    )
            except AttributeError:
                try:
                    return reverse("floorplan:view", kwargs={"pk": obj.pk})
                except Exception:
                    return "#"

        return self._get_values(
            Simulation,
            terms,
            fields,
            **{
                "get_type": get_type,
                "get_text": get_text,
                "get_url": get_url,
                "extra_q": Q(
                    created_date__gte=now() - datetime.timedelta(days=60),
                    status=SimulationStatus.READY,
                ),
            },
        )

    def get_home_values(self, terms, **kwargs):
        fields = [
            "lot_number__icontains",
            "street_line1__icontains",
            "city__name__icontains",
            "zipcode__icontains",
            "geocode_response__geocode__raw_street_line1__icontains",
            "hirl_certification__project_id__icontains",
        ]

        return self._get_values(
            Home,
            terms,
            fields,
            **{
                "get_text": lambda obj: obj.get_home_address_display(),
                "get_type": lambda obj: "Project",
            },
        )

    def get_sampleset_values(self, terms, **kwargs):
        def altname_or_nothing(obj):
            if obj.alt_name:
                return " [{}]".format(obj.alt_name)
            return ""

        fields = ["uuid__icontains", "alt_name__icontains"]

        return self._get_values(
            SampleSet,
            terms,
            fields,
            **{
                "get_text": lambda obj: "Sample Set {}{}".format(obj, altname_or_nothing(obj)),
                "extra_q": Q(
                    start_date__gte=datetime.datetime.today() - datetime.timedelta(days=60)
                ),
            },
        )

    def get_user_values(self, terms, **kwargs):
        def get_href(user):
            if not user.company:
                return "-"

            href = '<a href="{url}">{text}</a> ({obj.company.name})'
            if self.request.user.is_superuser:
                impersonate_url = reverse("impersonate-start", kwargs={"uid": user.id}) + "?next=/"
                href += (
                    '&emsp;<a class="pull-right btn btn-primary btn-xs" href="{}">'
                    '<i class="fa fa-sign-in"></i> Log in</a>'
                ).format(impersonate_url)
            return href

        fields = [
            "first_name__iexact",
            "last_name__iexact",
            "username__icontains",
            "full_name__icontains",
            "email__icontains",
        ]

        return self._get_values(
            User,
            terms,
            fields,
            annotations={"full_name": Concat("first_name", Value(" "), "last_name")},
            get_type=lambda obj: "User",
            get_href=get_href,
        )

    def get_document_values(self, terms, **kwargs):
        # We inject a unique suffix to a filename, so remove any explicit extensions that terminate
        # their search earlier than is good for our icontains lookup
        terms = set(os.path.splitext(term)[0] for term in terms)

        tz = self.request.user.timezone_preference

        def get_href(obj):
            dts = obj.created_date.astimezone(tz)
            base_href = '<a href="{url}">{text}</a>'
            suffix = " ({})".format(formats.date_format(dts, "SHORT_DATETIME_FORMAT"))
            return base_href + suffix

        fields = ["document__icontains", "task_id__icontains"]

        return self._get_values(
            AsynchronousProcessedDocument,
            terms,
            fields,
            **{
                "get_type": lambda obj: "Document",
                "get_href": get_href,
                "extra_q": Q(created_date__gte=now() - datetime.timedelta(days=60)),
            },
        )

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q")
        return context


class LocalStorageResetView(TemplateView):
    template_name = "debug/localstorage_reset.html"


class HistoryDataTableView(LoginRequiredMixin, LegacyAxisDatatableView):
    template_name = "simple_history/history_list.html"
    datatable_options = {
        "columns": [
            ("Date", ["history_date"], "get_column_Date_data"),
            (
                "User",
                ["history_user__username", "history_user__first_name", "history_user__last_name"],
                "get_column_User_data",
            ),
            ("Object", ["history_object"], "get_column_Object_data"),
            ("Type", ["history_type"], "get_column_Type_data"),
            ("Fields", None, "get_column_Fields_data"),
            ("Previous Values", None, "get_column_Previous_data"),
            ("Updated Values", None, "get_column_Updated_data"),
        ],
        "ordering": ["Date"],
    }

    def get_permission_required(self):
        return ("{app_label}.view_{model}".format(**self.kwargs),)

    def get_model_obj(self):
        """Return the generic model object"""
        if hasattr(self, "model_obj"):
            return self.model_obj
        model_ct = ContentType.objects.get(
            app_label=self.kwargs.get("app_label"), model=self.kwargs.get("model")
        )
        self.model_obj = model_ct.model_class()
        return self.model_obj

    def get_object(self, id=None):
        """If we have a pk then we know the row"""
        if id is None and self.kwargs.get("field") == "id":
            id = self.kwargs.get("constraint")
        self.object = self.get_model_obj().objects.get(pk=id)
        return self.object

    def get_queryset(self):
        """Narrow this based on your company"""
        if "constraint" in self.kwargs and self.kwargs["constraint"] in [None, "None"]:
            try:
                return self.get_model_obj().history.none()
            except ContentType.DoesNotExist:
                return []

        filter = {self.kwargs.get("field"): self.kwargs.get("constraint")}
        try:
            filter["content_type"] = int(self.request.GET.get("content_type_id"))
        except (TypeError, ValueError):
            pass
        data = self.get_model_obj().history.filter(**filter).order_by("history_id")
        keep_ids, _discard = [], []
        for item in list(data.values()):
            keep_id = item.pop("history_id")
            [item.pop(k, None) for k in ["history_date", "modified_date"]]
            if len(_discard) and _discard[-1] == item:
                continue
            _discard.append(item)
            keep_ids.append(keep_id)
        update = self.get_model_obj().history.filter(history_id__in=keep_ids).order_by("history_id")
        if not hasattr(self, "_fields"):
            self._user_dict = {}
            self._object_dict = {}
            self._related_dict = {}
            self._get_fields_changed_current_deltas(update)
        return update

    def _get_fields_changed_current_deltas(self, queryset):
        """This will iterate over the changes and collect the deltas"""
        object_list = []
        olist = queryset.values()
        for item in olist:
            item.pop("history_date", "modified_date")
            object_list.append(item)
        self._fields = {}
        for index in range(len(object_list)):
            _id = object_list[index]["history_id"]
            self._fields[_id] = get_revision_delta(
                self.get_model_obj(), object_list, index, user=self.request.user
            )

    def get_column_Date_data(self, obj, *args, **kwargs):
        tz = self.request.user.timezone_preference
        dts = obj.history_date.astimezone(tz)
        return formats.date_format(dts, "SHORT_DATETIME_FORMAT")

    def get_column_User_data(self, obj, *args, **kwargs):
        try:
            return self._user_dict[obj.history_user_id]
        except KeyError:
            link = ""
            try:
                name = obj.history_user.get_full_name()
                url = obj.history_user.get_absolute_url()
                link = "<a href='{}'>{}</a>".format(url, name)
            except (AttributeError, ObjectDoesNotExist):
                link = "Administrator*"
            self._user_dict[obj.history_user_id] = link
            return link

    def get_column_Object_data(self, obj, *args, **kwargs):
        try:
            return self._object_dict[obj.id]
        except KeyError:
            link, data_obj = "", ""
            try:
                data_obj = self.get_object(id=obj.id)
                name = "{}".format(data_obj)
                name = name if len(name) < 32 else name[0:32] + " ..."
                link = "<a href='{}'>{}</a>".format(data_obj.get_absolute_url(), name)
            except ObjectDoesNotExist:
                link = "Deleted"
            except AttributeError:
                link = "{}".format(data_obj)
            self._object_dict[obj.id] = link
            return link

    def get_column_Type_data(self, obj, *args, **kwargs):
        type_choices = (("+", "Created"), ("~", "Changed"), ("-", "Deleted"))
        return next((x[1] for x in type_choices if x[0] == obj.history_type), "-")

    def get_column_Fields_data(self, obj, *args, **kwargs):
        return "<br>".join(self._fields[obj.history_id]["fields"])

    def get_column_Previous_data(self, obj, *args, **kwargs):
        return "<br>".join(self._fields[obj.history_id]["previous"])

    def get_column_Updated_data(self, obj, *args, **kwargs):
        return "<br>".join(self._fields[obj.history_id]["updated"])


# django_select2 view that dispatches all ajax field requests
class ApiAutoResponseView(AutoResponseView):
    """
    Subclassed to send the request to the queryset filter process and process ValuesQuerySet.
    """

    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get("term", request.GET.get("term", ""))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                "results": [self.get_result(obj) for obj in context["object_list"]],
                "more": context["page_obj"].has_next(),
            }
        )

    def get_queryset(self):
        return self.widget.filter_queryset(self.request, self.term, self.queryset)

    def get_result(self, obj):
        """Custom implementation of django_select2's creation of the individual records."""
        pk = None
        if hasattr(obj, "pk"):
            pk = obj.pk
        elif isinstance(obj, dict):  # ValuesQuerySet record
            pk = obj.get("pk", obj.get("name"))
        elif isinstance(obj, (tuple, list)):  # ValuesListQuerySet record
            pk = obj[0]  # naive treatment of first item in values_list() result as pk
        else:
            raise ValueError("Unexpected object type %r" % (obj,))

        label_from_instance_kwargs = {}
        get_label_from_instance = self.widget.label_from_instance
        if "request" in inspect.getfullargspec(get_label_from_instance).args:
            label_from_instance_kwargs["request"] = self.request

        text = self.widget.label_from_instance(obj, **label_from_instance_kwargs)

        return {
            "text": text,
            "id": pk,
        }
