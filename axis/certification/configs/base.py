from datetime import datetime, timezone
import logging

from django_states.machine import StateMachine, StateDefinition, StateTransition
from django_states.exceptions import TransitionValidationError

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ConfigStateMachineMixin(object):
    state_choices_order = None  # list of names


class DefaultStateMachine(ConfigStateMachineMixin, StateMachine):
    state_choices_order = []

    log_transitions = False

    class initial(StateDefinition):
        initial = True
        description = "initial"


# Generic transition methods available for state machines to use
def has_transition_permission(transition, instance, user):
    if instance.can_change_state(user):
        return True

    return False


def validate_transition(transition, instance):
    """Yields transition validation errors to prevent premature state change to 'complete'"""
    if transition.to_state == "complete":
        if not can_transition_to_complete(transition, instance):
            yield TransitionValidationError("Cannot currently transition to 'complete'.")
    elif instance.state == "complete" and "complete" in transition.from_states:
        if not can_transition_from_complete(transition, instance):
            yield TransitionValidationError("Cannot currently transition out of 'complete'.")


def handle_transition(transition, instance, user, **kwargs):
    if transition.to_state == "complete":
        handle_transition_to_complete(transition, instance, user)
    if instance.state == "complete" and "complete" in transition.from_states:
        handle_transition_from_complete(transition, instance, user)

    instance.handle_state_change(transition, user=user)


def can_transition_from_complete(transition, instance, user=None):
    # Things like incentives being paid, etc, would block this.
    return instance.can_decertify(user)


def handle_transition_from_complete(transition, instance, user):
    # Undo a certification
    instance.completion_date = None


def can_transition_to_complete(transition, instance, user=None):
    from axis.home.models import EEPProgramHomeStatus

    # Compat layer.  This goes away once we add enough to this HomeStatus to generically support a
    # the BaseWorkflowStatus interface.
    if isinstance(instance, EEPProgramHomeStatus):
        return instance.can_user_certify(user)

    result = instance.get_progress_analysis(user=user, fail_fast=True)
    return result["status"]


def handle_transition_to_complete(transition, instance, user):
    from axis.home.models import EEPProgramHomeStatus
    from axis.home.utils import CertifyHome

    certification_date = datetime.now(timezone.utc)

    # Compat layer.  This goes away once we add enough to this HomeStatus to generically support a
    # the BaseWorkflowStatus interface.
    if isinstance(instance, EEPProgramHomeStatus):
        certify = HomeCertification(user, instance, certification_date)
        return certify.certify()

    # Simple TRC setup.
    # Save and state update will happen right after this return
    instance.completion_date = certification_date

    return True


class ConfigStateTransition(StateTransition):
    to_state = None
    from_state = None
    description = ""

    # Automatic behaviors
    has_permission = has_transition_permission
    validate = validate_transition
    handler = handle_transition

    # Shorthand for common transition needs
    can_transition_from_complete = classmethod(can_transition_from_complete)
    handle_transition_from_complete = classmethod(handle_transition_from_complete)
    can_transition_to_complete = classmethod(can_transition_to_complete)
    handle_transition_to_complete = classmethod(handle_transition_to_complete)


def get_state_machine(workflow, object_type):
    """Returns the state machine class in 'workflow' for a given 'object_type'."""
    config = workflow.get_config()
    state_machine = config.get_state_machine(object_type=object_type)
    if state_machine is None:
        state_machine = DefaultStateMachine
    return state_machine
