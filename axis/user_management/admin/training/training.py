"""training.py: """


from axis.user_management.models import Training
from django.contrib import admin

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 15:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingStatusesInline(admin.TabularInline):
    model = Training.statuses.through
    raw_id_fields = ("training", "company", "approver")


class TrainingAdmin(admin.ModelAdmin):
    raw_id_fields = ("trainee",)
    exclude = ("statuses",)
    inlines = (TrainingStatusesInline,)
    search_fields = ("name", "trainee__first_name", "trainee__last_name", "address")
    list_filter = ("training_type", "attendance_type")
    list_display = ("name", "trainee", "notes", "updated_at", "created_at")


admin.site.register(Training, TrainingAdmin)
