"""accreditation.py: """

__author__ = "Artem Hruzd"
__date__ = "12/24/2019 12:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class InspectionGradeTestMixin:
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
        from axis.relationship.models import Relationship
        from axis.user_management.models import InspectionGrade
        from ..factories import inspection_grade_factory

        general_super_user_factory()

        momentum_company = rater_organization_factory(name="momentum")
        rater_admin = rater_admin_factory(company=momentum_company)
        neea_company = provider_organization_factory(name="neea", slug="neea", is_customer=True)
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

        inspection_grade_factory(
            user=rater_admin, approver=provider_admin, letter_grade=InspectionGrade.A_GRADE
        )
        inspection_grade_factory(
            user=rater_admin, approver=provider_admin, letter_grade=InspectionGrade.B_GRADE
        )
        inspection_grade_factory(
            user=rater_admin, approver=provider_admin, letter_grade=InspectionGrade.C_GRADE
        )
        inspection_grade_factory(
            user=rater_admin, approver=provider_admin, letter_grade=InspectionGrade.D_GRADE
        )
        inspection_grade_factory(
            user=rater_admin, approver=provider_admin, letter_grade=InspectionGrade.F_GRADE
        )
