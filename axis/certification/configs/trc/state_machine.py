import logging

from django_states.machine import StateMachine, StateDefinition

from ..base import ConfigStateMachineMixin, ConfigStateTransition
from . import strings

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Shorthand for all of TRCs wide-open transition logic
ALL_STATES = [
    "initial",
    "pre_qual",
    "application",
    "technical_assistance",
    "incentive_reserved",
    "verification",
    "incentive_requested",
    "complete",
    "project_maintenance",
    "dropped",
    "waitlist",
]


class TRCStateMachine(ConfigStateMachineMixin, StateMachine):
    """State machine for both Project and Building types"""

    state_choices_order = (
        "to_initial",
        "to_pre_qual",
        "to_application",
        "to_technical_assistance",
        "to_incentive_reserved",
        "to_verification",
        "to_incentive_requested",
        "to_complete",
        "to_project_maintenance",
        "to_dropped",
        "to_waitlist",
    )

    # States
    class initial(StateDefinition):
        initial = True
        name = strings.STATE_NAMES["initial"]
        description = name

    class pre_qual(StateDefinition):
        name = strings.STATE_NAMES["pre_qual"]
        description = name

    class application(StateDefinition):
        name = strings.STATE_NAMES["application"]
        description = name

    class technical_assistance(StateDefinition):
        name = strings.STATE_NAMES["technical_assistance"]
        description = name

    class incentive_reserved(StateDefinition):
        name = strings.STATE_NAMES["incentive_reserved"]
        description = name

    class verification(StateDefinition):
        name = strings.STATE_NAMES["verification"]
        description = name

    class incentive_requested(StateDefinition):
        name = strings.STATE_NAMES["incentive_requested"]
        description = name

    class complete(StateDefinition):
        name = strings.STATE_NAMES["complete"]
        description = name

    class project_maintenance(StateDefinition):
        name = strings.STATE_NAMES["project_maintenance"]
        description = name

    class dropped(StateDefinition):
        name = strings.STATE_NAMES["dropped"]
        description = name

    class waitlist(StateDefinition):
        name = strings.STATE_NAMES["waitlist"]
        description = name

    # Transitions
    class to_pre_qual(ConfigStateTransition):
        description = strings.STATE_NAMES["pre_qual"]
        to_state = "pre_qual"
        from_states = ALL_STATES

    class to_application(ConfigStateTransition):
        description = strings.STATE_NAMES["application"]
        to_state = "application"
        from_states = ALL_STATES

    class to_technical_assistance(ConfigStateTransition):
        description = strings.STATE_NAMES["technical_assistance"]
        to_state = "technical_assistance"
        from_states = ALL_STATES

    class to_incentive_reserved(ConfigStateTransition):
        description = strings.STATE_NAMES["incentive_reserved"]
        to_state = "incentive_reserved"
        from_states = ALL_STATES

    class to_verification(ConfigStateTransition):
        description = strings.STATE_NAMES["verification"]
        to_state = "verification"
        from_states = ALL_STATES

    class to_incentive_requested(ConfigStateTransition):
        description = strings.STATE_NAMES["incentive_requested"]
        to_state = "incentive_requested"
        from_states = ALL_STATES

    class to_complete(ConfigStateTransition):
        description = strings.STATE_NAMES["complete"]
        to_state = "complete"
        from_states = ALL_STATES

    class to_project_maintenance(ConfigStateTransition):
        description = strings.STATE_NAMES["project_maintenance"]
        to_state = "project_maintenance"
        from_states = ALL_STATES

    class to_dropped(ConfigStateTransition):
        description = strings.STATE_NAMES["dropped"]
        to_state = "dropped"
        from_states = ALL_STATES

    class to_waitlist(ConfigStateTransition):
        description = strings.STATE_NAMES["waitlist"]
        to_state = "waitlist"
        from_states = ALL_STATES
