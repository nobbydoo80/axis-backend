"""mixins.py: Django User Management"""

__author__ = "Steven Klass"
__date__ = "9/18/14 1:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

log = logging.getLogger(__name__)


class TrainingTextMixin:
    @classmethod
    def setUpTestData(cls):
        from axis.company.tests.factories import (
            rater_organization_factory,
            provider_organization_factory,
        )
        from axis.core.tests.factories import (
            general_super_user_factory,
            provider_admin_factory,
            rater_admin_factory,
        )

        from axis.eep_program.models import EEPProgram
        from axis.user_management.states import TrainingStatusStates
        from axis.relationship.models import Relationship
        from axis.company.models import SponsorPreferences
        from ..factories import training_factory, training_status_factory

        general_super_user_factory()

        momentum_company = rater_organization_factory(name="momentum")
        rater_admin = rater_admin_factory(company=momentum_company)
        neea_company = provider_organization_factory(name="neea", slug="neea", is_customer=True)

        SponsorPreferences.objects.create(sponsor=neea_company, sponsored_company=momentum_company)

        aps_company = provider_organization_factory(name="aps", slug="aps", is_customer=True)
        provider_admin = provider_admin_factory(
            company=neea_company, username="neea_provider_admin"
        )

        eep_program = EEPProgram.objects.create(
            **{
                "name": "NEEA",
                "owner": neea_company,
                "is_legacy": False,
                "is_public": True,
                "is_active": True,
                "is_qa_program": False,
                "slug": "wa-code-study",
            }
        )
        eep_program.certifiable_by.add(neea_company)

        Relationship.objects.create_mutual_relationships(momentum_company, neea_company)

        training = training_factory(trainee=rater_admin)
        training_status_factory(
            training=training, state=TrainingStatusStates.NEW, company=neea_company
        )

        training = training_factory(trainee=rater_admin)
        training_status_factory(
            training=training,
            state=TrainingStatusStates.APPROVED,
            company=neea_company,
            approver=provider_admin,
        )

        training = training_factory(trainee=rater_admin)
        training_status_factory(
            training=training,
            state=TrainingStatusStates.REJECTED,
            company=neea_company,
            approver=provider_admin,
        )

        training = training_factory(trainee=rater_admin)
        training_status_factory(
            training=training,
            state=TrainingStatusStates.EXPIRED,
            company=neea_company,
            approver=provider_admin,
        )
