"""admin.py: Django scheduling"""


from django.contrib import admin
from axis.scheduling.models import ConstructionStatus, ConstructionStage, TaskType, Task

__author__ = "Gaurav Kapoor"
__date__ = "6/25/12 9:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Gaurav Kapoor",
    "Steven Klass",
]

admin.site.register(ConstructionStatus)


class ConstructionStatusInline(admin.TabularInline):
    model = ConstructionStatus
    list_display = ("stage", "start_date")
    can_delete = False
    extra = 1


class ConstructionStageAdmin(admin.ModelAdmin):
    inlines = (ConstructionStatusInline,)


class TaskTypeAdmin(admin.ModelAdmin):
    raw_id_fields = ("company",)
    list_display = ("name", "company", "content_type", "priority")


class TaskAdmin(admin.ModelAdmin):
    list_display = ("task_type", "datetime", "assigner", "get_assignees", "status", "is_public")
    raw_id_fields = ("assignees", "assigner", "home")

    def get_queryset(self, request):
        return super(TaskAdmin, self).get_queryset(request).prefetch_related("assignees")

    def get_assignees(self, obj):
        return "\n".join([user.get_full_name() for user in obj.assignees.all()])


admin.site.register(ConstructionStage, ConstructionStageAdmin)
admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(Task, TaskAdmin)
