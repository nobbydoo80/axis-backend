"""views.py: Django impersonate"""


import logging

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.utils.decorators import method_decorator

from datatableview.views.legacy import LegacyDatatableView
from datatableview import helpers

from django.contrib.auth import get_user_model

__author__ = "Steven Klass"
__date__ = "3/25/13 1:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class ImpersonateListView(LegacyDatatableView):
    template_name = "impersonate/user_list.html"

    datatable_options = {
        "columns": [
            ("Impersonate", None, "get_column_Impersonate_data"),
            ("Full Name", ["first_name", "last_name", "is_active"], "get_column_Full_Name"),
            ("Username", "username", helpers.link_to_model),
            ("Company", "company__name"),
            ("Company Type", "company__company_type"),
            ("Admin", "is_company_admin", helpers.make_boolean_checkmark),
        ],
        "unsortable_columns": ["Impersonate"],
    }

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(ImpersonateListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.filter(is_superuser=False).select_related("company")

    def get_column_Impersonate_data(self, obj, *args, **kwargs):
        href = '<a href="{}"><i class="fa fa-sign-in"></i> Log in</a>'
        url = reverse("impersonate-start", kwargs={"uid": obj.id})
        if self.request.GET.get("next"):
            url += "?next={}".format(self.request.GET.get("next"))
        return href.format(url)

    def get_column_Full_Name(self, obj, *args, **kwargs):
        name = obj.get_full_name()
        if not obj.is_active:
            name = (
                '<span class="text-muted">'
                + name
                + ' &nbsp;&nbsp; <i class="fa fa-user-times" title="Inactive"></i></span>'
            )
        return name

    def get_column_Company_Type_data(self, obj, *args, **kwargs):
        try:
            return obj.company.get_company_type_display()
        except AttributeError:
            return ""

    def get_column_Company_data(self, obj, *args, **kwargs):
        if obj.company:
            return helpers.link_to_model(obj.company)
        return ""

    def get_context_data(self, **kwargs):
        context = super(ImpersonateListView, self).get_context_data(**kwargs)
        if not self.request.headers.get(
            "x-requested-with"
        ) == "XMLHttpRequest" and self.request.GET.get("next"):
            context["next"] = self.request.GET.get("next")
        return context
