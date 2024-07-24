import logging

from django import forms

from axis.annotation.models import Annotation
from axis.eep_program.models import EEPProgram
from .models import CertifiableObject
from .api.utils import (
    build_form_field_from_spec,
    FieldsFromCertifiableObjectSettingsMixin,
    FieldsFromWorkflowStatusDataMixin,
)
from . import models
from . import utils

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CertifiableObjectExamineForm(forms.ModelForm):
    class Meta:
        model = models.CertifiableObject

        # NOTE: Does not include 'settings', because that's a separate form
        # NOTE: Does not include 'type', because it's dictated by object creation context
        fields = ("owner", "parent")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")

        self.workflow = kwargs.pop("workflow")
        self.config = kwargs.pop("config")
        self.object_type = kwargs.pop("object_type")

        super(CertifiableObjectExamineForm, self).__init__(*args, **kwargs)

        self.configure_fields()

    def configure_fields(self):
        # owner
        user_is_owner = self.instance.pk and self.user.company_id == self.instance.owner_id
        can_change_owner = self.user.is_superuser or user_is_owner
        if can_change_owner or not self.instance.pk:
            company_swap_candiates = utils.get_owner_swap_queryset(self.user, include_self=True)
            if company_swap_candiates is not None and company_swap_candiates.count() > 1:
                self.fields["owner"].queryset = company_swap_candiates
                if not self.instance.pk:
                    self.fields["owner"].initial = self.user.company_id
            else:
                del self.fields["owner"]
        else:
            del self.fields["owner"]

        # parent
        parent_type = self.config.get_parent_type(object_type=self.object_type, default=None)
        if parent_type:
            parent_queryset = models.CertifiableObject.objects.filter_by_user(self.user).filter(
                type=parent_type
            )
            self.fields["parent"].queryset = parent_queryset
            self.fields["parent"].label = self.config.get_object_type_name(
                object_type=parent_type, default="Parent"
            )
        else:
            del self.fields["parent"]


class WorkflowStatusExamineForm(forms.ModelForm):
    class Meta:
        model = models.WorkflowStatus

        # NOTE: Does not include 'data', because that's a separate form
        # NOTE: Does not include 'state' because that's handled from an action
        fields = ("owner", "eep_program")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")

        self.workflow = kwargs.pop("workflow")
        self.config = kwargs.pop("config")
        self.object_type = kwargs.pop("object_type")
        self.certifiable_object_id = kwargs.pop("certifiable_object_id")
        self.parent_id = kwargs.pop("parent_id")

        kwargs["initial"] = self.configure_initial(
            instance=kwargs.get("instance"), initial=kwargs.get("initial", {})
        )

        super(WorkflowStatusExamineForm, self).__init__(*args, **kwargs)

        self.configure_fields()

    def configure_initial(self, instance, initial):
        # Unfortunately the instance before init's super() can be None or unsaved.
        is_unsaved = instance is None or instance.pk is None

        # eep_program
        # Try to set the initial value to the parent's program
        if is_unsaved:
            filter_target = None
            if self.certifiable_object_id:
                filter_target = {
                    "workflowstatus__certifiable_object__children__id": self.certifiable_object_id,
                }
            elif self.parent_id:
                filter_target = {
                    "workflowstatus__certifiable_object__id": self.parent_id,
                }
            if filter_target:
                parent_program = EEPProgram.objects.only("id").filter(**filter_target).first()
                initial["eep_program"] = parent_program
        return initial

    def configure_fields(self):
        # eep_program
        if self.instance.pk:
            program_queryset = utils.get_available_eep_program_queryset_for_workflow_status(
                **{
                    "workflow_status_id": self.instance.pk,
                    "user": self.user,
                }
            )
        else:
            program_queryset = utils.get_available_eep_program_queryset_for_certifiable_object(
                **{
                    "certifiable_object_id": self.certifiable_object_id,
                    "user": self.user,
                }
            )
        self.fields["eep_program"].queryset = program_queryset
        self.fields["eep_program"].label = self.config.get_eep_program_verbose_name(
            **{
                "object_type": self.object_type,
                "default": "EEP Program",
            }
        )

        # This doesn't seem to work with our current select2 widget in angular_field.html
        # if self.config.get_eep_program_parent_sync(object_type=self.object_type, default=False):
        #     if self.config.get_parent_type(object_type=self.object_type):
        #         self.fields['eep_program'].widget.attrs['disabled'] = 'disabled'

        # owner
        user_is_owner = self.instance.pk and self.user.company_id == self.instance.owner_id
        can_change_owner = self.user.is_superuser or user_is_owner
        if can_change_owner or not self.instance.pk:
            company_swap_candiates = utils.get_owner_swap_queryset(self.user, include_self=True)
            if company_swap_candiates is not None and company_swap_candiates.count() > 1:
                self.fields["owner"].queryset = company_swap_candiates
                if not self.instance.pk:
                    self.fields["owner"].initial = self.user.company_id
            else:
                del self.fields["owner"]
        else:
            del self.fields["owner"]


class FormFieldsFromJsonMixin(object):
    """Relies on a FieldsFrom mixin to build form fields, then annotate extra stuff about them."""

    def __init__(self, *args, **kwargs):
        self.object_type = kwargs.pop("object_type")
        kwargs["initial"] = getattr(kwargs["instance"], self.CONFIG_KEY_NAME)
        super(FormFieldsFromJsonMixin, self).__init__(*args, **kwargs)

        self.fields.update(self.get_json_fields(object_type=self.object_type))

    def build_json_field(self, name, spec, context):
        kwargs = {}  # Avoid sending 'data' unless it's set on the serializer
        if hasattr(self, "initial"):
            kwargs["data"] = self.initial
        return build_form_field_from_spec(self, name, spec, context=context, **kwargs)


class CertifiableObjectSettingsForm(
    FormFieldsFromJsonMixin, FieldsFromCertifiableObjectSettingsMixin, forms.ModelForm
):
    class Meta:
        model = models.CertifiableObject
        fields = ()


class WorkflowStatusDataForm(
    FormFieldsFromJsonMixin, FieldsFromWorkflowStatusDataMixin, forms.ModelForm
):
    class Meta:
        model = models.WorkflowStatus
        fields = ()

    # WorkflowStatus data has a 'category' tag on it, so we'll crunch some hints about the final
    # fields list per category.
    def __init__(self, *args, **kwargs):
        self.group_has_fields = {}
        super(WorkflowStatusDataForm, self).__init__(*args, **kwargs)

    def build_json_field(self, name, field_spec, context):
        field = super(WorkflowStatusDataForm, self).build_json_field(name, field_spec, context)

        # Mark field's group as having something in it
        self.group_has_fields[field_spec["category"]] = True

        return field


class WorkflowStatusNoteForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ("content",)
