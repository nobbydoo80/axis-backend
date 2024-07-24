import importlib
import inspect
import logging
import os
import django

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from functools import partialmethod
from django_states.fields import StateField
from django_states.log import _create_state_log_model
from django_states.model_methods import (
    get_STATE_transitions,
    get_public_STATE_transitions,
    get_STATE_machine,
    get_STATE_display,
    get_STATE_info,
)
from simple_history.models import HistoricalRecords

from axis.core.accessors import RemoteIdentifiers
from axis.core.fields import AxisJSONField
from axis.relationship.models import Associations
from . import managers
from .. import configs
from .. import utils
from ..configs.base import get_state_machine
from ..configs.utils import ConfigReader

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def get_configs_dir():
    return utils.CONFIGS_DIRECTORY


class Workflow(models.Model):
    """Represents a company's configuration for a workflow around their CertifiableObjects."""

    # EEPProgram.workflow links to one of these Workflow instances.
    # The EEPProgram carries the 'owner' information.

    objects = managers.WorkflowQuerySet.as_manager()

    # Stores dynamic configuration, including Annotation-like fields a WorkflowStatus needs.
    config_path = models.FilePathField(
        path=get_configs_dir,
        allow_folders=True,
        allow_files=True,
        match=r"^[^_].*(?<!\.pyc)$",
    )  # directories or .py files

    def __str__(self):
        return os.path.basename(self.config_path)

    def get_config(self):
        module = self.get_config_module()
        Reader = module.config.get("reader", ConfigReader)
        return Reader(module.config)

    def get_config_module(self):
        return importlib.import_module(".".join((configs.__name__, self.get_config_name())))

    def get_config_name(self):
        return os.path.splitext(os.path.basename(self.config_path))[0]

    # Hook stuff
    # I think hooks that target only one dedicated object_type should probably just go on the that
    # model instead of this one, but having them all together helps to keep this from getting
    # confusing at this stage in the design.
    def get_hook(self, model_type, hook_name):
        """Gets a callback from the workflow config for the target model and hook name."""
        # NOTE: model_type is expected to be a model-based name, not one of the config's declared
        # 'object_type' values.
        module = self.get_config_module()
        try:
            hooks = module.hooks
        except AttributeError:
            return None

        hook_full_name = "{model_type}__{hook_name}".format(
            **{
                "model_type": model_type,
                "hook_name": hook_name,
            }
        )
        return getattr(hooks, hook_full_name, None)

    def prepare_save(self, object_type, obj, data, **kwargs):
        prepare_save = self.get_hook(object_type, "prepare_save")
        if prepare_save:
            return prepare_save(obj, data, **kwargs)
        return {}

    def post_save(self, object_type, obj, data, **kwargs):
        post_save = self.get_hook(object_type, "post_save")
        if post_save:
            post_save(obj, data, **kwargs)

    def get_requirement_tests(self, object_type, obj, **kwargs):
        get_requirement_tests = self.get_hook(object_type, "get_requirement_tests")
        if get_requirement_tests:
            return get_requirement_tests(obj, **kwargs)
        return []

    def can_decertify(self, obj, **kwargs):
        can_decertify = self.get_hook("workflow_status", "can_decertify")
        if can_decertify:
            return can_decertify(obj, **kwargs)

    def seek_state(self, obj, **kwargs):
        seek_state = self.get_hook("workflow_status", "seek_state")
        if seek_state:
            return seek_state(obj, **kwargs)

    def handle_state_change(self, transition, obj, **kwargs):
        # TODO: Consult hooks specific to the state machine name or obj.object_type or something,
        # which will reduce complexity in handlers for state machines that share state names.
        handler_name = "handle_transition_{transition}".format(transition=transition.get_name())
        handle_state_change = self.get_hook("workflow_status", handler_name)
        if handle_state_change:
            handle_state_change(obj, **kwargs)


class StateGuidedModel(models.Model):
    """Abstract base class for the interface used by Certification workflows."""

    # Our existing Home model inherits from this to make it compatible with this new system.

    type = None
    parent = None

    class Meta:
        abstract = True
        verbose_name = "State-Guided Model"


class CertifiableObject(StateGuidedModel):
    """Object which allows instances of WorkflowStatus."""

    # State information is not tracked on this model, but rather signifies that state information
    # *can be* tracked.

    objects = managers.CertifiableObjectQuerySet.as_manager()
    history = HistoricalRecords()
    identifiers = RemoteIdentifiers(
        choices=[
            ("trc", "TRC UUID"),
        ]
    )

    # This is analogous to the Home model in our original certification path, but Home is running
    # its own logic system and FKs to its hierarchy of geographic objects.

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    # A given WorkflowStatus supports only certain 'type' labels, dictated by its config.
    # Objects using an unknown type won't be valid options for use with that Workflow.
    type = models.CharField(max_length=25)  # 'home', 'building', 'unit', 'project', etc
    parent = models.ForeignKey(
        "self", related_name="children", blank=True, null=True, on_delete=models.SET_NULL
    )

    name = models.CharField(max_length=50, blank=True, null=True)  # cached attribute from settings

    settings = AxisJSONField()

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certifiable Object"

    def __str__(self):
        if self.name:
            return self.name
        return "{self.type}:{self.id}".format(self=self)

    def get_absolute_url(self):
        return reverse("certification:object:view", kwargs={"pk": self.pk, "type": self.type})

    @classmethod
    def can_be_added(cls, user):
        return True

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        company_id = user.company_id

        # if not user.has_perm('home.change_home'):
        #     return False

        if company_id == self.owner.id:
            return True

        Associations = WorkflowStatus.associations.rel.related_model
        associations = Associations.objects.filter(workflowstatus__certifiable_object_id=self.id)
        if associations.filter(company_id=company_id, is_accepted=True).exists():
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        is_owner = user.company_id == self.owner_id
        if is_owner and user.is_company_admin:
            return True

        return False

    def prepare_save(self, data, workflow, **kwargs):
        """
        Hook called just before the WorkflowStatus serializer saves this object with updated data.
        Only applies for existing objects, not unsaved ones.
        """
        return workflow.prepare_save("certifiable_object", self, data, **kwargs)

    def post_save(self, data, workflow, **kwargs):
        """
        Hook called just before the WorkflowStatus serializer saves this object with updated data.
        Only applies for existing objects, not unsaved ones.
        """
        workflow.post_save("certifiable_object", self, data, **kwargs)

    def get_settings(self):
        settings = {}
        settings.update(self.settings)
        return settings


class BaseWorkflowStatus(models.Model):
    """Interface base class for WorkflowStatus and EEPProgramHomeStatus"""

    # The fields on WorkflowStatus will end up going here, but I'm trying to be as low-impact as
    # possible (until we're ready) for things outside of the TRC SOW.  Specializations on this,
    # like HomeStatus, might offer more methods or data fields.

    class Meta:
        abstract = True

    def get_progress_analysis(self, **kwargs):
        return utils.get_progress_analysis(self, **kwargs)

    def get_completion_requirements(self):
        return []

    def get_completion_test_kwargs(self, user=None, **kwargs):
        """Common pre-crunched data available to all certification mini-tests via kwargs."""

        kwargs.update(
            {
                "user": user,  # Unreliable availability, use only for non-critical warnings
                "workflow": self.workflow,
                "certifiable_object": self.certifiable_object,
                "workflow_status": self,
                "object_type": self.certifiable_object.type,
                "state_name": self.get_state_display(),
                # These are for the examine view.
                "edit_url": "#instruction-edit",
            }
        )
        return kwargs


class WorkflowStatus(BaseWorkflowStatus, models.Model):
    """Tracks a shareable Workflow state for a CertifiableObject."""

    objects = managers.WorkflowStatusQuerySet.as_manager()
    history = HistoricalRecords()
    associations = Associations()
    annotations = GenericRelation("annotation.Annotation")
    identifiers = RemoteIdentifiers(
        choices=[
            ("trc", "TRC UUID"),
        ]
    )

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    state = StateField()

    workflow = models.ForeignKey("Workflow", on_delete=models.CASCADE)
    eep_program = models.ForeignKey(
        "eep_program.EEPProgram", on_delete=models.CASCADE
    )  # matches Workflow's eep_program
    certifiable_object = models.ForeignKey(
        "CertifiableObject", on_delete=models.CASCADE
    )  # 'workflowstatus_set'

    data = AxisJSONField()

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Workflow Statuses"

    def __init__(self, *args, **kwargs):
        super(WorkflowStatus, self).__init__(*args, **kwargs)
        # Prevent recursion
        stack = inspect.stack()
        if "configure_instance_state_machine" in [x.function for x in stack]:
            return
        self.configure_instance_state_machine()

    def __str__(self):
        return "WorkflowStatus for {self.owner} ({self.workflow}, type={self.certifiable_object.type}, state={self.state})".format(
            self=self
        )

    def get_absolute_url(self):
        return self.certifiable_object.get_absolute_url()

    def prepare_save(self, data, **kwargs):
        """
        Hook called just before the WorkflowStatus serializer saves this object with updated data.
        Only applies for existing objects, not unsaved ones.
        """
        return self.workflow.prepare_save("workflow_status", self, data, **kwargs)

    def post_save(self, data, **kwargs):
        """
        Hook called just before the WorkflowStatus serializer saves this object with updated data.
        Only applies for existing objects, not unsaved ones.
        """
        self.workflow.post_save("workflow_status", self, data, **kwargs)

    def save(self, *args, **kwargs):
        super(WorkflowStatus, self).save(*args, **kwargs)

        # Try to configure newly created instances (no adverse effects if already somehow done)
        self.configure_instance_state_machine()

    def configure_instance_state_machine(self):
        FIELD_NAME = "state"

        # Abandon effort to load the state machine if the workflow cannot be read.
        # The object is likely new in this case, without its own pk and without a working reference
        # to the (eventually required) workflow field.
        try:
            self.workflow
            self.certifiable_object
        except ObjectDoesNotExist:  # This is more of a "self doesn't exist" message
            return

        memoized_name = "_{state}_machine_configured".format(state=FIELD_NAME)
        if hasattr(self, memoized_name):
            return

        machine = get_state_machine(self.workflow, self.certifiable_object.type)
        if machine is None:
            setattr(self, memoized_name, True)
            return

        field = self._meta.get_field(FIELD_NAME)

        # Update values set by StateField.__init__()
        field._machine = machine

        # Update values set by StateField.contribute_to_class()
        field._choices = field._machine.get_state_choices()
        field.default = field._machine.initial_state

        # Update the log_model created by StateField.contribute_to_class(), which assigns this to
        # the class, but only accesses it from the instance.  So we'll ignore the class version and
        # leverage this instance attribute.  This is significant because our log_model needs to be
        # instance-specific and not model-specific.
        self._state_log_model = _create_state_log_model(self.__class__, FIELD_NAME, field._machine)

        # Override the class methods to always inject the instance's machine, not the class's
        # generic default machine.
        def call_with_instance_machine(self, *args, **kwargs):
            default_method = kwargs.pop("default_method")
            instance_machine = self._state_machine_configured
            return default_method(self, *args, machine=instance_machine, **kwargs)

        model_methods = [
            get_STATE_transitions,
            get_public_STATE_transitions,
            get_STATE_machine,
            get_STATE_display,
            get_STATE_info,
        ]

        for default_method in model_methods:
            name = default_method.__name__.replace("STATE", FIELD_NAME)
            f = partialmethod(call_with_instance_machine, default_method=default_method)

            setattr(self.__class__, name, f)

        setattr(self, memoized_name, machine)

    def get_state_transition_choices(self):
        choices = [
            (transition.get_name(), transition.description)
            for transition in self.get_state_info().possible_transitions
        ]

        ordering = self.get_state_machine().state_choices_order
        choices.sort(key=lambda name_label: ordering.index(name_label[0]))

        return choices

    def seek_state(self, **kwargs):
        """
        Consults the config's 'workflow_status__seek_state' hook for a candidate state name based on
        completed config requirements.  If no hook is available, the return value is None.

        If a state name is returned when this is called as part of the API serializer save, that
        state transition will attempt to be made automatically.
        """
        return self.workflow.seek_state(self, **kwargs)

    def handle_state_change(self, transition, **kwargs):
        return self.workflow.handle_state_change(transition, self, **kwargs)

    # Permissions
    @classmethod
    def can_be_added(cls, user):
        return True

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        company_id = user.company_id

        # if not user.has_perm('home.change_home'):
        #     return False

        if company_id == self.owner.id:
            return True

        if self.associations.filter(company_id=company_id, is_accepted=True).exists():
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        is_owner = user.company_id == self.owner_id
        if is_owner and user.is_company_admin:
            return True

        return False

    def can_change_state(self, user):
        """Permission hook for the given user's ability to make state changes."""
        return WorkflowStatus.objects.filter_by_user(user).filter(id=self.id).exists()

    def can_decertify(self, user, **kwargs):
        """Business logic hook for the given user's ability to back out of completion."""
        # Note that this is not necessarily a permission hook--can_change_state() determines that
        # information in advance, freeing this method up to inspect the object's circumstances for
        # the possibility of backing out of its completion state.
        # Incentives, program closures, etc, would trigger a False.
        return self.workflow.can_decertify(self, **kwargs)

    def get_settings(self, **kwargs):
        """Returns the computed settings of this object."""
        settings = {}
        settings.update(self.eep_program.workflow_default_settings)
        settings.update(self.certifiable_object.get_settings())

        # Not editable by the user but considered a setting
        settings["object_type"] = self.certifiable_object.type

        return settings

    def get_data(self, fields=None, include_required=True, include_optional=True):
        """
        Returns currently gathered data whose requirement specs match the inclusion kwarg filter
        flags. Note that if a data field is required but not yet available on this object, it will
        be missing from the returned data dictionary, and this is not an error.
        """

        # Note that explict names given in 'fields' will not be validated for accuracy.  This is to
        # allow private data to be requested from the JSON blob even if it's not represented in the
        # workflow field specs.
        # I'm open to being persuaded that private data is a bad idea and that all fields should be
        # in the spec no matter what (and just not displayed).  We can probably swing that now that
        # API PATCHes don't destroy data missing from the PATCH.

        config = self.workflow.get_config()
        object_type = self.certifiable_object.type
        data_spec = config.get_data_spec(object_type=object_type)

        if fields is None:
            fields = list(data_spec.keys())
        else:
            pass  # Possible future validation of provided names against data_spec.keys()

        data = self.data.copy()

        if include_required and include_optional:
            return data
        elif not include_required and not include_optional:
            raise ValueError("One of include_required, include_optional should be True.")

        for k in list(data.keys()):
            if k not in data_spec:  # Deprecated data point no longer collected
                continue

            is_required = data_spec[k]["required"]
            if is_required and not include_required:
                del data[k]
            elif not is_required and not include_optional:
                del data[k]
            elif data[k] is None:  # Select fields end up pushing None, so filter away to be safe
                del data[k]
        return data

    def update_computed_fields(self):
        utils.update_computed_fields(self)

    def get_completion_requirements(self, **kwargs):
        tests = super(WorkflowStatus, self).get_completion_requirements(**kwargs)
        # tests.append(self.test_all_required_data_provided)
        tests.extend(self.workflow.get_requirement_tests("workflow", self.workflow, **kwargs))
        return tests

    # # Completion checks
    # @utils.requirement_test("Required fields")
    # def test_all_required_data_provided(self, object_type, edit_url, **kwargs):
    #     """ Verifies that all required data fields have been collected. """
    #     config = self.workflow.get_config()
    #     data = self.get_data(include_required=True, include_optional=False)
    #
    #     settings = self.get_settings()  # already includes object_type
    #     required_specs = config.get_required_data_specs(**settings)
    #
    #     missing_data_names = set(required_specs.keys()) - set(data.keys())
    #     total_weight = len(required_specs)
    #     completion_weight = total_weight - len(missing_data_names)
    #     if missing_data_names:
    #         missing_data_labels = sorted([
    #             required_specs[name]['label'] for name in missing_data_names
    #         ])
    #         msg = strings.MISSING_REQUIRED_DATA_FROM_SPEC
    #         msg = msg.format(number=len(missing_data_labels))
    #         data = """<ul><li>{}</li></ul>""".format("</li><li>".join(missing_data_labels))
    #         return utils.FailingStatusTuple(message=msg, url=edit_url, data=data,
    #                                         weight=completion_weight, total_weight=total_weight)
    #     return utils.PassingStatusTuple([], weight=completion_weight, total_weight=total_weight)


# Home/HomeStatus compat mixins -- trying to keep all ducttape here
class CertifiableObjectHomeCompatMixin(models.Model):
    # StateGuidedModel hints
    type = "home"
    parent = None

    class Meta:
        abstract = True


class WorkflowStatusHomeStatusCompatMixin(models.Model):
    class Meta:
        abstract = True

    # Temp properties for integrating with WorkflowStatus
    @property
    def certifiable_object(self):
        return self.home

    @property
    def workflow(self):
        return self.eep_program.workflow

    @property
    def completion_date(self):
        return self.certification_date

    def get_progress_analysis(self, **kwargs):
        return utils.get_progress_analysis(self, **kwargs)

    def get_completion_requirements(self):
        return []

    def get_completion_test_kwargs(self, user=None, **kwargs):
        """Common pre-crunched data available to all certification mini-tests via kwargs."""

        kwargs.update(
            {
                "user": user,  # Unreliable availability, use only for non-critical warnings
                "workflow_status": self,  # In case some program tests want status details
                "certifiable_object": self.certifiable_object,
                "object_type": self.certifiable_object.type,
                # These are for the examine view.
                "edit_url": "#instruction-edit",
            }
        )
        return kwargs
