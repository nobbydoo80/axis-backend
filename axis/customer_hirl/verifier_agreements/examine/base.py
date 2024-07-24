"""Examine support for `customer_hirl.builder_agreements`"""


import logging
from operator import itemgetter

from django.apps import apps
from django.urls import reverse, reverse_lazy

from axis.examine import machinery
from ..states import VerifierAgreementStates
from axis.customer_hirl.models import VerifierAgreement

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


class BaseVerifierAgreementMachinery(machinery.ExamineMachinery):
    """
    Base machinery for both owners and enrollees.
    Do not use this directly.
    """

    model = VerifierAgreement
    delete_success_url = reverse_lazy("hirl:verifier_agreements:list")
    use_serializer_verbose_names = True  # Opting into serializer labels feature

    def can_edit_object(self, instance, user=None):
        """Gates edit permission by the current state. This is an object-level permission."""

        can_edit = super(BaseVerifierAgreementMachinery, self).can_edit_object(instance, user=user)
        role_can_edit = False
        if instance.has_owner_powers(user):
            role_can_edit = (
                VerifierAgreementStates.order_map[instance.state]
                >= VerifierAgreementStates.order_map[VerifierAgreementStates.APPROVED]
            )
        elif instance.has_verifier_powers(user):
            role_can_edit = instance.pk is not None  # state already 'new' from field default
        return can_edit and role_can_edit

    def can_delete_object(self, instance, user=None):
        """Return False, or True for super."""
        return False

    def get_object_name(self, instance):
        """Get object display string."""

        if instance.pk:
            return "{}".format(instance.verifier)
        return super(BaseVerifierAgreementMachinery, self).get_object_name(instance)

    def get_static_actions(self, instance):
        """Return static actions with contextual additions for the current state."""

        self.admin_actions = []

        actions = super(BaseVerifierAgreementMachinery, self).get_static_actions(instance)

        if (
            instance and instance.has_owner_powers(self.context["request"].user)
        ) and not self.create_new:
            # Get simple list transition methods.  Multiple results will come back for a transition
            # with more than one `source` state.  It is safe to collapse these because they share
            # all the same identifying information.
            transitions = list(
                dict((v.name, v) for v in instance.get_all_state_transitions()).values()
            )

            self.admin_actions += (
                [
                    {
                        "name": "Force specific status",
                        "icon": "wrench",
                        "description": """
                    Notifications and documents will not be generated !
                """,
                    }
                ]
                + list(
                    sorted(
                        (
                            {
                                "name": VerifierAgreementStates.verbose_names[transition.target],
                                "instruction": transition.target,
                                "icon": "dot-circle-o"
                                if transition.target == instance.state
                                else "circle-thin",
                                "order": VerifierAgreementStates.order_map[transition.target],
                            }
                            for transition in transitions
                        ),
                        key=itemgetter("order"),
                    )
                )
            )

        if self.admin_actions:
            actions.insert(
                0,
                self.Action(
                    "", icon="cog", instruction=None, type="dropdown", items=self.admin_actions
                ),
            )

        return actions

    def get_helpers(self, instance):
        """Return support dict for client page to trigger custom actions on the server."""

        helpers = super(BaseVerifierAgreementMachinery, self).get_helpers(instance)

        helpers["api_urls"] = {
            "force_state": reverse(
                "apiv2:hirl_verifier_agreement-force-state", kwargs={"pk": "__ID__"}
            ),
            "transition": reverse(
                "apiv2:hirl_verifier_agreement-transition", kwargs={"pk": "__ID__"}
            ),
        }

        helpers["va_version_to_sign"] = None

        if instance.pk:
            helpers["va_version_to_sign"] = instance.get_va_version_to_sign()

        return helpers
