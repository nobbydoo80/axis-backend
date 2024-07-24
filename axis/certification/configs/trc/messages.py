from axis.messaging.messages import ModernMessage
from . import strings

import logging


__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class TRCMessageMixin(object):
    company_slugs = ["trc"]


class TRCEscalatedMessage(TRCMessageMixin, ModernMessage):
    content = strings.PROJECT_ELEVATED_FOR_ADMIN
    sticky_alert = True
    category = "project"
    level = "warning"

    verbose_name = "Project Elevated"
    description = "Project has been elevated for admin attention."


class TRCIncentiveReservedMonthlyMessage(TRCMessageMixin, ModernMessage):
    content = strings.INCENTIVE_RESERVED_MONTHLY_MESSAGE
    sticky_alert = True
    category = "project_recurring"
    level = "info"

    verbose_name = "Incentive Reservation Reminder"
    description = "Recurring monthly reminder of date an incentive has been reserved."


class TRCIncentiveReservedConstructionReminderMessage(TRCMessageMixin, ModernMessage):
    content = strings.INCENTIVE_RESERVED_CONSTRUCTION_REMINDER_MESSAGE
    sticky_alert = True
    category = "project_recurring"
    level = "info"

    verbose_name = "Construction Start Reminder"
    description = "One-month and two-week notices ahead of the project's construction start date."


class TRCTransitionSuccessfulMixin(TRCMessageMixin):
    sticky_alert = False
    category = "project"
    level = "success"

    # verbose_name = "State Transition Successful"
    # description = "Notice that a state change has successfully occured."


TRANSITION_SUCCESSFUL_MESSAGES = {}
for state_name, msg in strings.TRANSITION_SUCCESSFUL_MESSAGE_STRINGS.items():
    state_display_name = strings.STATE_NAMES[state_name]
    message_name = "TransitionSuccessful_{}_Message".format(state_name)
    message_class = type(
        str(message_name),
        (TRCTransitionSuccessfulMixin, ModernMessage),
        {
            "content": msg,
            "verbose_name": "Project Transition to {}".format(state_display_name),
            "description": "Project has reached the {} state.".format(state_display_name),
        },
    )
    TRANSITION_SUCCESSFUL_MESSAGES[state_name] = message_class


class TRCNewSubstateMixin(TRCMessageMixin):
    sticky_alert = False
    category = "project"
    level = "success"

    # verbose_name = "New Substate"
    # description = "Notice that a new substate has been entered."


SUBSTATE_TRANSITION_MESSAGES = {}
for state_name, substate_info in strings.SUBSTATE_TRANSITION_MESSAGE_STRINGS.items():
    state_display_name = strings.STATE_NAMES[state_name]
    for substate_name, msg in substate_info.items():
        substate_display_name = strings.SUBSTATE_NAMES[state_name][substate_name]
        message_name = "NewSubstate_{}_{}_Message".format(state_name, substate_name)
        message_class = type(
            str(message_name),
            (TRCNewSubstateMixin, ModernMessage),
            {
                "content": msg,
                "verbose_name": "Project Transition to {}: {}".format(
                    state_display_name, substate_display_name
                ),
                "description": "Project has reached {}.".format(substate_display_name),
            },
        )
        substate_messages = SUBSTATE_TRANSITION_MESSAGES.setdefault(state_name, {})
        substate_messages[substate_name] = message_class
