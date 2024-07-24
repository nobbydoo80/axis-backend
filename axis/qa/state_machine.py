"""state_machine.py: Django qa"""

__author__ = "Steven Klass"
__date__ = "12/20/13 6:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging

from django.apps import apps
from django_states.machine import StateMachine, StateDefinition, StateTransition

from axis.qa.messages import (
    QAAddedMessage,
    QaCorrectionReceivedMessage,
    CustomerHIRLQaCorrectionReceivedMessage,
    QaCorrectionRequiredMessage,
    NEEABPAQACompleteFailedMessage,
    QAGatingCompleteMessage,
    QaCompleteMessage,
)

from .utils import (
    qa_state_change_handler,
    get_content_object_data_for_qa_messages,
    get_qa_message_context,
)
from axis.customer_neea.utils import NEEA_BPA_SLUGS

log = logging.getLogger(__name__)

customer_hirl_app = apps.get_app_config("customer_hirl")


class QAStateMachine(StateMachine):
    """
    This is the state machine for QA.
    """

    log_transitions = True

    class received(StateDefinition):
        description = "Received"
        initial = True

        def handler(self, instance):
            if instance.requirement.coverage_pct < 1.0:
                QAAddedMessage().send(
                    company=instance.home_status.company,
                    context={
                        "home": instance.home_status.home.get_addr(),
                        "home_url": instance.home_status.home.get_absolute_url(),
                        "qa_type": instance.requirement.get_type_display(),
                    },
                )
            qa_state_change_handler(instance)

    class in_progress(StateDefinition):
        description = "In Progress"

        def handler(self, instance):
            qa_state_change_handler(instance)

    class correction_required(StateDefinition):
        description = "Correction Required"

        def handler(self, instance):
            qa_state_change_handler(instance)

            data = get_content_object_data_for_qa_messages(instance)
            context = get_qa_message_context(instance, data)
            QaCorrectionRequiredMessage(url=context["action_url"]).send(
                context=context,
                company=data["company"],
            )

    class correction_received(StateDefinition):
        description = "Correction Received"

        def handler(self, instance):
            qa_state_change_handler(instance)

            if (
                getattr(instance, "home_status", None)
                and instance.home_status.eep_program.slug
                in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            ):
                from axis.qa.models import QARequirement

                requirement_type = instance.requirement.type
                if requirement_type == QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE:
                    verifier = instance.home_status.customer_hirl_rough_verifier
                else:
                    verifier = instance.home_status.customer_hirl_final_verifier

                qa_designee_name = ""
                qa_designee_url = ""
                if instance.qa_designee:
                    qa_designee_name = instance.qa_designee.get_full_name()
                    qa_designee_url = instance.qa_designee.get_absolute_url()

                verifier_name = ""
                verifier_url = ""
                if verifier:
                    verifier_name = verifier.get_full_name()
                    verifier_url = verifier.get_absolute_url()

                CustomerHIRLQaCorrectionReceivedMessage(url=instance.get_absolute_url()).send(
                    context={
                        "requirement_type": instance.requirement.get_type_display(),
                        "verifier_name": verifier_name,
                        "verifier_url": verifier_url,
                        "home_url": instance.home_status.home.get_absolute_url(),
                        "home_address": instance.home_status.home.get_addr(),
                        "qa_designee_name": qa_designee_name,
                        "qa_designee_url": qa_designee_url,
                        "qa_link": f"{instance.get_absolute_url()}#/tabs/qa",
                        "qa_notes": instance.qanote_set.all().order_by("-created_on"),
                    },
                    company=instance.owner,
                )
            else:
                data = get_content_object_data_for_qa_messages(instance)
                context = get_qa_message_context(instance, data)
                QaCorrectionReceivedMessage(url=context["action_url"]).send(
                    context=context,
                    company=data["owner"],
                )

    class complete(StateDefinition):
        description = "Complete"

        def handler(self, instance):
            qa_state_change_handler(instance)
            data = get_content_object_data_for_qa_messages(instance)
            context = get_qa_message_context(instance, data)

            if (
                instance.home_status.eep_program.slug in NEEA_BPA_SLUGS
                and instance.result == "fail"
            ):
                receiving_companies = filter(
                    None,
                    [
                        instance.home_status.company,
                        instance.home_status.get_electric_company(),
                        instance.home_status.get_gas_company(),
                    ],
                )
                message = NEEABPAQACompleteFailedMessage()

                for company in receiving_companies:
                    message(url=instance.get_absolute_url()).send(context=context, company=company)

            message = QAGatingCompleteMessage
            if instance.requirement.gate_certification:
                message = QaCompleteMessage

            if data["provider"]:  # FIXME: Remove this protection statement
                if instance.owner is not data["provider"]:
                    provider_context = context.copy()
                    message(url=context["action_url"]).send(
                        context=provider_context,
                        company=data["provider"],
                    )

            if data["rater"]:  # FIXME: Remove this protection statement
                if instance.owner is not data["rater"]:
                    rater_context = context.copy()
                    message(url=context["action_url"]).send(
                        context=rater_context,
                        company=data["rater"],
                    )

    class received_to_in_progress(StateTransition):
        from_state = "received"
        to_state = "in_progress"
        description = "QA has started"

        def has_permission(transition, instance, user):
            # This is an automated transition
            return True

    class in_progress_to_complete(StateTransition):
        from_state = "in_progress"
        to_state = "complete"
        description = "QA is complete"

        def has_permission(transition, instance, user):
            # This is an automated transition
            return True

    class in_progress_to_correction_required(StateTransition):
        from_state = "in_progress"
        to_state = "correction_required"
        description = "QA correction is requested"

        def has_permission(transition, instance, user):
            # This comes from a QA to the Rater
            return user.company.id == instance.owner.id or user.is_superuser

    class correction_required_to_correction_received(StateTransition):
        from_state = "correction_required"
        to_state = "correction_received"
        description = "QA correction is resubmitted"

        def has_permission(transition, instance, user):
            # This comes from a Rater back..
            home_status = instance.get_home_status()
            company = home_status.company
            return user.company.id == company.id or user.is_superuser

    class correction_received_to_correction_required(StateTransition):
        from_state = "correction_received"
        to_state = "correction_required"
        description = "QA correction is resubmitted"

        def has_permission(transition, instance, user):
            # This comes from a QA to the Rater
            return user.company.id == instance.owner.id or user.is_superuser

    class correction_received_to_complete(StateTransition):
        from_state = "correction_received"
        to_state = "complete"
        description = "QA correction complete"

        def has_permission(transition, instance, user):
            # This is an automated transition
            return True
