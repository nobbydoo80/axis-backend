"""inspection_grading.py: """

__author__ = "Artem Hruzd"
__date__ = "12/18/2019 11:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.user_management.models import InspectionGrade
from django.contrib import admin


class InspectionGradeAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "approver", "qa_status")
    list_display = (
        "user",
        "approver",
        "letter_grade",
        "numeric_grade",
        "qa_status",
        "graded_date",
        "notes",
    )
    list_filter = (
        "letter_grade",
        "numeric_grade",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "approver__first_name",
        "approver__last_name",
        "qa_status__id",
        "notes",
    )


admin.site.register(InspectionGrade, InspectionGradeAdmin)
