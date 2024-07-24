"""training.py: """


from axis.user_management.models import Accreditation
from django.contrib import admin
from django.contrib.admin.decorators import register

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 15:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


@register(Accreditation)
class AccreditationAdmin(admin.ModelAdmin):
    raw_id_fields = ("trainee",)
    list_display = ("trainee", "accreditation_id", "accreditation_cycle", "notes", "created_at")
    search_fields = ("trainee__first_name", "trainee__last_name", "name")
    list_filter = ("role",)
    date_hierarchy = "created_at"
