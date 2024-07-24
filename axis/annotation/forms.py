"""forms.py: Django annotation"""


import logging

from django import forms
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from axis.annotation.messages import NWESHMeetsOrBeatsAnsweredNo
from .models import Annotation

__author__ = "Autumn Valenta"
__date__ = "3/5/12 11:25 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
    "Steven Klass",
]

log = logging.getLogger(__name__)


FIELD_CLASSES = {
    "multiple-choice": forms.ChoiceField,
    "integer": forms.IntegerField,
    "float": forms.FloatField,
}


class RequiredAnnotationsForm(forms.Form):
    """
    This will create a custom form with all of the required annotations listed.  Similar to a
    formset but more concrete in that there is no extra and each one is it's own field.

    This should create a form which will allow you to add annotations quickly.

    Utility Number      <______>
    Owner Builder       <______>

    """

    content_type = None
    object_id = None

    def __init__(self, *args, **kwargs):
        from axis.customer_neea.utils import DEPRECATED_BOP_VALUES

        user = kwargs.pop("user", None)
        annotations = kwargs.pop("annotations", {})
        instance = kwargs.pop("instance", None)
        kwargs.pop("partial", None)  # serializer stand-in hack
        super(RequiredAnnotationsForm, self).__init__(*args, **kwargs)

        self.instance = instance
        self.user = user

        if instance:
            self.content_type = ContentType.objects.get_for_model(instance)
            self.object_id = instance.pk

        self._type_objects = {t.slug: t for t in annotations}
        for annotation_type, annotation in annotations.items():
            field_kwargs = {
                "label": annotation_type.name,
                "required": annotation_type.is_required,
                "initial": annotation.content if annotation else None,
            }
            FieldClass = FIELD_CLASSES.get(annotation_type.data_type, forms.CharField)

            if annotation_type.data_type == "multiple-choice":
                values = annotation_type.get_valid_multiplechoice_values()
                for i, value in enumerate(values):
                    if value in DEPRECATED_BOP_VALUES and field_kwargs["initial"] != value:
                        values.pop(i)
                field_kwargs["choices"] = [("", "---------")] + list(zip(*(values,) * 2))

            # TODO: When this needs to be enabled, we need a factory that returns the correct field
            # for the given data_type value.
            # elif annotation_type.data_type in AUTOCOMPLETE_TYPES:
            #     FieldClass = AutoCompleteSelectField
            #     field_kwargs.update({
            #         'id': 'my_{}'.format(annotation_type.data_type)})
            #         'help_text': None,
            #     })

            self.fields[annotation_type.slug] = FieldClass(**field_kwargs)

    def save(self, **kwargs):
        """Logic for committing changes and implicit deletions to the database."""
        # We accept kwargs here to let the form stand in place of a restframework Serializer for
        # the annotations api submission process.
        for k, content in self.cleaned_data.items():
            annotation_type = self._type_objects[k]

            if content in ["", None]:
                self._delete_annotation(annotation_type)
            else:
                self._save_annotation(annotation_type, content)
        return self.instance

    def is_valid(self, raise_exception=False):
        # Helps the form blend in as a DRF serializer.

        is_valid = super(RequiredAnnotationsForm, self).is_valid()
        if raise_exception and not is_valid:
            raise serializers.ValidationError(self.errors)
        return is_valid

    def _delete_annotation(self, type, content=None):
        # Delete annotations whose values changed to something blank.
        try:
            instance = type.annotation_set.get(
                content_type=self.content_type, object_id=self.object_id
            )
        except Annotation.DoesNotExist:
            # Annotation was perhaps sent blank, wasn't necessarily *changed* to blank
            pass
        else:
            instance.delete()
            try:
                log.debug(
                    "Removed %s [%s] Annotation %s",
                    self.content_type,
                    self.object_id,
                    instance.type,
                    content,
                )
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass

    def _save_annotation(self, type, content):
        try:
            log.debug(
                "%s [%s] Annotation %s : %s", self.content_type, self.object_id, type, content
            )
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        instance, created = Annotation.objects.get_or_create(
            content_type=self.content_type,
            object_id=self.object_id,
            type=type,
            defaults={"content": content},
        )
        if not created and instance.content != content:
            instance.content = content
            instance.save()

        if self.user and type.slug == "beat-annual-fuel-usage" and instance.content.lower() == "no":
            context = {"url": self.instance.get_absolute_url(), "text": "{}".format(self.instance)}
            NWESHMeetsOrBeatsAnsweredNo(url=self.instance.get_absolute_url()).send(
                user=self.user, context=context
            )


class SimpleAnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ("content", "is_public")
