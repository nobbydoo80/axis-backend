"""test_models.py: Django customer_eto"""

__author__ = "Steven Klass"
__date__ = "11/15/13 8:40 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import datetime
import logging
from decimal import Decimal
from unittest import mock

from django.core import management
from django.utils.timezone import now

from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from ..enumerations import PrimaryHeatingEquipment2020, HeatType
from ..reports.legacy_utils import get_legacy_calculation_data
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.strings import ETO_ACCOUNT_NUMBER_ADDED_BASE
from axis.customer_eto.tasks import submit_fasttrack_xml
from axis.customer_eto.tests.program_checks.test_eto_2020 import ETO2020ProgramTestMixin
from axis.customer_eto.tests.factories import eto_mocked_soap_responses as mocked_post
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import certify_single_home
from axis.messaging.models import Message
from axis.relationship.utils import create_or_update_spanning_relationships
from simulation.enumerations import FuelType, DistributionSystemType
from ..models import ETOAccount
from ...checklist.collection.test_mixins import CollectionRequestMixin
from ...company.tests.factories import (
    eep_organization_factory,
    provider_organization_factory,
    utility_organization_factory,
    rater_organization_factory,
    builder_organization_factory,
    qa_organization_factory,
)
from ...core.tests.factories import (
    qa_admin_factory,
    provider_admin_factory,
    rater_admin_factory,
)
from ...core.tests.test_views import DevNull
from ...eep_program.models import EEPProgram
from ...eep_program.tests.factories import basic_eep_program_factory
from ...filehandling.models import CustomerDocument
from ...floorplan.tests.factories import floorplan_with_remrate_factory
from ...gbr.tests.mocked_responses import gbr_mocked_response
from ...geographic.tests.factories import real_city_factory
from ...home.tests.factories import home_factory
from ...qa.models import QARequirement
from ...relationship.models import Relationship
from ...remrate_data.tests.factories import udrh_simulation_factory

log = logging.getLogger(__name__)


class ETO2018ProgramTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")

        cls.eto = eep_organization_factory(slug="eto", is_customer=True, name="ETO", city=cls.city)

        cls.peci = provider_organization_factory(
            slug="peci", is_customer=True, name="PECI", city=cls.city
        )
        provider_admin_factory(company=cls.peci, username="eto_provider_admin")

        cls.pac_pwr = utility_organization_factory(
            slug="pacific-power",
            is_customer=True,
            name="Pacific Power",
            city=cls.city,
            gas_provider=False,
            electricity_provider=True,
        )
        cls.nw_nat = utility_organization_factory(
            slug="nw-natural-gas",
            is_customer=True,
            name="NW Natural Gas",
            city=cls.city,
            gas_provider=True,
            electricity_provider=False,
        )
        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )
        ETOAccount.objects.create(company=cls.rater_company, account_number="123")
        rater_admin_factory(company=cls.rater_company, username="eto_rater_admin")

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        ETOAccount.objects.create(company=cls.builder_company, account_number="456")

        management.call_command(
            "build_program",
            "-p",
            "eto-2018",
            "--warn_only",
            "--no_close_dates",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-2018")
        cls.eep_program.certifiable_by.add(cls.peci)

        cls.qa = qa_organization_factory(
            slug="csg-qa",
            is_customer=True,
            name="CSG",
            city=cls.city,
        )
        qa_admin_factory(company=cls.qa, username="eto_qa_admin")
        QARequirement.objects.get_or_create(
            qa_company=cls.qa,
            coverage_pct=1,
            gate_certification=True,
            eep_program=cls.eep_program,
        )

        companies = [
            cls.eto,
            cls.qa,
            cls.peci,
            cls.rater_company,
            cls.builder_company,
            cls.pac_pwr,
            cls.nw_nat,
        ]

        Relationship.objects.create_mutual_relationships(*companies)

        simulation = udrh_simulation_factory(
            site__site_label="Portland, OR",
            version="15.3",
            flavor="rate",
            lightsandappliance__oven_fuel=1,
            lightsandappliance__clothes_dryer_fuel=1,
            lightsandappliance__clothes_dryer_energy_factor=3.01,
            percent_improvement=0.21,
            company=cls.rater_company,
        )

        assert simulation.results.udrh_percent_improvement > 0.20, (
            "Percent improvement %.2f" % simulation.results.udrh_percent_improvement
        )
        # print("Percent improvement %.2f" % simulation.results.udrh_percent_improvement)

        cls.floorplan = floorplan_with_remrate_factory(
            owner=cls.rater_company,
            remrate_target=simulation,
            subdivision__builder_org=cls.builder_company,
            subdivision__city=cls.city,
            subdivision__name="SubdivisionName",
        )

        from axis.remrate_data.models import Simulation
        from axis.floorplan.models import Floorplan

        assert Simulation.objects.count() == 2, "Simulation count"
        assert Floorplan.objects.count() == 1, "Floorplan count"

        cls.home = home_factory(subdivision=cls.floorplan.subdivision_set.first(), city=cls.city)

        cls.non_eto_eep_program = basic_eep_program_factory(
            slug="non_eto_eep_program", no_close_dates=True
        )


class ETOModelTests(ETO2018ProgramTestMixin, AxisTestCase):
    def test_auto_relationship_create(self):
        """Test to make sure that the relationships get automatically created"""
        stat = EEPProgramHomeStatus.objects.create(
            home=self.home, company=self.rater_company, eep_program=self.eep_program
        )
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertIn(self.eto, companies)
        self.assertIn(self.qa, companies)
        self.assertIn(self.peci, companies)

    def test_auto_relationship_change_add(self):
        """Test to make sure when the ETO program gets added via change that it also triggers"""
        stat = EEPProgramHomeStatus.objects.create(
            home=self.home,
            company=self.rater_company,
            eep_program=self.non_eto_eep_program,
        )
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertNotIn(self.eto, companies)
        self.assertNotIn(self.qa, companies)
        self.assertNotIn(self.peci, companies)

        stat.eep_program = self.eep_program
        stat.save()
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertIn(self.eto, companies)
        self.assertIn(self.qa, companies)
        self.assertIn(self.peci, companies)

    def test_auto_relationship_change_delete_non_complete(self):
        """Test to make sure when the ETO program gets deleted without the home being complete
        then that triggers a full relationship delete"""
        stat = EEPProgramHomeStatus.objects.create(
            home=self.home, company=self.rater_company, eep_program=self.eep_program
        )
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertIn(self.eto, companies)
        self.assertIn(self.qa, companies)
        self.assertIn(self.peci, companies)

        stat.eep_program = self.non_eto_eep_program
        stat.save()
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertNotIn(self.eto, companies)
        self.assertNotIn(self.qa, companies)
        self.assertNotIn(self.peci, companies)

    def test_auto_relationship_change_delete_complete(self):
        """Test to make sure that when an ETO Program gets added and then completed the best you
        can do is hide the relationship.  We do this because of incentives.."""
        stat = EEPProgramHomeStatus.objects.create(
            home=self.home,
            company=self.rater_company,
            floorplan=self.floorplan,
            eep_program=self.eep_program,
        )
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertIn(self.eto, companies)
        self.assertIn(self.qa, companies)
        self.assertIn(self.peci, companies)

        # This is pure hi-jack
        stat.state = "complete"
        stat.pct_complete = 100
        stat.certification_date = now()
        stat.save()

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        # This home was certified - we don't ever remove the relationship.
        self.assertIn(self.eto, companies)
        self.assertIn(self.qa, companies)
        self.assertIn(self.peci, companies)

    def test_auto_relationship_delete(self):
        """Test to make sure when we delete it we also remove it.."""
        stat = EEPProgramHomeStatus.objects.create(
            home=self.home,
            company=self.rater_company,
            floorplan=self.floorplan,
            eep_program=self.eep_program,
        )
        create_or_update_spanning_relationships(None, stat)

        companies = Company.objects.filter(id__in=stat.home.relationships.all().values("company"))

        self.assertIn(self.eto, companies)
        self.assertIn(self.qa, companies)
        self.assertIn(self.peci, companies)

        stat.delete()
        create_or_update_spanning_relationships(None, self.home)

        companies = Company.objects.filter(id__in=self.home.relationships.all().values("company"))

        self.assertNotIn(self.eto, companies)
        self.assertNotIn(self.qa, companies)
        self.assertNotIn(self.peci, companies)

    def test_eto_account_alert_dont_send(self):
        # We already have an ETO Account so we will validate that it won't send a message.
        builder = self.home.get_builder()

        eto_account = builder.eto_account
        self.assertIsNotNone(eto_account.account_number)
        self.assertEqual(Message.objects.all().count(), 0)

        stat = EEPProgramHomeStatus.objects.create(
            home=self.home,
            company=self.rater_company,
            floorplan=self.floorplan,
            eep_program=self.eep_program,
        )
        create_or_update_spanning_relationships(None, stat)

        # Trigger the post save
        eto_account.save()
        self.assertEqual(Message.objects.all().count(), 0)

    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def test_eto_account_csg_alert_send(self, _mock):
        # We already have an ETO Account so we will validate that it won't send a message.
        builder = self.home.get_builder()

        eto_account = builder.eto_account
        self.assertIsNotNone(eto_account.account_number)
        self.assertEqual(Message.objects.all().count(), 0)

        stat = EEPProgramHomeStatus.objects.create(
            home=self.home,
            company=self.rater_company,
            floorplan=self.floorplan,
            eep_program=self.eep_program,
        )
        create_or_update_spanning_relationships(None, stat)

        stat.make_transition("inspection_transition")
        self.assertEqual(Message.objects.all().count(), 0)

        stat.make_transition("qa_transition")
        msg = "has been notified they are gating the certification"
        self.assertGreater(Message.objects.filter(content__icontains=msg).count(), 0)

        stat.make_transition("certification_transition")
        msg = "has advanced to inspected status"
        self.assertGreater(Message.objects.filter(content__icontains=msg).count(), 0)
        msg_count = Message.objects.all().count()

        stat.save()
        self.assertEqual(Message.objects.all().count(), msg_count)

        stat.make_transition("completion_transition")
        self.assertEqual(Message.objects.all().count(), msg_count)

    def test_eto_account_alert_send(self):
        # Get rid of the account number
        builder = self.home.get_builder()

        eto_account = builder.eto_account
        eto_account.delete()

        builder = self.home.get_builder()

        self.assertRaises(ETOAccount.DoesNotExist, lambda: builder.eto_account)
        self.assertEqual(Message.objects.all().count(), 0)

        stat = EEPProgramHomeStatus.objects.create(
            home=self.home,
            company=self.rater_company,
            floorplan=self.floorplan,
            eep_program=self.eep_program,
        )
        create_or_update_spanning_relationships(None, stat)

        # This will fire off a bunch of missing ETO account number alerts
        message_ids = list(Message.objects.all().values_list("id", flat=True))

        eto_account = ETOAccount.objects.create(company=builder, account_number="12345")

        messages = Message.objects.all().exclude(id__in=message_ids)

        msg = ETO_ACCOUNT_NUMBER_ADDED_BASE.format(company=eto_account.company)
        self.assertGreater(messages.filter(content__istartswith=msg).count(), 0)


class MockResponse:
    """Basic Response client"""

    def __call__(self, *args, **kwargs):
        pass

    def __init__(self, status_code, content):
        self.status_code = status_code
        self.raw = content
        self.content = self._content = "%s" % content

    def raise_for_status(self):
        return False

    def json(self):
        return {}


class ETOFastTrackTests(ETO2020ProgramTestMixin, CollectionRequestMixin, AxisTestCase):
    def setUp(self):
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.simulation = self.home_status.floorplan.simulation
        self.simulation.heaters.update(fuel=FuelType.NATURAL_GAS)
        self.simulation.hvac_distribution_systems.update(
            system_type=DistributionSystemType.FORCED_AIR
        )
        answers = {
            "is-adu": "Yes",
            "builder-payment-redirected": "No",
            "has-battery-storage": "No",
            "primary-heating-equipment-type": {
                "input": "Gas Furnace",
                "comment": "Something",
            },
            "inspection-notes": {"input": "Primary", "comment": "Something"},
            "has-gas-fireplace": {"input": None},
            "ets-annual-etsa-kwh": {"input": 10000},
            "grid-harmonization-elements": {"input": "Energy smart homes – Base package"},
            "eto-additional-incentives": {"input": "Solar elements"},
            "smart-thermostat-brand": {"input": "Ecobee4"},
            # Not required but needed for FT / EPS Reporiting
            "ceiling-r-value": {"input": "20"},
            "equipment-water-heater": {"input": {"brand_name": "foo"}},
            "equipment-furnace": {"input": {"brand_name": "foo"}},
            "solar-elements": {"input": "Solar Ready"},
        }
        self.add_bulk_answers(data=answers, home_status=self.home_status)

        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), set())

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    @mock.patch("requests.post", side_effect=mocked_post)
    @mock.patch(
        "axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response
    )
    def test_fasttracksubmision_storage(self, _mock, _mock2):
        """Test to make sure that we cover all of the basics."""

        self.assertEqual(FastTrackSubmission.objects.filter(project_id=None).count(), 0)
        status = EEPProgramHomeStatus.objects.get()

        try:
            self.assertEqual(status.is_eligible_for_certification(), True)
        except AssertionError:
            import pprint

            for k, v in status.get_progress_analysis()["requirements"].items():
                if v["status"] is False:
                    print(k)
                    pprint.pprint(v)
            raise

        self.assertEqual(status.is_eligible_for_certification(), True)

        rater_admin = self.get_admin_user(company_type="rater")
        self.assertEqual(
            status.can_user_certify(rater_admin, perform_eligiblity_check=False), False
        )

        provider_admin = self.user_model.objects.filter(
            company__slug="csg-qa", is_company_admin=True
        )[0]
        certify_single_home(
            provider_admin,
            status,
            datetime.datetime.today(),
            bypass_check=True,  # Skip Gating QA
        )

        doc = CustomerDocument.objects.get()
        self.assertIsNotNone(doc.filesize)
        self.assertIsNotNone(doc.description)
        self.assertIn("Final", doc.description)

        status = EEPProgramHomeStatus.objects.get(id=status.id)
        self.assertIsNotNone(status.certification_date)
        self.assertEqual(status.state, "complete")

        submit_fasttrack_xml(status.id)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)

        target = get_legacy_calculation_data(status, return_fastrack_data=True)
        ft = FastTrackSubmission.objects.get()

        for k, v in target.items():
            if k in ["version", "solar_project_id"]:
                continue
            if k == "eps_calculator_version":
                self.assertEqual(ft.eps_calculator_version, v)
                continue
            if k == "project_id":
                self.assertIsNotNone(
                    getattr(ft, k),
                )
                continue
            if k in [
                "homestatus_id",
                "state_abbreviation",
                "mode",
                "gas_utility",
                "electric_utility",
                "gas_hot_water",
                "electric_load_profile",
                "gas_load_profile",
                "estimated_annual_energy_costs_code",
                "estimated_monthly_energy_costs_code",
            ]:
                continue

            v = Decimal(round(v, 2)) if v is not None else v
            v2 = Decimal(round(getattr(ft, k), 2)) if getattr(ft, k) is not None else getattr(ft, k)
            self.assertEqual(round(v, 2), round(v2, 2))

        self.assertIsNotNone(ft.project_id)

    def test_estimated_annual_energy_savings_cost(self):
        with self.subTest("Normal"):
            ft = FastTrackSubmission.objects.get()
            ft.estimated_annual_energy_costs_code = Decimal("10.0")
            ft.estimated_annual_energy_costs = Decimal("5.0")
            self.assertEqual(ft.estimated_annual_energy_savings_cost, Decimal("5.0"))

        with self.subTest("Negative"):
            ft = FastTrackSubmission.objects.get()
            ft.estimated_annual_energy_costs_code = Decimal("5.0")
            ft.estimated_annual_energy_costs = Decimal("10.0")
            self.assertEqual(ft.estimated_annual_energy_savings_cost, Decimal("0.0"))

    def test_heat_type(self):
        with self.subTest("Gas"):
            data = {"primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE}
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            self.assertEqual(ft.heat_type, HeatType.GAS)

        with self.subTest("Ele"):
            data = {
                "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE
            }
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            self.assertEqual(ft.heat_type, HeatType.ELECTRIC)

    def test_heat_pump_allocation_pct(self):
        with self.subTest("No HPWH"):
            ft = FastTrackSubmission.objects.get()
            ft.heat_pump_water_heater_incentive = Decimal("0.0")
            self.assertEqual(ft._heat_pump_allocation_pct, Decimal("0.0"))
        with self.subTest("Has HPWH"):
            ft = FastTrackSubmission.objects.get()
            ft.heat_pump_water_heater_incentive = Decimal("-250.0")
            ft.builder_electric_incentive = Decimal("50.0")
            ft.builder_gas_incentive = Decimal("50.0")
            self.assertEqual(ft._heat_pump_allocation_pct, Decimal("0.5"))

    def test_builder_heat_pump_water_heater_electric_incentive(self):
        ft = FastTrackSubmission.objects.get()
        ft.heat_pump_water_heater_incentive = Decimal("-250.0")
        ft.builder_electric_incentive = Decimal("50.0")
        ft.builder_gas_incentive = Decimal("50.0")
        self.assertEqual(ft.builder_heat_pump_water_heater_electric_incentive, Decimal("-125.0"))

    def test_builder_heat_pump_water_heater_gas_incentive(self):
        ft = FastTrackSubmission.objects.get()
        ft.heat_pump_water_heater_incentive = Decimal("-250.0")
        ft.builder_electric_incentive = Decimal("50.0")
        ft.builder_gas_incentive = Decimal("50.0")
        self.assertEqual(ft.builder_heat_pump_water_heater_electric_incentive, Decimal("-125.0"))

    def test_builder_electric_baseline_incentive(self):
        with self.subTest("Gas"):
            data = {"primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE}
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.builder_electric_incentive = Decimal("100.0")
            ft.ev_ready_builder_incentive = Decimal("25.0")
            self.assertEqual(ft.builder_electric_baseline_incentive, Decimal("75.0"))

        with self.subTest("Ele"):
            data = {
                "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE
            }
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.builder_electric_incentive = Decimal("100.0")
            ft.ev_ready_builder_incentive = Decimal("10.0")
            ft.cobid_builder_incentive = Decimal("10.0")
            ft.triple_pane_window_incentive = Decimal("10.0")
            ft.rigid_insulation_incentive = Decimal("10.0")
            ft.sealed_attic_incentive = Decimal("10.0")
            self.assertEqual(ft.builder_electric_baseline_incentive, Decimal("50.0"))

    def test_builder_gas_baseline_incentive(self):
        with self.subTest("Gas"):
            data = {"primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE}
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.builder_gas_incentive = Decimal("100.0")
            ft.cobid_builder_incentive = Decimal("10.0")
            ft.triple_pane_window_incentive = Decimal("10.0")
            ft.rigid_insulation_incentive = Decimal("10.0")
            ft.sealed_attic_incentive = Decimal("10.0")
            self.assertEqual(ft.builder_gas_baseline_incentive, Decimal("60.0"))

        with self.subTest("Ele"):
            data = {
                "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE
            }

            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.builder_gas_incentive = Decimal("100.0")
            self.assertEqual(ft.builder_gas_baseline_incentive, Decimal("100.0"))

    def test_total_builder_sle_incentive(self):
        ft = FastTrackSubmission.objects.get()
        ft.net_zero_solar_incentive = Decimal("10.0")
        ft.solar_ready_builder_incentive = Decimal("10.0")
        ft.solar_storage_builder_incentive = Decimal("10.0")
        self.assertEqual(ft.total_builder_sle_incentive, Decimal("30.0"))

    def test_total_builder_incentive(self):
        ft = FastTrackSubmission.objects.get()
        ft.net_zero_solar_incentive = Decimal("10.0")
        self.assertEqual(
            ft.total_builder_incentive,
            ft.builder_gas_incentive
            + ft.builder_electric_incentive
            + ft.total_builder_sle_incentive,
        )

    def test_rater_electric_baseline_incentive(self):
        with self.subTest("Gas"):
            data = {"primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE}
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.rater_electric_incentive = Decimal("100.0")
            self.assertEqual(ft.rater_electric_baseline_incentive, Decimal("100.0"))

        with self.subTest("Ele"):
            data = {
                "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE
            }
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.rater_electric_incentive = Decimal("100.0")
            ft.cobid_verifier_incentive = Decimal("10.0")
            self.assertEqual(ft.rater_electric_baseline_incentive, Decimal("90.0"))

    def test_rater_gas_baseline_incentive(self):
        with self.subTest("Gas"):
            data = {"primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE}
            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.rater_gas_incentive = Decimal("100.0")
            ft.cobid_verifier_incentive = Decimal("10.0")
            self.assertEqual(ft.rater_gas_baseline_incentive, Decimal("90.0"))

        with self.subTest("Ele"):
            data = {
                "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE
            }

            self.add_bulk_answers(data=data, home_status=self.home_status, remove_prior=True)
            ft = FastTrackSubmission.objects.get()
            ft.rater_gas_incentive = Decimal("100.0")
            ft.cobid_verifier_incentive = Decimal("10.0")
            self.assertEqual(ft.rater_gas_baseline_incentive, Decimal("100.0"))

    def test_total_rater_sle_incentive(self):
        ft = FastTrackSubmission.objects.get()
        ft.solar_ready_verifier_incentive = Decimal("10.0")
        self.assertEqual(ft.total_rater_sle_incentive, Decimal("10.0"))

    def test_total_rater_incentive(self):
        ft = FastTrackSubmission.objects.get()
        ft.solar_ready_verifier_incentive = Decimal("10.0")
        self.assertEqual(
            ft.total_rater_incentive,
            ft.rater_electric_incentive + ft.rater_gas_incentive + ft.total_rater_sle_incentive,
        )
