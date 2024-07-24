"""base.py: Django """


__author__ = "Steven K"
__date__ = "12/17/2019 14:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from django.urls import reverse

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.models import ETOAccount
from axis.eep_program.models import EEPProgram

from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.home.models import EEPProgramHomeStatus, Home

log = logging.getLogger(__name__)


class EEPProgramETOProgramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for ETO eep_program"""

    client_class = AxisClient

    def test_get_eto_builder_account_number_status_missing_eto_acct_number(self):
        """
        Test for get_eto_builder_account_number_status() case when home_status' home  builder does
        NOT have an ETO Account number [builder.eto_account.account_number]
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_builder_account_number_status(home_status, "co_edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        builder = home_status.home.get_builder()
        url = reverse("company:view", kwargs={"type": builder.company_type, "pk": builder.pk})
        self.assertEqual(result.url, url)
        self.assertIn(
            "Program requires the {company_type} to have an ETO Account number.".format(
                company_type=builder.company_type
            ),
            result.message,
        )

    def test_get_eto_builder_account_number_status_empty_account_number(self):
        """
        Test for get_eto_builder_account_number_status() case when home_status' home  builder does
        have an ETO Account number [builder.eto_account.account_number] but is an empty string ('')
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        builder = home_status.home.get_builder()
        eto_account = ETOAccount.objects.create(company=builder, account_number="")
        builder.eto_account = eto_account
        builder.save()
        result = eep_program.get_eto_builder_account_number_status(home_status, "co_edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        url = reverse("company:view", kwargs={"type": builder.company_type, "pk": builder.pk})
        self.assertEqual(result.url, url)
        self.assertIn(
            "Program requires the {company_type} to have an ETO Account number.".format(
                company_type=builder.company_type
            ),
            result.message,
        )

    def test_get_eto_builder_account_number_status_home_missing_builder(self):
        """
        Test for get_eto_builder_account_number_status() case when home_status' home does not
        have a builder
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwrgs = {"lot_number": "{}".format("99"), "street_line1": "{} N. Main St".format("033")}
        home = Home(**kwrgs)
        home.save()
        home_status = EEPProgramHomeStatus(
            eep_program=eep_program, home=home, company=eep_program.owner
        )
        home_status.save()
        result = eep_program.get_eto_builder_account_number_status(home_status, "co_edit_url")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Missing", result.message)
        self.assertEqual(result.url, "co_edit_url")

    def test_get_eto_builder_account_number_status_passing_status(self):
        """Test for get_eto_builder_account_number_status() case for passing status"""
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        builder = home_status.home.get_builder()
        eto_account = ETOAccount.objects.create(company=builder, account_number="12345")
        builder.eto_account = eto_account
        builder.save()
        result = eep_program.get_eto_builder_account_number_status(home_status, "co_edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_eto_rater_account_number_status_missing_eto_acct_number(self):
        """
        Test for get_eto_rater_account_number_status() case when home_status' home  rater does
        NOT have an ETO Account number [rater.eto_account.account_number]
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_rater_account_number_status(home_status)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        rater = home_status.company
        url = reverse("company:view", kwargs={"type": rater.company_type, "pk": rater.pk})
        self.assertEqual(result.url, url)
        self.assertIn(
            "Program requires the {company_type} to have an ETO Account number.".format(
                company_type=rater.company_type
            ),
            result.message,
        )

    def test_get_eto_rater_account_number_status_empty_account_number(self):
        """
        Test for get_eto_rater_account_number_status() case when home_status' home  rater does
        have an ETO Account number [rater.eto_account.account_number] but is an empty string ('')
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        rater = home_status.company
        eto_account = ETOAccount.objects.create(company=rater, account_number="")
        rater.eto_account = eto_account
        rater.save()
        result = eep_program.get_eto_rater_account_number_status(home_status)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        rater = home_status.company
        url = reverse("company:view", kwargs={"type": rater.company_type, "pk": rater.pk})
        self.assertEqual(result.url, url)
        self.assertIn(
            "Program requires the {company_type} to have an ETO Account number.".format(
                company_type=rater.company_type
            ),
            result.message,
        )

    def test_get_eto_rater_account_number_status_passing_status(self):
        """Test for get_eto_rater_account_number_status() case for passing status"""
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="-eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        rater = home_status.company
        eto_account = ETOAccount.objects.create(company=rater, account_number="12345")
        rater.eto_account = eto_account
        rater.save()
        result = eep_program.get_eto_rater_account_number_status(home_status)
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_verify_approved_utility_failing_status_eto_2020(self):
        """_verify_approved_utility program slug eto-2020"""
        slug = "eto-2020"
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", slug
        )
        self.assertFalse(result.status)

    def test_verify_approved_utility_wa_state_failing_status_eto_2020(self):
        """_verify_approved_utility program slug eto-2020"""
        slug = "eto-2020"
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", slug
        )
        self.assertFalse(result.status)

    def test_verify_approved_utility_passing_status_eto_2020(self):
        """_verify_approved_utility program slug eto-2020"""
        from axis.customer_eto.calculator.eps.constants.eto_2020 import ETO_2020_FUEL_RATES

        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        utility_slug = random.choice(list(fuel_rates.keys()))
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", slug
        )
        self.assertTrue(result.status)

    def test_verify_approved_utility_wa_state_passing_status_eto_2020(self):
        """_verify_approved_utility program slug eto-2020"""
        from axis.customer_eto.calculator.eps.constants.eto_2020 import (
            ETO_2020_FUEL_RATES,
            ETO_2020_FUEL_RATES_WA_OVERRIDE,
        )

        slug = "eto-2020"
        fuel_rates = dict(ETO_2020_FUEL_RATES)
        fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))
        utility_slug = random.choice(list(fuel_rates.keys()))
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", slug
        )
        self.assertTrue(result.status)

    def test_verify_approved_utility_failing_status(self):
        """_verify_approved_utility non eto-2020"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", "eto-2019"
        )
        self.assertFalse(result.status)

    def test_verify_approved_utility_wa_state_failing_status(self):
        """_verify_approved_utility non eto-2020"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", "eto-2019"
        )
        self.assertFalse(result.status)

    def test_verify_approved_utility_passing_status(self):
        """_verify_approved_utility non eto-2020"""
        from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES

        fuel_rates = dict(ETO_2019_FUEL_RATES)
        utility_slug = random.choice(list(fuel_rates.keys()))
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", "eto-2019"
        )
        self.assertTrue(result.status)

    def test_verify_approved_utility_wa_state_passing_status(self):
        """_verify_approved_utility non eto-2020"""
        from axis.customer_eto.calculator.eps import (
            ETO_2019_FUEL_RATES,
            ETO_2019_FUEL_RATES_WA_OVERRIDE,
        )

        fuel_rates = dict(ETO_2019_FUEL_RATES)
        fuel_rates.update(dict(ETO_2019_FUEL_RATES_WA_OVERRIDE))
        utility_slug = random.choice(list(fuel_rates.keys()))
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.get_gas_company()
        utility_company.slug = utility_slug
        utility_company.save()
        self.assertIn(utility_company.slug, fuel_rates)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = eep_program.homestatuses.first()
        result = eep_program._verify_approved_utility(
            home_status, utility_company, "label", "edit_url", "eto-2019"
        )
        self.assertTrue(result.status)

    def test_get_built_green_wa_electric_utility_required_status_passing_status(self):
        """Test get_built_green_wa_electric_utility_required_status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        utility_company = home_status.home.get_electric_company()
        self.assertIsNotNone(utility_company)
        result = eep_program.get_built_green_wa_electric_utility_required_status(
            home_status.home, home_status, "companies_edit_url"
        )
        self.assertTrue(result.status)

    def test_get_built_green_wa_electric_utility_required_status_failing_status(self):
        """Test get_built_green_wa_electric_utility_required_status"""
        from axis.home.tests.factories import custom_home_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        home = custom_home_factory()
        utility_company = home.get_electric_company()
        home_status.home = home
        self.assertIsNone(utility_company)
        result = eep_program.get_built_green_wa_electric_utility_required_status(
            home, home_status, "companies_edit_url"
        )
        self.assertFalse(result.status)

    def test_get_built_green_wa_gas_utility_required_status_no_floorplan(self):
        """Test get_built_green_wa_gas_utility_required_status, home_status
        has no floorplan, expected result None"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        home_status.floorplan = None
        result = eep_program.get_built_green_wa_gas_utility_required_status(
            home_status.home, home_status, "companies_edit_url"
        )
        self.assertIsNone(result)

    def test_get_built_green_wa_gas_utility_required_status_no_simulation(self):
        """Test get_built_green_wa_gas_utility_required_status, home_status
        has no simulation, expected result None"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = eep_program.homestatuses.first()
        self.assertIsNotNone(home_status.floorplan)
        self.assertIsNone(home_status.floorplan.remrate_target)
        result = eep_program.get_built_green_wa_gas_utility_required_status(
            home_status.home, home_status, "companies_edit_url"
        )
        self.assertIsNone(result)

    def test_get_built_green_wa_gas_utility_required_status_failing_status(self):
        """Test get_built_green_wa_gas_utility_required_status, home_status has
        no simulation, expected result None"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory
        from axis.home.tests.factories import custom_home_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        stats = eep_program.homestatuses.first()
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(floorplan=floorplan)
        home_status = eep_program.homestatuses.first()
        self.assertIsNotNone(home_status.floorplan.remrate_target)
        home = custom_home_factory()
        utility_company = home.get_electric_company()
        home_status.home = home
        self.assertIsNone(utility_company)
        result = eep_program.get_built_green_wa_gas_utility_required_status(
            home, home_status, "companies_edit_url"
        )
        self.assertFalse(result.status)

    def test_get_built_green_wa_gas_utility_required_status_no_equipement_passing_status(self):
        """Test get_built_green_wa_gas_utility_required_status,
        simulation has no installedequipment"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        stats = eep_program.homestatuses.first()
        floorplan = floorplan_with_remrate_factory()
        floorplan.remrate_target.installedequipment_set.filter(system_type__in=[1, 7]).delete()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(floorplan=floorplan)
        home_status = eep_program.homestatuses.first()
        self.assertIsNotNone(home_status.floorplan.remrate_target)
        home = home_status.home
        utility_company = home.get_electric_company()
        self.assertIsNotNone(utility_company)
        result = eep_program.get_built_green_wa_gas_utility_required_status(
            home, home_status, "companies_edit_url"
        )
        self.assertTrue(result.status)

    def test_get_built_green_wa_gas_utility_required_status_passing_status(self):
        """Test get_built_green_wa_gas_utility_required_status"""
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        stats = eep_program.homestatuses.first()
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(id=stats.id).update(floorplan=floorplan)
        home_status = eep_program.homestatuses.first()
        self.assertIsNotNone(home_status.floorplan.remrate_target)
        home = home_status.home
        utility_company = home.get_electric_company()
        self.assertIsNotNone(utility_company)
        result = eep_program.get_built_green_wa_gas_utility_required_status(
            home, home_status, "companies_edit_url"
        )
        self.assertTrue(result.status)
