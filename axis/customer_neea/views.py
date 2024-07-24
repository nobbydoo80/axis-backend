"""views.py: Django customer_neea"""

import logging
import tempfile

import datatableview.helpers
from datatableview.views.legacy import LegacyDatatableMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http.response import Http404, HttpResponse
from django.urls import reverse
from django.utils import formats
from django.views.generic.base import TemplateView

from axis.annotation.models import Type, Annotation
from axis.checklist.models import Answer
from axis.company.models import Company
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisDetailView, LegacyAxisDatatableView
from axis.eep_program.models import EEPProgram
from axis.geocoder.models import Geocode
from axis.home.forms import NEEAUtilityFilterForm
from axis.home.models import EEPProgramHomeStatus, Home
from axis.home.views import (
    AsynchronousProcessedDocumentCreateHomeStatusXLS,
    HomeStatusView,
    HomeStatusReportMixin,
)
from axis.qa.models import QARequirement
from axis.relationship.models import Relationship
from axis.remrate_data.utils import get_ACH50_string_value
from .forms import (
    LegacyNEEAHomeStatusForm,
    HomeStatusUtilityRawReportForm,
    HomeStatusUtilityCustomReportForm,
    HomeStatusUtilityBPAReportForm,
)
from .models import LegacyNEEAPartner, LegacyNEEAHome, LegacyNEEAPartnerToHouse, LegacyNEEABOP

__author__ = "Steven Klass"
__date__ = "9/5/12 5:30 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

EPA_PROGRAM_SLUGS = [
    "energy-star-version-3-rev-07",
    "energy-star-version-3-rev-08",
    "energy-star-version-31-rev-05",
    "energy-star-version-31-rev-08",
]


class LegacyMixin(object):
    """Disable the automatic site buttons for Add/Edit/Delete controls."""

    show_add_button = False
    show_edit_button = False
    show_delete_button = False
    show_cancel_button = False


class LegacyNEEAContactDetailView(AuthenticationMixin, LegacyMixin, AxisDetailView):
    """NEEA Legacy Contacts"""

    permission_required = "customer_neea.view_legacyneeacontact"

    def get_context_data(self, **kwargs):
        """Add in the builders and subdivisions"""
        context = super(LegacyNEEAContactDetailView, self).get_context_data(**kwargs)
        return context


class LegacyNEEAPartnerListView(AuthenticationMixin, LegacyMixin, LegacyAxisDatatableView):
    """NEEA Legacy Partners"""

    permission_required = "customer_neea.view_legacyneeapartner"

    datatable_options = {
        "columns": [
            ("Name", "partner_name", datatableview.helpers.link_to_model),
            (
                "Address",
                [
                    "address__street_no",
                    "address__street_modifier",
                    "address__street_name",
                    "address__zip_code__city",
                    "address__zip_code__state_abbr",
                    "address__zip_code__zip_code",
                ],
            ),
            ("Partner Type", "partner_type"),
            ("Partner Since", "partner_since_date"),
        ],
    }

    def get_queryset(self):
        """Narrow this based on your company"""
        return LegacyNEEAPartner.objects.filter_by_user(
            self.request.user, active=True
        ).select_related("address")

    def get_column_Partner_Since_data(self, instance, *args, **kwargs):
        try:
            return instance.partner_since_date.strftime("%m/%d/%Y")
        except AttributeError:
            return "-"


class LegacyNEEAPartnerDetailView(AuthenticationMixin, LegacyMixin, AxisDetailView):
    """NEEA Legacy Partners"""

    permission_required = "customer_neea.view_legacyneeapartner"
    model = LegacyNEEAPartner

    def get_context_data(self, **kwargs):
        context = super(LegacyNEEAPartnerDetailView, self).get_context_data(**kwargs)

        matches = Geocode.objects.get_matches(
            raw_address=self.object.address.get_formatted_address(skip_lot=True),
            entity_type="street_address",
        )

        if matches.count() == 1:
            for k, v in matches[0].get_normalized_fields().items():
                if k in ["longitude", "latitude"]:
                    setattr(self.object, k, v)

        return context


class LegacyNEEAHomeListView(
    AuthenticationMixin, LegacyMixin, HomeStatusReportMixin, LegacyAxisDatatableView
):
    """NEEA Legacy Partners"""

    permission_required = "customer_neea.view_legacyneeahome"
    template_name = "customer_neea/legacyneeahome_list.html"
    model = LegacyNEEAHome

    datatable_options = {
        "columns": [
            (
                "Address",
                [
                    "address__street_no",
                    "address__street_modifier",
                    "address__street_name",
                    "address__zip_code__city",
                    "address__zip_code__state_abbr",
                    "address__zip_code__zip_code",
                ],
                datatableview.helpers.link_to_model,
            ),
            ("Type", "home_type__name"),
            ("Description", "description"),
            ("Start Date", "project_start_date"),
            ("Completion Date", "estimated_completion_date"),
        ],
        "ordering": ["-project_start_date"],
    }
    select_related = ["home_type", "address"]

    def filter_by_partner(self, partner_ids, **kwargs):
        """Filter by list of Company ids that are builders."""
        partners = LegacyNEEAPartner.objects.filter(id__in=partner_ids)

        if partners.count():
            homes = LegacyNEEAHome.objects.filter(legacyneeapartnertohouse__partner__in=partners)
            self.filter["id__in"].append(homes.values_list("id", flat=True))

        if kwargs.get("return_filters"):
            self.add_filter("Partner", partners)

    def filter_by_bop(self, bop_ids, **kwargs):
        """Filter by list of Company ids that are builders."""
        bops = LegacyNEEABOP.objects.filter(id__in=bop_ids)

        if bops.count():
            homes = LegacyNEEAHome.objects.filter(legacyneeainspection__bop__in=bops)
            self.filter["id__in"].append(homes.values_list("id", flat=True))

        if kwargs.get("return_filters"):
            self.add_filter("BOP", bops)

    def filter_by_location(self, **kwargs):
        us_state = kwargs.get("us_state")

        if us_state not in self.null_list:
            us_states = self._get_list_from_type(us_state)
            self.filter["address__zip_code__state__in"] = us_states
            if kwargs.get("return_filters"):
                self.add_filter("US State", ", ".join([x.upper() for x in us_states]))

    def get_external_qs_filters(self, queryset, user, return_filters=False, **kwargs):
        """
        Get the list of items for this view. In this case it's narrowed based on your company
        """
        self.filters = []

        self.filter = {"id__in": []}
        self.exclude = {"id__in": []}

        self.null_list = ["", "undefined", None]

        kwargs = self.prevision_kwargs(**kwargs)
        kwargs["return_filters"] = return_filters
        kwargs["user"] = user

        partner_ids = kwargs.get("partner_id")
        bop_ids = kwargs.get("bop_id")

        if partner_ids:
            self.filter_by_partner(self._get_list_from_type(partner_ids), **kwargs)

        if bop_ids:
            self.filter_by_bop(self._get_list_from_type(bop_ids), **kwargs)

        self.filter_by_location(**kwargs)

        if not self.filter["id__in"]:
            del self.filter["id__in"]
        else:
            self.filter["id__in"] = set.intersection(*[set(x) for x in self.filter["id__in"]])
        if not self.exclude["id__in"]:
            del self.exclude["id__in"]
        else:
            self.exclude["id__in"] = set.intersection(*[set(x) for x in self.exclude["id__in"]])

        queryset = queryset.filter(**self.filter).exclude(**self.exclude)

        if not return_filters:
            return queryset.distinct()

    def get_queryset(self):
        """Narrow this based on your company"""
        qs = LegacyNEEAHome.objects.filter_by_user(self.request.user)
        if not hasattr(self, "qs"):
            self.qs = qs
        if (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            log.debug("Ajax")
            qs = self.get_external_qs_filters(qs, user=self.request.user, **self.request.GET)
            qs = qs.select_related(*self.select_related)
            return qs.distinct()
        else:
            log.debug("None")
            return EEPProgramHomeStatus.objects.none()

    def get_column_Start_Date_data(self, obj, *args, **kwargs):
        try:
            return formats.date_format(obj.project_start_date, "SHORT_DATE_FORMAT")
        except Exception:
            return "-"

    def get_column_Completion_Date_data(self, obj, *args, **kwargs):
        try:
            return formats.date_format(obj.estimated_completion_date, "SHORT_DATE_FORMAT")
        except Exception:
            return "-"

    def get_context_data(self, **kwargs):
        context = super(LegacyNEEAHomeListView, self).get_context_data(**kwargs)
        context["form"] = LegacyNEEAHomeStatusForm(user=self.request.user)

        homes = LegacyNEEAHome.objects.filter_by_user(self.request.user)
        partner_ids = homes.values_list("legacyneeapartnertohouse__partner", flat=True)
        partner_qs = LegacyNEEAPartner.objects.filter(id__in=partner_ids).order_by("partner_name")
        context["form"].fields["partner"].queryset = partner_qs.distinct()

        _states = list(set(homes.values_list("address__zip_code__state", flat=True)))
        _states = [("", "---------")] + [(y, y) for y in _states if y]
        context["form"].fields["us_state"].choices = _states

        bop_ids = homes.values_list("legacyneeainspection__bop", flat=True)
        bop_qs = LegacyNEEABOP.objects.filter(id__in=bop_ids)
        context["form"].fields["bop"].queryset = bop_qs

        return context


class LegacyNEEAHomeDetailView(AuthenticationMixin, LegacyMixin, AxisDetailView):
    """NEEA Legacy Partners"""

    permission_required = "customer_neea.view_legacyneeahome"

    def get_context_data(self, **kwargs):
        """Add in the builders and subdivisions"""
        context = super(LegacyNEEAHomeDetailView, self).get_context_data(**kwargs)

        matches = Geocode.objects.get_matches(
            raw_address=self.object.address.get_formatted_address(skip_lot=True),
            entity_type="street_address",
        )

        if matches.count() == 1:
            for k, v in matches[0].get_normalized_fields().items():
                if k in ["longitude", "latitude"]:
                    setattr(self.object, k, v)

        context["inspections"] = context["incentives"] = None

        if self.object.legacyneeainspection_set.count():
            # assert self.object.legacyneeainspection_set.count() == 1
            context["inspections"] = self.object.legacyneeainspection_set.all()
            # context['incentives'] = context['inspections'].legacyneeainspectionincentive_set.all()
        try:
            partners = LegacyNEEAPartnerToHouse.objects.get_distinct_partners(self.object)
        except LegacyNEEAPartnerToHouse.DoesNotExist:
            partners = None
        context["partners"] = partners
        return context


class HomeCertificationView(AuthenticationMixin, TemplateView):
    def generate_report(self, home_stats):
        from axis.customer_neea.reports import NWESHCertificationReport

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=NWESH_Certificate.pdf"

        filename = tempfile.NamedTemporaryFile()

        report = NWESHCertificationReport(filename=filename)
        report.build(home_stats=home_stats, certifier_id=self.request.user.id)

        response.write(filename.read())

        return response

    def get(self, *args, **kwargs):
        if "pk" in kwargs:
            from axis.home.models import EEPProgramHomeStatus

            try:
                home_stat = EEPProgramHomeStatus.objects.get(id=kwargs["pk"])
            except EEPProgramHomeStatus.DoesNotExist:
                raise Http404()
            return self.generate_report([home_stat])


# FIXME: HomeStatusView uses the modern DatatableView but this hasn't been ported to work that way.
class UtilityStatusView(LegacyDatatableMixin, HomeStatusView):
    required_permission = "home.view_home"
    template_name = "customer_neea/utility_stats.html"
    show_add_button = False
    form_class = NEEAUtilityFilterForm

    datatable_options = {
        "columns": [
            ("Axis ID", ["home__id"]),
            (
                "Address",
                [
                    "home__street_line1",
                    "home__street_line2",
                    "home__state",
                    "home__zipcode",
                    "home__lot_number",
                ],
            ),
            ("City", ["home__city__name"]),
            ("Multifamily", "home__is_multi_family", "get_column_multifamily"),
            ("Program", "eep_program__name"),
            ("Home Status", "state_description", "get_column_Home_Status_data"),
            ("Date Certified", "certification_date", "get_column_date_certified_data"),
            ("Heat Type", ["annotations__content", "home__answers__answer"], "get_Heat_Type_data"),
            ("QA Status", "qastatus__state", "get_column_QA_Status_data"),
            (
                "% Better Than Code",
                "standardprotocolcalculator__percent_improvement",
                "get_column_pct_better_than_code_data",
            ),
            (
                "Total Savings (kWh)",
                "standardprotocolcalculator__total_kwh_savings",
                "get_column_total_savings_kwh_data",
            ),
            (
                "Incentive Status",
                "incentivepaymentstatus__state",
                "get_column_incentive_status_data",
            ),
            # ('Total Consumption (kWh)', None, 'get_column_total_consumption_data_kwh'),
            # ('Total Consumption (Therm)', None, 'get_column_total_consumption_data'),
        ],
        # 'page_length': 25,
        # 'unsortable_columns': ['Report', 'Heat Type'],
    }

    # prefetch_related = [
    #     'incentivepaymentstatus',# 'annotations',
    # ]

    select_related = [
        "home__city",
        # 'home__subdivision',
        # 'home__subdivision__community',
        # 'eep_program',
        # 'floorplan',
        # 'qastatus',
        # 'annotations',
        "floorplan__remrate_target",
        "floorplan__remrate_target__results",
        "floorplan__remrate_target__infiltration",
        "floorplan__remrate_target__building__building_info",
    ]

    href = '<a href"{}">{}</a>'

    def _filter_queryset(self, qs=None):
        # NEEA wants to allow visibility into some nationally sponsored programs for their utilities
        # that use this page. More programs may come in the future.
        if qs is None:
            qs = EEPProgramHomeStatus.objects.filter_by_user(user=self.request.user)
        return qs.filter(
            Q(eep_program__owner__slug="neea") | Q(eep_program__slug__in=EPA_PROGRAM_SLUGS)
        )

    def get_queryset(self):
        qs = super(UtilityStatusView, self).get_queryset()

        if not (
            self.request.headers.get("x-requested-with") == "XMLHttpRequest"
            or self.request.GET.get("ajax") == "true"
        ):
            return EEPProgramHomeStatus.objects.none()

        qs = self._filter_queryset(qs)

        if not hasattr(self, "annotation_dict"):
            ann_dict = {}
            objs = list(qs.values_list("id", flat=True))
            ct = ContentType.objects.get_for_model(EEPProgramHomeStatus)
            types = Type.objects.filter(slug__in=["heat-source"])
            anns = Annotation.objects.filter(content_type=ct, type__in=types, object_id__in=objs)
            for ann in anns.values("object_id", "content", "type__slug"):
                if ann.get("object_id") not in ann_dict:
                    ann_dict[ann.get("object_id")] = {"heat-source": None}
                ann_dict[ann.get("object_id")][ann.get("type__slug")] = ann.get("content")
            self.annotation_dict = ann_dict
            log.debug("Created annotation dict..")
        if not hasattr(self, "builder_dict"):
            rel_dict = {}
            stats_dict = dict(qs.values_list("home_id", "id"))
            ct = ContentType.objects.get_for_model(Home)
            rels = Relationship.objects.filter(
                content_type=ct, object_id__in=stats_dict.keys(), company__company_type="builder"
            )
            for company_id, name, obj_id in rels.values_list(
                "company_id", "company__name", "object_id"
            ):
                status = stats_dict.get(obj_id)
                if status not in rel_dict:
                    url = reverse("company:view", kwargs={"type": "builder", "pk": company_id})
                    href = '<a href="{url}">{name}</a>'
                    rel_dict[status] = href.format(url=url, name=name)
            self.builder_dict = rel_dict
            log.debug("Created builder dict..")
        if not hasattr(self, "remdata_dict"):
            keys = [
                "id",
                "floorplan__remrate_target__infiltration__heating_value",
                "floorplan__remrate_target__infiltration__cooling_value",
                "floorplan__remrate_target__infiltration__units",
                "floorplan__remrate_target__building__building_info__volume",
                "floorplan__remrate_target__version",
                "floorplan__remrate_target__flavor",
                "floorplan__remrate_target__results__heating_consumption",
                "floorplan__remrate_target__results__cooling_consumption",
                "floorplan__remrate_target__results__hot_water_consumption",
                "floorplan__remrate_target__results__photo_voltaic_consumption",
                "floorplan__remrate_target__results__lights_and_appliances_total_consumption",
            ]
            remdata_dict = {}
            for stat_id, hval, cval, units, vol, ver, flavor, hc, cc, hw, pv, la in list(
                qs.values_list(*keys)
            ):
                if remdata_dict.get(stat_id) not in remdata_dict:
                    remdata_dict[stat_id] = {
                        "heating_value": None,
                        "cooling_value": None,
                        "total_consumption": 0,
                    }
                remdata_dict[stat_id]["heating_value"] = get_ACH50_string_value(
                    hval, units, vol
                ).value
                remdata_dict[stat_id]["cooling_value"] = get_ACH50_string_value(
                    cval, units, vol
                ).value
                remdata_dict[stat_id]["version"] = ver
                remdata_dict[stat_id]["flavor"] = flavor
                if remdata_dict[stat_id]["total_consumption"] == 0:
                    val = sum([x for x in [hc, cc, hw, pv, la] if x])
                    remdata_dict[stat_id]["total_consumption"] = val

            self.remdata_dict = remdata_dict

        return qs

    def get_datatable_options(self):
        options = super(UtilityStatusView, self).get_datatable_options()
        options = options.copy()
        options["columns"] = options["columns"][:]
        options["columns"].insert(0, ("Report", None, "get_column_program_report_data"))
        options["unsortable_columns"] = ["Date Initiated", "Report"]
        return options

    # Datatable columns
    def get_column_program_report_data(self, obj, *args, **kwargs):
        url = reverse("home:report:checklist", kwargs={"home_status": obj.id})
        href = '&nbsp;&nbsp;&nbsp;&nbsp;<a href="{url}"><i class="fa fa-cloud-download"></i></a>'
        return href.format(url=url)

    def get_column_Axis_ID_data(self, obj, *args, **kwargs):
        return obj.home.get_id()

    def get_column_Address_data(self, obj, *args, **kwargs):
        text = obj.home.get_home_address_display(
            include_lot_number=True, include_confirmed=True, company=self.request.company
        )
        return datatableview.helpers.link_to_model(obj.home, text=text)

    def get_column_multifamily(self, obj, *args, **kwargs):
        return "Yes" if obj.home.is_multi_family else "No"

    def get_column_City_data(self, obj, *args, **kwargs):
        try:
            return obj.home.city.name
        except AttributeError:
            return "-"

    def get_column_date_certified_data(self, obj, *args, **kwargs):
        if not obj.certification_date:
            return "-"
        return formats.date_format(obj.certification_date, "SHORT_DATE_FORMAT")

    def get_column_Home_Status_data(self, obj, *args, **kwargs):
        return obj.state_description

    def get_column_QA_Status_data(self, obj, *args, **kwargs):
        # FIXME: NEEA doesn't see any QAstatus items by default, so this filter comes back empty
        # queryset = obj.qastatus_set.filter_by_user(self.request.user)

        queryset = obj.qastatus_set.all()
        return "<br>".join([qastatus.state_description for qastatus in queryset]) or "-"

    def get_column_pct_better_than_code_data(self, obj, *args, **kwargs):
        if obj.standardprotocolcalculator_set.count():
            if obj.standardprotocolcalculator_set.first().pct_improvement_method == "alternate":
                return "{:.2%}".format(
                    obj.standardprotocolcalculator_set.first().revised_percent_improvement
                )
            return "{:.2%}".format(obj.standardprotocolcalculator_set.first().percent_improvement)
        return "-"

    def get_column_total_savings_kwh_data(self, obj, *args, **kwargs):
        if obj.standardprotocolcalculator_set.count():
            return "{:.2f}".format(obj.standardprotocolcalculator_set.first().total_kwh_savings)
        return "-"

    def get_Heat_Type_data(self, obj, *args, **kwargs):
        annotation = obj.annotations.filter(type__slug="heat-source").first()
        text = None
        if annotation:
            text = annotation.content
        else:
            answer = Answer.objects.filter(
                home__homestatuses=obj, question__slug="neea-heating_source"
            ).first()
            if answer:
                text = answer.answer
        return text or "-"

    def get_column_incentive_status_data(self, obj, *args, **kwargs):
        try:
            return obj.incentivepaymentstatus.state_description
        except AttributeError:
            return "-"

    # Filter form and queryset work
    def setup_ipp_state_field(self, form, user, context, **kwargs):
        field = form.fields["ipp_state"]

        self.show_ipp_field = context["show_ipp"] = (
            self._filter_queryset().filter(incentivepaymentstatus__state__isnull=False).exists()
        )
        if not self.show_ipp_field:
            field.widget = field.hidden_widget()

    def setup_qa_type_field(self, form, user, context, **kwargs):
        # Change the queryset logic; NEEA can't do filter_by_user() and get any QA results, so we
        # check for QA presence in the base queryset instead.

        is_neea = user.company.slug == "neea"
        has_neea_association = user.company.sponsors.filter(slug="neea").exists()

        field = form.fields["qatype"]
        show_field = all(
            [
                # Other companies *could* see this, but we've not traditionally revealed it
                (is_neea or has_neea_association),
                user.has_perm("qa.view_qastatus"),
                getattr(self, "show_qa", False) or context["show_qa"],
            ]
        )
        if show_field:
            choices = list(self.qs.values_list("qastatus__requirement__type", flat=True).distinct())
            valid_choices = [x for x in QARequirement.QA_REQUIREMENT_TYPES if x[0] in choices]
            field.choices = [("", "---------")] + valid_choices
            show_field = len(choices) > 1

        if not show_field:
            field.widget = field.hidden_widget()

    def setup_qa_state_field(self, form, user, context, **kwargs):
        # Change the queryset logic; NEEA can't do filter_by_user() and get any QA results, so we
        # check for QA presence in the base queryset instead.

        is_neea = user.company.slug == "neea"
        has_neea_association = user.company.sponsors.filter(slug="neea").exists()

        field = form.fields["qastatus"]
        show_field = all(
            [
                # Other companies *could* see this, but we've not traditionally revealed it
                (is_neea or has_neea_association),
                user.has_perm("qa.view_qastatus"),
                getattr(self, "show_qa", False) or context["show_qa"],
            ]
        )
        if show_field:
            show_field = self.qs.values_list("qastatus").exists()
            if user.company.company_type not in ["provider", "qa"] and not user.is_superuser:
                choices = [x for x in field.choices if x[0] != "-3"]
                field.choices = choices
        if not show_field:
            field.widget = field.hidden_widget()

    def setup_has_bpa_association_field(self, form, user, context, **kwargs):
        is_neea = user.company.slug == "neea"
        has_neea_association = user.company.sponsors.filter(slug="neea").exists()

        show_field = all([(is_neea or has_neea_association)])

        field = form.fields["has_bpa_association"]
        if not show_field:
            field.widget = field.hidden_widget()

    def extra_filters(self, **kwargs):
        self.filter_by_has_bpa_association(**kwargs)

    def filter_by_has_bpa_association(self, has_bpa_association=None, **kwargs):
        if has_bpa_association is None:
            return

        bpa_company = Company.objects.get(slug="bpa")
        companies_with_bpa_association = list(
            bpa_company.sponsored_companies.values_list("id", flat=True)
        )
        if has_bpa_association is True:
            self.filter["home__relationships__company_id__in"] = companies_with_bpa_association
        elif has_bpa_association is False:
            self.exclude["home__relationships__company_id__in"] = companies_with_bpa_association
        self.add_filter("BPA Affiliation", has_bpa_association)

    def get_context_data(self, **kwargs):
        kwargs["show_heat_sources"] = True
        context = super(UtilityStatusView, self).get_context_data(**kwargs)
        user = self.request.user

        has_bpa_association = True
        if user.company.company_type == "utility":
            has_bpa_association = user.company.sponsors.filter(slug="neea").exists()
        context["has_bpa_association"] = has_bpa_association

        filter_form = context["filter_form"]

        # Ensure custom field is configured
        setup_args = [context["filter_form"], user, context]
        self.setup_has_bpa_association_field(*setup_args, **kwargs)

        hide_widgets = ["subdivision", "eep", "hvac", "qa", "general", "metro", "rating_type"]
        for field_name in hide_widgets:
            filter_form.fields[field_name].widget = filter_form.fields[field_name].hidden_widget()

        # Late config of program queryset
        # Note that empty ``order_by()`` makes the ``distinct()`` do what you expect.
        homestatuses = EEPProgramHomeStatus.objects.filter_by_user(user).order_by()
        program_ids_in_use = homestatuses.values_list("eep_program", flat=True).distinct()

        program_filter = Q(owner__slug="neea") | Q(slug__in=EPA_PROGRAM_SLUGS)
        programs = EEPProgram.objects.filter_by_user(user, ignore_dates=True).filter(
            program_filter, id__in=program_ids_in_use
        )
        filter_form.fields["eep_program"].queryset = programs

        if not self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            qs = homestatuses.filter(eep_program__owner__slug="neea")
            qs = self.get_external_qs_filters(qs, user=self.request.user)

            annotations = Annotation.objects.filter(
                type__slug="heat-source", object_id__in=list(qs.values_list("id", flat=True))
            )
            answers = Answer.objects.filter(
                question__slug="neea-heating_source",
                home_id__in=list(qs.values_list("home", flat=True)),
            )

            heat_source_types = {
                "Gas Heat Homes": {"ids": [], "id": "-1"},
                "Heat Pump Homes": {"ids": [], "id": "-2"},
                "Other Heat Homes": {"ids": [], "id": "-3"},
            }

            if annotations.count():
                self.process_heat_types(
                    heat_source_types, annotations.values_list("object_id", "content")
                )
            if answers.count():
                self.process_heat_types(heat_source_types, answers.values_list("home", "answer"))

            for key, value in heat_source_types.items():
                heat_source_types[key]["counter"] = len(set(value["ids"]))
                heat_source_types[key].pop("ids")
            context["heat_source_counter"] = heat_source_types

        return context

    def process_heat_types(self, storage, heat_types):
        """We add ids to a list instead of incrementing a counter to prevent counting dupes later."""
        for object_id, heat_type in heat_types:
            if "heat pump" in heat_type.lower():
                storage["Heat Pump Homes"]["ids"].append(object_id)
            elif "gas" in heat_type.lower():
                storage["Gas Heat Homes"]["ids"].append(object_id)
            else:
                storage["Other Heat Homes"]["ids"].append(object_id)


class AsynchronousProcessedDocumentCreateUtilityRawHomeStatusXLS(
    AsynchronousProcessedDocumentCreateHomeStatusXLS
):
    form_class = HomeStatusUtilityRawReportForm

    def get_context_data(self, **kwargs):
        context = super(
            AsynchronousProcessedDocumentCreateUtilityRawHomeStatusXLS, self
        ).get_context_data(**kwargs)
        context["title"] = "Project Utility Report"
        return context


class AsynchronousProcessedDocumentCreateUtilityCustomHomeStatusXLS(
    AsynchronousProcessedDocumentCreateHomeStatusXLS
):
    form_class = HomeStatusUtilityCustomReportForm

    def get_context_data(self, **kwargs):
        context = super(
            AsynchronousProcessedDocumentCreateUtilityCustomHomeStatusXLS, self
        ).get_context_data(**kwargs)
        context["title"] = "Project Utility Custom Report"
        return context


class AsynchronousProcessedDocumentCreateUtilityBPAHomeStatusXLS(
    AsynchronousProcessedDocumentCreateHomeStatusXLS
):
    form_class = HomeStatusUtilityBPAReportForm

    def get_context_data(self, **kwargs):
        context = super(
            AsynchronousProcessedDocumentCreateUtilityBPAHomeStatusXLS, self
        ).get_context_data(**kwargs)
        context["title"] = "Project Utility BPA Report"
        return context
