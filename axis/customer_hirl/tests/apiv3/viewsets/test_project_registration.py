"""project_registration.py: """

__author__ = "Artem Hruzd"
__date__ = "04/16/2021 11:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import copy
import random
from unittest import mock

from django.apps import apps
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status

from axis.annotation.models import Annotation
from axis.annotation.tests.factories import type_factory as annotation_type_factory
from axis.company.models import SponsorPreferences
from axis.company.tests.factories import (
    builder_organization_factory,
    provider_organization_factory,
    rater_organization_factory,
    developer_organization_factory,
    communityowner_organization_factory,
    architect_organization_factory,
)
from axis.core.tests.factories import (
    provider_user_factory,
    builder_user_factory,
    rater_user_factory,
    contact_card_factory,
    contact_card_email_factory,
    contact_card_phone_factory,
    SET_NULL,
)
from axis.core.tests.factories import rater_admin_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration, BuilderAgreement
from axis.customer_hirl.tests.factories import (
    verifier_agreement_factory,
    coi_document_factory,
    builder_agreement_factory,
    hirl_project_factory,
    hirl_project_registration_factory,
    hirl_green_energy_badge_factory,
)
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import city_factory
from axis.home.models import EEPProgramHomeStatus, Home
from axis.invoicing.models import Invoice, InvoiceItemGroup, InvoiceItem
from axis.invoicing.tests.factories import invoice_factory
from axis.relationship.models import Relationship
from axis.subdivision.models import Subdivision
from axis.subdivision.tests.factories import subdivision_factory
from axis.user_management.models import Accreditation
from axis.user_management.tests.factories import accreditation_factory

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestHIRLProjectRegistrationViewSet(ApiV3Tests):
    def test_list(self):
        list_url = reverse_lazy("api_v3:hirl_project_registrations-list")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
        )

        kwargs = dict(url=list_url, user=hirl_user)

        data = self.list(**kwargs)
        self.assertEqual(len(data), HIRLProjectRegistration.objects.count())
        self.assertEqual(data[0]["id"], sf_registration.id)
        self.assertEqual(data[0]["projects_count"], 0)

    @mock.patch(
        "axis.customer_hirl.messages." "HIRLProjectBuilderIsNotWaterSensePartnerMessage.send"
    )
    @mock.patch(
        "axis.customer_hirl.messages." "SingleFamilyProjectCreatedHIRLNotificationMessage.send"
    )
    def test_create_single_family_project_as_hirl_user(
        self, sf_created_ngbs_message, builder_is_not_water_sense_partner_message
    ):
        list_url = reverse_lazy("api_v3:hirl_project_registrations-create-single-family")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        registration_user = rater_admin_factory(
            first_name="Rater User", company__name="Rater Company"
        )
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=registration_user.company
        )
        registration_user.company.update_permissions()

        verifier_agreement_factory(
            verifier=registration_user,
            owner=hirl_company,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        coi_document_factory(company=registration_user.company)
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020", slug="ngbs-sf-new-construction-2020-new"
        )
        accreditation_factory(trainee=registration_user, name=Accreditation.NGBS_2020_NAME)
        city = city_factory(name="Providence", county__name="Maricopa", county__state="RI")
        geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St, Providence, RI, 34342",
        )
        geocode_response = geocode.responses.first()

        accessory_geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="Unit B",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St Unit B, Providence, RI, 34342",
        )
        accessory_geocode_response = geocode.responses.first()

        adu_geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="ADU",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St ADU, Providence, RI, 34342",
        )
        adu_geocode_response = geocode.responses.first()

        builder_organization = builder_organization_factory()

        builder_agreement_factory(
            owner=hirl_company,
            company=builder_organization,
            state=BuilderAgreement.COUNTERSIGNED,
        )

        hirl_green_energy_badge = hirl_green_energy_badge_factory()

        builder_organization_contact = contact_card_factory(company=builder_organization)
        contact_card_email_factory(contact_card=builder_organization_contact)
        contact_card_phone_factory(contact_card=builder_organization_contact)

        minimum_required_data = {
            "eep_program": eep_program.pk,
            "builder_organization": builder_organization.pk,
            "builder_organization_contact": builder_organization_contact.pk,
            "projects": [
                {
                    "home_address_geocode": geocode.pk,
                    "home_address_geocode_response": geocode_response.pk,
                    "is_accessory_structure": False,
                    "hud_disaster_case_number": 5,
                    "green_energy_badges": [
                        hirl_green_energy_badge.pk,
                    ],
                    "is_require_water_sense_certification": True,
                    "is_require_rough_inspection": False,
                },
                {
                    "home_address_geocode": accessory_geocode.pk,
                    "home_address_geocode_response": accessory_geocode_response.pk,
                    "is_accessory_structure": True,
                    "accessory_structure_description": "Description text here",
                    "hud_disaster_case_number": "5",
                    "green_energy_badges": [],
                    "is_require_water_sense_certification": False,
                    "is_require_rough_inspection": False,
                },
                {
                    "home_address_geocode": adu_geocode.pk,
                    "home_address_geocode_response": adu_geocode_response.pk,
                    "is_accessory_dwelling_unit": True,
                    "accessory_dwelling_unit_description": "ADU description",
                    "hud_disaster_case_number": "5",
                    "green_energy_badges": [],
                    "is_require_water_sense_certification": False,
                    "is_require_rough_inspection": False,
                },
            ],
        }

        with self.subTest(
            "Test is_accessory_structure=True and accessory_structure_description = None",
        ):
            invalid_data = copy.deepcopy(minimum_required_data)
            invalid_data["projects"][1]["accessory_structure_description"] = None
            self.create(
                url=list_url,
                user=registration_user,
                data=invalid_data,
                expected_status=status.HTTP_400_BAD_REQUEST,
            )

        with self.subTest(
            "Test is_accessory_dwelling_unit=True and accessory_dwelling_unit_description = None",
        ):
            invalid_data = copy.deepcopy(minimum_required_data)
            invalid_data["projects"][2]["accessory_dwelling_unit_description"] = None
            self.create(
                url=list_url,
                user=registration_user,
                data=invalid_data,
                expected_status=status.HTTP_400_BAD_REQUEST,
            )

        with self.subTest(
            "Test is_accessory_structure=True and is_accessory_dwelling_unit=True",
        ):
            invalid_data = copy.deepcopy(minimum_required_data)
            invalid_data["projects"][1]["is_accessory_dwelling_unit"] = True
            self.create(
                url=list_url,
                user=registration_user,
                data=invalid_data,
                expected_status=status.HTTP_400_BAD_REQUEST,
            )

        self.create(url=list_url, user=registration_user, data=minimum_required_data)
        project, as_project, adu_project = list(HIRLProject.objects.order_by("id"))

        # we created three projects
        self.assertEqual(sf_created_ngbs_message.call_count, 6)

        self.assertEqual(builder_is_not_water_sense_partner_message.call_count, 1)

        self.assertEqual(project.registration.eep_program.pk, eep_program.pk)
        self.assertEqual(project.registration.builder_organization.pk, builder_organization.pk)

        self.assertEqual(
            project.registration.builder_organization_contact.id, builder_organization_contact.id
        )

        self.assertEqual(project.home_address_geocode.pk, geocode.pk)
        self.assertEqual(project.home_address_geocode_response.pk, geocode_response.pk)
        self.assertEqual(project.is_accessory_structure, False)
        self.assertEqual(as_project.is_accessory_dwelling_unit, False)
        self.assertEqual(project.hud_disaster_case_number, "5")
        self.assertEqual(project.is_require_water_sense_certification, True)
        self.assertEqual(project.is_require_rough_inspection, False)
        self.assertEqual(project.green_energy_badges.count(), 1)
        self.assertEqual(project.green_energy_badges.all().first(), hirl_green_energy_badge)

        # AS Project
        self.assertEqual(as_project.home_address_geocode.pk, accessory_geocode.pk)
        self.assertEqual(as_project.home_address_geocode_response.pk, accessory_geocode_response.pk)
        self.assertEqual(as_project.is_accessory_structure, True)
        self.assertEqual(as_project.is_accessory_dwelling_unit, False)
        self.assertEqual(as_project.hud_disaster_case_number, "5")
        self.assertEqual(as_project.is_require_water_sense_certification, False)
        self.assertEqual(as_project.is_require_rough_inspection, False)
        self.assertEqual(as_project.green_energy_badges.count(), 0)

        # ADU Project
        self.assertEqual(adu_project.home_address_geocode.pk, adu_geocode.pk)
        self.assertEqual(adu_project.home_address_geocode_response.pk, adu_geocode_response.pk)
        self.assertEqual(adu_project.is_accessory_structure, False)
        self.assertEqual(adu_project.is_accessory_dwelling_unit, True)
        self.assertEqual(adu_project.hud_disaster_case_number, "5")
        self.assertEqual(adu_project.is_require_water_sense_certification, False)
        self.assertEqual(adu_project.is_require_rough_inspection, False)
        self.assertEqual(adu_project.green_energy_badges.count(), 0)

    def test_create_single_family_is_build_to_rent_project_as_hirl_user(self):
        list_url = reverse_lazy("api_v3:hirl_project_registrations-create-single-family")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        registration_user = rater_admin_factory(
            first_name="Rater User", company__name="Rater Company"
        )
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=registration_user.company
        )
        registration_user.company.update_permissions()

        verifier_agreement_factory(
            verifier=registration_user,
            owner=hirl_company,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        coi_document_factory(company=registration_user.company)
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020", slug="ngbs-sf-new-construction-2020-new"
        )
        accreditation_factory(trainee=registration_user, name=Accreditation.NGBS_2020_NAME)
        city = city_factory(name="Providence", county__name="Maricopa", county__state="RI")
        geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St, Providence, RI, 34342",
        )
        geocode_response = geocode.responses.first()

        builder_organization = builder_organization_factory()
        developer_organization = builder_organization_factory()

        builder_agreement_factory(
            owner=hirl_company,
            company=builder_organization,
            state=BuilderAgreement.COUNTERSIGNED,
        )

        hirl_green_energy_badge = hirl_green_energy_badge_factory()

        builder_organization_contact = contact_card_factory(company=builder_organization)
        contact_card_email_factory(contact_card=builder_organization_contact)
        contact_card_phone_factory(contact_card=builder_organization_contact)

        developer_organization_contact = contact_card_factory(company=developer_organization)
        contact_card_email_factory(contact_card=developer_organization_contact)
        contact_card_phone_factory(contact_card=developer_organization_contact)

        minimum_required_data = {
            "eep_program": eep_program.pk,
            "builder_organization": builder_organization.pk,
            "builder_organization_contact": builder_organization_contact.pk,
            "developer_organization": developer_organization.pk,
            "developer_organization_contact": developer_organization_contact.pk,
            "is_build_to_rent": True,
            "projects": [
                {
                    "home_address_geocode": geocode.pk,
                    "home_address_geocode_response": geocode_response.pk,
                    "is_accessory_structure": False,
                    "hud_disaster_case_number": 5,
                    "green_energy_badges": [
                        hirl_green_energy_badge.pk,
                    ],
                    "is_require_water_sense_certification": True,
                    "is_require_rough_inspection": False,
                }
            ],
        }

        with self.subTest(
            "Test is_build_to_rent=True and developer_organization = None",
        ):
            invalid_data = minimum_required_data.copy()
            invalid_data["developer_organization"] = None
            self.create(
                url=list_url,
                user=registration_user,
                data=invalid_data,
                expected_status=status.HTTP_400_BAD_REQUEST,
            )

        with self.subTest(
            "Test is_build_to_rent=True and developer_organization_contact = None",
        ):
            invalid_data = minimum_required_data.copy()
            invalid_data["developer_organization_contact"] = None
            self.create(
                url=list_url,
                user=registration_user,
                data=invalid_data,
                expected_status=status.HTTP_400_BAD_REQUEST,
            )

        self.create(url=list_url, user=registration_user, data=minimum_required_data)
        project = HIRLProject.objects.order_by("id").first()

        self.assertEqual(project.registration.developer_organization.pk, developer_organization.pk)
        self.assertEqual(
            project.registration.developer_organization_contact.pk,
            developer_organization_contact.pk,
        )
        self.assertEqual(
            project.registration.entity_responsible_for_payment,
            HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY,
        )
        self.assertEqual(
            project.registration.project_client,
            HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
        )
        self.assertTrue(project.registration.is_build_to_rent)

    @mock.patch(
        "axis.customer_hirl.messages." "HIRLProjectBuilderIsNotWaterSensePartnerMessage.send"
    )
    @mock.patch(
        "axis.customer_hirl.messages." "MultiFamilyProjectCreatedHIRLNotificationMessage.send"
    )
    @mock.patch("axis.customer_hirl.messages." "HIRLProjectRegistrationCreatedMessage.send")
    def test_create_multi_family_project_as_hirl_user(
        self,
        mf_registration_created_message,
        mf_created_ngbs_message,
        builder_is_not_water_sense_partner_message,
    ):
        list_url = reverse_lazy("api_v3:hirl_project_registrations-create-multi-family")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        registration_user = rater_admin_factory(
            first_name="Rater User", company__name="Rater Company"
        )
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=registration_user.company
        )
        registration_user.company.update_permissions()

        verifier_agreement_factory(
            verifier=registration_user,
            owner=hirl_company,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        coi_document_factory(company=registration_user.company)
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020", slug="ngbs-sf-new-construction-2020-new"
        )
        accreditation_factory(trainee=registration_user, name=Accreditation.NGBS_2020_NAME)
        city = city_factory(name="Providence", county__name="Maricopa", county__state="RI")
        geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St, Providence, RI, 34342",
        )
        geocode_response = geocode.responses.first()

        commercial_space_geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="Unit C",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St Unit C, Providence, RI, 34342",
        )
        commercial_space_geocode_response = commercial_space_geocode.responses.first()

        accessory_geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="Unit B",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St Unit B, Providence, RI, 34342",
        )
        accessory_geocode_response = accessory_geocode.responses.first()

        builder_organization = builder_organization_factory()

        builder_agreement_factory(
            owner=hirl_company,
            company=builder_organization,
            state=BuilderAgreement.COUNTERSIGNED,
        )

        developer_organization = developer_organization_factory()
        community_owner_organization = communityowner_organization_factory()
        architect_organization = architect_organization_factory()

        hirl_green_energy_badge = hirl_green_energy_badge_factory()

        builder_organization_contact = contact_card_factory(company=builder_organization)
        contact_card_email_factory(contact_card=builder_organization_contact)
        contact_card_phone_factory(contact_card=builder_organization_contact)

        developer_organization_contact = contact_card_factory(company=developer_organization)
        contact_card_email_factory(contact_card=developer_organization_contact)
        contact_card_phone_factory(contact_card=developer_organization_contact)

        community_owner_organization_contact = contact_card_factory(
            company=community_owner_organization
        )
        contact_card_email_factory(contact_card=community_owner_organization_contact)
        contact_card_phone_factory(contact_card=community_owner_organization_contact)

        architect_organization_contact = contact_card_factory(company=architect_organization)
        contact_card_email_factory(contact_card=architect_organization_contact)
        contact_card_phone_factory(contact_card=architect_organization_contact)

        kwargs = dict(
            url=list_url,
            user=registration_user,
            data={
                "eep_program": eep_program.pk,
                "builder_organization": builder_organization.pk,
                "builder_organization_contact": builder_organization_contact.pk,
                "project_name": "project_name",
                "project_client": HIRLProjectRegistration.PROJECT_CLIENT_BUILDER,
                "multi_family_number_of_units": 10,
                "project_website_url": "http://mywebsite.com/",
                "estimated_completion_date": "2030-11-01",
                "party_named_on_certificate": HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY,
                "application_packet_completion": HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY,
                "project_contact_first_name": "project_contact_first_name",
                "project_contact_last_name": "project_contact_last_name",
                "project_contact_email": "project_contact_email@gmail.com",
                "project_contact_phone_number": "2123415678",
                "developer_organization": developer_organization.pk,
                "developer_organization_contact": developer_organization_contact.pk,
                "community_owner_organization": community_owner_organization.pk,
                "community_owner_organization_contact": community_owner_organization_contact.pk,
                "architect_organization": architect_organization.pk,
                "architect_organization_contact": architect_organization_contact.pk,
                "marketing_first_name": "marketing_first_name",
                "marketing_last_name": "marketing_last_name",
                "marketing_email": "marketing_email@gmail.com",
                "marketing_phone": "4803415678",
                "sales_website_url": "http://localhost:4200/hi/projects/add/multi-family",
                "sales_email": "sales_email@gmail.com",
                "sales_phone": "4803415678",
                "billing_first_name": "billing_first_name",
                "billing_last_name": "billing_last_name",
                "billing_email": "billing_email@gmail.com",
                "billing_phone": "4803415678",
                "entity_responsible_for_payment": HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY,
                "projects": [
                    {
                        "home_address_geocode": geocode.pk,
                        "home_address_geocode_response": geocode_response.pk,
                        "is_accessory_structure": False,
                        "accessory_structure_description": "",
                        "hud_disaster_case_number": "5",
                        "building_number": "123",
                        "story_count": 15,
                        "is_require_water_sense_certification": True,
                        "green_energy_badges": [
                            hirl_green_energy_badge.pk,
                        ],
                        "commercial_spaces": [
                            {
                                "home_address_geocode": commercial_space_geocode.pk,
                                "home_address_geocode_response": commercial_space_geocode_response.pk,
                                "is_include_commercial_space": True,
                                "commercial_space_type": HIRLProject.CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE,
                                "total_commercial_space": 5,
                                "building_number": "123",
                                "story_count": 1,
                                "green_energy_badges": [],
                            }
                        ],
                    },
                    {
                        "home_address_geocode": accessory_geocode.pk,
                        "home_address_geocode_response": accessory_geocode_response.pk,
                        "is_accessory_structure": True,
                        "accessory_structure_description": "Description text here",
                        "hud_disaster_case_number": 5,
                        "is_include_commercial_space": False,
                        "building_number": "123",
                        "story_count": 15,
                        "green_energy_badges": [],
                    },
                ],
            },
        )

        self.create(**kwargs)

        # we created two projects and should receive two notifications by Verifier
        self.assertEqual(mf_created_ngbs_message.call_count, 6)
        # Do not send registration if we have project
        self.assertEqual(mf_registration_created_message.call_count, 0)

        self.assertEqual(builder_is_not_water_sense_partner_message.call_count, 1)

        project, commercial_space, accessory_structure = list(HIRLProject.objects.order_by("id"))

        # check project data
        self.assertEqual(project.registration.eep_program.pk, eep_program.pk)

        self.assertEqual(project.registration.builder_organization.pk, builder_organization.pk)
        self.assertEqual(
            project.registration.builder_organization_contact.id, builder_organization_contact.id
        )

        self.assertEqual(project.registration.developer_organization.pk, developer_organization.pk)
        self.assertEqual(
            project.registration.developer_organization_contact.id,
            developer_organization_contact.id,
        )

        self.assertEqual(
            project.registration.community_owner_organization.pk, community_owner_organization.pk
        )
        self.assertEqual(
            project.registration.community_owner_organization_contact.id,
            community_owner_organization_contact.id,
        )

        self.assertEqual(project.registration.architect_organization.pk, architect_organization.pk)
        self.assertEqual(
            project.registration.architect_organization_contact.id,
            architect_organization_contact.id,
        )

        self.assertEqual(project.registration.marketing_first_name, "marketing_first_name")
        self.assertEqual(project.registration.marketing_last_name, "marketing_last_name")
        self.assertEqual(project.registration.marketing_email, "marketing_email@gmail.com")
        self.assertEqual(project.registration.marketing_phone, "4803415678")

        self.assertEqual(project.registration.sales_email, "sales_email@gmail.com")
        self.assertEqual(project.registration.sales_phone, "4803415678")
        self.assertEqual(
            project.registration.sales_website_url,
            "http://localhost:4200/hi/projects/add/multi-family",
        )

        self.assertEqual(project.registration.billing_first_name, "billing_first_name")
        self.assertEqual(project.registration.billing_last_name, "billing_last_name")
        self.assertEqual(project.registration.billing_email, "billing_email@gmail.com")
        self.assertEqual(project.registration.billing_phone, "4803415678")

        self.assertEqual(project.home_address_geocode.pk, geocode.pk)
        self.assertEqual(project.home_address_geocode_response.pk, geocode_response.pk)
        self.assertEqual(project.is_accessory_structure, False)
        self.assertEqual(project.hud_disaster_case_number, "5")
        self.assertEqual(project.green_energy_badges.count(), 1)
        self.assertEqual(project.green_energy_badges.all().first(), hirl_green_energy_badge)
        self.assertEqual(project.story_count, 15)

        # check commercial space data

        self.assertEqual(commercial_space.is_include_commercial_space, True)
        self.assertEqual(
            commercial_space.commercial_space_type, HIRLProject.CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE
        )
        self.assertEqual(commercial_space.total_commercial_space, 5)
        self.assertEqual(commercial_space.building_number, "123")
        self.assertEqual(commercial_space.story_count, 1)
        self.assertEqual(commercial_space.commercial_space_parent.pk, project.pk)

        # check accessory structure data

        self.assertTrue(accessory_structure.is_accessory_structure)
        self.assertEqual(
            accessory_structure.accessory_structure_description, "Description text here"
        )

        with self.subTest("Create new project without Buildings"):
            no_project_kwargs = dict(kwargs)
            no_project_kwargs["data"]["projects"] = []
            self.create(**no_project_kwargs)
            # Send message if we do not have any project
            mf_registration_created_message.assert_called_once()

    @mock.patch(
        "axis.customer_hirl.messages." "LandDevelopmentProjectCreatedHIRLNotificationMessage.send"
    )
    def test_create_land_development_project_as_hirl_user(self, ld_created_ngbs_message):
        list_url = reverse_lazy("api_v3:hirl_project_registrations-create-land-development")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        registration_user = rater_admin_factory(
            first_name="Rater User", company__name="Rater Company"
        )
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=registration_user.company
        )
        registration_user.company.update_permissions()

        verifier_agreement_factory(
            verifier=registration_user,
            owner=hirl_company,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        coi_document_factory(company=registration_user.company)
        eep_program = basic_eep_program_factory(
            name="NGBS Land Development 2020", slug="ngbs-land-development-2020-new"
        )
        accreditation_factory(trainee=registration_user, name=Accreditation.NGBS_2020_NAME)
        city = city_factory(name="Providence", county__name="Maricopa", county__state="RI")
        geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St, Providence, RI, 34342",
        )
        geocode_response = geocode.responses.first()

        letter_geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="Letter",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St Letter, Providence, RI, 34342",
        )
        letter_geocode_response = letter_geocode.responses.first()

        phase_geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="Phase",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St Phase, Providence, RI, 34342",
        )
        phase_geocode_response = phase_geocode.responses.first()

        developer_organization = developer_organization_factory()

        builder_agreement_factory(
            owner=hirl_company,
            company=developer_organization,
            state=BuilderAgreement.COUNTERSIGNED,
        )

        developer_organization_contact = contact_card_factory(company=developer_organization)
        contact_card_email_factory(contact_card=developer_organization_contact)
        contact_card_phone_factory(contact_card=developer_organization_contact)
        number_of_lots = 5

        base_data = {
            "eep_program": eep_program.pk,
            "developer_organization": developer_organization.pk,
            "developer_organization_contact": developer_organization_contact.pk,
            "ld_workflow": HIRLProjectRegistration.LD_WORKFLOW_LETTER_OF_APPROVAL_AND_FULL_CERTIFICATION,
            "project_website_url": "https://mywebsite.com/",
            "estimated_completion_date": "2030-11-01",
            "project_description": "test",
            "projects": [
                {
                    "home_address_geocode": geocode.pk,
                    "home_address_geocode_response": geocode_response.pk,
                    "number_of_lots": number_of_lots,
                    "land_development_project_type": HIRLProject.LD_PROJECT_TYPE_PHASE_PROJECT,
                    "are_all_homes_in_ld_seeking_certification": True,
                    "land_development_phase_number": 1,
                },
                {
                    "home_address_geocode": letter_geocode.pk,
                    "home_address_geocode_response": letter_geocode_response.pk,
                    "land_development_project_type": HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT,
                },
                {
                    "home_address_geocode": phase_geocode.pk,
                    "home_address_geocode_response": phase_geocode_response.pk,
                    "number_of_lots": number_of_lots,
                    "land_development_project_type": HIRLProject.LD_PROJECT_TYPE_PHASE_PROJECT,
                    "are_all_homes_in_ld_seeking_certification": True,
                    "land_development_phase_number": 2,
                },
            ],
        }

        self.create(url=list_url, user=registration_user, data=base_data)
        main_project = HIRLProject.objects.order_by("id").first()

        # we create 3 projects
        self.assertEqual(ld_created_ngbs_message.call_count, 6)

        # registration check
        self.assertEqual(main_project.registration.eep_program.pk, eep_program.pk)
        self.assertEqual(
            main_project.registration.developer_organization.pk, developer_organization.pk
        )
        self.assertEqual(main_project.registration.project_description, "test")
        self.assertEqual(main_project.registration.project_website_url, "https://mywebsite.com/")
        self.assertEqual(
            main_project.registration.estimated_completion_date.strftime("%Y-%m-%d"), "2030-11-01"
        )
        self.assertEqual(
            main_project.registration.ld_workflow,
            HIRLProjectRegistration.LD_WORKFLOW_LETTER_OF_APPROVAL_AND_FULL_CERTIFICATION,
        )
        self.assertEqual(
            main_project.registration.developer_organization_contact.id,
            developer_organization_contact.id,
        )

        # main project check
        self.assertEqual(main_project.home_address_geocode.pk, geocode.pk)
        self.assertEqual(main_project.home_address_geocode_response.pk, geocode_response.pk)

        self.assertEqual(
            main_project.land_development_project_type, HIRLProject.LD_PROJECT_TYPE_PHASE_PROJECT
        )
        self.assertEqual(main_project.number_of_lots, number_of_lots)
        self.assertFalse(main_project.is_require_rough_inspection)

    @mock.patch(
        "axis.customer_hirl.messages.project.IsAppealsHIRLProjectCreatedNotificationMessage.send"
    )
    def test_create_is_appeals_project_registration_additional_notification(
        self, is_appeals_project_created_message_send
    ):
        """
        Send additional IsAppealsHIRLProjectCreatedNotificationMessage for all projects with is_appeals_project flag
        :param is_appeals_project_created_message_send:
        Mock for IsAppealsHIRLProjectCreatedNotificationMessage.send
        """

        list_url = reverse_lazy("api_v3:hirl_project_registrations-create-single-family")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        registration_user = rater_admin_factory(
            first_name="Rater User", company__name="Rater Company"
        )
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=registration_user.company
        )
        registration_user.company.update_permissions()

        verifier_agreement_factory(
            verifier=registration_user,
            owner=hirl_company,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        coi_document_factory(company=registration_user.company)
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020", slug="ngbs-sf-new-construction-2020-new"
        )
        accreditation_factory(trainee=registration_user, name=Accreditation.NGBS_2020_NAME)
        city = city_factory(name="Providence", county__name="Maricopa", county__state="RI")
        geocode = Geocode.objects.create(
            raw_street_line1="479 Washington St",
            raw_street_line2="",
            raw_zipcode="34342",
            raw_city=city,
            raw_address="479 Washington St, Providence, RI, 34342",
        )
        geocode_response = geocode.responses.first()

        builder_organization = builder_organization_factory()
        developer_organization = builder_organization_factory()

        builder_agreement_factory(
            owner=hirl_company,
            company=builder_organization,
            state=BuilderAgreement.COUNTERSIGNED,
        )

        hirl_green_energy_badge = hirl_green_energy_badge_factory()

        builder_organization_contact = contact_card_factory(company=builder_organization)
        contact_card_email_factory(contact_card=builder_organization_contact)
        contact_card_phone_factory(contact_card=builder_organization_contact)

        developer_organization_contact = contact_card_factory(company=developer_organization)
        contact_card_email_factory(contact_card=developer_organization_contact)
        contact_card_phone_factory(contact_card=developer_organization_contact)

        minimum_required_data = {
            "eep_program": eep_program.pk,
            "builder_organization": builder_organization.pk,
            "builder_organization_contact": builder_organization_contact.pk,
            "developer_organization": developer_organization.pk,
            "developer_organization_contact": developer_organization_contact.pk,
            "is_build_to_rent": True,
            "projects": [
                {
                    "home_address_geocode": geocode.pk,
                    "home_address_geocode_response": geocode_response.pk,
                    "is_accessory_structure": False,
                    "hud_disaster_case_number": 5,
                    "green_energy_badges": [
                        hirl_green_energy_badge.pk,
                    ],
                    "is_require_water_sense_certification": True,
                    "is_require_rough_inspection": False,
                    "is_appeals_project": True,
                }
            ],
        }

        self.create(url=list_url, user=registration_user, data=minimum_required_data)

        self.assertEqual(is_appeals_project_created_message_send.call_count, 1)

    @mock.patch(
        "axis.invoicing.messages."
        "invoice_item_group."
        "HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage.send"
    )
    def test_approve_single_family_project_as_hirl_user(
        self, hirl_responsible_entity_for_payment_invoice_item_group_created_message
    ):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_user = builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program__slug="ngbs-sf-certified-2020-new",
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None, home_status=SET_NULL
        )

        # set home_status for None to approve home and create new
        sf_project.home_status = None
        sf_project.save()

        sf_project.refresh_from_db()
        self.assertIsNone(sf_project.most_recent_notice_sent)

        approve_url = reverse_lazy(
            "api_v3:hirl_project_registrations-approve",
            kwargs={
                "pk": sf_project.registration.pk,
            },
        )

        self.client.force_authenticate(user=hirl_user)
        response = self.client.post(approve_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        hirl_responsible_entity_for_payment_invoice_item_group_created_message.assert_called_once()

        sf_project.refresh_from_db()

        self.assertEqual(
            sf_project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE
        )

        self.assertIsNotNone(sf_project.most_recent_notice_sent)

    @mock.patch("axis.invoicing.messages.invoice.InvoiceCreatedNotificationMessage.send")
    def test_approve_single_family_project_as_hirl_user_with_rough_bypass(
        self, invoice_created_message_send
    ):
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020",
            slug="ngbs-sf-new-construction-2020-new",
            customer_hirl_certification_fee=300,
        )

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        # set CA for ERFP company to be able to generate Invoice
        builder_agreement_factory(
            owner=hirl_company, company=builder_organization, state=BuilderAgreement.COUNTERSIGNED
        )

        rater_organization = rater_organization_factory()
        rater_user_factory(is_company_admin=True, company=rater_organization)

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program=eep_program,
            builder_organization=builder_organization,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            is_require_rough_inspection=False,
            is_appeals_project=True,
        )
        hirl_green_energy_badge = hirl_green_energy_badge_factory(cost=100)
        hirl_green_energy_badge2 = hirl_green_energy_badge_factory(cost=100)

        sf_project.green_energy_badges.add(hirl_green_energy_badge)
        sf_project.green_energy_badges.add(hirl_green_energy_badge2)

        self.assertIsNone(sf_project.most_recent_notice_sent)

        approve_url = reverse_lazy(
            "api_v3:hirl_project_registrations-approve",
            kwargs={
                "pk": sf_project.registration.pk,
            },
        )

        self.client.force_authenticate(user=hirl_user)
        response = self.client.post(approve_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        sf_project.refresh_from_db()

        self.assertEqual(
            sf_project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_FINAL_QA_STATE
        )

        self.assertIsNotNone(sf_project.most_recent_notice_sent)
        # send message to NGBS, verifier and ERFP * 2(because we send separate notification for Appeals Fee Invoice)
        self.assertEqual(invoice_created_message_send.call_count, 6)
        # invoice exists
        invoices = Invoice.objects.all().order_by("id")

        # One general invoice and one invoice for Appeals Fee
        self.assertEqual(invoices.count(), 2)

        common_invoice = invoices[0]
        appeals_invoice = invoices[1]

        # first invoice contains all Fee Groups from All projects in registration
        self.assertEqual(
            common_invoice.note,
            "Automatically generated after approve, because project rough bypass have been set",
        )
        self.assertEqual(
            list(common_invoice.invoiceitemgroup_set.all()),
            list(
                sf_project.home_status.invoiceitemgroup_set.exclude(
                    category=InvoiceItemGroup.APPEALS_FEE_CATEGORY
                )
            ),
        )

        # second invoice contains only Appeals Fee Group
        self.assertEqual(
            appeals_invoice.note,
            "Automatically generated after approve for Appeals Fees, "
            "because project rough bypass have been set",
        )
        self.assertEqual(
            list(appeals_invoice.invoiceitemgroup_set.all()),
            list(
                sf_project.home_status.invoiceitemgroup_set.filter(
                    category=InvoiceItemGroup.APPEALS_FEE_CATEGORY
                )
            ),
        )

    @mock.patch(
        "axis.customer_hirl.messages.project.HIRLProjectInvoiceCantGeneratedWithoutClientAgreement.send"
    )
    def test_approve_single_family_project_as_hirl_user_with_rough_bypass_but_without_client_agreement(
        self, invoice_not_created_message_send
    ):
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020",
            slug="ngbs-sf-new-construction-2020-new",
            customer_hirl_certification_fee=300,
        )

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        rater_user_factory(is_company_admin=True, company=rater_organization)

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program=eep_program,
            builder_organization=builder_organization,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            is_require_rough_inspection=False,
        )
        hirl_green_energy_badge = hirl_green_energy_badge_factory(cost=100)
        hirl_green_energy_badge2 = hirl_green_energy_badge_factory(cost=100)

        sf_project.green_energy_badges.add(hirl_green_energy_badge)
        sf_project.green_energy_badges.add(hirl_green_energy_badge2)

        self.assertIsNone(sf_project.most_recent_notice_sent)

        approve_url = reverse_lazy(
            "api_v3:hirl_project_registrations-approve",
            kwargs={
                "pk": sf_project.registration.pk,
            },
        )

        self.client.force_authenticate(user=hirl_user)
        response = self.client.post(approve_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        sf_project.refresh_from_db()

        self.assertEqual(
            sf_project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_FINAL_QA_STATE
        )

        self.assertIsNotNone(sf_project.most_recent_notice_sent)
        # send message to NGBS, verifier, Client and ERFP
        self.assertEqual(invoice_not_created_message_send.call_count, 4)
        # we can't generate invoice without countersigned CA
        invoice = Invoice.objects.first()
        self.assertIsNone(invoice)

    @mock.patch(
        "axis.invoicing.messages."
        "invoice_item_group."
        "HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage.send"
    )
    def test_approve_multi_family_project_as_hirl_user(
        self, hirl_responsible_entity_for_payment_invoice_item_group_created_message
    ):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )

        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_user = builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        developer_organization = developer_organization_factory()
        communityowner_organization = communityowner_organization_factory()
        architect_organization = architect_organization_factory()

        mf_registration = hirl_project_registration_factory(
            registration_user=company_admin_rater_user,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
            community_owner_organization=communityowner_organization,
            architect_organization=architect_organization,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            story_count=0,
            number_of_units=0,
            home_status=SET_NULL,
        )

        approve_url = reverse_lazy(
            "api_v3:hirl_project_registrations-approve",
            kwargs={
                "pk": mf_registration.pk,
            },
        )

        self.client.force_authenticate(user=hirl_user)
        response = self.client.post(approve_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        hirl_responsible_entity_for_payment_invoice_item_group_created_message.assert_called_once()

        mf_project.refresh_from_db()

        self.assertIsNotNone(mf_project.home_status)
        self.assertEqual(Subdivision.objects.count(), 1)

        subdivision = Subdivision.objects.first()

        # expect relationships between subdivision and provided organizations

        self.assertEqual(subdivision.relationships.filter(company=hirl_company).count(), 1)

        self.assertEqual(subdivision.relationships.filter(company=rater_organization).count(), 1)

        self.assertEqual(subdivision.relationships.filter(company=builder_organization).count(), 1)

        self.assertEqual(
            subdivision.relationships.filter(company=architect_organization).count(), 1
        )

        self.assertEqual(
            subdivision.relationships.filter(company=developer_organization).count(), 1
        )

        self.assertEqual(
            subdivision.relationships.filter(company=communityowner_organization).count(), 1
        )

        # expect relationships between home and provided organizations

        self.assertEqual(subdivision.relationships.filter(company=hirl_company).count(), 1)

        self.assertEqual(
            mf_project.home_status.home.relationships.filter(company=rater_organization).count(), 1
        )

        self.assertEqual(
            mf_project.home_status.home.relationships.filter(company=builder_organization).count(),
            1,
        )

        self.assertEqual(
            subdivision.relationships.filter(company=architect_organization).count(), 1
        )

        self.assertEqual(
            subdivision.relationships.filter(company=developer_organization).count(), 1
        )

        self.assertEqual(
            subdivision.relationships.filter(company=communityowner_organization).count(), 1
        )

    def test_approve_multi_family_project_with_mf_volume_discount(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )

        builder_organization = builder_organization_factory(name="PUG Builder")

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

        developer_organization = developer_organization_factory()
        communityowner_organization = communityowner_organization_factory()
        architect_organization = architect_organization_factory()

        customer_hirl_certification_fee = 300

        mf_registration = hirl_project_registration_factory(
            registration_user=company_admin_rater_user,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
            community_owner_organization=communityowner_organization,
            architect_organization=architect_organization,
            eep_program__customer_hirl_certification_fee=customer_hirl_certification_fee,
        )

        for i in range(0, 10):
            mf_project = hirl_project_factory(
                registration=mf_registration,
                street_line1=f"{479+i} Washington St",
                home_address_geocode_response=None,
                story_count=random.randint(1, 3),
                number_of_units=random.randint(1, 3),
                home_status=SET_NULL,
            )

        as_project = hirl_project_factory(
            registration=mf_registration,
            street_line1=f"{479 + 11} Washington St",
            home_address_geocode_response=None,
            story_count=1,
            number_of_units=1,
            home_status=SET_NULL,
            is_accessory_structure=True,
        )
        cs_project = hirl_project_factory(
            registration=mf_registration,
            street_line1=f"{479 + 12} Washington St",
            home_address_geocode_response=None,
            story_count=1,
            number_of_units=1,
            home_status=SET_NULL,
            is_include_commercial_space=True,
            commercial_space_type=HIRLProject.CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE,
            total_commercial_space=200,
        )

        mf_project_with_more_story_count_than_needed = hirl_project_factory(
            registration=mf_registration,
            street_line1=f"{479 + 13} Washington St",
            home_address_geocode_response=None,
            story_count=6,
            number_of_units=1,
            home_status=SET_NULL,
        )

        approve_url = reverse_lazy(
            "api_v3:hirl_project_registrations-approve",
            kwargs={
                "pk": mf_registration.pk,
            },
        )

        self.client.force_authenticate(user=hirl_user)
        response = self.client.post(approve_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        discount_items = InvoiceItem.objects.filter(
            name="MF Volume Pricing Discount(10-19 buildings)"
        )

        self.assertEqual(discount_items.count(), 10)

    @mock.patch("axis.customer_hirl.messages." "ProjectRegistrationERFPNotificationMessage.send")
    def test_change_entity_responsible_for_payment_user(
        self, project_registration_erfp_notification_message
    ):
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        mf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            entity_responsible_for_payment=HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY,
        )

        mf_registration.entity_responsible_for_payment = (
            HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY
        )
        mf_registration.save()

        project_registration_erfp_notification_message.assert_called_once()

    def test_delete_approved_sf_registration_without_subdivsion(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

        self.test_approve_single_family_project_as_hirl_user()
        approved_registration = HIRLProjectRegistration.objects.get()

        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 1)
        self.assertEqual(HIRLProject.objects.count(), 1)

        delete_url = reverse_lazy(
            "api_v3:hirl_project_registrations-detail",
            kwargs={
                "pk": approved_registration.pk,
            },
        )
        self.delete(url=delete_url, user=hirl_user)

        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

    def test_delete_approved_sf_registration_with_subdivsion(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

        self.test_approve_single_family_project_as_hirl_user()
        approved_registration = HIRLProjectRegistration.objects.get()
        approved_registration.subdivision = subdivision_factory(
            builder_org=approved_registration.builder_organization
        )
        approved_registration.save()

        self.assertEqual(Subdivision.objects.count(), 1)
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 1)
        self.assertEqual(HIRLProject.objects.count(), 1)

        delete_url = reverse_lazy(
            "api_v3:hirl_project_registrations-detail",
            kwargs={
                "pk": approved_registration.pk,
            },
        )
        self.delete(url=delete_url, user=hirl_user)

        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

    def test_delete_approved_mf_registration_with_subdivsion(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

        self.test_approve_multi_family_project_as_hirl_user()
        approved_registration = HIRLProjectRegistration.objects.get()

        self.assertEqual(Subdivision.objects.count(), 1)
        self.assertEqual(Home.objects.count(), 1)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 1)
        self.assertEqual(HIRLProject.objects.count(), 1)

        delete_url = reverse_lazy(
            "api_v3:hirl_project_registrations-detail",
            kwargs={
                "pk": approved_registration.pk,
            },
        )
        self.delete(url=delete_url, user=hirl_user)

        self.assertEqual(Subdivision.objects.count(), 0)
        self.assertEqual(Home.objects.count(), 0)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 0)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

    def test_delete_not_approved_registration(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
        )
        hirl_project_factory(
            registration=sf_registration,
        )

        self.assertEqual(HIRLProjectRegistration.objects.count(), 1)
        self.assertEqual(HIRLProject.objects.count(), 1)

        delete_url = reverse_lazy(
            "api_v3:hirl_project_registrations-detail",
            kwargs={
                "pk": sf_registration.pk,
            },
        )
        self.delete(url=delete_url, user=hirl_user)
        self.assertEqual(HIRLProjectRegistration.objects.count(), 0)
        self.assertEqual(HIRLProject.objects.count(), 0)

    def test_abandon_state(self):
        annotation_type_factory(slug="note")

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        builder_user = builder_user_factory()

        customer_hirl_certification_fee = 300
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020",
            slug="ngbs-sf-new-construction-2020-new",
            owner=hirl_company,
            customer_hirl_certification_fee=customer_hirl_certification_fee,
        )

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_user.company,
            state=HIRLProjectRegistration.ACTIVE_STATE,
            eep_program=eep_program,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_status=SET_NULL,
        )

        sf_project2 = hirl_project_factory(
            registration=sf_registration,
            home_status=SET_NULL,
        )

        sf_project.create_home_status()

        sf_project2.create_home_status()

        self.assertEqual(Annotation.objects.all().count(), 0)
        # project 1
        self.assertEqual(HIRLProjectRegistration.objects.count(), 1)
        self.assertEqual(HIRLProject.objects.count(), 2)
        self.assertEqual(sf_project.billing_state, HIRLProject.NEW_BILLING_STATE)
        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        invoiceitemgroup = sf_project.home_status.invoiceitemgroup_set.first()
        self.assertEqual(invoiceitemgroup.total, customer_hirl_certification_fee)

        # project 2
        self.assertEqual(sf_project2.home_status.invoiceitemgroup_set.count(), 1)
        self.assertEqual(sf_project2.billing_state, HIRLProject.NEW_BILLING_STATE)

        invoiceitemgroup = sf_project2.home_status.invoiceitemgroup_set.first()
        self.assertEqual(invoiceitemgroup.total, customer_hirl_certification_fee)
        invoice_project2 = invoice_factory(
            issuer=hirl_company,
            customer=builder_user.company,
            invoice_item_groups=[
                invoiceitemgroup,
            ],
        )
        sf_project2.refresh_from_db()
        self.assertEqual(invoice_project2.total, customer_hirl_certification_fee)
        self.assertEqual(sf_project2.billing_state, HIRLProject.NOTICE_SENT_BILLING_STATE)

        abandon_url = reverse_lazy(
            "api_v3:hirl_project_registrations-abandon",
            kwargs={
                "pk": sf_registration.pk,
            },
        )

        with self.subTest("Only NGBS and can abandon registration"):
            self.create(
                url=abandon_url, user=builder_user, expected_status=status.HTTP_403_FORBIDDEN
            )

        with self.subTest("Abandon only when in [PENDING_STATE, ACTIVE_STATE]"):
            for state in [
                HIRLProjectRegistration.NEW_STATE,
                HIRLProjectRegistration.REJECTED_STATE,
                HIRLProjectRegistration.ABANDONED_STATE,
            ]:
                sf_registration.state = state
                sf_registration.save()

                self.create(
                    url=abandon_url, user=hirl_user, expected_status=status.HTTP_403_FORBIDDEN
                )

            # rollback to previous state
            sf_registration.state = HIRLProjectRegistration.ACTIVE_STATE
            sf_registration.save()

        with self.subTest(
            "Abandon only when Home Status for projects in correct state for transition"
        ):
            project = sf_registration.projects.first()
            self.assertEqual(
                project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE
            )
            project.home_status.state = EEPProgramHomeStatus.ABANDONED_STATE
            project.home_status.save()

            self.create(
                url=abandon_url,
                user=hirl_user,
                data={"reason": "text", "billing_state": HIRLProject.NOT_PURSUING_BILLING_STATE},
                expected_status=status.HTTP_400_BAD_REQUEST,
            )

            # rollback to previous state
            project.home_status.state = EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE
            project.home_status.save()

        self.create(
            url=abandon_url,
            user=hirl_user,
            data={"reason": "text", "billing_state": HIRLProject.NOT_PURSUING_BILLING_STATE},
            expected_status=status.HTTP_200_OK,
        )

        sf_registration.refresh_from_db()
        sf_project.refresh_from_db()
        sf_project2.refresh_from_db()

        self.assertEqual(sf_registration.state_change_reason, "text")
        # check that annotation for home_status created for both projects
        self.assertEqual(sf_project.home_status.annotations.all().count(), 1)
        self.assertEqual(sf_project2.home_status.annotations.all().count(), 1)

        self.assertEqual(sf_project.home_status.state, EEPProgramHomeStatus.ABANDONED_STATE)
        # expect manual_billing_state state change and fee adjustment based on this state
        self.assertEqual(sf_project.manual_billing_state, HIRLProject.NOT_PURSUING_BILLING_STATE)
        invoiceitemgroup = sf_project.home_status.invoiceitemgroup_set.first()
        self.assertEqual(invoiceitemgroup.total, 0)

        # project billing_state with invoice not changed
        self.assertEqual(sf_project2.manual_billing_state, HIRLProject.AUTOMATICALLY_BILLING_STATE)
        self.assertEqual(sf_project2.billing_state, HIRLProject.NOTICE_SENT_BILLING_STATE)
        invoiceitemgroup = sf_project2.home_status.invoiceitemgroup_set.first()
        self.assertEqual(invoiceitemgroup.total, customer_hirl_certification_fee)

    def test_registration_activity_metrics_by_month(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(company=hirl_company)

        non_customer_hirl_user = provider_user_factory()

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program__owner=hirl_company,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None, home_status=SET_NULL
        )
        today = timezone.now().today()

        sf_project.create_home_status()
        sf_project.refresh_from_db()
        sf_project.home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        sf_project.home_status.certification_date = today
        sf_project.home_status.save()

        url = reverse_lazy(
            "api_v3:hirl_project_registrations-registration-activity-metrics-by-month"
        )
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(url, format="json")

        first_day_of_month = today.replace(day=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["month"], first_day_of_month.strftime("%Y-%m-%d"))
        self.assertEqual(response.data[0]["registrations_count"], 1)

        with self.subTest("Restrict access for non HIRL users"):
            self.client.force_authenticate(user=non_customer_hirl_user)
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_activity_metrics_units_by_month(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(company=hirl_company)

        non_customer_hirl_user = provider_user_factory()

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program__owner=hirl_company,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            number_of_units=1,
        )
        today = timezone.now().today()

        sf_project.create_home_status()
        sf_project.refresh_from_db()
        sf_project.home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        sf_project.home_status.certification_date = today
        sf_project.home_status.save()

        url = reverse_lazy(
            "api_v3:hirl_project_registrations-registration-activity-metrics-units-by-month"
        )
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(url, format="json")

        first_day_of_month = today.replace(day=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["month"], first_day_of_month.strftime("%Y-%m-%d"))
        self.assertEqual(response.data[0]["units_count"], 2)

        with self.subTest("Restrict access for non HIRL users"):
            self.client.force_authenticate(user=non_customer_hirl_user)
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch(
        "axis.customer_hirl.messages." "SingleFamilyProjectCreatedHIRLNotificationMessage.send"
    )
    def test_create_sf_project_for_existing_registration_as_hirl_user(
        self, sf_created_ngbs_message
    ):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        sf_registration = hirl_project_registration_factory(
            registration_user=hirl_user,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_address_geocode_response=None,
            story_count=0,
            number_of_units=0,
            home_status=SET_NULL,
        )

        sf_registration.active()
        sf_registration.save()

        sf_project.refresh_from_db()
        sf_project.create_home_status()
        sf_project.refresh_from_db()

        city = city_factory(name="Providence", county__name="Maricopa", county__state="RI")
        geocode = Geocode.objects.create(
            raw_street_line1="999 Washington St",
            raw_street_line2="",
            raw_zipcode="34345",
            raw_city=city,
            raw_address="999 Washington St, Providence, RI, 34345",
        )
        geocode_response = geocode.responses.first()

        hirl_green_energy_badge = hirl_green_energy_badge_factory()

        list_url = reverse_lazy(
            "api_v3:hirl_project_registration-hirl_projects-create-single-family",
            args=(str(sf_registration.id),),
        )

        kwargs = dict(
            url=list_url,
            user=hirl_user,
            data={
                "projects": [
                    {
                        "home_address_geocode": geocode.pk,
                        "home_address_geocode_response": geocode_response.pk,
                        "is_accessory_structure": False,
                        "accessory_structure_description": "",
                        "hud_disaster_case_number": "5",
                        "is_require_water_sense_certification": True,
                        "green_energy_badges": [
                            hirl_green_energy_badge.pk,
                        ],
                    }
                ],
            },
        )

        self.create(**kwargs)

        # we created two projects and should receive two notifications by Verifier
        self.assertEqual(sf_created_ngbs_message.call_count, 1)

        old_project, new_project = list(HIRLProject.objects.order_by("id"))

        self.assertEqual(new_project.hud_disaster_case_number, "5")
        self.assertEqual(
            list(new_project.green_energy_badges.all()),
            [
                hirl_green_energy_badge,
            ],
        )
        self.assertIsNotNone(new_project.home_status)
