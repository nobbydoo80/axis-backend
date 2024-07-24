"""admin.py: Django sponsor_preferences"""

__author__ = "Steven Klass"
__date__ = "3/2/12 2:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command

from axis.company.models import (
    SponsorPreferences,
)

log = logging.getLogger(__name__)

User = get_user_model()


@admin.register(SponsorPreferences)
class SponsorPreferencesAdmin(admin.ModelAdmin):
    list_display = ("sponsor", "sponsored_company")
    raw_id_fields = ("sponsor", "sponsored_company")
    search_fields = ("sponsor__name", "sponsored_company__name")

    def save_model(self, request, obj, form, change):
        """
        Update permissions and delete cache after save
        :param request:
        :param obj:
        :param form:
        :param change:
        :return:
        """
        super().save_model(request, obj, form, change)
        call_command("set_permissions", company_id=obj.sponsored_company.id, no_confirm=True)
        cache.clear()
