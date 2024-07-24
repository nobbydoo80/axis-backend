import os
import logging

from django.core.exceptions import ValidationError

from rest_framework import serializers

from django.contrib.auth import get_user_model
from axis.core.utils import RemoteIdentifiersMixin
from axis.company.models import Company
from axis.eep_program.models import EEPProgram
from ..configs.base import get_state_machine
from .. import models
from .. import strings
from .utils import (
    build_serializer_field_from_spec,
    FieldsFromCertifiableObjectSettingsMixin,
    FieldsFromWorkflowStatusDataMixin,
)


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


# JSON config data serialization tools
class SerializersFieldsFromJsonMixin(object):
    def get_fields(self):
        fields = super(SerializersFieldsFromJsonMixin, self).get_fields()
        settings = self.get_json_fields_settings()
        fields.update(self.get_json_fields(**settings))
        return fields

    def get_json_fields(self, object_type, **settings):
        fields = super(SerializersFieldsFromJsonMixin, self).get_json_fields(
            object_type, **settings
        )

        # Strip away serializer fields for data not represented in the patch request.
        # This is important to preserve 'data' key-values on the instance that aren't represented
        # in the UI used to perform this update.
        if hasattr(self, "initial_data"):
            for field_name in fields.keys():
                if field_name not in self.initial_data:
                    del fields[field_name]

        return fields

    def get_json_fields_settings(self):
        settings = {
            "object_type": self.context["type"],
        }
        if "json_fields_settings" in self.context:
            settings.update(self.context["json_fields_settings"])
        return settings

    def build_json_field(self, name, spec, context):
        context.update(self.context)
        kwargs = {}
        if hasattr(self, "initial_data"):
            kwargs["data"] = self.initial_data
        return build_serializer_field_from_spec(self, name, spec, context=context, **kwargs)

    def validate(self, data):
        # Normalize field formats that passed validation but need massaging for storage purposes.
        # Transformations of the data here should be done with confidence because the serializer
        # fields already validated the incoming data.

        # Rich decimal numbers
        if hasattr(self, "_data_spec"):
            comma_fields = ("dollar", "rich_decimal")
            for field, spec in self._data_spec.items():
                if spec.get("specialized_type") in comma_fields and field in data:
                    data[field] = float(data[field].replace(",", ""))

        return data

    def save(self, *args, **kwargs):
        # We don't want super()'s logic to try and save self.validated_data to the instance, because
        # it's going to try, even though the field's list is blank on the serializers (???).

        validated_data = kwargs[self.CONFIG_KEY_NAME]
        workflow = self._get_workflow()

        # Allow workflow config hook to run
        forward_kwargs = self.instance.prepare_save(validated_data, workflow=workflow)

        # Only save the targetted data attribute.
        setattr(self.instance, self.CONFIG_KEY_NAME, validated_data)
        self.instance.save()

        # Allow workflow config hook to run
        self.instance.post_save(validated_data, workflow=workflow, **forward_kwargs)

        return self.instance


class CertifiableObjectSettingsSerializer(
    SerializersFieldsFromJsonMixin,
    FieldsFromCertifiableObjectSettingsMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = models.CertifiableObject
        fields = ()


class WorkflowStatusDataSerializer(
    SerializersFieldsFromJsonMixin, FieldsFromWorkflowStatusDataMixin, serializers.ModelSerializer
):
    class Meta:
        model = models.WorkflowStatus
        fields = ()


class DataInfoSerializer(serializers.Serializer):
    """
    Nested serializer used to expand on a ``SerializersFieldsFromJsonMixin``'s use of model ids.
    """

    # NOTE: This serializer relies on having '_model' set after init to power the lookup of this
    # information.  For some reason sending it via the 'context' kwarg only gets the context
    # overwritten later on, and sending a 'model' confuses the field itself.

    # This serializer receives a single id as a value, despite turning into a nested structure.
    # Every field  here needs to transform the same id into a different value.

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_instance(self, id):
        if not hasattr(self, "_instance"):
            self._instance = self._model.objects.get(pk=id)
        return self._instance

    def to_representation(self, value):
        from axis.core.serializers import UserInfoSerializer  # Circular import

        data = super(DataInfoSerializer, self).to_representation(value)

        instance = self.get_instance(value)
        if self._model is User:
            data.update(UserInfoSerializer(instance=instance).data)
        elif hasattr(instance, "get_json_info_repr"):
            data.update(instance.get_json_info_repr())

        return data

    def get_id(self, value):
        return value  # the original 'source' the serializer was given is already the id

    def get_name(self, value):
        return "{}".format(self.get_instance(value))


class JsonPrimaryKeyField(serializers.PrimaryKeyRelatedField):
    """A PrimaryKeyRelatedField that tolerates the key missing from the supplied value dict."""

    def get_attribute(self, instance):
        try:
            return super(JsonPrimaryKeyField, self).get_attribute(instance)
        except KeyError:
            return None

    def to_internal_value(self, data):
        # Keep PK as a PK; we don't really care about the model instance right now
        return data

    def to_representation(self, value):
        # There's normally a model instance as value, but in our JSON it's always just the PK.
        return value


class JsonFieldsSaverMixin(object):
    """Targets nested serializers on a primary ModelSerializer to force validation and saving."""

    DATA_FIELDS = None

    def __init__(self, *args, **kwargs):
        super(JsonFieldsSaverMixin, self).__init__(*args, **kwargs)

        # Automatically get rid of blank strings in fields submitted to us.  This is important for
        # fields like the date picker which can be backspaced to empty and then fail to validate an
        # empty string to a valid date format.
        if hasattr(self, "initial_data"):
            for k, v in self.initial_data.items():
                if v == "":
                    self.initial_data[k] = None

    def get_fields(self):
        fields = super(JsonFieldsSaverMixin, self).get_fields()

        # Force nested serializer to wake up and build its fields now.  Cash prize to the one that
        # figures out why DRF doesn't like when a serializer field is called 'data'.
        for field_name in self.DATA_FIELDS:
            field = fields[field_name]
            field.instance = self.instance
            field.context.update(self.context)
            if hasattr(self, "initial_data"):
                field.initial_data = self.initial_data
            field.get_fields()

        return fields

    def validate(self, data):
        # Trip validation for the data field.  See note from get_fields()
        for field_name in self.DATA_FIELDS:
            self.fields[field_name].is_valid(raise_exception=True)
        return data

    def save(self, **kwargs):
        instance = super(JsonFieldsSaverMixin, self).save(**kwargs)

        # An artifact of Examine not knowing how to store nested data dictionaries in the main
        # 'object' data means that we have to forward the whole field soup to the nested
        # serializers.  They're all sharing the same request.data payload.
        for field_name in self.DATA_FIELDS:
            field = self.fields[field_name]
            field.instance = instance  # Ensure newly saved base object is now available

            # Overlay new data atop the old data; don't completely replace the old data
            old_data = getattr(instance, field_name)
            updated_data = dict(old_data, **field.validated_data)

            field.save(**{field_name: updated_data})

        return instance


# State advancement
class WorkflowStatusStateChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkflowStatus
        fields = ()

    def get_fields(self):
        fields = super(WorkflowStatusStateChangeSerializer, self).get_fields()

        if self.instance and self.instance.pk:
            transitions = self.instance.get_state_info().possible_transitions
            fields["transition"] = serializers.ChoiceField(
                write_only=True, choices=[transition.get_name() for transition in transitions]
            )

        return fields

    def validate(self, data):
        user = self.context["request"].user
        state_info = self.instance.get_state_info()

        try:
            state_info.test_transition(data["transition"], user=user)
        except Exception as e:
            if hasattr(e, "validation_errors"):
                raise ValidationError(e.validation_errors)
            raise ValidationError(str(e))

        return data

    def save(self, **kwargs):
        user = self.context["request"].user

        state_info = self.instance.get_state_info()
        state_info.make_transition(self.validated_data["transition"], user=user)

        return self.instance


# Related-only uses
class CompanyIdentityInfoSerializer(serializers.ModelSerializer):
    """Lightweight representation of a company to be nested on some other object."""

    url = serializers.ReadOnlyField(source="get_absolute_url")
    company_type_name = serializers.CharField(source="get_company_type_display", read_only=True)

    class Meta:
        model = Company
        fields = ("id", "name", "url", "company_type", "company_type_name")


class EEPProgramInfoSerializer(serializers.ModelSerializer):
    """Lightweight representation of an EEPProgram to be nested on some other object."""

    url = serializers.ReadOnlyField(source="get_absolute_url")

    class Meta:
        model = EEPProgram
        fields = ("id", "name", "url")


class CertifiableObjectInfoSerializer(serializers.ModelSerializer):
    """Lightweight representation of a CertifiableObject to be nested on the WorkflowStatus."""

    class Meta:
        model = models.CertifiableObject
        fields = ("id", "name", "type")


# Primary object serializers
class CertifiableObjectSerializer(
    JsonFieldsSaverMixin, RemoteIdentifiersMixin, serializers.ModelSerializer
):
    """Recursive serializer for representing a CertObj and its parents."""

    DATA_FIELDS = ["settings"]

    url = serializers.SerializerMethodField()
    owner_info = CompanyIdentityInfoSerializer(source="owner", read_only=True)
    settings = CertifiableObjectSettingsSerializer(required=False, allow_null=True)

    # Placeholder for get_fields() to populate with a self-reference to this same serializer
    parent_info = None

    class Meta:
        model = models.CertifiableObject
        fields = ("id", "url", "owner", "owner_info", "parent", "type", "settings", "name")
        read_only_fields = ("name", "type")
        extra_kwargs = {
            "owner": {"required": False, "allow_null": True},
        }

    def get_fields(self):
        """Adds recursive parent serializer for other CertObjs"""
        fields = super(CertifiableObjectSerializer, self).get_fields()

        # Self-reference for a parent_info field
        parent_info_field = CertifiableObjectSerializer(source="parent", read_only=True)
        fields["parent_info"] = parent_info_field

        return fields

    def get_url(self, instance):
        if instance.pk:
            return instance.get_absolute_url()
        return None

    def validate(self, data):
        data = super(CertifiableObjectSerializer, self).validate(data)

        object_type = self.context["type"]

        # Ensure type is set implicitly
        if self.instance is None:
            data["type"] = object_type

        # Ensure an implicit owner is available if it was left blank or not included on the frontend
        # form.
        if data.get("owner") is None:
            data["owner"] = self.context["request"].user.company

        workflow = models.Workflow.objects.get()  # FIXME: Needs it's own direct reference
        config = workflow.get_config()
        repr_setting = config.lookup("object_types", object_type, "repr_setting", default=None)
        if repr_setting:
            data["name"] = self.initial_data.get(repr_setting)  # Maybe it's not filled out

        return data


class WorkflowStatusSerializer(
    JsonFieldsSaverMixin, RemoteIdentifiersMixin, serializers.ModelSerializer
):
    # WARNING: Don't send a 'data' field in a create/update request, send the loose values in
    # request.data and they'll be moved there automatically.

    DATA_FIELDS = ["data"]

    owner_info = CompanyIdentityInfoSerializer(source="owner", read_only=True)
    eep_program_info = EEPProgramInfoSerializer(source="eep_program", read_only=True)
    certifiable_object_info = CertifiableObjectInfoSerializer(
        source="certifiable_object", read_only=True
    )
    data = WorkflowStatusDataSerializer(required=False, allow_null=True)

    state_description = serializers.SerializerMethodField()

    class Meta:
        model = models.WorkflowStatus
        fields = (
            "id",
            "owner",
            "owner_info",
            "workflow",
            "eep_program",
            "eep_program_info",
            "certifiable_object",
            "certifiable_object_info",
            "state",
            "state_description",
            "data",
            "completion_date",
        )
        read_only_fields = ("workflow", "state", "completion_date")
        extra_kwargs = {
            "owner": {"required": False, "allow_null": True},
        }

    def get_state_description(self, instance):
        """Returns the state description or None for new objects."""
        # This is required to avoid problems with telling a simpler DRF field to default the value
        # to None, or the state to something correct like 'initial' for the built-in machine.
        if instance.pk:
            return instance.get_state_info().description
        return None

    def validate(self, data):
        data = super(WorkflowStatusSerializer, self).validate(data)

        user = self.context["request"].user
        object_type = data["certifiable_object"].type

        # Inject the 'workflow' from the eep_program
        workflow = data["eep_program"].workflow
        if workflow is None:
            raise ValidationError("The selected EEP Program does not declare a workflow.")
        data["workflow"] = workflow

        # Ensure programs match when this object is the child of another
        # TODO: This is probably a config option more than core always-on logic
        object_parent = data["certifiable_object"].parent
        if object_parent:
            existing_statuses = object_parent.workflowstatus_set.filter_by_user(user)
            valid_program_ids = set(existing_statuses.values_list("eep_program__id", flat=True))
            if data["eep_program"].id not in valid_program_ids:
                raise ValidationError(
                    "Program '%s' is not used in the parent %s."
                    % (
                        data["eep_program"],
                        object_parent.type,
                    )
                )

        # Ensure max program constraint is enforced
        config = workflow.get_config()
        max_programs = config.get_max_programs(object_type=object_type, default=None)
        if max_programs is not None:
            workflow_statuses = data["certifiable_object"].workflowstatus_set.filter_by_user(user)
            num_programs = workflow_statuses.count()

            if not self.instance:
                num_programs += 1  # This one is about to be added

            if num_programs > max_programs:
                name = config.get_object_type_name(object_type=object_type)
                name_plural = config.get_object_type_name_plural(
                    object_type=object_type, default=name
                )

                msg = strings.TOO_MANY_WORKFLOW_STATUSES
                msg = msg.format(
                    **{
                        "workflow_name": workflow.get_config_name(),
                        "object_type_plural": name_plural,
                        "max_number": max_programs,
                        "plural_s": "s" if max_programs != 1 else "",
                    }
                )
                raise ValidationError(msg)

        # Ensure a correct default state for new objects
        if self.instance is None:
            state_machine = get_state_machine(workflow, object_type)
            data["state"] = state_machine.initial_state

        # Ensure an implicit owner is available if it was left blank or not included on the frontend
        # form.
        if data.get("owner") is None:
            data["owner"] = self.context["request"].user.company

        return data

    def save(self, **kwargs):
        instance = super(WorkflowStatusSerializer, self).save(**kwargs)

        user = self.context["request"].user
        new_state = instance.seek_state(keep_old=True)
        log.info(
            "Seeking new automatic state for WorkflowStatus(id=%s, state=%s): %s",
            instance.pk,
            instance.state,
            new_state,
        )
        if new_state:
            if instance.state != new_state:
                state_info = instance.get_state_info()
                try:
                    state_info.make_transition("to_{state}".format(state=new_state), user=user)
                except Exception as e:
                    log.info(
                        "Cannot automatically transition from %r to %r: %s",
                        instance.state,
                        new_state,
                        e,
                    )
            else:
                log.info("Avoiding no-op transition to same state.")
        else:
            log.info("No new state provided by config hook.")

        # Updates to WorkflowStatus data fields trigger computation updates
        instance.update_computed_fields()

        return instance


class PreliminaryValidationWorkflowStatusSerializer(
    JsonFieldsSaverMixin, serializers.ModelSerializer
):
    """
    Allows validation for a WorkflowStatus without the context of the (eventually) required
    CertifiableObject, owner, etc.

    This serializer being valid will not result in a savable object.
    """

    DATA_FIELDS = ["data"]

    data = WorkflowStatusDataSerializer(required=False, allow_null=True)

    class Meta:
        model = models.WorkflowStatus
        fields = ("id", "eep_program", "state", "data")

    def save(self, **kwargs):
        raise NotImplementedError(
            "You can't save this serializer, so we're stopping you right now."
        )
