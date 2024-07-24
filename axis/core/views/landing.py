"""views.py: Django core views"""
import datetime
import logging
from collections import OrderedDict, defaultdict
from functools import partial

import dateutil.parser
from django.apps import apps
from django.contrib.sites.models import Site
from django.db.models import Count

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from rest_framework.response import Response

from axis.core.utils import get_n_days_range, get_current_quarter_range
from axis.home.models import Home
from axis.qa import strings as qa_strings
from axis.relationship.models import Relationship
from .views import NewsListView
from ..utils import select_queryset_values

__author__ = "Autumn Valenta"
__date__ = "2015/12/14 11:14:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)
customer_neea_app = apps.get_app_config("customer_neea")
customer_hirl_app = apps.get_app_config("customer_hirl")
frontend_app = apps.get_app_config("frontend")

tooltips = {
    "neeautilities": {
        "certified_incentives": {
            "n": "Homes certified in the specified date range",
            "savings_kwh": "Sum of kWh savings for homes certified in the specified date range",
            "savings_therms": "Sum of Therms savings for homes certified in the specified date range",
            "approved_payments": "Certified homes with approved payments in the specified date range",
            "pending_payments": "Certified home without approved payments in the specified date range",
            "approved_dollars": "Sum of Builder Incentives for homes certified in the specified date range with approved payments",
            "pending_dollars": "Sum of Builder Incentives for homes certified in the specified date range without approved payments",
        },
        "uncertified": {
            "not_complete": "Total number of homes not certified",
            "pending_inspection": "Total number of program certifications pending start of data collection",
            "inspection": "Total number of program certifications with data collection in progress",
            "certification_pending": "Total number of program certifications with data collection completed",
            "abandoned": "Total number of abandoned program certifications",
        },
    },
}


class DefaultDashboard(NewsListView):
    template_name = "core/landing/generic.html"

    def get_context_data(self, **kwargs):
        context = super(DefaultDashboard, self).get_context_data(**kwargs)

        # FIXME: Can we please figure out why get_current() is failing instead of pretending it's
        # fine?
        try:
            context["site"] = Site.objects.get_current()
        except Site.DoesNotExist as err:
            log.exception("Unable to get_current Site?")
            context["site"] = "Unknown"

        if self.request.user.is_authenticated:
            context["news"] = self.get_cached_flat_page_news_data(query_type="all", limit=2)

        if self.request.user.is_authenticated:
            us_states = list(
                Home.objects.filter_by_user(self.request.user)
                .values_list("city__county__state", flat=True)
                .order_by("city__county__state")
                .distinct()
            )

            populated_fields = {
                "us_state": us_states,
            }
            for field_name, values in populated_fields.items():
                if len(values) and values[0] is None:
                    values.pop(0)
                if len(values) > 1:
                    context[field_name + "_options"] = values

        return context


class SuperUserDashboard(DefaultDashboard):
    template_name = "core/landing/generic.html"


class PublicDashboard(DefaultDashboard):
    template_name = "core/landing/public.html"

    def get_context_data(self, **kwargs):
        context = super(PublicDashboard, self).get_context_data(**kwargs)
        context["news"] = self.get_cached_flat_page_news_data(query_type="public", limit=3)
        try:
            context["products"] = self.get_cached_flat_page_news_data(query_type="product")[0]
        except IndexError:
            context["products"] = "Got Nothing.."
        try:
            context["info"] = self.get_cached_flat_page_news_data(query_type="info")[0]
        except IndexError:
            context["info"] = "Got Nothing.."
        return context


class QARecentObservationsMixin(object):
    MAX_RECENT_HOMES = 5

    def get_context_data(self, **kwargs):
        context = super(QARecentObservationsMixin, self).get_context_data(**kwargs)

        from axis.home.models import Home
        from axis.qa.models import Observation
        from axis.qa.utils import get_recent_observations

        aliases = {
            "observation_type__name": "observation_type",
            "qa_status__home_status__home__id": "home_id",
        }

        alias_values = partial(select_queryset_values, **aliases)

        # Recent
        f_homeid = "qa_status__home_status__home__id"
        queryset = (
            Observation.objects.filter_by_user(self.request.user)
            .filter(qa_status__requirement__type="file")
            .filter(qa_status__subdivision=None)
            .values(f_homeid, "created_on")
            .annotate(homeid=Count(f_homeid))
        )
        recent_qs = alias_values(
            get_recent_observations(queryset),
            **{
                "user__first_name": None,
                "user__last_name": None,
            },
        )
        addresses = (
            Home.objects.filter(id__in=(item["home_id"] for item in recent_qs))
            .values_list("id", "street_line1")
            .order_by("-homestatuses__qastatus__observation__created_on")
        )

        addresses = dict(addresses)

        for data in recent_qs:
            # Wrap the 'street_line1' value into a dictionary so we can add more data from other
            # query.
            home_repr = addresses[data["home_id"]]
            if isinstance(home_repr, str):
                item = {"home_repr": home_repr}
                addresses[data["home_id"]] = item

            # Put this data into the home-centric dict
            item.setdefault("observations", [])
            item["observations"].append(data)

        context["recent_observations"] = list(addresses.items())[: self.MAX_RECENT_HOMES]

        return context


class QADashboard(QARecentObservationsMixin, DefaultDashboard):
    template_name = "core/landing/qa.html"

    def get_context_data(self, **kwargs):
        context = super(QADashboard, self).get_context_data(**kwargs)

        # ETO QA should be restricted to seeing just ETO-centric qa tables.
        # Other QA should generally see both ETO-specific and generic tables.

        show_eto_qa_tables = True
        show_neea_qa_tables = True
        show_generic_qa_tables = True

        # Hide ETO tables from "CLEAResult QA (NEEA)" and CRQA-reincarnated entities
        if self.request.company.slug in [
            "clearesult-qa",
            "qa-performance-path-qa-benton-rea",
            "qa-performance-path-qa-cec",
            "qa-performance-path-qa-clark-pud",
            "qa-performance-path-qa-inland-power",
            "qa-performance-path-qa-pse",
            "qa-performance-path-qa-snopud" "qa-pacific-power-qa-wa",
            "wa-code-study-qa",
        ]:
            show_eto_qa_tables = False

        # Restrict ETO companies to seeing just ETO tables.
        if self.request.company.slug in ["eto", "csg-qa", "peci"]:
            show_generic_qa_tables = False

        if self.request.company.slug in [
            "clearesult-qa",
            "qa-performance-path-qa-benton-rea",
            "qa-performance-path-qa-cec",
            "qa-performance-path-qa-clark-pud",
            "qa-performance-path-qa-inland-power",
            "qa-performance-path-qa-pse",
            "qa-performance-path-qa-snopud",
            "wa-code-study-qa",
        ]:
            show_neea_qa_tables = True

        context["show_eto_qa_tables"] = show_eto_qa_tables
        context["show_neea_qa_tables"] = show_neea_qa_tables
        context["show_generic_qa_tables"] = show_generic_qa_tables
        context["tooltips"] = qa_strings

        return context


class RaterProviderDashboard(QARecentObservationsMixin, DefaultDashboard):
    template_name = "core/landing/raterprovider.html"

    def get_context_data(self, **kwargs):
        context = super(RaterProviderDashboard, self).get_context_data(**kwargs)

        has_eto_association = (
            Relationship.objects.get_reversed_companies(self.request.company)
            .filter(slug="eto")
            .exists()
        )

        # ETO Provider/Rater see everything
        # Regular Provider/Rater don't see ETO tables
        context["show_eto_qa_tables"] = has_eto_association
        context["show_generic_qa_tables"] = True
        context["tooltips"] = qa_strings

        return context


class NoQARaterProviderDashboard(DefaultDashboard):
    template_name = "core/landing/raterprovider_no_qa.html"


class EEPDashboard(QARecentObservationsMixin, DefaultDashboard):
    template_name = "core/landing/eep.html"

    def get_context_data(self, **kwargs):
        context = super(EEPDashboard, self).get_context_data(**kwargs)
        context["tooltips"] = qa_strings

        if self.request.company.slug == "neea":
            context["show_neea_qa_tables"] = True
            context["show_generic_qa_tables"] = True
            context["neea_or_neea_utility"] = True

        return context


class UtilityDashboard(RaterProviderDashboard):
    template_name = "core/landing/utility.html"


class BuilderDashboard(DefaultDashboard):
    template_name = "core/landing/builder.html"


class NEEAUtilitiesDashboard(DefaultDashboard):
    template_name = "core/landing/neea_utilities.html"

    def get_context_data(self, **kwargs):
        context = super(NEEAUtilitiesDashboard, self).get_context_data(**kwargs)

        company = self.request.user.company

        is_neea = company.slug == "neea"
        is_utility = company.company_type == "utility"
        has_neea_affiliation = company.sponsors.filter(slug="neea").exists()
        context["neea_or_neea_utility"] = any(
            [
                is_neea,
                is_utility and has_neea_affiliation,
            ]
        )
        context["tooltips"] = qa_strings
        context["tooltips_neeautilities"] = tooltips["neeautilities"]
        return context


class HomeDashboardRoutingView(View):
    """View with a ``dispatch`` method that calls up a sub-view."""

    default_dashboard = DefaultDashboard
    superuser_dashboard = SuperUserDashboard
    public_dashboard = PublicDashboard

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        dashboard = self._get_dashboard(user=user)

        view = dashboard.as_view()
        log.info("%(user)s homepage heartbeat", {"user": user.username}, extra={"request": request})
        return view(request, *args, **kwargs)

    def _get_dashboard(self, user):
        dashboards = OrderedDict(
            [
                # The categories listed here are in order of priority when looking for overrides to the
                # generic default.
                (
                    "slug",
                    {
                        "aps": BuilderDashboard,
                        "provider-best-energy-rating-consulting": BuilderDashboard,
                        "dr-wastchak": BuilderDashboard,
                        "e3-energy-llc": BuilderDashboard,
                        "energy-inspectors": BuilderDashboard,
                        "efl": BuilderDashboard,
                        "provider-protex": BuilderDashboard,
                        "rater-evo-energy-solutions": BuilderDashboard,
                        "trc": DefaultDashboard,
                        customer_hirl_app.CUSTOMER_SLUG: DefaultDashboard,
                    },
                ),
                ("sponsored", {customer_hirl_app.CUSTOMER_SLUG: DefaultDashboard}),
                (
                    "company_type",
                    {
                        "qa": QADashboard,
                        "provider": RaterProviderDashboard,
                        "rater": RaterProviderDashboard,
                        "eep": EEPDashboard,
                        "builder": BuilderDashboard,
                        "utility": UtilityDashboard,
                    },
                ),
            ]
        )

        neea_utility_slugs = dict(
            [
                (slug, NEEAUtilitiesDashboard)
                for slug in customer_neea_app.NEEA_SP_INCENTIVE_UTILITY_SLUGS
            ]
        )
        dashboards["slug"].update(neea_utility_slugs)

        if not user.is_authenticated:
            return self.public_dashboard
        elif user.is_superuser:
            return self.superuser_dashboard
        else:
            # Find an applicable override for the current company
            for override_category, overrides in dashboards.items():
                if override_category == "sponsored":
                    for sponsor_slug, candidate_dashboard in overrides.items():
                        if user.is_sponsored_by_company(sponsor_slug, only_sponsor=True):
                            return candidate_dashboard
                else:
                    value = getattr(user.company, override_category)
                    if value in overrides:
                        return overrides[value]
        return self.default_dashboard


# Utility for DRF viewsets to fetch request data and push responses in the right format
class DashboardMetricsControlsMixin(object):
    def get_filter_controls(self, request, use_quarters=False, day_range=30):
        if use_quarters:
            date_start, date_end = get_current_quarter_range(as_datetime=True)
        else:
            date_start, date_end = get_n_days_range(day_range, as_datetime=True)

        # Default control values
        controls = {
            "date_start": date_start,
            "date_end": date_end,
            "us_state": None,
            "utility": None,
            "style": None,
        }

        # Update controls based on request
        for k in controls:
            if k in request.query_params:
                controls[k] = request.query_params[k]

        # Parse request data
        if isinstance(controls["date_start"], str):
            try:
                controls["date_start"] = dateutil.parser.parse(controls["date_start"]).replace(
                    tzinfo=datetime.timezone.utc
                )
            except:
                controls["date_start"] = date_start  # Revert back to default
        if isinstance(controls["date_end"], str):
            try:
                controls["date_end"] = dateutil.parser.parse(controls["date_end"]).replace(
                    tzinfo=datetime.timezone.utc
                )
            except:
                controls["date_end"] = date_end  # Revert back to default

        return controls

    def make_metrics_response(self, data, controls, choices=None):
        if not choices:
            choices = {}
        # Render dates into strings
        controls["date_start"] = controls["date_start"].strftime("%m/%d/%Y")
        controls["date_end"] = controls["date_end"].strftime("%m/%d/%Y")

        def get_sums_info():
            # Sum all numerical values in common keys, stripping away failed blank (string) entries
            sums = defaultdict(int)
            if len(data):
                for metrics in data:
                    for k in metrics:
                        if k.endswith("_id"):
                            continue
                        try:
                            0 + metrics[k]
                        except:
                            continue  # Don't care about non-numerical summation failures
                        sums[k] += metrics[k]
            return dict(sums)

        return Response(
            {
                "data": data,
                "sums": get_sums_info(),
                "controls": controls,
                "choices": choices,
            }
        )
