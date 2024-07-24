import os
import logging

from django.urls import reverse

from axis import examine
from axis.annotation.machinery import annotations_machinery_factory
from .. import models
from .. import forms
from . import api


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def get_workflowstatus_annotations_machinery_class():
    NotesMachinery = annotations_machinery_factory(
        models.WorkflowStatus,
        type_slug="note",
        **{
            "form_class": forms.WorkflowStatusNoteForm,
            # Use table-driven template stuff
            "template_set": "table",
            "regionset_template": None,
            "region_template": None,
            "detail_template": "examine/certification/note_table_detail.html",
            "form_template": "examine/certification/note_table_form.html",
            "visible_fields": ["created_on", "user", "content"],
            "verbose_names": {
                "created_on": "Date",
                "user": "User",
                "content": "Note",
            },
        },
    )
    return NotesMachinery


class CertifiableObjectExamineMachinery(examine.PrimaryMachinery):
    model = models.CertifiableObject
    type_name = api.CertifiableObjectExamineViewSet.url_basename
    api_provider = api.CertifiableObjectExamineViewSet

    form_class = forms.CertifiableObjectExamineForm

    # Overridden by workflow
    DEFAULT_TEMPLATES = {
        "region": "examine/certification/certifiable_object_region.html",
        "detail": "examine/certification/certifiable_object_detail.html",
        "form": "examine/certification/certifiable_object_form.html",
    }

    def __init__(self, *args, **kwargs):
        super(CertifiableObjectExamineMachinery, self).__init__(*args, **kwargs)

        workflow_id = self.context["workflow_id"]
        user = self.context["request"].user
        self.workflow = models.Workflow.objects.filter_by_user(user).get(id=workflow_id)
        self.config = self.workflow.get_config()

    def get_object_list_url(self):
        default_url = reverse("certification:object:list", kwargs={"type": self.context["type"]})
        object_type = self.context["type"]
        return self.config.get_object_list_url(object_type=object_type, default=default_url)

    def get_delete_success_url(self):
        if self.instance.parent:
            return self.instance.parent.get_absolute_url()
        return self.get_object_list_url()

    def get_verbose_name(self, instance=None):
        return self.context["type"].capitalize()

    def get_default_instruction(self, instance):
        """Puts machinery in edit mode when freshly generated via the redirect view."""
        if self.context["request"].GET.get("new"):
            return "edit"
        return super(CertifiableObjectExamineMachinery, self).get_default_instruction(instance)

    # Templates
    def get_template_set(self):
        user = self.context["request"].user
        object_type = self.context["type"]
        workflow = models.Workflow.objects.filter_by_user(user).get(id=self.context["workflow_id"])
        config = workflow.get_config()

        workflow_object_templates = config.get_examine_object_templates(
            **{
                "object_type": object_type,
                "default": {},
            }
        )

        template_set = {}
        template_set.update(super(CertifiableObjectExamineMachinery, self).get_template_set())
        template_set.update(self.DEFAULT_TEMPLATES)
        template_set.update(workflow_object_templates)

        return template_set

    # Form
    def get_form_kwargs(self, instance, **kwargs):
        kwargs = super(CertifiableObjectExamineMachinery, self).get_form_kwargs(instance, **kwargs)
        kwargs.update(
            {
                "workflow": self.workflow,
                "config": self.config,
                "object_type": self.context["type"],
                "user": self.context["request"].user,
            }
        )
        kwargs.setdefault("initial", {}).update(self.context)
        return kwargs

    def get_helpers(self, instance):
        helpers = super(CertifiableObjectExamineMachinery, self).get_helpers(instance)
        form = forms.CertifiableObjectSettingsForm(
            instance=instance,
            **{
                "object_type": self.context["type"],
            },
        )
        helpers["settings_form"] = self.serialize_form_spec(instance, form)
        helpers["settings_labels"] = {name: field.label for name, field in form.fields.items()}

        # FIXME: TRC-specific
        # FIXME: Extra extra temporary, not using real calc framework yet
        if not self.create_new:
            from ..configs.trc.fields import count_buildings, sum_building_values

            workflowstatus = instance.workflowstatus_set.first()
            if workflowstatus:
                stats = {
                    "number_of_buildings": count_buildings,
                    "number_of_units": sum_building_values,
                    "conditioned_floor_area": sum_building_values,
                }
                helpers["stats"] = {
                    # These stats don't rely on the item_spec or context, so we send them empty
                    name: value_getter(
                        instance=workflowstatus, field_name=name, item_spec={}, context={}
                    )
                    for name, value_getter in stats.items()
                }

        return helpers


class WorkflowStatusExamineMachinery(examine.ExamineMachinery):
    model = models.WorkflowStatus
    type_name = api.WorkflowStatusExamineViewSet.url_basename
    api_provider = api.WorkflowStatusExamineViewSet

    form_class = forms.WorkflowStatusExamineForm

    DEFAULT_TEMPLATES = {
        "regionset": "examine/certification/workflow_status_regionset.html",
        "region": "examine/certification/workflow_status_region.html",
        "detail": "examine/certification/workflow_status_detail.html",
        "form": "examine/certification/workflow_status_form.html",
    }

    def __init__(self, *args, **kwargs):
        super(WorkflowStatusExamineMachinery, self).__init__(*args, **kwargs)

        workflow_id = self.context["workflow_id"]
        user = self.context["request"].user
        self.workflow = models.Workflow.objects.filter_by_user(user).get(id=workflow_id)
        self.config = self.workflow.get_config()

    def get_max_regions(self):
        return self.context["max_regions"]

    def get_verbose_name(self, instance=None):
        return self.config.get_eep_program_tab_label(object_type=self.context["type"])

    def get_object_name(self, instance):
        if instance.pk is None:
            return "New {}".format(self.get_verbose_name())
        return "{eep_program}".format(
            **{
                "eep_program": instance.eep_program.name,
            }
        )

    # Footwork for obtaining a lazy pk for the parent CertifiableObject when it AND this machinery
    # are in linked create modes.
    def _reverse_url(self, url_name, **kwargs):
        parent_pk = self.context.get("certifiable_object", "__certifiable_object_pk__")
        kwargs["certifiable_object_pk"] = parent_pk
        return super(WorkflowStatusExamineMachinery, self)._reverse_url(url_name, **kwargs)

    def get_region_dependencies(self):
        return {
            "certifiableobject": [
                {
                    "field_name": "id",
                    "serialize_as": "certifiable_object",
                }
            ],
        }

    # Templates
    def get_template_set(self):
        workflow_status_templates = self.config.get_examine_status_templates(
            **{
                "object_type": self.context["type"],
                "default": {},
            }
        )

        template_set = {}
        template_set.update(super(WorkflowStatusExamineMachinery, self).get_template_set())
        template_set.update(self.DEFAULT_TEMPLATES)
        template_set.update(workflow_status_templates)

        return template_set

    # Actions
    def get_default_actions(self, instance):
        actions = super(WorkflowStatusExamineMachinery, self).get_default_actions(instance)

        for i, action in enumerate(actions[:]):
            if action["instruction"] == "edit":
                # State transition
                transition_action = self._get_state_transition_action(instance)
                if transition_action:
                    actions.insert(i, transition_action)

                # Elevation action  (FIXME: TRC-specific)
                state_allows_escalation = True
                if state_allows_escalation:
                    escalation_action = None
                    if not instance.data.get("escalated"):
                        escalation_action = self._get_escalate_action(instance)
                    else:
                        escalation_action = self._get_deescalate_action(instance)
                    actions.insert(i, escalation_action)

        return actions

    def _get_state_transition_action(self, instance):
        state_info = instance.get_state_info()
        state_transition_choices = instance.get_state_transition_choices()
        if not len(state_transition_choices):
            return None

        to_name = "to_" + state_info.name  # name of the transition to the state we're already in
        if state_info.name == "complete":
            icon = "circle"
        else:
            icon = "circle-o"
        return self.Action(
            **{
                "name": state_info.description,
                "icon": icon,
                "instruction": None,
                "type": "dropdown",
                "items": [
                    {
                        "name": label,
                        "icon": ("arrow-right" if transition_name == to_name else "BLANK"),
                        "instruction": "change_state",
                        "class": ("active" if transition_name == to_name else ""),
                        # Extra stuff that ends up in the call to handleAction() for this item
                        "transition": transition_name,
                    }
                    for transition_name, label in state_transition_choices
                ],
            }
        )

    def _get_escalate_action(self, instance):
        return self.Action(
            **{
                "name": "Elevate",
                "instruction": "trc_escalate",
            }
        )

    def _get_deescalate_action(self, instance):
        return self.Action(
            **{
                "name": "De-elevate",
                "instruction": "trc_deescalate",
            }
        )

    # Form
    def get_form_kwargs(self, instance, **kwargs):
        kwargs = super(WorkflowStatusExamineMachinery, self).get_form_kwargs(instance, **kwargs)
        kwargs.update(
            {
                "workflow": self.workflow,
                "config": self.config,
                "object_type": self.context["type"],
                "certifiable_object_id": self.context["certifiable_object"],
                "user": self.context["request"].user,
                "parent_id": self.context.get("parent"),  # Unreliable hint
            }
        )
        return kwargs

    # Helpers
    def get_helpers(self, instance):
        helpers = super(WorkflowStatusExamineMachinery, self).get_helpers(instance)
        form = forms.WorkflowStatusDataForm(
            instance=instance,
            **{
                "object_type": self.context["type"],
            },
        )
        helpers["data_form"] = self.serialize_form_spec(instance, form)

        # Config tweaks
        helpers["display_program_link"] = self.config.get_eep_program_display_link(
            object_type=self.context["type"]
        )

        # Context helpers
        helpers["group_has_fields"] = form.group_has_fields
        helpers["data_labels"] = {name: field.label for name, field in form.fields.items()}

        api_url_kwargs = {
            "certifiable_object_pk": instance.certifiable_object_id,
            "pk": instance.id,
        }
        helpers["state_transition_url"] = reverse(
            "apiv2:workflowstatus-transition", kwargs=api_url_kwargs
        )
        helpers["requirements_url"] = reverse(
            "apiv2:workflowstatus-progress", kwargs=api_url_kwargs
        )

        ## Nested machinery
        helpers["machinery"] = {}

        # Generic notes system
        notes = (
            instance.annotations.filter_by_user(self.context["request"].user) if instance.pk else []
        )
        NotesMachinery = get_workflowstatus_annotations_machinery_class()
        notes_machinery = NotesMachinery(objects=notes, context=self.context)
        helpers["machinery"]["notes"] = notes_machinery.get_summary()

        # FIXME: TRC-specific
        from axis.company.forms import ContactForm
        from axis.certification.configs.trc import utils

        contact_form = ContactForm(user=self.context["request"].user)
        helpers["contact_form"] = self.serialize_form_spec(instance, contact_form)
        helpers["escalate_url"] = reverse("apiv2:trc_projects-escalate", kwargs={"pk": instance.pk})
        helpers["deescalate_url"] = reverse(
            "apiv2:trc_projects-deescalate", kwargs={"pk": instance.pk}
        )
        helpers["is_past_date_threshold"] = True
        helpers["state_sublabel"] = utils.get_state_sublabel(instance)

        return helpers
