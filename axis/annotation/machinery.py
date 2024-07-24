"""machinery.py: Django filehandling"""


import logging
import re

from django.contrib.contenttypes.models import ContentType

from axis import examine
from .models import Annotation
from .forms import SimpleAnnotationForm

__author__ = "Autumn Valenta"
__date__ = "2/25/15 10:01 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


def annotations_machinery_factory(model, bases=None, type_slug=None, form_class=None, **attrs):
    from axis.core.api import annotations_viewsets

    if bases is None:
        bases = (BaseAnnotationExamineMachinery,)

    attrs.update(
        {
            "model_name": model._meta.model_name,
            "type_name": "%s_annotations" % (model._meta.model_name,),
            "api_provider": annotations_viewsets[model.__name__],
            "content_type_id": ContentType.objects.get_for_model(model).pk,
        }
    )

    # Don't shadow something on the base if the local kwarg is unsest
    if type_slug:
        attrs["annotation_type_slug"] = type_slug
        attrs["verbose_name"] = re.sub(r"[-_]", " ", type_slug).capitalize()
    if form_class:
        attrs["form_class"] = form_class

    safe_type = type_slug.replace("-", "_")
    Machinery = type(str("%sAnnotationsMachinery_%s" % (model.__name__, safe_type)), bases, attrs)
    return Machinery


class BaseAnnotationExamineMachinery(examine.ExamineMachinery):
    """Generic machinery for a formset of Annotation instances."""

    model = Annotation
    form_class = SimpleAnnotationForm

    content_type_id = None
    annotation_type_slug = None

    verbose_name = "Note"
    verbose_name_plural = "Notes"

    edit_name = ""
    edit_icon = "pencil-square-o"
    save_name = ""
    save_icon = "floppy-o"
    delete_name = ""
    delete_icon = "trash-o"

    regionset_template = "examine/annotation/note_regionset.html"
    region_template = "examine/annotation/note_region.html"
    detail_template = "examine/annotation/note_detail.html"
    form_template = "examine/annotation/note_form.html"

    def __init__(self, *args, **kwargs):
        if kwargs.get("objects") and self.annotation_type_slug:
            kwargs["objects"] = kwargs["objects"].filter(type__slug=self.annotation_type_slug)
        super(BaseAnnotationExamineMachinery, self).__init__(*args, **kwargs)

    def can_delete_object(self, instance, user=None):
        if instance.user == user or (user and user.is_superuser):
            return True
        return False

    def can_edit_object(self, instance, user=None):
        if user and (instance.user == user or user.is_superuser):
            return True
        return False

    def get_context(self):
        context = super(BaseAnnotationExamineMachinery, self).get_context()
        context.update(
            {
                "type": self.annotation_type_slug,
                "content_type": self.content_type_id,
            }
        )
        return context

    def get_region_dependencies(self):
        return {
            self.model_name: [
                {
                    "field_name": "id",
                    "serialize_as": "object_id",
                }
            ],
        }
