__author__ = "Artem Hruzd"
__date__ = "03/16/2021 17:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import random
from decimal import Decimal
from unittest import mock

from django.apps import apps
from django.core import mail
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from axis.company.tests.factories import (
    provider_organization_factory,
    builder_organization_factory,
)
from axis.core.tests.factories import provider_admin_factory, SET_NULL
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration
from axis.customer_hirl.tests.factories import (
    hirl_project_factory,
    hirl_green_energy_badge_factory,
    hirl_project_registration_factory,
)
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.home.models import EEPProgramHomeStatus
from axis.invoicing.models import (
    Invoice,
    InvoiceItemGroup,
    InvoiceItem,
    InvoiceItemTransaction,
)
from axis.invoicing.tests.factories import (
    invoice_factory,
    invoice_item_group_factory,
    invoice_item_factory,
)

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectTests(AxisTestCase):
    def test_calculate_certification_fees_cost(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            street_line1="479 Washington St",
            registration=sf_registration,
            home_address_geocode_response=None,
        )

        self.assertEqual(sf_project.calculate_certification_fees_cost(), 300)

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            street_line1="480 Washington St",
            registration=mf_registration,
            story_count=2,
            home_address_geocode_response=None,
        )

        self.assertEqual(mf_project.calculate_certification_fees_cost(), 300)

        mf_project.story_count = 4
        mf_project.save()

        self.assertEqual(mf_project.calculate_certification_fees_cost(), 700)

        mf_project.story_count = 9
        mf_project.save()

        self.assertEqual(mf_project.calculate_certification_fees_cost(), 1000)

        # Accessory structure

        mf_project.is_accessory_structure = True
        mf_project.save()

        self.assertEqual(
            mf_project.calculate_certification_fees_cost(),
            customer_hirl_app.ACCESSORY_STRUCTURE_SEEKING_CERTIFICATION_FEE,
        )

        # Dwelling Unit Structure
        mf_project.is_accessory_structure = False
        mf_project.is_accessory_dwelling_unit = True
        mf_project.save()

        self.assertEqual(
            mf_project.calculate_certification_fees_cost(),
            customer_hirl_app.ACCESSORY_DWELLING_UNIT_STRUCTURE_CERTIFICATION_FEE,
        )

        # Commercial space project with Core & Shell type
        mf_project.is_accessory_structure = False
        mf_project.is_accessory_dwelling_unit = False
        mf_project.is_include_commercial_space = True
        mf_project.commercial_space_type = HIRLProject.CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE
        mf_project.save()

        self.assertEqual(
            mf_project.calculate_certification_fees_cost(),
            customer_hirl_app.COMMERCIAL_SPACE_CORE_AND_SHELL_CERTIFICATION_FEE,
        )

        # Commercial space with Full type
        mf_project.is_accessory_structure = False
        mf_project.is_include_commercial_space = True
        mf_project.commercial_space_type = HIRLProject.FULL_COMMERCIAL_SPACE_TYPE
        mf_project.save()

        self.assertEqual(
            mf_project.calculate_certification_fees_cost(),
            customer_hirl_app.COMMERCIAL_SPACE_FULL_FITTED_CERTIFICATION_FEE,
        )

        # check discount for builder-neal-communities
        builder_organization = builder_organization_factory(slug="builder-neal-communities")
        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
        )
        sf_project = hirl_project_factory(
            street_line1="479 Washington St",
            registration=sf_registration,
            home_address_geocode_response=None,
        )

        self.assertEqual(sf_project.calculate_certification_fees_cost(), 75)

        # wri program certification fee always 100
        wri_eep_program = basic_eep_program_factory(
            name=random.choice(customer_hirl_app.WRI_PROGRAM_LIST),
            customer_hirl_certification_fee=100,
            customer_hirl_per_unit_fee=30,
        )
        mf_registration = hirl_project_registration_factory(
            eep_program=wri_eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            street_line1="481 Washington St",
            registration=mf_registration,
            story_count=12,
            home_address_geocode_response=None,
        )

        self.assertEqual(mf_project.calculate_certification_fees_cost(), 100)

    def test_calculate_per_unit_fee_cost(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            slug="ngbs-sf-certified-2020-new",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )

        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            street_line1="479 Washington St",
            registration=sf_registration,
            number_of_units=0,
            home_address_geocode_response=None,
        )
        self.assertEqual(sf_project.calculate_per_unit_fee_cost(), 0)

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            street_line1="480 Washington St",
            registration=mf_registration,
            number_of_units=2,
            story_count=0,
            home_address_geocode_response=None,
        )

        self.assertEqual(mf_project.calculate_per_unit_fee_cost(), 60)
        with self.subTest("Create Invoice for existing fee group and change unit count"):
            mf_project.create_home_status()
            invoice = invoice_factory()
            for group in mf_project.home_status.invoiceitemgroup_set.all():
                group.invoice = invoice
                group.save()
            # reload invoice to get total
            invoice = Invoice.objects.filter(id=invoice.id).first()
            # 300 program certification fee + 60 per unit fee
            self.assertEqual(invoice.total, 360)

            # add two units
            mf_project = HIRLProject.objects.get(id=mf_project.id)
            mf_project.number_of_units = mf_project.number_of_units + 2
            mf_project.save()

            new_invoice_item_groups = mf_project.home_status.invoiceitemgroup_set.exclude(
                invoice=invoice
            )
            self.assertEqual(new_invoice_item_groups.count(), 1)
            # customer_hirl_per_unit_fee * 2 = 60
            self.assertEqual(new_invoice_item_groups[0].total, 60)

    def test_is_appeals_project(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            slug="ngbs-sf-certified-2020-new",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )

        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )

        sf_project = hirl_project_factory(
            street_line1="479 Washington St",
            registration=sf_registration,
            number_of_units=0,
            home_status=SET_NULL,
            home_address_geocode_response=None,
            is_appeals_project=False,
        )
        sf_project.create_home_status()

        sf_project = HIRLProject.objects.get(id=sf_project.id)

        self.assertEqual(sf_project.calculate_appeals_fee_cost(), 0)

        appel_fees = sf_project.home_status.invoiceitemgroup_set.filter(
            invoiceitem__name=customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL
        )

        self.assertEqual(appel_fees.count(), 0)

        with self.subTest("Is appeals project"):
            sf_project.is_appeals_project = True
            sf_project.save()

            sf_project.refresh_from_db()

            self.assertEqual(
                sf_project.calculate_appeals_fee_cost(),
                customer_hirl_app.DEFAULT_APPEALS_SINGLE_FAMILY_FEE,
            )

            appeal_fees = InvoiceItem.objects.filter(
                group__home_status=sf_project.home_status,
                name=customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL,
            )

            self.assertEqual(appeal_fees.count(), 1)
            self.assertEqual(
                appeal_fees[0].cost, customer_hirl_app.DEFAULT_APPEALS_SINGLE_FAMILY_FEE
            )

        with self.subTest("Is not appeals project"):
            sf_project = HIRLProject.objects.get(id=sf_project.id)
            sf_project.is_appeals_project = False
            sf_project.save()

            sf_project.refresh_from_db()
            self.assertEqual(sf_project.calculate_appeals_fee_cost(), 0)

            appeal_fees = InvoiceItem.objects.filter(
                group__home_status=sf_project.home_status,
                name=customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL,
            )

            self.assertEqual(appeal_fees.count(), 2)
            # we have to items where diff = 0
            self.assertEqual(
                appeal_fees[0].cost,
                customer_hirl_app.DEFAULT_APPEALS_SINGLE_FAMILY_FEE * -1,
            )
            self.assertEqual(
                appeal_fees[1].cost, customer_hirl_app.DEFAULT_APPEALS_SINGLE_FAMILY_FEE
            )

    def test_is_appeals_project_fee_max_capacity(self):
        customer_hirl_app.MAX_APPEALS_FEE_PER_REGISTRATION = 1100
        customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE = 1000

        eep_program = basic_eep_program_factory(
            name="MF 2020 New Construction",
            slug="ngbs-mf-certified-2020-new",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )

        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )

        mf_project = hirl_project_factory(
            street_line1="479 Washington St",
            registration=mf_registration,
            story_count=1,
            number_of_units=1,
            home_status=SET_NULL,
            home_address_geocode_response=None,
            is_appeals_project=True,
        )
        mf_project.create_home_status()
        mf_project.refresh_from_db()

        self.assertEqual(
            mf_project.calculate_appeals_fee_cost(),
            customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE,
        )

        appeal_fees = InvoiceItem.objects.filter(
            group__home_status=mf_project.home_status,
            name=customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL,
        )

        self.assertEqual(appeal_fees.count(), 1)
        self.assertEqual(appeal_fees[0].cost, customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE)

        # check second project
        mf_project2 = hirl_project_factory(
            street_line1="480 Washington St",
            registration=mf_registration,
            story_count=1,
            number_of_units=1,
            home_status=SET_NULL,
            home_address_geocode_response=None,
            is_appeals_project=True,
        )
        mf_project2.create_home_status()

        mf_project2.refresh_from_db()

        remaining_fee = (
            customer_hirl_app.MAX_APPEALS_FEE_PER_REGISTRATION
            - customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE
        )
        self.assertEqual(
            mf_project2.calculate_appeals_fee_cost(),
            remaining_fee,
        )

        appeal_fees = InvoiceItem.objects.filter(
            group__home_status=mf_project2.home_status,
            name=customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL,
        )

        self.assertEqual(appeal_fees.count(), 1)
        self.assertEqual(appeal_fees[0].cost, remaining_fee)

    def test_change_story_count_for_multi_family_project(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=0,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            story_count=0,
            number_of_units=0,
            home_address_geocode_response=None,
        )

        mf_registration.active()
        mf_project.save()

        mf_project.home_status = None
        mf_project.save()
        mf_project.create_home_status()

        certification_fee_cost = mf_project.calculate_certification_fees_cost()
        invoice_items_count = InvoiceItem.objects.count()

        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()

        # initially we have 2 Invoice items: certification fee and per unit fee
        self.assertEqual(mf_project.fee_total, certification_fee_cost)
        self.assertEqual(invoice_items_count, 2)

        mf_project.story_count = 4
        mf_project.save()

        invoice_items_count = InvoiceItem.objects.count()
        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()
        certification_fee_cost = mf_project.calculate_certification_fees_cost()

        self.assertEqual(mf_project.fee_total, certification_fee_cost)
        self.assertEqual(invoice_items_count, 3)

        mf_project.story_count = 9
        mf_project.save()

        invoice_items_count = InvoiceItem.objects.count()
        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()
        certification_fee_cost = mf_project.calculate_certification_fees_cost()

        self.assertEqual(mf_project.fee_total, certification_fee_cost)
        self.assertEqual(invoice_items_count, 4)

    def test_change_story_count_for_multi_family_project_with_green_energy_badges(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=0,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            story_count=0,
            number_of_units=0,
            home_address_geocode_response=None,
        )

        mf_registration.active()
        mf_project.save()

        green_energy_badge = hirl_green_energy_badge_factory(name="test badge", cost=10)

        mf_project.home_status = None
        mf_project.save()

        # add green energy badge
        mf_project.green_energy_badges.add(green_energy_badge)
        mf_project.create_home_status()

        certification_fee_cost = mf_project.calculate_certification_fees_cost()
        invoice_items_count = InvoiceItem.objects.count()

        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()

        # initially we have 3 Invoice items: certification fee and
        # per unit fee and green energy badge fee(cost*2)
        self.assertEqual(mf_project.fee_total, certification_fee_cost + 20)
        self.assertEqual(invoice_items_count, 3)

        # update story_count
        mf_project.story_count = 9
        mf_project.save()

        invoice_items_count = InvoiceItem.objects.count()
        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()
        certification_fee_cost = mf_project.calculate_certification_fees_cost()

        self.assertEqual(mf_project.fee_total, certification_fee_cost + 60)
        self.assertEqual(invoice_items_count, 5)

    def test_change_number_of_units_for_multi_family_project(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=0,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            story_count=0,
            number_of_units=0,
            home_address_geocode_response=None,
        )

        mf_registration.active()
        mf_project.save()

        mf_project.home_status = None
        mf_project.save()
        mf_project.create_home_status()

        per_unit_fee_cost = mf_project.calculate_per_unit_fee_cost()
        invoice_items_count = InvoiceItem.objects.count()

        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()

        # initially we have 2 Invoice items: certification fee and per unit fee
        self.assertEqual(mf_project.fee_total, per_unit_fee_cost)
        self.assertEqual(invoice_items_count, 2)

        mf_project.number_of_units = 4
        mf_project.save()

        invoice_items_count = InvoiceItem.objects.count()
        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()
        per_unit_fee_cost = mf_project.calculate_per_unit_fee_cost()

        self.assertEqual(mf_project.fee_total, per_unit_fee_cost)
        self.assertEqual(invoice_items_count, 3)

        mf_project.number_of_units = 9
        mf_project.save()

        invoice_items_count = InvoiceItem.objects.count()
        mf_project = HIRLProject.objects.filter().annotate_billing_info().first()
        per_unit_fee_cost = mf_project.calculate_per_unit_fee_cost()

        self.assertEqual(mf_project.fee_total, per_unit_fee_cost)
        self.assertEqual(invoice_items_count, 4)

    @mock.patch("axis.customer_hirl.messages.HIRLProjectRegistrationStateChangedMessage.send")
    def test_check_sf_project_fees(self, hirl_project_status_state_changed_message):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        sf_registration.active()
        sf_registration.save()

        hirl_project_status_state_changed_message.assert_called_once()
        sf_project.create_home_status()

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        invoice_item_group = sf_project.home_status.invoiceitemgroup_set.first()

        self.assertEqual(invoice_item_group.invoiceitem_set.count(), 1)
        # we should have only certification fee here without any badges
        self.assertEqual(invoice_item_group.total, eep_program.customer_hirl_certification_fee)

        # try to add badge
        hirl_green_energy_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)

        sf_project.green_energy_badges.add(hirl_green_energy_badge)
        sf_project.save()

        invoice_item_group = sf_project.home_status.invoiceitemgroup_set.first()

        # created invoice via signal items must be protected
        self.assertEqual(invoice_item_group.invoiceitem_set.count(), 2)
        self.assertEqual(invoice_item_group.invoiceitem_set.filter(protected=True).count(), 2)

        self.assertEqual(
            invoice_item_group.total,
            eep_program.customer_hirl_certification_fee + hirl_green_energy_badge.cost,
        )

        # try to remove badge
        sf_project.green_energy_badges.remove(hirl_green_energy_badge)
        sf_project.save()

        invoice_item_group = sf_project.home_status.invoiceitemgroup_set.first()
        self.assertEqual(invoice_item_group.invoiceitem_set.count(), 1)
        self.assertEqual(invoice_item_group.total, eep_program.customer_hirl_certification_fee)

        # try to add badge with invoice
        invoice = invoice_factory()

        invoice_item_group.invoice = invoice
        invoice_item_group.save()

        sf_project.green_energy_badges.add(hirl_green_energy_badge)
        sf_project.save()

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 2)

    def test_build_to_rent_sf_project_fees(self):
        eep_program = basic_eep_program_factory(
            slug=random.choice(
                customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_NEW_CONSTRUCTION_SLUGS
                + customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SF_REMODEL_SLUGS
            ),
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            is_build_to_rent=True,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        sf_registration.active()
        sf_registration.save()

        sf_project.create_home_status()

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        invoice_item_group = sf_project.home_status.invoiceitemgroup_set.first()

        self.assertEqual(invoice_item_group.invoiceitem_set.count(), 1)
        # we should have only certification fee
        self.assertEqual(invoice_item_group.total, customer_hirl_app.BUILD_TO_RENT_FEE)

    def test_calculate_billing_state(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
        )

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NEW_BILLING_STATE)

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.create_home_status()

        hirl_green_energy_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)
        sf_project.green_energy_badges.add(hirl_green_energy_badge)

        total_fees = InvoiceItem.objects.filter(
            group__home_status=sf_project.home_status, protected=True
        ).aggregate(total_fees=Coalesce(Sum("cost"), 0, output_field=DecimalField()))["total_fees"]
        # certification fee + our two test badges
        expected_fees_cost = sf_project.calculate_certification_fees_cost() + 10
        self.assertEqual(total_fees, expected_fees_cost)

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NEW_NOTIFIED_BILLING_STATE)

        # imagine that builder "approve" group fees by creating invoice for them
        invoice = Invoice.objects.create(
            issuer=hirl_company,
            customer=sf_project.registration.get_company_responsible_for_payment(),
        )

        for group in InvoiceItemGroup.objects.filter(home_status=sf_project.home_status):
            group.invoice = invoice
            group.save()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NOTICE_SENT_BILLING_STATE)

        # imagine ngbs import JAMIS file and invoice been partially paid

        sf_project.pay(amount=expected_fees_cost / Decimal(2))

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NOTICE_SENT_BILLING_STATE)
        sf_project.pay(amount=expected_fees_cost / Decimal(2))

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()
        self.assertEqual(sf_project.billing_state, HIRLProject.NOTICE_SENT_BILLING_STATE)

        sf_project.home_status.state = EEPProgramHomeStatus.CERTIFICATION_PENDING_STATE
        sf_project.home_status.make_transition(transition="completion_transition")
        sf_project.home_status.save()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.COMPLETED_BILLING_STATE)

    def test_pay_with_overpay(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.create_home_status()

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        test_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)
        another_badge = hirl_green_energy_badge_factory(name="Another Badge", cost=10)
        sf_project.green_energy_badges.add(test_badge)
        sf_project.green_energy_badges.add(another_badge)

        total_fees = InvoiceItem.objects.filter(
            group__home_status=sf_project.home_status, protected=True
        ).aggregate(total_fees=Coalesce(Sum("cost"), 0, output_field=DecimalField()))["total_fees"]
        # certification fee + our two test badges
        expected_fees_cost = sf_project.calculate_certification_fees_cost() + 20
        self.assertEqual(total_fees, expected_fees_cost)

        overpay = 10
        sf_project.pay(amount=expected_fees_cost + overpay)

        invoice_items = InvoiceItem.objects.filter(
            group__home_status=sf_project.home_status
        ).order_by("created_at")

        self.assertEqual(
            invoice_items[0].total_paid, sf_project.calculate_certification_fees_cost()
        )
        self.assertEqual(invoice_items[1].total_paid, 10)
        self.assertEqual(invoice_items[2].total_paid, 10)
        self.assertEqual(invoice_items[3].total_paid, overpay)

    def test_pay_partially(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.registration.save()
        sf_project.create_home_status()
        sf_project.save()

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        test_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)
        another_badge = hirl_green_energy_badge_factory(name="Another Badge", cost=10)
        sf_project.green_energy_badges.add(test_badge)
        sf_project.green_energy_badges.add(another_badge)

        total_fees = InvoiceItem.objects.filter(
            group__home_status=sf_project.home_status, protected=True
        ).aggregate(total_fees=Coalesce(Sum("cost"), 0, output_field=DecimalField()))["total_fees"]
        # certification fee + our two test badges
        expected_fees_cost = sf_project.calculate_certification_fees_cost() + 20
        self.assertEqual(total_fees, expected_fees_cost)

        date_paid = timezone.now()
        sf_project.pay(amount=20, date_paid=date_paid)

        invoice_items = InvoiceItem.objects.filter(
            group__home_status=sf_project.home_status, protected=True
        ).order_by("created_at")

        self.assertEqual(invoice_items[0].total_paid, 20)
        self.assertEqual(invoice_items[1].total_paid, 0)
        self.assertEqual(invoice_items[2].total_paid, 0)

        transactions = InvoiceItemTransaction.objects.all()
        for transaction in transactions:
            self.assertEqual(transaction.created_at, date_paid)

    def test_pay_order(self):
        """
        If appeals fees are present, apply payment to that fee group first
        If no appeals fees are present, apply payment to fees based on invoice
        date from OLDEST to MOST RECENT
        :return:
        """

        customer_hirl_certification_fee = 300
        customer_hirl_per_unit_fee = 30

        eep_program = basic_eep_program_factory(
            name="MF 2020 New Construction",
            customer_hirl_certification_fee=customer_hirl_certification_fee,
            customer_hirl_per_unit_fee=customer_hirl_per_unit_fee,
            is_multi_family=True,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            is_appeals_project=True,
            story_count=1,
            number_of_units=1,
        )

        # activate a project and create new home with program
        mf_project.registration.active()
        mf_project.registration.save()
        mf_project.create_home_status()
        mf_project.save()

        # check data
        self.assertEqual(mf_project.home_status.invoiceitemgroup_set.count(), 2)

        (
            appeals_fees_group,
            certification_fees_group,
        ) = mf_project.home_status.invoiceitemgroup_set.all()

        self.assertEqual(appeals_fees_group.category, InvoiceItemGroup.APPEALS_FEE_CATEGORY)

        self.assertEqual(
            appeals_fees_group.total, customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE
        )

        self.assertEqual(
            appeals_fees_group.current_balance, customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE
        )

        self.assertEqual(
            certification_fees_group.total,
            customer_hirl_certification_fee + customer_hirl_per_unit_fee,
        )

        self.assertEqual(
            certification_fees_group.total,
            customer_hirl_certification_fee + customer_hirl_per_unit_fee,
        )

        # additional fee group created by user
        new_fee_group = invoice_item_group_factory(home_status=mf_project.home_status)

        additional_fees_cost = 50
        additional_fees_item = invoice_item_factory(
            group=new_fee_group, name="Additional fees", cost=additional_fees_cost
        )

        with self.subTest(
            "Pay partially and make sure that Transaction is created for Appeals fees first"
        ):
            mf_project.pay(amount=1)
            self.assertEqual(InvoiceItemTransaction.objects.all().count(), 1)
            transaction = InvoiceItemTransaction.objects.filter(
                item__group=appeals_fees_group
            ).first()
            self.assertEqual(transaction.amount, 1)

        with self.subTest(
            "Pay the rest and make sure we have order for transactions: Appeals fee, Oldest Certification Fee, New Fee"
        ):
            mf_project.pay(
                amount=customer_hirl_app.DEFAULT_APPEALS_MULTI_FAMILY_FEE
                + customer_hirl_certification_fee
                + customer_hirl_per_unit_fee
                + additional_fees_cost
                # we already pay 1 above
                - 1
            )

            self.assertEqual(InvoiceItemTransaction.objects.all().count(), 5)
            (
                appeals_fee_transaction,
                appeals_fee_transaction1,
                certification_fee_transaction,
                per_unit_fee_transaction,
                additional_fees_transaction,
            ) = InvoiceItemTransaction.objects.all().order_by("created_at")

            self.assertEqual(
                appeals_fee_transaction.item.name, customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL
            )
            self.assertEqual(
                appeals_fee_transaction1.item.name, customer_hirl_app.DEFAULT_APPEALS_FEE_LABEL
            )
            self.assertEqual(
                certification_fee_transaction.item.name, f"Certification Fee: {eep_program.name}"
            )
            self.assertEqual(per_unit_fee_transaction.item.name, "Certification Fee: Unit Fee")
            self.assertEqual(additional_fees_transaction.item.name, additional_fees_item.name)

    def test_manual_set_billing_state_to_complimentary(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        hirl_organization = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        # create special ngbs Accounting user to get him via app.get_accounting_users()
        provider_admin_factory(company=hirl_organization, email="khall@homeinnovation.com")

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.registration.save()
        sf_project.create_home_status()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NEW_NOTIFIED_BILLING_STATE)

        sf_project.manual_billing_state = HIRLProject.COMPLIMENTARY_BILLING_STATE
        sf_project.save()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.COMPLIMENTARY_BILLING_STATE)
        self.assertEqual(sf_project.fee_total, 0)

    def test_initial_home_status_state_sf_project(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            slug="ngbs-sf-certified-2020-new",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.registration.save()
        sf_project.create_home_status()

        sf_project.refresh_from_db()

        self.assertEqual(
            sf_project.home_status.state,
            EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE,
        )

    def test_set_manual_billing_state_to_not_pursing(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        hirl_organization = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        # create special ngbs Accounting user to get him via app.get_accounting_users()
        provider_admin_factory(company=hirl_organization, email="khall@homeinnovation.com")

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.registration.save()
        sf_project.create_home_status()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NEW_NOTIFIED_BILLING_STATE)

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        test_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)
        another_badge = hirl_green_energy_badge_factory(name="Another Badge", cost=10)
        sf_project.green_energy_badges.add(test_badge)
        sf_project.green_energy_badges.add(another_badge)

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        # certification fee + our two test badges
        expected_fees_cost = sf_project.calculate_certification_fees_cost() + 20
        self.assertEqual(sf_project.fee_total, expected_fees_cost)
        self.assertEqual(sf_project.fee_total_paid, 0)

        sf_project.manual_billing_state = HIRLProject.NOT_PURSUING_BILLING_STATE
        sf_project.save()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NOT_PURSUING_BILLING_STATE)
        self.assertEqual(sf_project.fee_total, 0)

    def test_set_manual_billing_state_to_not_pursing_if_it_is_already_paid(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        hirl_organization = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        # create special ngbs Accounting user to get him via app.get_accounting_users()
        provider_admin_factory(company=hirl_organization, email="khall@homeinnovation.com")

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None
        )

        # activate a project and create new home with program
        sf_project.registration.active()
        sf_project.registration.save()
        sf_project.create_home_status()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NEW_NOTIFIED_BILLING_STATE)

        self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

        test_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)
        another_badge = hirl_green_energy_badge_factory(name="Another Badge", cost=10)
        sf_project.green_energy_badges.add(test_badge)
        sf_project.green_energy_badges.add(another_badge)

        sf_project.pay(amount=1)

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        # certification fee + our two test badges
        expected_fees_cost = sf_project.calculate_certification_fees_cost() + 20
        self.assertEqual(sf_project.fee_total, expected_fees_cost)
        self.assertEqual(sf_project.fee_total_paid, 1)

        sf_project.manual_billing_state = HIRLProject.NOT_PURSUING_BILLING_STATE
        sf_project.save()

        sf_project = HIRLProject.objects.filter(id=sf_project.id).annotate_billing_info().first()

        self.assertEqual(sf_project.billing_state, HIRLProject.NOT_PURSUING_BILLING_STATE)
        self.assertEqual(sf_project.fee_total, expected_fees_cost)

        # 3 emails. Registration created, Fees Updated and Billing state has been manually changed
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(
            mail.outbox[2].subject,
            "Billing state has been manually changed for Project",
        )

    def test_change_number_of_lots_for_land_development_project(self):
        eep_program = basic_eep_program_factory(
            name="2020 Land Development",
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        ld_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.LAND_DEVELOPMENT_PROJECT_TYPE,
        )
        ld_project = hirl_project_factory(
            registration=ld_registration,
            number_of_lots=10,
            home_status=SET_NULL,
        )

        ld_registration.active()

        ld_project.save()
        ld_project.create_home_status()

        with self.subTest("Check with number of lots less than 99"):
            certification_fees_cost = ld_project.calculate_certification_fees_cost()
            invoice_items_count = InvoiceItem.objects.count()

            ld_project = HIRLProject.objects.filter().annotate_billing_info().first()

            self.assertEqual(ld_project.fee_total, certification_fees_cost)
            self.assertEqual(invoice_items_count, 1)

        with self.subTest("Check with number of lots more than 99"):
            ld_project.number_of_lots = 120
            ld_project.save()

            invoice_items_count = InvoiceItem.objects.count()
            ld_project = HIRLProject.objects.filter().annotate_billing_info().first()
            certification_fees_cost = ld_project.calculate_certification_fees_cost()

            self.assertEqual(ld_project.fee_total, certification_fees_cost)
            self.assertEqual(invoice_items_count, 2)

    def test_initial_invoice_date(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=300,
            customer_hirl_per_unit_fee=30,
        )
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_status=SET_NULL,
            home_address_geocode_response=None,
        )
        # activate a project and create new home with program
        sf_project.create_home_status()

        with self.subTest("No Invoice"):
            sf_project = HIRLProject.objects.filter(id=sf_project.id).first()
            self.assertEqual(sf_project.initial_invoice_date, None)

        with self.subTest("With Invoices, but without Appeals Fee"):
            self.assertEqual(sf_project.home_status.invoiceitemgroup_set.count(), 1)

            invoice = Invoice.objects.create(
                issuer=hirl_company,
                customer=sf_project.registration.get_company_responsible_for_payment(),
            )

            for group in sf_project.home_status.invoiceitemgroup_set.filter(invoice__isnull=True):
                group.invoice = invoice
                group.save()

            # ignore invoice 2, because we need earlier date
            invoice2 = Invoice.objects.create(
                issuer=hirl_company,
                customer=sf_project.registration.get_company_responsible_for_payment(),
            )

            InvoiceItemGroup.objects.create(home_status=sf_project.home_status)

            for group in sf_project.home_status.invoiceitemgroup_set.filter(invoice__isnull=True):
                group.invoice = invoice2
                group.save()

            sf_project = HIRLProject.objects.filter(id=sf_project.id).first()

            # make sure we have two invoices
            self.assertEqual(
                Invoice.objects.filter(
                    invoiceitemgroup__home_status__customer_hirl_project=sf_project
                ).count(),
                2,
            )
            self.assertEqual(sf_project.initial_invoice_date, invoice.created_at)

        with self.subTest("With only Appeals Fee Invoice"):
            # remove all existing groups
            sf_project.home_status.invoiceitemgroup_set.all().delete()
            sf_project.initial_invoice_date = None
            sf_project.save()

            invoice = Invoice.objects.create(
                issuer=hirl_company,
                customer=sf_project.registration.get_company_responsible_for_payment(),
            )

            InvoiceItemGroup.objects.create(
                home_status=sf_project.home_status,
                category=InvoiceItemGroup.APPEALS_FEE_CATEGORY,
            )

            for group in sf_project.home_status.invoiceitemgroup_set.filter(invoice__isnull=True):
                group.invoice = invoice
                group.save()

            sf_project = HIRLProject.objects.filter(id=sf_project.id).first()
            self.assertIsNone(sf_project.initial_invoice_date)
