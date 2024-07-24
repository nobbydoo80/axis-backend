# -*- coding: utf-8 -*-
"""test_project_registration.py: """

__author__ = "Artem Hruzd"
__date__ = "08/18/2022 16:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from axis.company.tests.factories import (
    provider_organization_factory,
    builder_organization_factory,
    developer_organization_factory,
)
from axis.core.tests.factories import SET_NULL
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import hirl_project_registration_factory
from axis.eep_program.tests.factories import basic_eep_program_factory


customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectRegistrationTests(AxisTestCase):
    def test_get_project_client_company(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        builder_organization = builder_organization_factory()
        developer_organization = developer_organization_factory()

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
            architect_organization=SET_NULL,
        )

        with self.subTest("Single Family cases"):
            self.assertEqual(sf_registration.get_project_client_company(), builder_organization)

            sf_registration.is_build_to_rent = True
            sf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER
            sf_registration.save()
            self.assertEqual(sf_registration.get_project_client_company(), developer_organization)

        with self.subTest("Multi Family cases"):
            sf_registration.project_type = HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            sf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_BUILDER
            sf_registration.save()

            self.assertEqual(sf_registration.get_project_client_company(), builder_organization)

            sf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER
            sf_registration.save()
            self.assertEqual(sf_registration.get_project_client_company(), developer_organization)

            sf_registration.project_client = HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT
            sf_registration.save()

            with self.assertRaises(ObjectDoesNotExist):
                sf_registration.get_project_client_company()

    def test_get_company_responsible_for_payment(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        builder_organization = builder_organization_factory()
        developer_organization = developer_organization_factory()

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            developer_organization=developer_organization,
            architect_organization=SET_NULL,
        )

        with self.subTest("Single Family cases"):
            self.assertEqual(
                sf_registration.get_company_responsible_for_payment(), builder_organization
            )

            sf_registration.is_build_to_rent = True
            sf_registration.entity_responsible_for_payment = (
                HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY
            )
            sf_registration.save()
            self.assertEqual(
                sf_registration.get_company_responsible_for_payment(), developer_organization
            )

        with self.subTest("Multi Family cases"):
            sf_registration.project_type = HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            sf_registration.entity_responsible_for_payment = (
                HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY
            )
            sf_registration.save()

            self.assertEqual(
                sf_registration.get_company_responsible_for_payment(), builder_organization
            )

            sf_registration.entity_responsible_for_payment = (
                HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY
            )
            sf_registration.save()
            self.assertEqual(
                sf_registration.get_company_responsible_for_payment(), developer_organization
            )

            sf_registration.entity_responsible_for_payment = (
                HIRLProjectRegistration.ARCHITECT_RESPONSIBLE_ENTITY
            )
            sf_registration.save()

            with self.assertRaises(ObjectDoesNotExist):
                sf_registration.get_company_responsible_for_payment()
