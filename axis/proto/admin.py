import logging

from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from . import models, merge

__author__ = "Autumn Valenta"
__date__ = "8/15/18 1:36 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def methodattrs(**kwargs):
    def decorator(f):
        for k, v in kwargs.items():
            setattr(f, k, v)
        return f

    return decorator


def resolved_object(obj, styles=[]):
    content_object = obj.content_object
    if content_object:
        return mark_safe(
            '<a style="{}" href="{}">{}</a>'.format(
                ";".join(styles),
                content_object.get_absolute_url(),
                content_object,
            )
        )
    return "(None)"


class CandidateInline(admin.TabularInline):
    model = models.Candidate
    fields = ("id", resolved_object, "object_id", "levenshtein_distance", "profile_delta")
    readonly_fields = ("id", resolved_object)
    extra = 0


@admin.register(models.ProtoObject)
class ProtoObjectAdmin(admin.ModelAdmin):
    search_fields = (
        "content_type__model",
        "content_type__app_label",
        "data",
        "data_profile",
        "object_id",
        "selected_object_id",
        "candidate__id",
        "import_error",
        "import_traceback",
    )
    list_display = (
        "id",
        "_model",
        "_content_object",
        "_candidates",
        "selected_object_id",
        "_data_profile",
        "owner",
        "date_created",
        "import_failed",
        "import_error",
    )
    list_filter = ("import_failed",)  # 'content_type__app_label')
    inlines = (CandidateInline,)

    def get_queryset(self, request):
        queryset = super(ProtoObjectAdmin, self).get_queryset(request)
        queryset = queryset.annotate(Count("candidate")).filter(candidate__count__gt=0)
        return queryset

    @methodattrs(short_description="Model")
    def _model(self, obj):
        return ".".join((obj.content_type.model, obj.content_type.app_label))

    @methodattrs(short_description="Resolved object", allow_tags=True)
    def _content_object(self, obj):
        return resolved_object(obj)

    @methodattrs(short_description="Candidates", allow_tags=True)
    def _candidates(self, obj):
        n = obj.candidate_set.count()
        if n:
            return '<a href="/admin/proto/candidate/?proto_object_id={}">{}</a>'.format(obj.id, n)
        return "(None)"

    @methodattrs(short_description="Data profile")
    def _data_profile(self, obj):
        return obj.data_profile[:10]


@admin.register(models.Candidate)
class CandidateAdmin(admin.ModelAdmin):
    search_fields = (
        "content_type__model",
        "content_type__app_label",
        "proto_object__id",
        "object_id",
    )
    list_display = (
        "id",
        "_proto_object",
        "_content_object",
        "levenshtein_distance",
        "profile_delta",
    )
    actions = (
        # 'action_indentify_merges',
        # 'action_reject',
        "action_select",
        # 'action_realize',
        "action_home_merge",
    )

    raw_id_fields = ("proto_object",)

    def has_add_permission(self, request):
        return False

    def lookup_allowed(self, lookup, value):
        special_filters = [
            "proto_object__selected_object_id__isnull",
            "proto_object__object_id__isnull",
        ]
        if lookup in special_filters:
            return True
        return super(CandidateAdmin, self).lookup_allowed(lookup, value)

    @methodattrs(short_description="ProtoObject", allow_tags=True)
    def _proto_object(self, obj):
        def get_color(h):
            modifier = 0.5  # Half the colors so they're darker on average
            r, g, b = h[0:2], h[2:4], h[4:6]
            return "rgb({},{},{})".format(
                *[
                    int(int(r, 16) * modifier),
                    int(int(g, 16) * modifier),
                    int(int(b, 16) * modifier),
                ]
            )

        proto_obj = obj.proto_object

        styles = [
            "color: {}".format(get_color(proto_obj.data_profile)),
        ]

        if proto_obj.content_object is None and obj.levenshtein_distance == 0:
            styles.append("font-weight: bold")

        # has_high_confidence_match = proto_obj.candidate_set.filter(**{
        #     'levenshtein_distance': 0,
        # }).exists()
        # if has_high_confidence_match:
        #     styles.append('font-weight: bold')

        content_object = proto_obj.content_object
        if content_object:
            proto_obj_repr = "[MATCHED] {}".format(content_object)
        else:
            proto_obj_repr = "{label}: {id}, {hash}".format(
                **{
                    "label": self._model(obj),
                    "id": proto_obj.id,
                    "hash": proto_obj.data_profile[:10],
                }
            )

        display = '<a style="{style}" href="/admin/proto/protoobject/{proto_obj_id}/">{repr}</a>'
        return display.format(
            **{
                "proto_obj_id": proto_obj.id,
                "repr": proto_obj_repr,
                "style": ";".join(styles),
            }
        )

    @methodattrs(short_description="Model")
    def _model(self, obj):
        return ".".join((obj.content_type.model, obj.content_type.app_label))

    @methodattrs(short_description="Candidate", allow_tags=True)
    def _content_object(self, obj):
        styles = []
        extra = ""

        proto_obj = obj.proto_object

        if proto_obj.content_object is None and obj.levenshtein_distance == 0:
            styles.append("font-weight: bold")

        selected_id = obj.proto_object.selected_object_id
        if selected_id == obj.object_id:
            styles.append("background-color: yellow")
            extra += " <b>(SELECTED)</b>"

        candidate_repr = resolved_object(obj, styles=styles)

        return candidate_repr + extra

    # @methodattrs(short_description='')
    # def action_indentify_merges(self, request, queryset):
    #     # We don't care about the provided queryset (we expect it to be empty)
    #     # Use the whole set of objects.
    #     from axis.home.models import Home
    #     queryset = Home.objects.filter_by_user()
    #     merge.identify_merges(queryset=queryset)

    @methodattrs(short_description="[SELECT] Mark selected candidates for merge during FINALIZE")
    def action_select(self, request, queryset):
        for candidate in queryset.iterator():
            candidate.proto_object.selected_object_id = candidate.object_id
            candidate.proto_object.save()

    @methodattrs(
        short_description="[FINALIZE ALL] Merge all proto-object data to whichever candidate was SELECTED"
    )
    def action_realize(self, request, queryset):
        pass

    @methodattrs(
        short_description="[MERGE TO EXISTING] Merge selected candidates into their existing proto-object"
    )
    def action_home_merge(self, request, queryset):
        from .discover import HomeDiscoverer

        discoverer = HomeDiscoverer()

        for candidate in queryset:
            master_obj = candidate.proto_object.content_object
            obj = candidate.content_object

            # Consolidate all existing data fingerprints to the master instance
            discoverer.redirect(obj, to=master_obj)

            # Perform merge
            discoverer.axis_merge(obj, to=master_obj)
