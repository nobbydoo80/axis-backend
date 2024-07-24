"""admin.py: Django remrate"""


import logging
from django.contrib import admin
from axis.company.models import Company
from .models import Simulation

__author__ = "Steven Klass"
__date__ = "8/11/13 2:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)


class SimilarInline(admin.TabularInline):
    model = Simulation.similar.through
    fields = ["from_simulation"]
    fk_name = "from_simulation"
    raw_id_fields = ("from_simulation",)
    extra = 0


class ReferenceInline(admin.TabularInline):
    model = Simulation.references.through
    fields = ["from_simulation"]
    fk_name = "from_simulation"
    raw_id_fields = ("from_simulation",)
    extra = 0


class SimulationAdmin(admin.ModelAdmin):
    search_fields = [
        "company__name",
        "remrate_user__username",
        "building__filename",
        "building__project__name",
    ]
    list_display = (
        "name",
        "company",
        "remrate_user",
        "sync_status",
        "get_similar",
        "get_references",
        "blg_file",
    )
    readonly_fields = (
        "_source_result_number",
        "simulation_date",
        "version",
        "rating_number",
        "sync_status",
        "building_run_flag",
        "export_type",
        "number_of_runs",
        "get_similar",
        "get_references",
        "blg_file",
    )
    actions = [
        "assign_references",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("rating_number", "simulation_date", "sync_status"),
                    ("company", "remrate_user"),
                    ("version", "flavor"),
                    ("building_run_flag", "number_of_runs"),
                    ("_source_result_number", "export_type", "blg_file"),
                )
            },
        ),
        (
            "Advanced options",
            {"classes": ("collapse",), "fields": (("get_similar",), ("get_references",))},
        ),
    )
    # exclude = ('similar', 'references')
    # inlines = (SimilarInline, ReferenceInline)

    def name(self, obj):
        return "{}".format(obj)

    def sync_status(self, obj):
        return "%s" % obj.building.get_sync_status_display()

    def blg_file(self, obj):
        return obj.building.filename

    blg_file.short_description = "Filename"

    def get_similar(self, obj):
        return "\n".join(["{}".format(x) for x in obj.similar.all()])

    get_similar.short_description = "Similar Homes"

    def get_references(self, obj):
        return "\n".join(["{}".format(x) for x in obj.references.all()])

    get_references.short_description = "Reference Homes"

    def save_model(self, request, obj, form, change):
        result = super(SimulationAdmin, self).save_model(request, obj, form, change)
        if "company" in form.changed_data or "remrate_user" in form.changed_data:
            for s_obj in list(obj.references.all()) + [obj]:
                if s_obj in obj.references.all():
                    s_obj.company = form.cleaned_data.get("company")
                    s_obj.remrate_user = form.cleaned_data.get("remrate_user")
                    s_obj.save()
                building = s_obj.building
                building.company = form.cleaned_data.get("company")
                building.remrate_user = form.cleaned_data.get("remrate_user")
                building.save()
        return result

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "company":
            kwargs["queryset"] = Company.objects.filter(remrate_user_ids__isnull=False).distinct()
        return super(SimulationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def assign_references(self, request, queryset):
        results = []
        for simulation in queryset:
            results.append(simulation.assign_references_and_similar())
        self.message_user(request, "<br>".join(results))

    assign_references.short_description = "Assign References and Similar"


admin.site.register(Simulation, SimulationAdmin)
