""" SampleSet built-in admin configuration. """


import logging

from django.contrib import admin
from django.contrib.auth.models import Group

from .models import SampleSet

__author__ = "Autumn Valenta"
__date__ = "07-22-14 11:32 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSetHomeStatusInline(admin.TabularInline):
    model = SampleSet.home_statuses.through
    fields = ["home_status", "revision", "is_test_home", "is_active"]
    raw_id_fields = ["home_status"]
    max_num = 7
    extra = 1


class SampleSetAdmin(admin.ModelAdmin):
    model = SampleSet
    ordering = ["id"]

    search_fields = ["id", "uuid", "alt_name", "owner__name", "start_date", "confirm_date"]
    date_hierarchy = "start_date"
    list_display = [
        "uuid",
        "alt_name",
        "revision",
        "owner",
        "start_date",
        "confirm_date",
        "is_metro_sampled",
    ]
    list_filter = ["start_date", "confirm_date", "is_metro_sampled", "revision"]

    inlines = (SampleSetHomeStatusInline,)


admin.site.register(SampleSet, SampleSetAdmin)
