from axis.company.models import Company, BuilderOrganization
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.models import User
from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory
from axis.qa.models import QARequirement, QAStatus

__author__ = "Michael Jeffrey"
__date__ = "10/21/15 5:37 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


class QAManagerTestMixin(CompaniesAndUsersTestMixin):
    include_company_types = ["general", "qa", "utility", "provider", "builder", "rater"]
    include_unrelated_companies = False

    @classmethod
    def setUpTestData(cls):
        from axis.home.models import EEPProgramHomeStatus
        from axis.home.tests.factories import custom_home_factory
        from axis.eep_program.models import EEPProgram
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.eep_program.utils import create_qa_program_from_base
        from axis.relationship.models import Relationship

        super(QAManagerTestMixin, cls).setUpTestData()

        qa = User.objects.get(company__company_type="qa", is_company_admin=True)
        qa.company.update_permissions("qa")

        utility = User.objects.get(company__company_type="utility", is_company_admin=True)
        Company.objects.filter(company_type="utility").update(is_eep_sponsor=True)

        provider = User.objects.get(company__company_type="provider", is_company_admin=True)

        cls.rater = User.objects.get(company__company_type="rater", is_company_admin=True)

        builder = User.objects.get(company__company_type="builder", is_company_admin=True)
        cls.eep_program = basic_eep_program_factory(owner=utility.company, no_close_dates=True)
        original_slug = cls.eep_program.slug
        create_qa_program_from_base(cls.eep_program)
        EEPProgram.objects.filter(is_qa_program=True).update(
            viewable_by_company_type="provider,qa,utility"
        )
        cls.eep_program = EEPProgram.objects.get(slug=original_slug)

        home_one = custom_home_factory(builder_org=builder.company)
        home_two = custom_home_factory(builder_org=builder.company)

        orgs = [cls.rater.company, provider.company, qa.company, utility.company, builder.company]
        Relationship.objects.create_mutual_relationships(*orgs)

        for company in orgs:
            Relationship.objects.validate_or_create_relations_to_entity(home_one, company)
            Relationship.objects.validate_or_create_relations_to_entity(home_two, company)

        home_status_one = EEPProgramHomeStatus.objects.create(
            eep_program=cls.eep_program, company=cls.rater.company, home=home_one
        )
        home_status_two = EEPProgramHomeStatus.objects.create(
            eep_program=cls.eep_program, company=cls.rater.company, home=home_two
        )

        field_qa = QARequirement.objects.create(
            qa_company=qa.company, eep_program=cls.eep_program, type="field"
        )
        file_qa = QARequirement.objects.create(
            qa_company=qa.company, eep_program=cls.eep_program, type="file"
        )
        QAStatus.objects.create(home_status=home_status_one, owner=qa.company, requirement=field_qa)
        QAStatus.objects.create(home_status=home_status_two, owner=qa.company, requirement=field_qa)
        QAStatus.objects.create(home_status=home_status_one, owner=qa.company, requirement=file_qa)
        QAStatus.objects.create(home_status=home_status_two, owner=qa.company, requirement=file_qa)

        basic_incentive_payment_status_factory(home_status=home_status_one, owner=builder.company)
        basic_incentive_payment_status_factory(home_status=home_status_two, owner=builder.company)


class QATestMixin(CompaniesAndUsersTestMixin):
    include_company_types = ["qa", "utility", "provider", "builder", "rater"]
    include_unrelated_companies = False

    @classmethod
    def setUpTestData(cls):
        from axis.home.models import EEPProgramHomeStatus
        from axis.home.tests.factories import custom_home_factory
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.eep_program.utils import create_qa_program_from_base
        from axis.relationship.models import Relationship
        from axis.subdivision.tests.factories import subdivision_factory

        super(QATestMixin, cls).setUpTestData()

        cls.qa = User.objects.get(company__company_type="qa", is_company_admin=True)
        cls.qa.company.update_permissions("qa")

        utility = User.objects.get(company__company_type="utility", is_company_admin=True)
        Company.objects.filter(company_type="utility").update(is_eep_sponsor=True)

        provider = User.objects.get(company__company_type="provider", is_company_admin=True)
        cls.rater = User.objects.get(company__company_type="rater", is_company_admin=True)
        cls.builder = User.objects.get(company__company_type="builder", is_company_admin=True)

        cls.eep_program = basic_eep_program_factory(owner=utility.company, no_close_dates=True)
        program_slug = cls.eep_program.slug

        cls.qa_eep_program = create_qa_program_from_base(cls.eep_program)
        from axis.eep_program.models import EEPProgram

        EEPProgram.objects.filter(is_qa_program=True).update(
            viewable_by_company_type="provider,qa,utility"
        )

        # re-look up the program, because the util breaks the reference
        cls.eep_program = EEPProgram.objects.get(slug=program_slug)

        home = custom_home_factory(builder_org=cls.builder.company)
        subdivision = subdivision_factory(
            builder_org=Company.objects.get(id=cls.builder.company.id)
        )
        home.subdivision = subdivision
        home.save()

        orgs = [
            cls.rater.company,
            provider.company,
            cls.qa.company,
            utility.company,
            cls.builder.company,
        ]
        for company in orgs:
            Relationship.objects.validate_or_create_relations_to_entity(home, company)

        cls.home_status = EEPProgramHomeStatus.objects.create(
            eep_program=cls.eep_program, company=cls.rater.company, home=home
        )
        cls.home_status.save()

    def _get_requirement_and_qa_status(
        self,
        requirement_type="file",
        requirement_gate_certification=False,
        qa_status_state="received",
    ):
        requirement = QARequirement.objects.create(
            qa_company=self.qa.company,
            eep_program=self.eep_program,
            type=requirement_type,
            gate_certification=requirement_gate_certification,
        )
        qa_status = QAStatus.objects.create(
            owner=self.qa.company,
            state=qa_status_state,
            requirement=requirement,
            home_status=self.home_status,
        )
        return requirement, qa_status
