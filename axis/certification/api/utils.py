import logging

from django import forms
from django.apps import apps
from django.db.models.query import QuerySet

try:
    from django.db.models.query import ModelIterable

    legacy_queryset = False
except:
    from django.db.models.query import ValuesQuerySet, ValuesListQuerySet

    legacy_queryset = True

from rest_framework import serializers
from django_select2.forms import Select2Widget

from axis.core.fields import ApiModelChoiceField

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


SERIALIZER_FIELD_TYPES = {
    "number": serializers.IntegerField,
    "decimal": serializers.FloatField,
    "text": serializers.CharField,
    "date": serializers.DateField,
    "select": serializers.ChoiceField,
}

FORM_FIELD_TYPES = {
    "number": forms.IntegerField,
    "decimal": forms.FloatField,
    "text": forms.CharField,
    "date": forms.DateField,
    "select": forms.ChoiceField,
}
FORM_WIDGET_TYPES = {
    "textarea": forms.Textarea,
}


class FieldsFromJsonMixin(object):
    """
    Base mixin for examine forms and serializers, building out fields for dynamic fields specified
    in a workflow config's data collection or settings spec.
    """

    CONFIG_KEY_NAME = None  # a key from object_types[type] ('data' or 'settings')

    def get_json_fields(self, object_type, **settings):
        """
        Builds fields from the data spec dictionary that powers the dynamic fields
        (i.e., in config['object_types']['{TYPE}'], either the 'data' or the 'settings' key),
        then prunes away items that declare settings requirements on the certifiable_object.
        """

        fields = {}

        # Compile settings for restricting final fields
        settings["object_type"] = object_type
        if self.instance:
            if isinstance(self.instance, list):
                if len(self.instance) > 0:
                    settings.update(self.instance[0].get_settings())
            elif self.instance.pk:
                settings.update(self.instance.get_settings())

        # Get and filter field data spec
        workflow = self._get_workflow()
        if workflow:  # If an object is brand new it might not have any way to know
            config = workflow.get_config()
            data_spec = config.lookup("object_types", object_type, self.CONFIG_KEY_NAME)
            data_spec = restrict_field_spec(data_spec, settings)
            self._data_spec = data_spec

            # Build fields
            context = {
                "object_type": object_type,
            }
            for field_name, item in data_spec.items():
                fields.update(self.build_json_field(field_name, item, context=context))

        return fields

    def build_json_field(self, name, spec, context):
        """Returns a dictionary of fields to add based on the given field spec."""
        raise NotImplementedError()

    def _get_workflow(self):
        # TODO: Remove this method, rely on context only
        raise NotImplementedError()


class FieldsFromCertifiableObjectSettingsMixin(FieldsFromJsonMixin):
    # Incomplete base class still requiring a build_json_field serializer/form implementation
    CONFIG_KEY_NAME = "settings"

    def _get_workflow(self):
        # TODO: Remove this method, rely on context only
        if hasattr(self, "context") and "workflow" in self.context:
            return self.context["workflow"]

        # FIXME: this is an issue for generalizing the mechanism for Homes
        from ..models import Workflow

        return Workflow.objects.get()


class FieldsFromWorkflowStatusDataMixin(FieldsFromJsonMixin):
    # Incomplete base class still requiring a build_json_field serializer/form implementation
    CONFIG_KEY_NAME = "data"

    def _get_workflow(self):
        # TODO: Remove this method, rely on context only
        if hasattr(self, "context") and "workflow" in self.context:
            return self.context["workflow"]

        if self.instance:
            if isinstance(self.instance, list):
                if len(self.instance) > 0:
                    return self.instance[0].eep_program.workflow
            elif self.instance.pk:
                return self.instance.eep_program.workflow
        return None


class empty:
    pass


def build_serializer_field_from_spec(serializer, field_name, item_spec, context, data=empty):
    """
    Returns a dictionary of serializer fields for this one item_spec to support the field's
    operations.
    """
    from .serializers import DataInfoSerializer, JsonPrimaryKeyField

    model = None  # Only used on FK widgets, but setting depends on the field spec
    fields = {}

    if isinstance(serializer.instance, list) and len(serializer.instance):
        instance = serializer.instance[0]
    elif serializer.instance:
        instance = serializer.instance
    else:
        instance = None

    Field = SERIALIZER_FIELD_TYPES.get(item_spec["type"], serializers.CharField)

    field_kwargs = {
        "label": item_spec["label"],
        "required": False,
        "allow_null": True,
        "validators": item_spec.get("validators", []),
    }

    if "choices" in item_spec:
        choices = item_spec["choices"]
        if callable(choices):
            choices = choices()
        field_kwargs["choices"] = choices

    if item_spec["type"] == "date":
        field_kwargs["input_formats"] = ["%m/%d/%Y", "%Y-%m-%d"]
    elif item_spec["type"] == "text":
        field_kwargs["allow_blank"] = True

    if "value" in item_spec:
        value_getter = item_spec["value"]
        if isinstance(value_getter, dict):
            value_getter = value_getter.get(context["object_type"])
        if value_getter and instance:
            value = value_getter(
                **{
                    "instance": instance,
                    "field_name": field_name,
                    "item_spec": item_spec,
                    "context": context,
                }
            )
            # field_kwargs['default'] = value

    if "model" in item_spec:
        model = apps.get_model(item_spec["model"])

    if "api_widget" in item_spec:
        # The form field version is handling all the actual footwork in this case.
        # The serializer field just needs to accept the right model from a limited queryset.
        widget = item_spec["api_widget"]
        if callable(widget):
            widget = widget()
        viewset = widget.viewset_class(request=context["request"])

        if model:
            Field = JsonPrimaryKeyField
            if data is not empty:
                field_kwargs["queryset"] = viewset.filter_queryset(viewset.get_queryset())
            else:
                field_kwargs["read_only"] = True  # stops us from needing 'queryset'
        else:
            Field = serializers.ChoiceField
            field_kwargs["allow_blank"] = True

            # NOTE: It's possible we need to support non-Model viewsets instead of assuming a Model
            # version will return a choices-coerceable object list
            if data is not empty:  # Avoid queryset/choices crunching unless we're doing validation
                object_list = viewset.filter_queryset(viewset.get_queryset())

                # This is the wrong code branch if the object_list is actually a real queryset.
                # Notify the developer instead of allowing the non-ForeignKey code to run.
                bad_config = False
                if not legacy_queryset:
                    if isinstance(object_list.iterator(), ModelIterable):
                        bad_config = True
                else:
                    if isinstance(object_list, QuerySet) and not isinstance(
                        object_list, (ValuesQuerySet, ValuesListQuerySet)
                    ):
                        bad_config = True

                if bad_config:
                    raise ValueError(
                        "You forgot to add {'model': '%s.%s'} to the '%s' field spec."
                        % (
                            object_list.model._meta.app_label,
                            object_list.model._meta.object_name,
                            field_name,
                        )
                    )

                # The display label part of this choices list is completely unimportant
                field_kwargs["choices"] = [
                    (obj.get("pk", obj.get("name")), "(redacted)") for obj in object_list
                ]
            else:
                field_kwargs["choices"] = []
                field_kwargs["read_only"] = True

    if model:
        # Add an extra '*_info' field to represent the user-friendly version of the current value.
        info_field = DataInfoSerializer(source=field_name, read_only=True)
        info_field._model = model  # See note on serializer class about this strategy
        fields[field_name + "_info"] = info_field

    fields[field_name] = Field(**field_kwargs)

    return fields


def build_form_field_from_spec(form, field_name, item_spec, context, data=empty):
    """
    Returns a dictionary of form fields for this one item_spec to support the field's operations.
    """

    fields = {}

    Field = FORM_FIELD_TYPES.get(item_spec["type"], forms.CharField)
    field_kwargs = {
        "label": item_spec["label"],
        "required": False,
        "validators": item_spec.get("validators", []),
    }

    # Computed fields supply a value callback of their own, but we build a form field anyway if
    # asked, disabled, so that the computed value can be shown in a readonly way that matches the
    # surrounding fields.
    is_computed = False
    if "value" in item_spec:
        value_spec = item_spec["value"]
        if isinstance(value_spec, dict):
            value_spec = value_spec.get(context["object_type"])

        # We don't care what the computed value is, only that it has one or not for this object_type
        is_computed = bool(value_spec)

    if "choices" in item_spec:
        choices = item_spec["choices"]
        if callable(choices):
            choices = choices()
        field_kwargs["choices"] = choices

    if "widget_type" in item_spec:
        field_kwargs["widget"] = FORM_WIDGET_TYPES.get(item_spec["widget_type"])

    if "api_widget" in item_spec:
        Field = ApiModelChoiceField
        widget = item_spec["api_widget"]
        if callable(widget):
            widget = widget()
        field_kwargs["widget"] = widget

    field = Field(**field_kwargs)

    # Add any attrs to the widget for rendering

    # Resolve lazy callables
    attrs = item_spec.get("attrs", {}).copy()
    type_attrs = attrs.get(context["object_type"], {})
    attrs.update(type_attrs)
    for attr, value in attrs.items():
        if callable(value):
            attrs[attr] = value(field_name, form.instance)

    # TEMP: TRC sends us data automatically and so we disabled those fields indefinitely, but during
    # local testing we don't want to be locked out of supplying the value up front.
    if ("disabled" in attrs) and (not is_computed) and (data.get(field_name) is None):
        del attrs["disabled"]

    field.widget.attrs.update(attrs)

    fields[field_name] = field

    return fields


def restrict_field_spec(field_spec, settings, predicate=None):
    """Returns only items from the larger spec that apply explicitly to the target's settings."""
    # This is a key part of how the ConfigReader returns data specs in its convenience methods,
    # allowing the returned specs to be filtered by the object_type's individual requirements.
    new_spec = {}

    if predicate is None:
        predicate = lambda spec: True

    # Copy items from the field_spec that either have no special settings or whose settings match
    # those provided in the ``settings`` dictionary.
    for name, spec in field_spec.items():
        keep = True

        requirements = spec.get("settings", {})
        for req_name, allowed_values in requirements.items():
            if not isinstance(allowed_values, (tuple, list, set)):
                allowed_values = [allowed_values]
            if settings.get(req_name) not in allowed_values:
                keep = False
            elif not predicate(spec):
                keep = False

        if keep:
            new_spec[name] = field_spec[name]

    return new_spec
