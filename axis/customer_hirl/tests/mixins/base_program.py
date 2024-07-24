"""scoring_base_fixturecompiler.py: """

__author__ = "Artem Hruzd"
__date__ = "01/24/2021 15:58"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.customer_hirl.models import BuilderAgreement
from axis.customer_hirl.tests.factories import builder_agreement_factory


class HIRLScoringBaseTaskMixin:
    """
    Create 2 homes with eep_program_home_status for each(sf and mf)
    and annotations for each eep_program_home_status
    """

    program_builder_classes = []

    @classmethod
    def setUpTestData(cls):
        """Fixture populate method"""
        from django.apps import apps
        from django.contrib.contenttypes.models import ContentType

        from axis.annotation.models import Type as AnnotationType
        from axis.annotation.tests.factories import type_factory, annotation_factory
        from axis.company.models import SponsorPreferences
        from axis.company.tests.factories import (
            provider_organization_factory,
            rater_organization_factory,
            builder_organization_factory,
        )
        from axis.core.tests.factories import (
            provider_user_factory,
            rater_user_factory,
            builder_user_factory,
        )

        from axis.customer_hirl.tests.factories import hirl_green_energy_badge_factory
        from axis.customer_hirl.models import HIRLProjectRegistration
        from axis.customer_hirl.tests.factories import (
            hirl_project_factory,
            coi_document_factory,
            verifier_agreement_factory,
            hirl_project_registration_factory,
        )
        from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
        from axis.geographic.tests.factories import real_city_factory
        from axis.home.models import EEPProgramHomeStatus
        from axis.qa.models import QARequirement
        from axis.relationship.models import Relationship
        from axis.user_management.models import Accreditation
        from axis.user_management.tests.factories import accreditation_factory

        customer_hirl_app = apps.get_app_config("customer_hirl")

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_agreement_factory(
            owner=hirl_company, company=builder_organization, state=BuilderAgreement.COUNTERSIGNED
        )
        builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        # set user company sponsored by HIRL add verifier agreement,
        # create COI for company and add all accreditations
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=rater_organization
        )
        Relationship.objects.create_mutual_relationships(rater_organization, hirl_company)
        rater_organization.update_permissions()

        verifier_agreement_factory(
            verifier=company_admin_rater_user,
            owner=hirl_company,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        coi_document_factory(company=company_admin_rater_user.company)

        accreditation_factory(
            trainee=company_admin_rater_user,
            name=Accreditation.NGBS_2012_NAME,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            trainee=company_admin_rater_user,
            name=Accreditation.NGBS_2015_NAME,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            trainee=company_admin_rater_user,
            name=Accreditation.NGBS_2020_NAME,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            trainee=company_admin_rater_user,
            name=Accreditation.NGBS_WRI_VERIFIER_NAME,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            trainee=company_admin_rater_user,
            name=Accreditation.NGBS_GREEN_FIELD_REP_NAME,
            state=Accreditation.ACTIVE_STATE,
        )

        phoenix_city = real_city_factory(name="Phoenix", state="AZ")

        for index, program_builder_cls in enumerate(cls.program_builder_classes):
            program_builder = program_builder_cls()
            eep_program = program_builder.build()
            eep_program.customer_hirl_certification_fee = 100
            eep_program.save()

            QARequirement.objects.create(
                qa_company=hirl_company,
                type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                eep_program=eep_program,
            )

            QARequirement.objects.create(
                qa_company=hirl_company,
                type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                eep_program=eep_program,
            )

            eep_program_home_status_content_type = ContentType.objects.get_for_model(
                EEPProgramHomeStatus
            )

            for type_slug, type_data in program_builder.annotations.items():
                annotation_type = AnnotationType.objects.filter(slug=type_slug).first()
                if not annotation_type:
                    annotation_type = type_factory(
                        slug=type_slug,
                        applicable_content_types=[
                            eep_program_home_status_content_type,
                        ],
                        **type_data,
                    )

            project_type = HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
            if eep_program.is_multi_family:
                project_type = HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE

            registration = hirl_project_registration_factory(
                project_type=project_type,
                eep_program=eep_program,
                builder_organization=builder_organization,
                registration_user=company_admin_rater_user,
            )

            hirl_project = hirl_project_factory(
                registration=registration,
                home_status__home__street_line1=f"home address test{index}",
                home_status__home__lot_number=f"{index}",
                home_status__home__is_multi_family=eep_program.is_multi_family,
                home_status__home__zipcode=f"{index * 1000}",
                home_status__home__city=phoenix_city,
                home_status__company=company_admin_rater_user.company,
                home_status__eep_program=eep_program,
                home_address_geocode_response=None,
                story_count=1,
                number_of_units=1,
            )

            # remove home_status that automatically created in factory
            # and use create_home_status() to create correct one
            hirl_project.home_status.delete()

            registration.active()
            registration.save()

            hirl_project.create_home_status()
            hirl_project.save()

            hirl_green_energy_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=50)

            hirl_project.green_energy_badges.add(hirl_green_energy_badge)
            hirl_project.save()
