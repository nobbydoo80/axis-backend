"""admin.py: Django annotation"""


import logging

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Type, Annotation

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AnnotationTypeAdmin(admin.ModelAdmin):
    """Inline Document"""

    model = Type
    list_display = ("name", "slug", "data_type", "is_unique", "description")
    search_fields = ("name", "data_type", "slug")
    filter_horizontal = ("applicable_content_types",)
    readonly_fields = ("slug",)


class AnnotationInlineForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ("id", "type", "content")

    def __init__(self, *args, **kwargs):
        super(AnnotationInlineForm, self).__init__(*args, **kwargs)
        if getattr(self, "instance", None) and self.instance:
            try:
                initial = self.instance.content
                annotation_type = self.instance.type
            except ObjectDoesNotExist:
                pass
            else:
                required = annotation_type.is_required
                self.fields["type"].queryset = Type.objects.filter(id=annotation_type.id)
                self.fields["type"].widget.attrs["editable"] = False

                if annotation_type.data_type == "multiple-choice":
                    choices = [("", "---------")]
                    choices += zip(*(annotation_type.get_valid_multiplechoice_values(),) * 2)
                    self.fields["content"] = forms.ChoiceField(
                        choices=choices,
                        label=annotation_type.name,
                        required=required,
                        initial=initial,
                    )
                elif annotation_type.data_type == "integer":
                    self.fields["content"] = forms.IntegerField(required=required)
                elif annotation_type.data_type == "float":
                    self.fields["content"] = forms.FloatField(required=required)
                else:
                    self.fields["content"] = forms.CharField(
                        label=annotation_type.name, required=required, initial=initial
                    )


class AnnotationAdmin(GenericTabularInline):
    """Inline Document"""

    form = AnnotationInlineForm
    model = Annotation
    extra = 0


class GenericAnnotationAdmin(admin.ModelAdmin):
    model = Annotation
    list_display = ("type", "content", "content_type", "object_id", "is_public")
    list_filter = ("is_public",)
    search_fields = ("type__name", "type__slug", "object_id")
    date_hierachy = "created_on"
    raw_id_fields = ("type", "user")


admin.site.register(Type, AnnotationTypeAdmin)
admin.site.register(Annotation, GenericAnnotationAdmin)
