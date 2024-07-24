"""accreditation.py: """

__author__ = "Artem Hruzd"
__date__ = "12/24/2019 12:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationTestMixin:
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
        from axis.relationship.models import Relationship
        from axis.user_management.models import Accreditation
        from ..factories import accreditation_factory

        general_super_user_factory()

        momentum_company = rater_organization_factory(name="momentum")
        rater_admin = rater_admin_factory(company=momentum_company)
        neea_company = provider_organization_factory(name="neea", slug="neea", is_customer=True)
        provider_admin = provider_admin_factory(
            company=neea_company, username="neea_provider_admin"
        )

        Relationship.objects.create_mutual_relationships(momentum_company, neea_company)

        accreditation_factory(
            trainee=rater_admin, approver=provider_admin, state=Accreditation.INACTIVE_STATE
        )
        accreditation_factory(
            trainee=rater_admin, approver=provider_admin, state=Accreditation.ACTIVE_STATE
        )
        accreditation_factory(
            trainee=rater_admin, approver=provider_admin, state=Accreditation.PROBATION_NEW_STATE
        )
        accreditation_factory(
            trainee=rater_admin,
            approver=provider_admin,
            state=Accreditation.PROBATION_DISCIPLINARY_STATE,
        )
