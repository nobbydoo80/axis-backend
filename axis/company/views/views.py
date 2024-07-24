"""views.py: Django company"""


import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import formats
from django.views.generic import TemplateView, RedirectView

from ...core.utils import get_frontend_url

try:
    from django.apps import apps

    get_model = apps.get_model
except:
    from django.db.models import get_model

import datatableview.helpers

from django.contrib.auth import get_user_model
from django.apps import apps
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    LegacyAxisDatatableView,
)
from ..models import Company
from ..strings import COMPANY_TYPES_MAPPING, COMPANY_TYPES_PLURAL
import axis.company.forms  # Full import path so that we can refer to it without conflict

__author__ = "Steven Klass"
__date__ = "3/2/12 2:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
User = get_user_model()

frontend_app = apps.get_app_config("frontend")


# Utilities
def get_company_model(company_type):
    return get_model("company", "%sOrganization" % company_type.capitalize())


def get_company_form(company_type):
    return getattr(axis.company.forms, "%sCompanyForm" % company_type.capitalize())


def get_existing_company_form(company_type):
    return getattr(axis.company.forms, "AddExisting%sForm" % company_type.capitalize())


class CompanyUrlKwargsMixin(object):
    """Assigns the company type to the kwargs used to reverse urls for the generic templates."""

    def _get_url_kwargs(self, **kwargs):
        kwargs["type"] = self.kwargs["type"]
        return kwargs

    def get_list_url_kwargs(self, **kwargs):
        return self._get_url_kwargs(**kwargs)

    def get_add_url_kwargs(self, **kwargs):
        return self._get_url_kwargs(**kwargs)

    def get_edit_url_kwargs(self, **kwargs):
        return self._get_url_kwargs(**kwargs)

    def get_delete_url_kwargs(self, **kwargs):
        return self._get_url_kwargs(**kwargs)

    def get_cancel_url_kwargs(self, **kwargs):
        return self._get_url_kwargs(**kwargs)


class CompanyMixin(AuthenticationMixin, CompanyUrlKwargsMixin):
    allow_geocoding = True


class LegacyCompanyListRedirectView(RedirectView):
    """
    Temporary view to redirect old legacy links to new Frontend
    """

    def get_redirect_url(self, *args, **kwargs):
        return get_frontend_url("company", self.kwargs["type"])


class LegacyCompanyCreateRedirectView(RedirectView):
    """
    Temporary view to redirect old legacy links to new Frontend
    """

    def get_redirect_url(self, *args, **kwargs):
        return get_frontend_url("company", self.kwargs["type"])


class LegacyCompanyDetailRedirectView(RedirectView):
    """
    Temporary view to redirect old legacy links to new Frontend
    """

    def get_redirect_url(self, *args, **kwargs):
        return get_frontend_url("company", self.kwargs["type"], "detail", self.kwargs["pk"])


class BoundCompaniesAjaxView(AuthenticationMixin, TemplateView):
    """Ajax view for generic objects bound to a company."""

    def get(self, context, **kwargs):
        """Handles AJAX requests separately from normal GET."""
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HttpResponse(
                json.dumps({"html": self.get_formatted_list_data()}),
                content_type="application/json",
            )
        return super(BoundCompaniesAjaxView, self).get(context, **kwargs)

    def get_queryset(self):
        self.admin = self.request.user.is_company_admin
        ModelObj = get_model(self.kwargs["app_label"], self.kwargs["model"])
        self.model = ModelObj.objects.get(id=self.kwargs.get("pk"))
        relationship_ids = self.model.relationships.values_list("company_id", flat=True)
        self.owned = list(
            self.model.relationships.filter(is_owned=True).values_list("company_id", flat=True)
        )
        return Company.objects.filter(id__in=relationship_ids)

    def get_serialized_data(self):
        """Get the serialized data stream."""
        my_relationship_ids = self.request.user.company.relationships.get_companies(ids_only=True)

        queryset = self.get_queryset().values_list(
            "id",
            "name",
            "company_type",
            "users",
            "utilityorganization__electricity_provider",
            "utilityorganization__gas_provider",
        )

        users = []
        if hasattr(self.model, "users"):
            users = self.model.users.all().values(
                "id", "username", "first_name", "last_name", "is_public"
            )

        data = {}
        for comp_list in queryset:
            obj_id, name, company_type, user_id, elec, gas = comp_list
            if company_type not in data.keys():
                data[company_type] = {}
            if obj_id not in data[company_type].keys():
                url = reverse("company:view", kwargs={"type": company_type, "pk": obj_id})
                data[company_type][obj_id] = {
                    "users": [],
                    "name": name,
                    "id": obj_id,
                    "url": url,
                    "to_add": False,
                    "type": company_type,
                    "elec": elec,
                    "gas": gas,
                    "owned": True if obj_id in self.owned else False,
                }
            if obj_id not in my_relationship_ids:
                data[company_type][obj_id]["to_add"] = True
            user_d = next((x for x in users if x["id"] == user_id), None)
            if user_d:
                url = reverse("profile:detail", kwargs={"pk": user_d.get("id")})
                href = '<a href="{}">{} {}</a>'.format(
                    url, user_d.get("first_name"), user_d.get("last_name")
                )
                data[company_type][obj_id]["users"].append(href)
        return data

    def get_formated_element(self, value_dict):
        """Generates an html ``<li>`` element with nested ``<ul>`` if users exist on the obj."""

        li = "<li>"
        details = []
        if value_dict["elec"]:
            details.append("Electric")
        if value_dict["gas"]:
            details.append("Gas")
        details = "&nbsp;({})".format(", ".join(details)) if len(details) else ""
        if value_dict["to_add"]:
            li += "{}{}{}".format(
                value_dict.get("name"), "&nbsp;&#8856;" if value_dict["owned"] else "", details
            )
            if self.admin and value_dict["type"] != self.request.user.company.company_type:
                url = reverse(
                    "relationship:add_id",
                    kwargs={
                        "app_label": "company",
                        "model": "company",
                        "object_id": value_dict["id"],
                    },
                )
                li += "&emsp;<a href='{}'>Add</a>".format(url)
        else:
            li += '<a href="{}">{}</a>{}{}'.format(
                value_dict.get("url"),
                value_dict.get("name"),
                "&nbsp;&#8856;" if value_dict["owned"] else "",
                details,
            )
        if len(value_dict.get("users")):
            li += "<ul><li>" + "</li><li>".join(value_dict["users"]) + "</li></ul>"
        li += "</li>"
        return li

    def get_formatted_list_data(self):
        """Returns the formatted data."""
        formated_data = []
        for key, comp_ids in self.get_serialized_data().items():
            if len(comp_ids.keys()) > 1:
                div_name = next((v[1] for k, v in COMPANY_TYPES_PLURAL.items() if k == key))
            else:
                div_name = next((v[0] for k, v in COMPANY_TYPES_PLURAL.items() if k == key))
            div = '<div class="span-6 last">{}<ul>'.format(div_name)
            for comp_id, comp_value in comp_ids.items():
                div += self.get_formated_element(comp_value)
            div += "</ul></div>"
            formated_data.append(div)
        return "\n".join(formated_data)


# Contacts


# Note that this is the dummy model version
class CompanyContactListView(CompanyMixin, LegacyAxisDatatableView):
    """A basic Contact List for companies"""

    template_name = "company/contact_list.html"
    show_add_button = False

    datatable_options = {
        "columns": [
            (
                "Company Type",
                "company__company_type",
                datatableview.helpers.attrgetter("company.get_company_type_display"),
            ),
            ("Company Name", "company__name"),
            ("Website", "company__home_page"),
            ("Serves Electricity", "company__utilityorganization__electricity_provider"),
            ("Serves Gas", "company__utilityorganization__gas_provider"),
            # ('H-QUITO Accredited', 'company__hvacorganization__hquito_accredited',  # TODO Enable me at 3.8
            (
                "H-QUITO Accredited",
                None,
                datatableview.helpers.attrgetter("company.get_hquito_accredited_display"),
            ),
            ("First Name", "user__first_name"),
            ("Last Name", "user__last_name"),
            ("Email", ["user__email", "company__default_email"]),
            (
                "Address",
                ["company__street_line1", "user__street_line1"],
                datatableview.helpers.attrgetter("company.street_line1"),
            ),
            ("City", ["company__city__name", "user__city__name"]),
            (
                "State",
                ["company__state", "user__state"],
                datatableview.helpers.attrgetter("company.state"),
            ),
            (
                "ZIP Code",
                ["company__zipcode", "user__zipcode"],
                datatableview.helpers.attrgetter("company.zipcode"),
            ),
            ("Title", ["user__title"]),
            (
                "Phone",
                [
                    "user__work_phone",
                    "user__cell_phone",
                    "user__alt_phone",
                    "company__office_phone",
                ],
            ),
            ("User Type", None, "get_column_User_Type_data"),
            ("Last Login", "user__last_login"),
        ],
        "hidden_columns": [
            "Company Type",
            "Website",
            "Serves Electricity",
            "Serves Gas",
            "First Name",
            "Last Name",
            "State",
            "ZIP Code",
            "Title",
            "User Type",
            "Last Login",
        ],
    }

    def has_permission(self):
        if self.request.user.company.company_type in self.request.path:
            return False
        return self.request.user.company.is_active

    def get_datatable_options(self):
        options = self.datatable_options.copy()
        if self.kwargs.get("type") in ["rater", "builder"]:
            columns = []
            for column in options["columns"]:
                if column[0] not in ["Serves Electricity", "Serves Gas"]:
                    columns.append(column)
            options["columns"] = columns
        if self.kwargs.get("type") != "hvac":
            columns = []
            for column in options["columns"]:
                if column[0] not in ["H-QUITO Accredited"]:
                    columns.append(column)
            options["columns"] = columns

        column_labels = [spec[0] for spec in options["columns"]]
        options["hidden_columns"] = [
            name for name in options["hidden_columns"] if name in column_labels
        ]

        return options

    def get_queryset(self):
        """Narrow this based on your company"""
        co_type = self.kwargs["type"]
        companies = Company.objects.filter_by_user(user=self.request.user, show_attached=True)
        companies = companies.filter(company_type=co_type).select_related("city")
        self.company_cities = dict(companies.values_list("id", "city__name"))
        # DEBUG: Uncomment this part to get only the first company with more than 0 users.
        #        The intention is that the resulting list has len(users)+1 rows.
        # from django.db.models import Count
        # companies = companies.annotate(n=Count('users')).filter(n__gt=0)[:1]
        return companies.get_contact_list()

    def get_column_City_data(self, obj, *args, **kwargs):
        return self.company_cities.get(obj.company_id)

    def get_column_Company_Name_data(self, obj, *args, **kwargs):
        return datatableview.helpers.link_to_model(obj.company)

    def get_column_Serves_Electricity_data(self, obj, *args, **kwargs):
        try:
            return datatableview.helpers.make_boolean_checkmark(obj.company.electricity_provider)
        except ObjectDoesNotExist:
            return ""

    def get_column_Serves_Gas_data(self, obj, *args, **kwargs):
        try:
            return datatableview.helpers.make_boolean_checkmark(obj.company.gas_provider)
        except ObjectDoesNotExist:
            return ""

    def get_column_Full_Name_data(self, obj, *args, **kwargs):
        if obj.user:
            return datatableview.helpers.link_to_model(obj.user, text=obj.user.get_full_name())
        return ""

    def get_column_First_Name_data(self, obj, *args, **kwargs):
        if obj.user:
            return obj.user.first_name
        return ""

    def get_column_Last_Name_data(self, obj, *args, **kwargs):
        if obj.user:
            return obj.user.last_name
        return ""

    def get_column_Title_data(self, obj, *args, **kwargs):
        if obj.user:
            return obj.user.title
        return ""

    def get_column_Phone_data(self, obj, *args, **kwargs):
        if obj.user:
            phone_numbers = filter(
                bool,
                [
                    obj.user.work_phone,
                    obj.user.cell_phone,
                    obj.user.alt_phone,
                    "--",
                ],
            )
            phone_numbers = list(phone_numbers)
            return phone_numbers[0]
        return obj.company.office_phone

    def get_column_User_Type_data(self, obj, *args, **kwargs):
        if obj.user:
            if obj.user.is_active:
                if obj.user.is_company_admin:
                    return "Admin"
                return "User"
            return "Contact"
        return "Default"

    def get_column_Email_data(self, obj, *args, **kwargs):
        href = ""
        if obj.user:
            email = obj.user.email
        else:
            email = obj.company.default_email
        if email:
            href = '<a href="mailto:{}">{}</a>'.format(email, email)
        return href

    def get_column_Last_Login_data(self, obj, *args, **kwargs):
        if obj.user and obj.user.last_login:
            tz = self.request.user.timezone_preference
            dts = obj.user.last_login.astimezone(tz)
            return formats.date_format(dts, "SHORT_DATE_FORMAT")
        return ""

    def get_context_data(self, **kwargs):
        context = super(CompanyContactListView, self).get_context_data(**kwargs)
        context["type"] = self.kwargs["type"]

        pretty_title = COMPANY_TYPES_MAPPING.get(self.kwargs["type"])
        context["pretty_title"] = "{} Contact Report".format(pretty_title)

        return context
