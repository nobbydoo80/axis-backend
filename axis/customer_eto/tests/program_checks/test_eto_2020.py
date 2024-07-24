__author__ = "Steven K"
__date__ = "12/17/2019 14:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random
from unittest.mock import patch

from django.core import management

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.tests.factories import (
    eep_organization_factory,
    provider_organization_factory,
    utility_organization_factory,
    rater_organization_factory,
    builder_organization_factory,
    qa_organization_factory,
)
from axis.core.tests.factories import (
    provider_admin_factory,
    qa_admin_factory,
    rater_admin_factory,
)
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.calculator.eps import ETO_2020_FUEL_RATES
from axis.eep_program.models import EEPProgram
from axis.floorplan.tests.factories import (
    floorplan_with_simulation_factory,
    floorplan_with_remrate_factory,
)
from axis.geographic.tests.factories import climate_zone_factory, real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import (
    home_factory,
    eep_program_custom_home_status_factory,
)
from axis.home.utils import get_eps_data
from axis.qa.models import QARequirement
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    HotWaterEfficiencyUnit,
    WaterHeaterLiquidVolume,
    DistributionSystemType,
    CoolingEfficiencyUnit,
    CoolingSystemType,
    SourceType,
    Location,
    MechanicalVentilationType,
    ResidenceType,
    FoundationType,
    HeatingEfficiencyUnit,
    VentilationRateUnit,
    AnalysisType,
    HeatingCoolingCapacityUnit,
    Color,
    InfiltrationUnit,
)
from simulation.tests.factories import mechanical_equipment_factory, slab_factory
from ...models import ETOAccount
from ...strings import ETO_2020_CHECKSUMS

log = logging.getLogger(__name__)


def get_completion_requirements(self):
    return [
        self.get_floorplan_simulation_error_status,
        self.get_floorplan_simulation_warning_status,
        self.eep_program.get_min_max_simulation_version,
        self.eep_program.get_simulation_udrh_check,
        self.eep_program.get_eto_approved_utility_electric_utility,
        self.eep_program.get_eto_approved_utility_gas_utility,
        self.eep_program.get_eto_gas_heated_utility_check,
        self.eep_program.get_eto_electric_heated_utility_check,
    ]


def get_completion_requirements_question_only(self):
    return [self.get_required_questions_remaining_status]


class ETO2020ProgramTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")

        cls.eto = eep_organization_factory(slug="eto", is_customer=True, name="ETO", city=cls.city)

        cls.peci = provider_organization_factory(
            slug="peci", is_customer=True, name="EPS New Construction", city=cls.city
        )
        cls.provider_user = provider_admin_factory(company=cls.peci, username="eto_provider_admin")

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
        rater_admin_factory(company=cls.rater_company, username="eto_rater_admin")
        cls.rater_eto_account = ETOAccount.objects.create(
            company=cls.rater_company, account_number="123", ccb_number="828x82"
        )

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        ETOAccount.objects.create(company=cls.builder_company, account_number="456")

        management.call_command(
            "build_program",
            "-p",
            "eto-2020",
            "--no_close_dates",
            "--warn_only",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-2020")
        EEPProgram.objects.filter(id=cls.eep_program.id).update(
            program_close_date=None,
            program_submit_date=None,
            program_end_date=None,
        )
        cls.eep_program.certifiable_by.add(cls.peci)

        cls.qa = qa_organization_factory(slug="csg-qa", is_customer=True, name="CSG", city=cls.city)
        qa_admin_factory(company=cls.qa, username="eto_qa_admin")
        QARequirement.objects.get_or_create(
            qa_company=cls.qa,
            coverage_pct=1,
            gate_certification=True,
            eep_program=cls.eep_program,
        )

        companies = [
            cls.eto,
            cls.peci,
            cls.rater_company,
            cls.qa,
            cls.builder_company,
            cls.pac_pwr,
            cls.nw_nat,
        ]

        Relationship.objects.create_mutual_relationships(*companies)

        basement_location = Location.CONDITIONED_BASEMENT
        cls.floorplan_factory_kwargs = dict(
            owner=cls.rater_company,
            use_udrh_simulation=True,
            simulation__pct_improvement=21.0,
            simulation__conditioned_area=2150.0,
            simulation__source_type=random.choice([SourceType.EKOTROPE, SourceType.REMRATE_SQL]),
            simulation__version="99.99.99",  # Works for both
            simulation__flavor="Rate",  # Works for both
            simulation__design_model=AnalysisType.OR_2020_ZONAL_DESIGN,
            simulation__reference_model=AnalysisType.OR_2020_ZONAL_REFERENCE,
            simulation__residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            simulation__infiltration__infiltration_unit=InfiltrationUnit.ACH50,
            simulation__location__climate_zone__zone="4",
            simulation__location__climate_zone__moisture_regime="C",
            simulation__location__weather_station="Eugene",
            simulation__location__us_state="OR",
            simulation__analysis__source_qualifier=ETO_2020_CHECKSUMS[1][0],  # Zonal!
            simulation__analysis__source_name=ETO_2020_CHECKSUMS[1][1],  # Zonal!
            simulation__heater__fuel=FuelType.NATURAL_GAS,
            simulation__heater__efficiency_unit=HeatingEfficiencyUnit.AFUE,
            simulation__heater__capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            simulation__water_heater__style=WaterHeaterStyle.CONVENTIONAL,
            simulation__water_heater__fuel=FuelType.ELECTRIC,
            simulation__water_heater__efficiency=0.92,
            simulation__water_heater__efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
            simulation__water_heater__tank_units=WaterHeaterLiquidVolume.GALLON,
            simulation__mechanical_ventilation__type=MechanicalVentilationType.SUPPLY_ONLY,
            simulation__mechanical_ventilation__hour_per_day=24.0,
            simulation__mechanical_ventilation__ventilation_rate=3500.0,
            simulation__mechanical_ventilation__ventilation_rate_unit=VentilationRateUnit.CFM,
            simulation__distribution_system__system_type=DistributionSystemType.RADIANT,
            simulation__distribution_system__location=Location.CONDITIONED_SPACE,
            simulation__appliances__refrigerator_consumption=700,
            simulation__appliances__refrigerator_location=Location.CONDITIONED_SPACE,
            simulation__appliances__dishwasher_consumption=300,
            simulation__appliances__clothes_washer_efficiency=0.5,
            simulation__appliances__clothes_washer_label_electric_consumption=500,
            simulation__appliances__clothes_dryer_efficiency=2.5,
            simulation__appliances__clothes_dryer_location=Location.CONDITIONED_SPACE,
            simulation__appliances__clothes_dryer_fuel=FuelType.ELECTRIC,
            simulation__appliances__oven_fuel=FuelType.ELECTRIC,
            simulation__air_conditioner_count=0,
            simulation__utility_rate_fuel__electric={"name": "PAC-Jan2021"},
            simulation__utility_rate_fuel__natural_gas={"name": "NWN_OR-Jan2021"},
            simulation__frame_floor_count=1,
            simulation__frame_floor__exterior_location=basement_location,
            simulation__foundation_wall_count=1,
            simulation__foundation_wall__interior_location=basement_location,
            # The HPXML serializer can't handle roofs with adiabatic interior location
            simulation__roof__interior_location=random.choice(
                [l for l in Location.roof_interior() if l != Location.ADIABATIC]
            ),
            # The HPXML serializer can't handle roofs with the STD_140 colors
            simulation__roof__exterior_color=random.choice(
                [c for c in Color.roof() if c not in [Color.STD140, Color.STD140_LOWABS]]
            ),
            subdivision__builder_org=cls.builder_company,
            subdivision__city=cls.city,
            subdivision__name="Subdivision",
        )

        floorplan = floorplan_with_simulation_factory(**cls.floorplan_factory_kwargs)

        assert str(floorplan.simulation.location.climate_zone) == "4C"
        assert str(floorplan.simulation.climate_zone) == "4C"
        home = home_factory(
            subdivision=floorplan.subdivision_set.first(), city=cls.city, zipcode=97229
        )
        cls.home_status = eep_program_custom_home_status_factory(
            home=home,
            floorplan=floorplan,
            eep_program=cls.eep_program,
            company=cls.rater_company,
        )

        rel_ele = create_or_update_spanning_relationships(cls.pac_pwr, cls.home_status.home)[0][0]
        rel_gas = create_or_update_spanning_relationships(cls.nw_nat, cls.home_status.home)[0][0]
        create_or_update_spanning_relationships(cls.qa, cls.home_status.home)
        create_or_update_spanning_relationships(cls.peci, cls.home_status.home)

        home._generate_utility_type_hints(rel_gas, rel_ele)

        assert cls.home_status.get_electric_company().id == cls.pac_pwr.pk
        assert cls.home_status.get_gas_company().id == cls.nw_nat.pk


class ETO2020ProgramSimulationRequiredQuestions(
    ETO2020ProgramTestMixin, CollectionRequestMixin, AxisTestCase
):
    """ETO 2020 Program Checks"""

    def setUp(self):
        method_to_patch = "axis.home.models.EEPProgramHomeStatus.get_completion_requirements"
        self.patcher = patch(method_to_patch, get_completion_requirements_question_only)
        self.mock_foo = self.patcher.start()
        self.addCleanup(self.patcher.stop)  # add this line
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)

        self.rem_simulation = self.home_status.floorplan.remrate_target
        self.simulation = self.home_status.floorplan.simulation

        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)

        expected = {
            "is-adu",
            "builder-payment-redirected",
            "eto-additional-incentives",
            "smart-thermostat-brand",
            "has-gas-fireplace",
            "has-battery-storage",
            "ceiling-r-value",
            "primary-heating-equipment-type",
            "equipment-water-heater",
            "inspection-notes",
            "equipment-heating-other-brand",
            "equipment-heating-other-type",
            "equipment-heating-other-model-number",
        }

        self.assertEqual(
            set(measures),
            expected,
            "SetUp - Initial expected is wrong {}".format(set(measures) - expected),
        )
        self.add_bulk_answers(data={k: "FOO" for k in expected}, home_status=self.home_status)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

    def test_simulation_with_heat_pumps(self):
        """
        Test the simulation checks that will add new questions
        """

        self.simulation.water_heaters.update(style=WaterHeaterStyle.AIR_SOURCE_HEAT_PUMP)
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-heat-pump-water-heater-serial-number"})

    def test_simulation_gas_forced_air_heaters(self):
        """
        Test the simulation checks that will add new questions
        """
        self.assertNotIn("equipment-furnace", self.get_answered_questions())
        self.simulation.heaters.update(fuel=FuelType.NATURAL_GAS)
        self.simulation.hvac_distribution_systems.update(
            system_type=DistributionSystemType.FORCED_AIR
        )
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertTrue(self.simulation.heaters.gas_forced_air().exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-furnace"})

    def test_simulation_conventional_natural_gas_water_heaters(self):
        """
        Test the simulation checks that will add new questions
        """
        self.assertNotIn(
            "equipment-gas-tank-water-heater-serial-number",
            self.get_answered_questions(),
        )
        self.simulation.water_heaters.update(
            fuel=FuelType.NATURAL_GAS, style=WaterHeaterStyle.CONVENTIONAL
        )
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-gas-tank-water-heater-serial-number"})

    def test_simulation_tankless_natural_gas_water_heaters(self):
        """
        Test the simulation checks that will add new questions
        """
        self.assertNotIn(
            "equipment-gas-tankless-water-heater-serial-number",
            self.get_answered_questions(),
        )
        self.simulation.water_heaters.update(
            fuel=FuelType.NATURAL_GAS, style=WaterHeaterStyle.TANKLESS
        )
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-gas-tankless-water-heater-serial-number"})

    def test_simulation_air_source_heat_pumps(self):
        """
        Test the simulation checks that will add new questions
        """
        self.assertNotIn("equipment-heat-pump", self.get_answered_questions())
        mechanical_equipment_factory(
            company=self.simulation.company,
            simulation=self.simulation,
            equipment_type="air_source_heat_pump",
        )
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-heat-pump"})

    def test_simulation_non_ashp_w_heater(self):
        """Heaters get three distinct questions"""

        self.simulation.mechanical_equipment.filter(heater__isnull=False).delete()
        non_ashp_questions = [
            "equipment-heating-other-type",
            "equipment-heating-other-brand",
            "equipment-heating-other-model-number",
        ]
        for question in non_ashp_questions:
            self.remove_collected_input(question)

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        mechanical = mechanical_equipment_factory(
            company=self.simulation.company,
            simulation=self.simulation,
            equipment_type="heater",
            fuel=FuelType.ELECTRIC,
        )
        self.simulation.hvac_distribution_systems.update(
            system_type=DistributionSystemType.RADIANT, heating_system=mechanical
        )

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), set(non_ashp_questions))

        self.simulation.heaters.update(fuel=FuelType.NATURAL_GAS)
        self.simulation.hvac_distribution_systems.update(
            system_type=DistributionSystemType.FORCED_AIR
        )
        self.add_collected_input("FOO", "equipment-furnace")

        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(
            self.home_status.floorplan.simulation.mechanical_equipment.non_air_source_heat_pump_heating().count(),
            0,
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), set())

    def test_simulation_non_ashp_w_gshp(self):
        """When we use a GSHP and no heater we should see these questions"""
        self.simulation.mechanical_equipment.filter(heater__isnull=False).delete()

        non_ashp_questions = [
            "equipment-heating-other-type",
            "equipment-heating-other-brand",
            "equipment-heating-other-model-number",
        ]
        for question in non_ashp_questions:
            self.remove_collected_input(question)

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        mechanical_equipment_factory(
            company=self.simulation.company,
            simulation=self.simulation,
            equipment_type="ground_source_heat_pump",
        )

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), set(non_ashp_questions))

    def test_air_conditioner_system_type(self):
        """
        Test the simulation checks that will add new questions
        """

        required_questions = [
            "equipment-air-conditioner-brand",
            "equipment-air-conditioner-model-number-outdoor",
            "equipment-air-conditioner-model-number-indoor",
        ]
        self.assertNotIn(set(required_questions), set(self.get_answered_questions()))
        self.assertFalse(self.simulation.air_conditioners.exists())

        mechanical_equipment_factory(
            company=self.simulation.company,
            simulation=self.simulation,
            equipment_type="air_conditioner",
            system_type=CoolingSystemType.AIR_CONDITIONER,
            efficiency_unit=CoolingEfficiencyUnit.SEER,
            efficiency=12.99,
        )

        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertTrue(self.home_status.floorplan.simulation.air_conditioners.exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        # All three must be satisfied.
        self.simulation.air_conditioners.update(efficiency=13.01)

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)

        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), set(required_questions))

    def test_mechanical_ventilation_systems_type(self):
        """
        Test the simulation checks that will add new questions
        """

        self.assertTrue(self.simulation.mechanical_ventilation_systems.exists())
        self.simulation.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.BALANCED
        )
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-ventilation-balanced"})

        self.simulation.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.EXHAUST_ONLY
        )
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-ventilation-exhaust"})

    def test_refrigerator_consumption(self):
        """
        Test the simulation checks that will add new questions
        """

        self.simulation.appliances.refrigerator_consumption = 690
        self.simulation.appliances.save()
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-refrigerator"})

    def test_dishwasher_consumption(self):
        """
        Test the simulation checks that will add new questions
        """

        self.simulation.appliances.dishwasher_consumption = 269
        self.simulation.appliances.save()
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-dishwasher"})

    def test_clothes_washer_efficiency(self):
        """
        Test the simulation checks that will add new questions
        """

        self.simulation.appliances.clothes_washer_efficiency = 0.808
        self.simulation.appliances.clothes_washer_label_electric_consumption = 486
        self.simulation.appliances.save()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-clothes-washer"})

    def test_clothes_dryer_efficiency(self):
        """
        Test the simulation checks that will add new questions
        """

        self.simulation.appliances.clothes_dryer_efficiency = 2.63
        self.simulation.appliances.save()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        questions = self.home_status.get_unanswered_questions()
        measures = questions.values_list("measure", flat=True)
        self.assertEqual(set(measures), {"equipment-clothes-dryer"})


class ETO2020ProgramChecks(ETO2020ProgramTestMixin, CollectionRequestMixin, AxisTestCase):
    """ETO 2020 Program Checks"""

    def setUp(self):
        method_to_patch = "axis.home.models.EEPProgramHomeStatus.get_completion_requirements"
        self.patcher = patch(method_to_patch, get_completion_requirements)
        self.mock_foo = self.patcher.start()
        self.addCleanup(self.patcher.stop)  # add this line
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        if missing_checks:
            msg = "Failing Certification Eligibility Requirements:\n  - "
            print(msg + "\n  - ".join(missing_checks))
        self.assertEqual(len(missing_checks), 0)
        self.rem_simulation = self.home_status.floorplan.remrate_target
        self.simulation = self.home_status.floorplan.simulation

    def test_get_min_simulation_version(self):
        """Tests that our minimum verision for Eko and REM work"""
        sim_v = random.choice([(SourceType.EKOTROPE, "3.0.0"), (SourceType.REMRATE_SQL, "15.7.1")])

        kwargs = {
            "simulation__source_type": sim_v[0],
            "simulation__version": sim_v[1],
            "simulation__flavor": "Rate",
            "simulation__all_electric": True,
        }
        floorplan = floorplan_with_simulation_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(id=self.home_status.id).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        self.assertIn(
            floorplan.simulation.source_type,
            [SourceType.REMRATE_SQL, SourceType.EKOTROPE],
        )

        result = self.home_status.eep_program.get_min_max_simulation_version(
            home_status, edit_url="foo"
        )
        self.assertTrue(result.status)

        floorplan.simulation.version = "0.0.0"
        floorplan.simulation.save()

        home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        result = self.home_status.eep_program.get_min_max_simulation_version(
            home_status, edit_url="foo"
        )
        self.assertFalse(result.status)
        self.assertIn("Simulation data must be REM >=", result.message)

    def test_get_eto_2020_analysis_type_check(self):
        """This verifies the right UHRH was used.  Not needed for Ekotrope"""
        self.simulation.source_type = SourceType.REMRATE_SQL
        self.simulation.analyses.update(source_name="FOOBAR")
        self.simulation.save()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated", missing_checks[0])

        self.simulation.analyses.update(source_name=ETO_2020_CHECKSUMS[1][1])
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.analyses.update(source_qualifier="FOOBAR")
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated with as built home", missing_checks[0])

    def test_get_eto_simulation_compare_fields_ventilation_exists(self):
        """Simulation Mechanical Ventilation System may not be "none"”"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        mechanical_ventilation = self.simulation.mechanical_ventilation_systems.get()
        mechanical_ventilation.delete()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("system should exist", missing_checks[0])

    def test_get_eto_remdata_compare_fields_ventilation_rate(self):
        """REM ventilation rate must equal to or > ASHRAE 62.2 2010:
        ((# of bdrms+1)*7.5)+(conditioned floor area*.01)”"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        mechanical_ventilation = self.simulation.mechanical_ventilation_systems.get()

        mechanical_ventilation.ventilation_rate = 24
        mechanical_ventilation.save()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertIn("ASHRAE 62.2 2010", missing_checks[0])

    def test_get_eto_approved_utility_rate_electric(self):
        """Validate electric fuel rate matches an approved list"""
        fuel_rates = dict(ETO_2020_FUEL_RATES)

        self.assertIsNotNone(self.home_status.get_electric_company())

        utility = self.home_status.get_electric_company()
        self.assertIsNotNone(fuel_rates.get(utility.slug))

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.assertEqual(utility.slug, "pacific-power")

        rem_utility = self.simulation.utility_rates.filter(fuel=FuelType.ELECTRIC).get()
        self.assertEqual(rem_utility.name, "PAC-Jan2021")

        utility.slug = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("is not an allowed Electric company", missing_checks[0])

    def test_get_eto_approved_utility_gas_utility(self):
        """Validate gas utility is in the list of ok'd utilities"""

        utility = self.home_status.get_gas_company()
        self.assertEqual(utility.slug, "nw-natural-gas")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        utility.slug = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("is not an allowed Gas company", missing_checks[0])

    def test_get_eto_approved_utility_electric_utility(self):
        """Validate electric utility is in the list of ok'd utilities"""

        utility = self.home_status.get_electric_company()
        self.assertEqual(utility.slug, "pacific-power")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        utility.slug = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("is not an allowed Electric company", missing_checks[0])

    def test_get_eto_simulation_compare_fields_cz(self):
        """Validate climate zone in Simulation – compare to AXIS climate zone"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        self.assertEqual(self.simulation.location.climate_zone.as_string(), "4C")

        new_cz = climate_zone_factory(zone="3", moisture_regime="A")
        self.simulation.location.climate_zone = new_cz

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Climate zone does not match home", missing_checks[0])

    def test_get_eto_simulation_compare_fields_housing_type(self):
        """Simulation residence type must be one of: Single family detached, duplex single unit,
        townhouse, end unit, or townhouse, inside unit"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        self.assertEqual(self.simulation.residence_type, ResidenceType.SINGLE_FAMILY_DETACHED)

        self.simulation.residence_type = ResidenceType.DUPLEX_WHOLE
        self.simulation.save()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Single family detached", missing_checks[0])

    def test_get_eto_simulation_compare_fields_foundation_type(self):
        """Simulation foundation type Conditioned Crawlspaces is not allowed"""
        slab_factory(simulation=self.simulation)
        self.simulation.save()

        self.simulation.frame_floors.all().delete()
        self.simulation.foundation_walls.all().delete()

        # Clear cache to ensure the foundation type is calculated afresh
        del self.simulation.foundation_type
        del self.simulation.basement_and_crawl_locations
        self.assertEqual(self.simulation.foundation_type, FoundationType.SLAB_ON_GRADE)

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.foundation_type = FoundationType.CONDITIONED_CRAWL_SPACE
        self.simulation.save()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Conditioned Crawlspaces", missing_checks[0])

    def test_get_eto_simulation_compare_fields_refrigerator_location(self):
        """Simulation refrigerator location must be "conditioned" """
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        appliances = self.simulation.appliances
        self.assertEqual(appliances.refrigerator_location, Location.CONDITIONED_SPACE)

        appliances.refrigerator_location = Location.UNCONDITIONED_SPACE
        appliances.save()

        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Refrigerator location must", missing_checks[0])

    def test_get_eto_simulation_compare_fields_clothes_dryer_location(self):
        """Simulation Clothes Dryer location must be "conditioned" """
        self.assertEqual(
            self.simulation.appliances.clothes_dryer_location,
            Location.CONDITIONED_SPACE,
        )
        appliances = self.simulation.appliances

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        appliances.clothes_dryer_location = Location.UNCONDITIONED_SPACE
        appliances.save()

        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Clothes dryer location must", missing_checks[0])

    def test_get_eto_simulation_compare_fields_mechanical_ventilation_exhaust_time(
        self,
    ):
        """If REM mechanical ventilation type is Exhaust only, then Hours/day must be 24"""
        mechanical_ventilation = self.simulation.mechanical_ventilation_systems.get()
        self.assertEqual(mechanical_ventilation.type, MechanicalVentilationType.SUPPLY_ONLY)
        self.assertEqual(mechanical_ventilation.hour_per_day, 24)

        mechanical_ventilation.type = MechanicalVentilationType.AIR_CYCLER
        mechanical_ventilation.save()

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertIn("ventilation may not be Air", missing_checks[0])

        mechanical_ventilation.type = MechanicalVentilationType.SUPPLY_ONLY
        mechanical_ventilation.hour_per_day = 23
        mechanical_ventilation.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("must be 24hr/day", missing_checks[0])

    def test_get_eto_gas_heated_utility_check(self):
        """Verify Gas Utility requirements based on checklist"""

        self.assertIsNotNone(self.home_status.get_gas_company())

        utility = self.home_status.get_gas_company()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        self.assertEqual(utility.slug, "nw-natural-gas")

        self.add_collected_input("gas furnace", "primary-heating-equipment-type")
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        utility.slug = "FOO"
        utility.save()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 2)
        self.assertIn(
            "Gas heated homes are only supported by NWN, CASCADE, or Avista",
            missing_checks,
        )

        self.home_status.home.relationships.filter(company=utility).delete()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Gas heated homes must have a gas utility.", missing_checks)

    def test_get_eto_electric_heated_utility_check(self):
        """Verify Electric Utility requirements based on checklist"""

        self.assertIsNotNone(self.home_status.get_gas_company())

        utility = self.home_status.get_electric_company()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.add_collected_input("electric stove", "primary-heating-equipment-type")
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        utility.slug = "FOO"
        utility.save()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 2)
        self.assertIn("Electrically heated homes are only supported by PAC or PGE", missing_checks)

        self.home_status.home.relationships.filter(company=utility).delete()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("You must have an electric utility.", missing_checks)

    def test_get_eto_percent_improvement_oregon_with_simulation(self):
        """
        Test that with a simulation we can actually get to a EPS Score
        """

        self.add_collected_input("Gas Furnace", "primary-heating-equipment-type")
        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug="eto-2020")

        kwargs = {
            "name": "New FP",
            "owner": home_status.company,
            "use_udrh_simulation": True,
            "simulation__source_type": random.choice([SourceType.REMRATE_SQL, SourceType.EKOTROPE]),
            "simulation__flavor": "Rate",
            "simulation__version": "99.99.99",
            "simulation__all_electric": True,
            "simulation__location__climate_zone__zone": "4",
            "simulation__location__climate_zone__moisture_regime": "C",
            "simulation__location__weather_station": "Eugene",
            "simulation__pct_improvement": 25.0,
        }
        floorplan = floorplan_with_simulation_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program__slug="eto-2020").update(
            floorplan=floorplan
        )

        self.assertIn(
            floorplan.simulation.source_type,
            [SourceType.REMRATE_SQL, SourceType.EKOTROPE],
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug="eto-2020")

        from axis.customer_eto.calculator.eps import get_eto_calculation_data
        from axis.customer_eto.forms import EPSCalculatorForm

        variables = get_eto_calculation_data(home_status)
        form = EPSCalculatorForm(variables)
        valid = form.is_valid()
        self.assertTrue(valid)

        from axis.customer_eto.calculator.eps import get_eto_calculation_completed_form

        calculation_form = get_eto_calculation_completed_form(home_status)
        self.assertTrue(calculation_form.is_valid())

        from ...reports.legacy_utils import get_legacy_calculation_data

        results = get_legacy_calculation_data(home_status, return_errors=True)
        self.assertNotIn("errors", results)

        data = get_eps_data(home_status)
        self.assertNotIn("errors", data)

        eep_program = home_status.eep_program
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertTrue(result.status)

    def test_get_eto_percent_improvement_oregon_with_remrate_sim(self):
        """
        Test that with a simulation we can actually get to a EPS Score
        """

        self.add_collected_input("Gas Furnace", "primary-heating-equipment-type")

        from axis.customer_eto.calculator.eps import get_eto_calculation_data
        from axis.customer_eto.forms import EPSCalculatorForm
        from axis.remrate_data.models import Simulation as RemSimulation
        from simulation.models import Simulation

        self.assertEqual(RemSimulation.objects.count(), 0)
        self.assertEqual(Simulation.objects.count(), 1)

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug="eto-2020")
        kwargs = {
            "owner": home_status.company,
            "use_udrh_simulation": True,
            "remrate_target__flavor": "Rate",
            "remrate_target__version": "99.99.99",
            "remrate_target__site__site_label": "Portland, OR",
            "remrate_target__udrh_filename": ETO_2020_CHECKSUMS[0][1],
            "remrate_target__udrh_checksum": ETO_2020_CHECKSUMS[0][0],
            "remrate_target__percent_improvement": 0.22,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(RemSimulation.objects.count(), 2)
        self.assertEqual(Simulation.objects.count(), 2)

        EEPProgramHomeStatus.objects.filter(eep_program__slug="eto-2020").update(
            floorplan=floorplan
        )

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug="eto-2020")

        self.assertEqual(RemSimulation.objects.count(), 2)
        self.assertEqual(Simulation.objects.count(), 2)

        variables = get_eto_calculation_data(home_status)
        form = EPSCalculatorForm(variables)
        valid = form.is_valid()
        try:
            self.assertTrue(valid)
        except AssertionError:
            print(form.errors)
            raise

        from axis.customer_eto.calculator.eps import get_eto_calculation_completed_form

        calculation_form = get_eto_calculation_completed_form(home_status)
        self.assertTrue(calculation_form.is_valid())

        from ...reports.legacy_utils import get_legacy_calculation_data

        results = get_legacy_calculation_data(home_status, return_errors=True)
        self.assertNotIn("errors", results)

        data = get_eps_data(home_status)
        self.assertNotIn("errors", data)

        eep_program = home_status.eep_program
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertTrue(result.status)
