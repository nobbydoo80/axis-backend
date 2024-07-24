"""state_machine.py: Django Program Home Status State machine."""


import logging
from django_states.machine import StateMachine, StateDefinition, StateTransition

__author__ = "Steven Klass"
__date__ = "1/11/13 7:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class IPPItemStateMachine(StateMachine):
    """
    This is the state machine for Incentive Payments.
    """

    log_transitions = True

    class start(StateDefinition):
        """
        All initial requirements are met.
        Home has been certified.
        Home has not been paid previously.
        """

        description = "Received"
        initial = True

    class ipp_failed_restart(StateDefinition):
        """
        After a home has failed this is where it comes back when
        the rater has corrected.
        """

        description = "Correction Received"

    class ipp_payment_requirements(StateDefinition):
        """
        All initial requirements are met.
        Home has been certified.
        Home has not been paid previously.
        """

        description = "Approved"

    class ipp_payment_failed_requirements(StateDefinition):
        """
        All initial requirements are met.
        Home has been certified.
        Home has not been paid previously.
        """

        description = "Correction Required"

    class ipp_payment_automatic_requirements(StateDefinition):
        """
        All initial requirements are met.
        Home has been certified.
        Home has not been paid previously.
        """

        description = "Approved for Payment"

    class payment_pending(StateDefinition):
        """
        All initial requirements are ment
        """

        description = "Payment Pending"

    class complete(StateDefinition):
        """
        All initial requirements are ment
        """

        description = "Paid"

    # ---- State Transitions ---

    class pending_requirements(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_states = ["start", "ipp_failed_restart"]
        to_state = "ipp_payment_requirements"
        description = "Verify (Manually) all requirements (Floorplan, RemRate)"

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_payment.add_incentivedistribution") or user.has_perm(
                "incentive_payment.change_incentivepaymentstatus"
            )

    class failed_requirements(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_states = ["start", "ipp_failed_restart"]
        to_state = "ipp_payment_failed_requirements"
        description = "Failed any Manual Requirements"

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_payment.add_incentivedistribution") or user.has_perm(
                "incentive_payment.change_incentivepaymentstatus"
            )

    class corrected_requirements(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_state = "ipp_payment_failed_requirements"
        to_state = "ipp_failed_restart"
        description = "Corrected all Manual Requirements"

        def has_permission(transition, instance, user):
            return user.has_perm("home.add_home")

    class pending_automatic_requirements(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_state = "ipp_payment_requirements"
        to_state = "ipp_payment_automatic_requirements"
        description = "Verify (Automatic) all requirements (Metersets)"

    class pending_payment_requirements(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_state = "ipp_payment_automatic_requirements"
        to_state = "payment_pending"
        description = "Incentive Payment has been requested."

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_payment.add_incentivedistribution")

    class reset_prior_approved(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_states = ["ipp_payment_automatic_requirements", "ipp_failed_restart"]
        to_state = "start"
        description = "Reset an Approved Incentive Payment"

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_payment.add_incentivedistribution") or user.has_perm(
                "incentive_payment.change_incentivepaymentstatus"
            )

    class distribution_delete_reset(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_state = "payment_pending"
        to_state = "start"
        description = "Incentive Distribution has been deleted."

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_payment.add_incentivedistribution")

    class pending_complete(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_state = "payment_pending"
        to_state = "complete"
        description = "Incentive Payment has been paid."

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_payment.add_incentivedistribution")

    class undo_corrections_required_from_start(StateTransition):
        from_state = "ipp_payment_failed_requirements"
        to_state = "start"
        description = "Accidentally sent to Corrections Required"

        def has_permissions(transition, instance, user):
            return user.has_perm("incentive_paymnet.add_incentivedistribution")

    class undo_corrections_required_from_corrections_recieved(StateTransition):
        from_state = "ipp_payment_failed_requirements"
        to_state = "ipp_failed_restart"
        description = "Accidentally sent to Corrections Required"

        def has_permission(transition, instance, user):
            return user.has_perm("incentive_paymnet.add_incentivedistribution")

    @classmethod
    def get_state_choices(cls):
        """
        Gets all possible choices for a model.
        """
        order = [
            "start",
            "ipp_payment_requirements",
            "ipp_payment_automatic_requirements",
            "payment_pending",
            "complete",
            "ipp_payment_failed_requirements",
            "ipp_failed_restart",
        ]
        assert set(order) == set(cls.states.keys()), "State Mismatch!!"
        return [(k, cls.states[k].description) for k in order]
