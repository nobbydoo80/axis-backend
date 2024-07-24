"""state_machine.py: Django sampleset"""


import logging
from django_states.machine import StateMachine, StateDefinition, StateTransition

__author__ = "Steven Klass"
__date__ = "7/21/14 9:07 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSetStateMachine(StateMachine):
    """This is the state machine for Samplesets."""

    log_transitions = True

    class unconfirmed(StateDefinition):
        """This allows answers to be contributed"""

        initial = True
        description = "Un-Confirmed"

    class confirmed(StateDefinition):
        """This sets and locks in the answers"""

        description = "Confirmed"

    class confirm_transition(StateTransition):
        """Transition to a confirmed state"""

        from_state = "unconfirmed"
        to_state = "confirmed"
        description = "Transition to Confirmed"
        # TODO Lock in all answers..

    class rollback_confirm_transition(StateTransition):
        """Rollback a locked in answer set"""

        from_state = "confirmed"
        to_state = "unconfirmed"
        description = "Rollback to  Un-Confirmed"
        # TODO Un-Lock in all answers..

    @classmethod
    def get_state_choices(cls):
        """Gets all possible choices for a model."""
        order = ["unconfirmed", "confirmed"]
        assert set(order) == set(cls.states.keys()), "State Mismatch!!"
        return [(k, cls.states[k].description) for k in order]
