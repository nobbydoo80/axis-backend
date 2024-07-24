"""state_machine.py: Django Program Home Status State machine."""

import logging

from celery import chain

from django_states.machine import StateMachine, StateDefinition, StateTransition

from axis.qa.messages import (
    QaIsGatingCertificationMessage,
    YourQaCompanyIsGatingCertficationMessage,
)
from .messages import NEEABPAHomeCertificationPendingMessage, WSUHomeCertificationPendingMessage

__author__ = "Steven Klass"
__date__ = "1/11/13 7:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..customer_neea.utils import NEEA_BPA_SLUGS

log = logging.getLogger(__name__)


class HomeStatusStateMachine(StateMachine):
    """
    This is the state machine for Programs attached to a home.
    """

    log_transitions = True

    class pending_inspection(StateDefinition):
        """
        Prior to filling out a checklist verify the can (all eep home annotations are filled in)
        """

        initial = True
        description = "Pending"

    class inspection_transition(StateTransition):
        """This will verify all necessary checks prior to starting the checklist is ready to go."""

        from_state = "pending_inspection"
        to_state = "inspection"
        description = "Verify all required annotations are completed"

        def has_permission(transition, instance, user):
            return user.has_perm("checklist.add_answer") or user.has_perm("qa.change_qastatus")

    class inspection(StateDefinition):
        """
        Rater is currently inspecting the home.
        """

        description = "Active"

    class qa_transition(StateTransition):
        """Transition you from Inspection to Certification or Failure"""

        from_state = "inspection"
        to_state = "qa_pending"
        description = "Pending Certification Inspection"

        def has_permission(transition, instance, user):
            return user.has_perm("checklist.add_answer") or user.has_perm("qa.change_qastatus")

    class qa_pending(StateDefinition):
        """
        QA is gating this home
        """

        description = "Pending QA"

        def handler(self, instance):
            from axis.qa.models import QARequirement

            qa_requirements = QARequirement.objects.filter_for_home_status(instance)

            for requirement in qa_requirements:
                if requirement.coverage_pct >= 1 and requirement.gate_certification:
                    log.debug(
                        "Gating 100% Requirement for " "{} not met".format(requirement.qa_company)
                    )

                    url = instance.home.get_absolute_url() + "#/tabs/qa"

                    YourQaCompanyIsGatingCertficationMessage(
                        url=url,
                    ).send(
                        context={
                            "home": instance.home.get_addr(),
                            "home_detail": instance.home.get_absolute_url(),
                        },
                        company=requirement.qa_company,
                    )

                    if not instance.home.bulk_uploaded:
                        QaIsGatingCertificationMessage(
                            url=url,
                        ).send(
                            context={
                                "home": instance.home.get_addr(),
                                "home_url": instance.home.get_absolute_url(),
                                "qa_company": "{}".format(requirement.qa_company),
                            },
                            company=instance.company,
                        )
            if "eto" in instance.eep_program.slug:
                from axis.gbr.tasks import get_or_create_green_building_registry_entry

                get_or_create_green_building_registry_entry.delay(home_id=instance.home_id)

    class certification_transition(StateTransition):
        """
        QA is gating this home
        """

        from_state = "qa_pending"
        to_state = "certification_pending"
        description = "Pending QA to Pending Certification"

        def has_permission(transition, instance, user):
            return user.has_perm("checklist.add_answer") or user.has_perm("qa.change_qastatus")

    class certification_pending(StateDefinition):
        """
        The home has been certified
        """

        description = "Inspected"

        def handler(cls, instance):
            msg = None
            wsu = "provider-washington-state-university-extension-ene"

            if instance.eep_program.slug in NEEA_BPA_SLUGS:
                msg = NEEABPAHomeCertificationPendingMessage()
            elif instance.eep_program.owner.slug == wsu:
                msg = WSUHomeCertificationPendingMessage()

            if msg:
                certification_agent = instance.get_certification_agent()
                message_kwargs = {
                    "company": certification_agent,
                    "context": {
                        "home": instance.home.get_addr(),
                        "home_detail": instance.home.get_absolute_url(),
                        "program": "{}".format(instance.eep_program),
                    },
                }
                msg.send(**message_kwargs)

    class completion_transition(StateTransition):
        """Transition you from Certification to Complete"""

        from_state = "certification_pending"
        to_state = "complete"
        description = "Eligible to Complete Transition"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home") or user.has_perm("qa.change_qastatus")

    class complete(StateDefinition):
        """
        The home has been certified
        """

        description = "Certified"

        def handler(cls, instance):
            # update billing state for HIRLProject
            customer_hirl_project = getattr(instance, "customer_hirl_project", None)
            if customer_hirl_project:
                customer_hirl_project.calculate_billing_state()

            if "eto" in instance.eep_program.slug:
                from axis.customer_eto.tasks.eps import generate_eto_report
                from axis.gbr.tasks import get_or_create_green_building_registry_entry

                chain(
                    generate_eto_report.s(home_status_id=instance.pk),
                    get_or_create_green_building_registry_entry.s(
                        home_id=instance.home.pk, assessment="eps"
                    ),
                ).apply_async()

    class abandoned(StateDefinition):
        """
        The home has been certified
        """

        description = "Abandoned"

    class to_abandoned_transition(StateTransition):
        """Transition to Abandoned"""

        from_states = [
            "pending_inspection",
            "inspection",
            "qa_pending",
            "certification_pending",
            "customer_hirl_pending_project_data",
            "customer_hirl_pending_rough_qa",
            "customer_hirl_pending_final_qa",
        ]
        to_state = "abandoned"
        description = "Transition to Abandoned"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home")

    class abandoned_to_pending_transition(StateTransition):
        """Transition out of Abandoned"""

        from_state = "abandoned"
        to_state = "pending_inspection"

        description = "Transition to Abandoned"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home")

    class failed(StateDefinition):
        """
        The home has been certified
        """

        description = "Failed"

    class to_failed_transition(StateTransition):
        """Transition to Abandoned"""

        from_states = [
            "pending_inspection",
            "inspection",
            "qa_pending",
            "certification_pending",
        ]
        to_state = "failed"
        description = "Transition to Failed"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home")

    class failed_to_pending_transition(StateTransition):
        """Transition out of Abandoned"""

        from_state = "failed"
        to_state = "pending_inspection"

        description = "Transition out Failed"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home")

    class program_change_transition(StateTransition):
        """Transition to Abandoned"""

        from_states = [
            "pending_inspection",
            "inspection",
            "qa_pending",
            "certification_pending",
        ]
        to_state = "pending_inspection"
        description = "Transition back due to program change"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home")

    class certification_pending_to_pending_qa(StateTransition):
        """Transition out of Inspected"""

        from_state = "certification_pending"
        to_state = "qa_pending"

        description = "Transition back to Pending QA"

        def has_permission(transition, instance, user):
            return user.has_perm("home.change_home") or user.has_perm("qa.change_qastatus")

    # Customer HIRL
    class customer_hirl_pending_project_data_transition(StateTransition):
        from_state = "pending_inspection"
        to_state = "customer_hirl_pending_project_data"
        description = "Waiting Project Data to be completed"

    class customer_hirl_pending_project_data(StateDefinition):
        description = "Pending Project Data"

    class customer_hirl_pending_rough_qa(StateDefinition):
        description = "Pending Rough QA"

    class customer_hirl_pending_rough_qa_transition(StateTransition):
        from_state = "customer_hirl_pending_project_data"
        to_state = "customer_hirl_pending_rough_qa"
        description = "Waiting Rough Verification Report"

    class customer_hirl_pending_final_qa(StateDefinition):
        description = "Pending Final QA"

    class customer_hirl_pending_final_qa_transition(StateTransition):
        from_state = "customer_hirl_pending_rough_qa"
        to_state = "customer_hirl_pending_final_qa"
        description = "Waiting Final Verification Report"

    class customer_hirl_certification_pending_transition(StateTransition):
        """Transition you from Certification to Complete"""

        from_state = "customer_hirl_pending_final_qa"
        to_state = "certification_pending"
        description = "Eligible to Complete Transition"

    @classmethod
    def get_state_choices(cls):
        """
        Gets all possible choices for a model.
        """
        order = [
            "pending_inspection",
            "inspection",
            "qa_pending",
            "certification_pending",
            "complete",
            "failed",
            "abandoned",
            "customer_hirl_pending_project_data",
            "customer_hirl_pending_rough_qa",
            "customer_hirl_pending_final_qa",
        ]
        assert set(order) == set(cls.states.keys()), "State Mismatch!!"
        return [(k, cls.states[k].description) for k in order]
