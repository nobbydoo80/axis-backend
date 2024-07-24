"""admin.py - Axis"""

import logging

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import EkotropeAuthDetails, Project
from .tasks import spread_credentials

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "8/10/20 09:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

User = get_user_model()


class EkotropeAuthForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EkotropeAuthForm, self).__init__(*args, **kwargs)

        users = User.objects.filter(is_active=True, company__isnull=False)
        users = users.order_by("last_name", "first_name")
        keys = "id", "first_name", "last_name", "company__name", "company__company_type"
        users = users.values_list(*keys)
        users = [(_id, f"{_fir} {_last} - {_co} ({_ct})") for _id, _fir, _last, _co, _ct in users]
        self.fields["user"].choices = [("", 10 * "-")] + users

    class Meta:
        model = EkotropeAuthDetails
        fields = "__all__"


class EkotropeAuthAdmin(admin.ModelAdmin):
    """Ekotrope admin"""

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__company__name",
    ]
    list_display = ["_username", "_name", "_company", "username"]
    actions = ["spread_credentials_to_others"]
    form = EkotropeAuthForm

    def _username(self, instance):
        return instance.user.username

    def _name(self, instance):
        return f"{instance.user.first_name} {instance.user.last_name}"

    def _company(self, instance):
        try:
            return f"{instance.user.company.name}"
        except AttributeError:
            return "-"

    def spread_credentials_to_others(self, request, queryset):
        """Spread Credentials"""

        company_ids = list(set(queryset.values_list("user__company_id", flat=True)))
        for company_id in company_ids:
            spread_credentials(company_id)
        if len(company_ids) == 1:
            message_bit = "1 company"
        else:
            message_bit = "%s companies" % len(company_ids)
        self.message_user(request, "%s successfully had there credentials spread." % message_bit)

    spread_credentials_to_others.short_description = "Spread auth credentials to all company users"


admin.site.register(EkotropeAuthDetails, EkotropeAuthAdmin)


class EkotropeProjectAdmin(admin.ModelAdmin):
    """Ekotrope admin"""

    search_fields = [
        "id",
        "company__name",
    ]
    list_display = [
        "id",
        "created_date",
        "_company",
        "_name",
        "_model",
        "_builder",
        "import_failed",
    ]

    def _name(self, instance):
        return instance.data.get("name")

    def _company(self, instance):
        return instance.company.name

    def _model(self, instance):
        return instance.data.get("model")

    def _builder(self, instance):
        return instance.data.get("builder")

    def delete_model(self, request, obj):
        super(EkotropeProjectAdmin, self).delete_model(request, obj)


admin.site.register(Project, EkotropeProjectAdmin)
