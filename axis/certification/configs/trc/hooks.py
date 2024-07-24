import logging

from . import requirements
from . import utils


__author__ = "Autumn Valenta"
__date__ = "12/12/17 4:14 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# WorkflowStatus
def workflow_status__prepare_save(workflow_status, data, **kwargs):
    """
    Pre-save function called when this workflow is about to save on a workflowstatus via the
    main WorkflowStatus api serializer.
    """

    def newly_set(field_name):
        if field_name not in data:
            return False

        # Check that values are not just present, but set to something truthy
        new_value = data[field_name]
        has_old_value = workflow_status.data.get(field_name) is not None

        return new_value and not has_old_value

    post_save_kwargs = {}

    is_assignment_state = workflow_status.state in (
        "technical_assistance",
        "verification",
        "project_maintenance",
    )
    energy_advisor_newly_set = newly_set("energy_advisor")
    if is_assignment_state and energy_advisor_newly_set:
        post_save_kwargs["trigger_{state}_assigned".format(state=workflow_status.state)] = True

    return post_save_kwargs


def workflow_status__post_save(workflow_status, data, **kwargs):
    """
    Receives the instance and the data saved, plus kwargs generated from the return of prepare_save.
    """
    # Now that the data has successfully saved, read flags set in the prepare_save hook and send to
    # the user in the instance data.

    if kwargs.get("trigger_technical_assistance_assigned"):
        utils.send_technical_assistance_assigned_substate_notification(workflow_status)
    if kwargs.get("trigger_verification_assigned"):
        utils.send_verification_assigned_substate_notification(workflow_status)
    if kwargs.get("trigger_project_maintenance_assigned"):
        utils.send_project_maintenance_assigned_substate_notification(workflow_status)


def workflow_status__seek_state(workflow_status, **kwargs):
    return utils.seek_state(workflow_status, **kwargs)


# WorkflowStatus state changing
def workflow_status__can_decertify(workflow_status, **kwargs):
    # TRC's notion of "complete" isn't a lockout thing, because they're still going to collect data
    # on incentive fields.  They want to be able to seamlessly go in and out of the completion
    # state.
    return True


def workflow_status__handle_transition_to_application(workflow_status, user, **kwargs):
    utils.send_application_transition_notification(workflow_status)


def workflow_status__handle_transition_to_technical_assistance(workflow_status, user, **kwargs):
    utils.send_technical_assistance_transition_notification(workflow_status)

    if workflow_status.data.get("energy_advisor"):
        utils.send_technical_assistance_assigned_substate_notification(workflow_status)


def workflow_status__handle_transition_to_incentive_reserved(workflow_status, user, **kwargs):
    utils.send_incentive_reserved_transition_notification(workflow_status)


def workflow_status__handle_transition_to_verification(workflow_status, user, **kwargs):
    utils.send_verification_transition_notification(workflow_status)

    if workflow_status.data.get("energy_advisor"):
        utils.send_verification_assigned_substate_notification(workflow_status)


def workflow_status__handle_transition_to_incentive_requested(workflow_status, user, **kwargs):
    utils.send_incentive_requested_transition_notification(workflow_status)


def workflow_status__handle_transition_to_project_maintenance(workflow_status, user, **kwargs):
    utils.send_project_maintenance_transition_notification(workflow_status)

    if workflow_status.data.get("energy_advisor"):
        utils.send_project_maintenance_assigned_substate_notification(workflow_status)


def workflow_status__handle_transition_to_dropped(workflow_status, user, **kwargs):
    utils.send_dropped_transition_notification(workflow_status)


def workflow_status__handle_transition_to_waitlist(workflow_status, user, **kwargs):
    utils.send_waitlist_transition_notification(workflow_status)


# Workflow
def workflow__get_requirement_tests(workflow, **kwargs):
    return list(requirements.tests_list)
