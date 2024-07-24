import datetime
import logging

from axis.company.models import Company
from . import messages
from . import strings
from . import user_roles

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def get_company():
    return Company.objects.get(slug="trc")


def get_company_users():
    company = get_company()
    return company.users.filter(is_active=True)


def get_state_sublabel(workflow_status):
    """Returns the most accurate sub-state label for the fields filled out in the TRC data set."""
    state = workflow_status.state
    data = workflow_status.data

    label = ""

    # Get main label
    if state == "application":
        if data.get("application_form_received"):
            label = strings.SUBSTATE_NAMES["application"]["received"]
        else:
            label = strings.SUBSTATE_NAMES["application"]["notified"]
    elif state == "technical_assistance":
        if data.get("date_reservation_sent"):
            label = strings.SUBSTATE_NAMES["technical_assistance"]["pending"]
        elif data.get("energy_advisor"):
            label = strings.SUBSTATE_NAMES["technical_assistance"]["assigned"]
    elif state == "verification":
        if data.get("verification_performed"):
            label = strings.SUBSTATE_NAMES["verification"]["complete"]
        elif data.get("verification_scheduled"):
            label = strings.SUBSTATE_NAMES["verification"]["scheduled"]
        elif data.get("trc_verifier"):
            label = strings.SUBSTATE_NAMES["verification"]["assigned"]
    elif state == "incentive_requested":
        if data.get("incentive_request_date"):
            label = strings.SUBSTATE_NAMES["incentive_requested"]["approved"]
    elif state == "project_maintenance":
        if data.get("energy_advisor"):
            label = strings.SUBSTATE_NAMES["project_maintenance"]["assigned"]

    # Append escalated label
    if data.get("escalated"):
        if label:
            label += " - "
        label += "Elevated"

    return label


def seek_state(workflow_status, keep_old=False, forward_only=True, target_states=None, **kwargs):
    """
    Returns a state name as a hint for where the given workflowstatus can be transitioned based on
    completed field data.  Note that this pays no attention at all to if the transition will
    actually succeed, as it may be blocked by user permission, etc.
    """

    log.debug(
        "Starting seek_state for WorkflowStatus(id=%s).  Options: %r",
        workflow_status.pk,
        {
            "keep_old": keep_old,
            "forward_only": forward_only,
            "target_states": target_states,
        },
    )

    # Valid state setup
    state = None  # Thing to be returned by the end
    if keep_old:
        state = workflow_status.state

    if target_states:  # forward_only doesn't intuitively apply to this
        valid_states = target_states
    else:
        # Get states (transition names without the 'to_' in the front)
        valid_states = [choice[0][3:] for choice in workflow_status.get_state_transition_choices()]

        if forward_only and (state in valid_states):
            valid_states = valid_states[valid_states.index(state) :]

    # Ordered set of dependencies
    # If this needs to get more sophisticated, consider allowing callables in the dependency list
    # that allow testing of any condition, not just the presence of a field name.
    field_triggers = [("pre_qual", ("lead_contact_date",))]

    log.debug("Valid destination states: %r", valid_states)

    # State seeking
    data = workflow_status.data
    for new_state, required_fields in field_triggers:
        if new_state not in valid_states:
            log.debug("Skipping %r triggers; not one of: %r", new_state, valid_states)
            continue

        log.debug("Checking triggers for progress to %r state: %r", new_state, required_fields)
        valid = True
        for field in required_fields:
            if not data.get(field):
                valid = False
                log.debug("Failed the %r data-presence requirement for %r", new_state, field)
                break

        if valid:
            log.debug(
                "Passed the %r data-presence requirement for %r: %r",
                new_state,
                field,
                data.get(field),
            )
            state = new_state

    log.debug("Determined state: %r", state)

    return state


# State-change notifications
def _send_state_notification(workflow_status, message, role=None, admins=False):
    """Requests state change messages be sent to TRC users that match the given role."""
    users = get_company_users()

    if not role and not admins:
        raise ValueError("Need a 'role' or the 'admins' flag set to True.")

    # Limit to recipients to correct type
    if role:
        users = users.filter(title=role)
    elif admins:
        users = users.filter(is_company_admin=True)

    context = {
        "project": workflow_status.certifiable_object,
        "project_url": workflow_status.get_absolute_url(),
    }
    message(url=context["project_url"]).send(users=users, context=context)


def send_application_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["application"]
    _send_state_notification(workflow_status, role=user_roles.PIPELINE_ADMIN, message=message)


def send_technical_assistance_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["technical_assistance"]
    _send_state_notification(workflow_status, role=user_roles.TECHNICAL_MANAGER, message=message)


def send_incentive_reserved_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["incentive_reserved"]
    _send_state_notification(workflow_status, admins=True, message=message)


def send_verification_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["verification"]
    _send_state_notification(workflow_status, role=user_roles.PIPELINE_ADMIN, message=message)


def send_incentive_requested_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["incentive_requested"]
    _send_state_notification(workflow_status, role=user_roles.PIPELINE_ADMIN, message=message)


def send_project_maintenance_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["project_maintenance"]
    _send_state_notification(workflow_status, role=user_roles.TECHNICAL_MANAGER, message=message)


def send_dropped_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["dropped"]
    _send_state_notification(workflow_status, role=user_roles.TECHNICAL_MANAGER, message=message)


def send_waitlist_transition_notification(workflow_status):
    message = messages.TRANSITION_SUCCESSFUL_MESSAGES["waitlist"]
    _send_state_notification(workflow_status, role=user_roles.TECHNICAL_MANAGER, message=message)


def send_escalated_notification(workflow_status):
    users = get_company_users()

    # Send to admins only
    users = users.filter(is_company_admin=True)

    context = {
        "project": workflow_status.certifiable_object,
        "project_url": workflow_status.get_absolute_url(),
        "state_name": workflow_status.get_state_display(),
    }
    messages.TRCEscalatedMessage(url=context["project_url"]).send(users=users, context=context)


# Substate-change notifications
def _send_substate_notification(workflow_status, user_field, message):
    """Sends the given substate transition notification to the user."""
    users = get_company_users()
    user = users.get(id=workflow_status.data[user_field])

    context = {
        "project": workflow_status.certifiable_object,
        "project_url": workflow_status.get_absolute_url(),
    }
    message(url=context["project_url"]).send(user=user, context=context)


def send_technical_assistance_assigned_substate_notification(workflow_status):
    message = messages.SUBSTATE_TRANSITION_MESSAGES["technical_assistance"]["assigned"]
    _send_substate_notification(workflow_status, user_field="energy_advisor", message=message)


def send_verification_assigned_substate_notification(workflow_status):
    message = messages.SUBSTATE_TRANSITION_MESSAGES["verification"]["assigned"]
    _send_substate_notification(workflow_status, user_field="energy_advisor", message=message)


def send_project_maintenance_assigned_substate_notification(workflow_status):
    message = messages.SUBSTATE_TRANSITION_MESSAGES["project_maintenance"]["assigned"]
    _send_substate_notification(workflow_status, user_field="energy_advisor", message=message)


# Recurring reminder notifications
def send_incentive_reserved_monthly_notification(workflow_status, threshold_days):
    users = get_company_users()

    # Send to admins only
    users = users.filter(is_company_admin=True)

    context = {
        "days": threshold_days,
        "project": workflow_status.certifiable_object,
        "project_url": workflow_status.get_absolute_url(),
    }
    messages.TRCIncentiveReservedMonthlyMessage(url=context["project_url"]).send(
        users=users, context=context
    )


def send_incentive_reserved_construction_reminder_notification(workflow_status):
    users = get_company_users()

    # Send to admins only
    users = users.filter(is_company_admin=True)

    context = {
        "project": workflow_status.certifiable_object,
        "project_url": workflow_status.get_absolute_url(),
    }
    messages.TRCIncentiveReservedConstructionReminderMessage(url=context["project_url"]).send(
        users=users, context=context
    )


# Task timer utils
# FIXME: Move away from boolean returns; reveal time-until information so program requirements can
# reveal that information without reinventing the logic.
def is_timedelta_elapsed(instance, delta=None, date_field_name=None, date=None, **timedelta_kwargs):
    """Returns True if the date in 'date_field_name' is more than 'days' business days past."""
    assert date_field_name or date, "Need a date field lookup or a date value"

    if not date:
        if date_field_name in instance.data and instance.data[date_field_name]:
            date = instance.data[date_field_name]
            try:
                date = datetime.date(*[int(x) for x in date.split("-")])
            except Exception:
                pass

    if not date:
        return False

    today = datetime.datetime.today().date()
    if delta is None:
        delta = datetime.timedelta(**timedelta_kwargs)
    if date + delta < today:
        return True


def is_timedelta_near(
    instance, delta=None, date_field_name=None, date_obj=None, **timedelta_kwargs
):
    """Returns True if the date in 'date_field_name' is less than 'days' business days away."""
    assert date_field_name or date_obj, "Need a date field lookup or a date value"

    if not date_obj:
        if date_field_name in instance.data and instance.data[date_field_name]:
            date_obj = instance.data[date_field_name]

    if not date_obj:
        return False

    if not isinstance(date_obj, (datetime.date, datetime.datetime)):
        date_obj = date_obj.strip()
        try:
            date_obj = datetime.date(*[int(x) for x in date_obj.split("-")])
        except:
            log.warning(
                "Unable to parse %r from instance.data[%s] instance id %s",
                date_obj,
                date_field_name,
                instance.pk,
            )

    today = datetime.datetime.today().date()
    if delta is None:
        delta = datetime.timedelta(**timedelta_kwargs)

    if date_obj - delta >= today:
        return True


def is_businessday_elapsed(instance, date_field_name=None, date=None, **timedelta_kwargs):
    """Returns True if the date in 'date_field_name' is more than 'days' business days past."""
    delta = datetime.timedelta(**timedelta_kwargs)  # FIXME: Business days instead of raw days
    return is_timedelta_elapsed(instance, delta, date_field_name, date)


def get_date_of_state_entry(workflow_status, state):
    """
    Shorthand method for obtaining the datetime of the most recent successful transition of the
    given workflowstatus to the target state.  Note that this assumes that such a transition *did*
    occur, but not necessarily that ``state`` is the object's current state.
    """
    # NOTE: I imagine this is either a core util or something that goes onto the WorkflowStatus
    # model.
    transition = workflow_status.state_history.filter(
        state="transition_completed", to_state=state
    ).last()
    return transition.start_time


def issue_reminder_notifications():
    company = get_company()
    queryset = company.workflowstatus_set.all()

    # Escalated, stale
    for instance in queryset.filter_data("escalated"):
        thresholds = [2, 5]
        for threshold in reversed(thresholds):
            if is_businessday_elapsed(instance, "escalated", days=threshold):
                send_escalated_notification(instance)

    # Application, stale
    for instance in queryset.filter(state="application").has_no_data(
        "application_form_received", "escalated"
    ):
        stale_threshold = 2
        transition_date = get_date_of_state_entry(instance, state=instance.state)
        if is_businessday_elapsed(instance, transition_date, days=stale_threshold):
            send_application_transition_notification(instance)

    # Incentive Reserved, 4 week and 2 week warnings prior to construction start
    for instance in queryset.filter(state="incentive_reserved"):
        thresholds = [14, 30]
        for threshold in reversed(thresholds):
            if is_timedelta_near(
                instance,
                date_field_name="expected_construction_start_date",
                days=threshold,
            ):
                send_incentive_reserved_construction_reminder_notification(instance)

    # Incentive Reserved, warnings at one month intervals
    for instance in queryset.filter(state="incentive_reserved"):
        thresholds = [30, 60, 90]
        for threshold in reversed(thresholds):
            if is_timedelta_elapsed(
                instance,
                date_field_name="expected_construction_completion_date",
                days=threshold,
            ):
                send_incentive_reserved_monthly_notification(instance, threshold)
