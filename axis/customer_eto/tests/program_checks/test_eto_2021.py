"""test_eto_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 15:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random
import tempfile

import xmltodict
from PyPDF2 import PdfReader
from django.core import management

from axis.annotation.tests.test_mixins import AnnotationMixin
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
    rater_admin_factory,
    qa_admin_factory,
)
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.enumerations import (
    ClimateLocation,
    GasUtility,
    ElectricUtility,
    Fireplace2020,
    PNWUSStates,
    PrimaryHeatingEquipment2020,
    SolarElements2020,
    AdditionalIncentives2020,
    GridHarmonization2020,
    SmartThermostatBrands2020,
)
from axis.customer_eto.models import ETOAccount
from axis.customer_eto.strings import ETO_2021_CHECKSUMS
from axis.customer_eto.validations import get_eto_2021_simulation_validations
from axis.eep_program.models import EEPProgram
from axis.filehandling.models import CustomerDocument
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.geographic.tests.factories import real_city_factory, climate_zone_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import (
    home_factory,
    eep_program_custom_home_status_factory,
)
from axis.qa.models import QARequirement
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    HotWaterEfficiencyUnit,
    WaterHeaterLiquidVolume,
    DistributionSystemType,
    HeatingEfficiencyUnit,
    SourceType,
    ResidenceType,
    Location,
    FoundationType,
    AnalysisType,
    HeatingCoolingCapacityUnit,
    MechanicalVentilationType,
    VentilationRateUnit,
)
from simulation.models import Simulation

log = logging.getLogger(__name__)


class ETO2021ProgramTestMixin:
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
            company=cls.rater_company, account_number="123", ccb_number="95232"
        )

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        ETOAccount.objects.create(company=cls.builder_company, account_number="456")

        management.call_command(
            "build_program",
            "-p",
            "eto-2021",
            "--no_close_dates",
            "--warn_only",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-2021")

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

        cls.floorplan_factory_kwargs = dict(
            owner=cls.rater_company,
            use_udrh_simulation=True,
            simulation__pct_improvement=25.0,
            simulation__conditioned_area=2150.0,
            simulation__source_type=random.choice([SourceType.EKOTROPE, SourceType.REMRATE_SQL]),
            simulation__version="99.99.99",  # Works for both
            simulation__flavor="Rate",  # Works for both
            simulation__design_model=AnalysisType.OR_2020_ZONAL_DESIGN,
            simulation__reference_model=AnalysisType.OR_2020_ZONAL_REFERENCE,
            simulation__residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            simulation__frame_floor_count=1,
            simulation__frame_floor__exterior_location=Location.ENCLOSED_CRAWL,
            simulation__location__climate_zone__zone="4",
            simulation__location__climate_zone__moisture_regime="C",
            simulation__location__weather_station="Eugene, OR",
            simulation__analysis__source_qualifier=ETO_2021_CHECKSUMS[1][0],  # Zonal!
            simulation__analysis__source_name=ETO_2021_CHECKSUMS[1][1],  # Zonal!
            simulation__heater__fuel=FuelType.ELECTRIC,
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
            subdivision__builder_org=cls.builder_company,
            subdivision__city=cls.city,
            subdivision__name="Subdivision",
        )

        floorplan = floorplan_with_simulation_factory(**cls.floorplan_factory_kwargs)
        cls.simulation = floorplan.simulation

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

        # missing_checks = stat.report_eligibility_for_certification()
        # if missing_checks:
        #     print(
        #         "** Warning! Failing ETO-2020 Certification Eligibility Requirements:\n  - "
        #         + "\n  - ".join(missing_checks)
        #         + "\n** End Warning\n"
        #     )
        #
        #     questions = stat.get_unanswered_questions()
        #     measures = questions.values_list("measure", flat=True)
        #     if len(measures):
        #         print("Missing questions")
        #     for measure in measures:
        #         print(" * %s" % measure)

    @property
    def default_program_data(self):
        data = {
            "us_state": PNWUSStates.WA.value,
            "climate_location": ClimateLocation.PORTLAND.value,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_BOILER.value,
            "conditioned_area": 2500,
            "electric_utility": ElectricUtility.PACIFIC_POWER.value,
            "gas_utility": GasUtility.NW_NATURAL.value,
            "fireplace": Fireplace2020.FE_50_59.value,
            "code_heating_therms": 23.3,
            "code_heating_kwh": 1501.2,
            "code_cooling_kwh": 2503.6,
            "code_hot_water_therms": 25.2,
            "code_hot_water_kwh": 1025.2,
            "code_lights_and_appliance_therms": 5.2,
            "code_lights_and_appliance_kwh": 1975.2,
            "code_electric_cost": 32.1,
            "code_gas_cost": 8.1,
            "improved_heating_therms": 23.3,
            "improved_heating_kwh": 1501.2,
            "improved_cooling_kwh": 2503.6,
            "improved_hot_water_therms": 25.2,
            "improved_hot_water_kwh": 1025.2,
            "improved_lights_and_appliance_therms": 5.2,
            "improved_lights_and_appliance_kwh": 1975.2,
            "improved_pv_kwh": 5,
            "improved_solar_hot_water_therms": 2.1,
            "improved_solar_hot_water_kwh": 12.3,
            "improved_electric_cost": 32.1,
            "improved_gas_cost": 8.1,
        }
        return data.copy()


class ETO2021ProgramCompleteTestMixin(ETO2021ProgramTestMixin):
    """This provide a complete ready for certification test"""

    @classmethod
    def setUpTestData(cls):
        super(ETO2021ProgramCompleteTestMixin, cls).setUpTestData()

        collection_request = CollectionRequestMixin()
        answers = {
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            "smart-thermostat-brand": SmartThermostatBrands2020.BRYANT,
            "has-gas-fireplace": Fireplace2020.FE_60_69,
            "grid-harmonization-elements": GridHarmonization2020.ALL,
            "eto-additional-incentives": AdditionalIncentives2020.ENERGY_SMART,
            "solar-elements": SolarElements2020.SOLAR_PV,
            "ets-annual-etsa-kwh": 2000,
            "is-adu": "No",
            "builder-payment-redirected": "No",
            "has-battery-storage": "No",
            "ceiling-r-value": 32,
            "equipment-heating-other-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            "equipment-heating-other-brand": "Lame Brand",
            "equipment-heating-other-model-number": "XYZ",
            "equipment-water-heater": {"brand": "Brand", "model": "Model"},
            "equipment-dishwasher": {"brand": "Brand", "model": "Model"},
        }
        collection_request.add_bulk_answers(answers, home_status=cls.home_status)
        annotation = AnnotationMixin()
        annotation.add_annotation(
            content="foo", type_slug="hpxml_gbr_id", content_object=cls.home_status
        )


class ETO2021ProgramChecks(
    ETO2021ProgramCompleteTestMixin,
    CollectionRequestMixin,
    AnnotationMixin,
    AxisTestCase,
):
    """ETO 2021 Program Checks"""

    def test_missing_required_checklist_status(self):
        """Verify that you fail if you are missing required questions"""
        missing_checks = self.home_status.report_eligibility_for_certification()

        # unanswered = list(self.home_status.get_unanswered_questions().values_list('measure', flat=True))
        # print(unanswered)

        self.assertEqual(len(missing_checks), 0, missing_checks)

        self.remove_collected_input(measure_id="is-adu", home_status=self.home_status)

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)

    def test_get_eto_builder_incentive_status(self):
        """Verify that you fail if you are missing simulation"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        Floorplan.objects.all().update(simulation=None)

        home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        result = home_status.eep_program.get_eto_builder_incentive_status(home_status, "foo")
        self.assertFalse(result.status)
        self.assertIn("Unable to run Calculator", result.message)

        missing_checks = home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 2)
        self.assertEqual(
            {"Missing Simulation Data", "Unable to run Calculator"}, set(missing_checks)
        )

    def test_get_simulation_electric_utility_status(self):
        """Verify that if we have electricity in our sim we have an electric provider"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.assertIn(FuelType.ELECTRIC, self.simulation.get_fuels_used())
        Relationship.objects.filter(company=self.pac_pwr).delete()

        home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        result = home_status.get_simulation_electric_utility_status("foo")
        self.assertFalse(result.status)
        self.assertIn("Simulation data uses electricity", result.message)

        missing_checks = home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Simulation data uses electricity", missing_checks[0])

    def test_get_simulation_gas_utility_status(self):
        """Verify that if we have electricity in our sim we have an electric provider"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.water_heaters.update(fuel=FuelType.NATURAL_GAS)
        self.simulation.refresh_from_db()
        self.assertIn(FuelType.NATURAL_GAS, self.simulation.get_fuels_used())

        Relationship.objects.filter(company=self.nw_nat).delete()

        home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        result = home_status.get_simulation_gas_utility_status("foo")
        self.assertFalse(result.status)

        self.add_collected_input(
            measure_id="equipment-gas-tank-water-heater-serial-number", value="X"
        )

        missing_checks = home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Simulation data uses natural gas", missing_checks[0])

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

    def test_get_eto_2021_analysis_type_check(self):
        """This verifies the right UHRH was used.  Not needed for Ekotrope"""
        self.simulation.source_type = SourceType.REMRATE_SQL
        self.simulation.analyses.update(source_name="FOOBAR")
        self.simulation.save()

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated", missing_checks[0])

        self.simulation.analyses.update(source_name=ETO_2021_CHECKSUMS[1][1])
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.analyses.update(source_qualifier="FOOBAR")
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated with as built home", missing_checks[0])

    def test_get_floorplan_simulation_error_status(self):
        # Flesh out the chain
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        # Drill into the test
        result = self.home_status.get_floorplan_simulation_error_status()
        self.assertTrue(result.status)
        # Drill into the actual validations
        result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
        self.assertEqual(result["errors"], [])

        ventilation = self.simulation.mechanical_ventilation_systems.get()
        initial = ventilation.type
        ventilation.type = MechanicalVentilationType.AIR_CYCLER
        ventilation.save()
        self.simulation.refresh_from_db()
        with self.subTest("Air Cycler cannot exist"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("may not be Air Cycler", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        ventilation.type = initial
        ventilation.save()
        self.simulation.refresh_from_db()

        initial = self.simulation.bedroom_count
        self.simulation.bedroom_count = 1000
        self.simulation.save()
        # Cached Properties need to be fully pulled.
        self.simulation = Simulation.objects.get(id=self.simulation.id)
        with self.subTest("ASHRAE Failing"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("meet ASHRAE 62.2 2010", result["errors"][0])
            self.home_status = EEPProgramHomeStatus.objects.get()
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        self.simulation.bedroom_count = initial
        self.simulation.save()
        # Cached Properties need to be fully pulled.
        self.simulation = Simulation.objects.get(id=self.simulation.id)

        ventilation = self.simulation.mechanical_ventilation_systems.get()
        initial = ventilation.hour_per_day
        ventilation.hour_per_day = 23.9
        ventilation.save()
        self.simulation.refresh_from_db()
        with self.subTest("Ventilation Rate"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("must be 24hr/day", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        ventilation.hour_per_day = initial
        ventilation.save()
        self.simulation.refresh_from_db()

        initial = self.simulation.residence_type
        self.simulation.residence_type = ResidenceType.DUPLEX_WHOLE
        self.simulation.save()
        self.simulation.refresh_from_db()
        with self.subTest("Residence Type"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("Single family detached", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.simulation.residence_type = initial
        self.simulation.save()
        self.simulation.refresh_from_db()

        initial = self.simulation.foundation_type
        self.simulation.foundation_type = FoundationType.CONDITIONED_CRAWL_SPACE
        self.simulation.save()
        self.simulation.refresh_from_db()
        with self.subTest("Conditioned Crawlspaces"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("Conditioned Crawlspaces is not allowed", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        self.simulation.foundation_type = initial
        self.simulation.save()
        self.simulation.refresh_from_db()

        appliances = self.simulation.appliances
        initial = appliances.refrigerator_location
        appliances.refrigerator_location = Location.UNCONDITIONED_SPACE
        appliances.save()
        self.simulation.refresh_from_db()
        with self.subTest("Refrigerator Location"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("Refrigerator location must be conditioned", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        appliances.refrigerator_location = initial
        appliances.save()
        self.simulation.refresh_from_db()

        initial = appliances.clothes_dryer_location
        appliances.clothes_dryer_location = Location.UNCONDITIONED_SPACE
        appliances.save()
        self.simulation.refresh_from_db()
        with self.subTest("Dryer Location"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("Clothes dryer location must be conditioned", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        appliances.clothes_dryer_location = initial
        appliances.save()
        self.simulation.refresh_from_db()

        initial = self.simulation.location.climate_zone
        cz = climate_zone_factory(zone="99")
        self.simulation.location.climate_zone = cz
        self.simulation.location.save()
        self.simulation.refresh_from_db()
        with self.subTest("Climate Zone"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("Climate zone does not match home", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        self.simulation.location.climate_zone = initial
        cz.delete()
        self.simulation.location.save()
        self.simulation.refresh_from_db()

        utility_rate = self.simulation.utility_rates.filter(fuel=FuelType.NATURAL_GAS).last()
        initial = utility_rate.name
        utility_rate.name = "FOO"
        utility_rate.save()
        self.simulation.refresh_from_db()
        with self.subTest("Gas Company"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn(
                "AXIS gas utility must match EPS simulation library utility",
                result["errors"][0],
            )
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        utility_rate.name = initial
        utility_rate.save()
        self.simulation.refresh_from_db()

        utility_rate = self.simulation.utility_rates.filter(fuel=FuelType.ELECTRIC).last()
        initial = utility_rate.name
        utility_rate.name = "FOO"
        utility_rate.save()
        self.simulation.refresh_from_db()
        with self.subTest("Electric Company"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn(
                "AXIS electric utility must match EPS simulation library utility",
                result["errors"][0],
            )
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
        utility_rate.name = initial
        utility_rate.save()
        self.simulation.refresh_from_db()

        # Intentionally last
        self.simulation.mechanical_ventilation_systems.all().delete()
        self.simulation.refresh_from_db()
        with self.subTest("No Mechanical Ventilation"):
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 2)
            self.assertIn(
                "Mechanical ventilation system should exist",
                " ".join(result["errors"]),
            )
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)

    def test_get_floorplan_simulation_warning_status(self):
        result = self.home_status.get_floorplan_simulation_warning_status()
        self.assertTrue(result.status)
        # Drill into the test
        result = self.home_status.get_floorplan_simulation_error_status()
        self.assertTrue(result.status)
        # Drill into the actual validations
        result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
        self.assertEqual(result["warnings"], [])

        appliances = self.simulation.appliances
        initial = appliances.refrigerator_location
        appliances.refrigerator_location = Location.UNKNOWN
        appliances.save()
        with self.subTest("Refrigerator Location"):
            self.simulation.refresh_from_db()
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("Refrigerator location cannot be verified", result["warnings"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 0)
            self.home_status.refresh_from_db()
            result = self.home_status.get_floorplan_simulation_warning_status()
            self.assertEqual(result.status, None)
            self.assertIn("Simulation data mismatch", result.message)
        appliances.refrigerator_location = initial
        appliances.save()
        self.simulation.refresh_from_db()

        initial = appliances.clothes_dryer_location
        appliances.clothes_dryer_location = Location.UNKNOWN
        appliances.save()
        with self.subTest("Clothes Dryer Location"):
            self.simulation.refresh_from_db()
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("Clothes dryer location cannot be verified", result["warnings"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 0)
            self.home_status.refresh_from_db()
            result = self.home_status.get_floorplan_simulation_warning_status()
            self.assertEqual(result.status, None)
            self.assertIn("Simulation data mismatch", result.message)
        appliances.clothes_dryer_location = initial
        appliances.save()
        self.simulation.refresh_from_db()

        self.remove_collected_input(
            measure_id="primary-heating-equipment-type", home_status=self.home_status
        )
        initial = appliances.oven_fuel
        appliances.oven_fuel = FuelType.NATURAL_GAS
        appliances.save()
        self.simulation.refresh_from_db()
        with self.subTest("Gas Heaters"):
            self.add_collected_input(
                measure_id="primary-heating-equipment-type",
                value=PrimaryHeatingEquipment2020.GAS_FURNACE.value,
                home_status=self.home_status,
            )
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("no Gas Heaters exist in simulation", result["warnings"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
            self.assertIn("does not align checklist answer", missing_checks[0])
            self.home_status.refresh_from_db()
            result = self.home_status.get_floorplan_simulation_warning_status()
            self.assertEqual(result.status, None)
            self.assertIn("Simulation data mismatch", result.message)

        appliances.oven_fuel = initial
        appliances.save()
        self.remove_collected_input(
            measure_id="primary-heating-equipment-type", home_status=self.home_status
        )
        with self.subTest("ASHP"):
            self.add_collected_input(
                measure_id="primary-heating-equipment-type",
                value=PrimaryHeatingEquipment2020.DUCTED_ASHP.value,
                home_status=self.home_status,
            )
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("no ASHP's exist in simulation", result["warnings"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 0)
            self.home_status.refresh_from_db()
            result = self.home_status.get_floorplan_simulation_warning_status()
            self.assertEqual(result.status, None)
            self.assertIn("Simulation data mismatch", result.message)

        self.remove_collected_input(
            measure_id="primary-heating-equipment-type", home_status=self.home_status
        )
        with self.subTest("GSHP"):
            self.add_collected_input(
                measure_id="primary-heating-equipment-type",
                value=PrimaryHeatingEquipment2020.GSHP.value,
                home_status=self.home_status,
            )
            result = get_eto_2021_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("no GSHP's exist in simulation", result["warnings"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 0)
            self.home_status.refresh_from_db()
            result = self.home_status.get_floorplan_simulation_warning_status()
            self.assertEqual(result.status, None)
            self.assertIn("Simulation data mismatch", result.message)

    def test_get_eto_revised_primary_heating_fuel_type(self):
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        heater = self.simulation.heaters.all().get()
        initial = heater.fuel
        heater.fuel = FuelType.ELECTRIC
        heater.save()

        self.simulation.refresh_from_db()
        with self.subTest("Gas Fuel"):
            self.add_collected_input(
                measure_id="primary-heating-equipment-type",
                value=PrimaryHeatingEquipment2020.OTHER_GAS.value,
                home_status=self.home_status,
            )
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
            self.assertIn(
                "Primary heating fuel 'Electric' does not align checklist",
                missing_checks[0],
            )

        heater.fuel = initial
        heater.save()

        self.remove_collected_input(
            measure_id="primary-heating-equipment-type", home_status=self.home_status
        )

        heater.fuel = FuelType.NATURAL_GAS
        heater.save()

        # Cached dominant heating equipment
        self.home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)

        with self.subTest("Electric Fuel"):
            self.add_collected_input(
                measure_id="primary-heating-equipment-type",
                value=PrimaryHeatingEquipment2020.OTHER_ELECTRIC.value,
                home_status=self.home_status,
            )
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
            self.assertIn(
                "Primary heating fuel 'Natural gas' does not align checklist",
                missing_checks[0],
            )

    def test_get_simulation_udrh_check(self):
        """Test to make sure we fail our checksum checks"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

        self.simulation.source_type = SourceType.REMRATE_SQL
        self.simulation.save()
        self.simulation.refresh_from_db()

        initial = self.simulation.analyses.first().source_name
        self.simulation.analyses.update(source_name="foo")
        self.home_status.refresh_from_db()
        with self.subTest("Source Names (UDRH Filename)"):
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
            self.assertIn("Incorrect UDRH associated to checksum", missing_checks[0])

        self.simulation.analyses.update(source_name=initial)
        self.simulation.refresh_from_db()

        self.simulation.analyses.update(source_qualifier="foobar")
        self.home_status.refresh_from_db()
        with self.subTest("Source Names (Checksum)"):
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
            self.assertIn("Incorrect UDRH associated with as built home", missing_checks[0])

        self.simulation.analyses.update(source_qualifier="C8A062FC")
        self.home_status.refresh_from_db()
        with self.subTest("Source Names (Checksum mismatch)"):
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)
            self.assertIn(
                "Incorrect UDRH checksum associated with OR Perf Path",
                missing_checks[0],
            )

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

    def test_generate_project_tracker_data(self):
        """Test that we can generate an project tracker report"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        with self.subTest("Home Based"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
            management.call_command(
                "generate_project_tracker_xml",
                "--home",
                self.home_status.home.id,
                "--user",
                self.provider_user.username,
                "--filename",
                filename.name,
                stdout=DevNull(),
            )

            with open(filename.name) as fh:
                data = fh.read()
            data = xmltodict.parse(data)
            self.assertEqual(set(data.keys()), {"soap:Envelope"})

        with self.subTest("Home Status Based"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
            management.call_command(
                "generate_project_tracker_xml",
                "--home-status",
                self.home_status.id,
                "--user",
                self.provider_user.id,
                "--filename",
                filename.name,
                stdout=DevNull(),
            )
            with open(filename.name) as fh:
                data = fh.read()
            data = xmltodict.parse(data)
            self.assertEqual(set(data.keys()), {"soap:Envelope"})

    def test_generate_eps_report(self):
        """Test that we can generate an eps report"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        self.home_status.state = "complete"
        self.home_status.save()

        with self.subTest("With Store"):
            management.call_command(
                "generate_eto_report",
                "--home-status",
                self.home_status.id,
                "--store",
                stdout=DevNull(),
            )
            doc = CustomerDocument.objects.get()
            self.assertIsNotNone(doc.filesize)
            self.assertIsNotNone(doc.description)
            self.assertIsNotNone(doc.filename)
            document = PdfReader(doc.document)
            self.assertEqual(document.metadata["/Author"], "Pivotal Energy Solutions")
            self.assertEqual(len(document.pages), 2)
            self.assertIsNone(document.get_fields())

        with self.subTest("Home Based"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            management.call_command(
                "generate_eto_report",
                "--home",
                self.home_status.home.id,
                "--user",
                self.provider_user.username,
                "--filename",
                filename,
                stdout=DevNull(),
            )
            with open(filename, "rb") as fh:
                document = PdfReader(fh)
                self.assertEqual(document.metadata["/Author"], str(self.provider_user))
                self.assertEqual(len(document.pages), 2)
                self.assertIsNone(document.get_fields())

        with self.subTest("Home Status Based"):
            filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
            management.call_command(
                "generate_eto_report",
                "--home-status",
                self.home_status.id,
                "--user",
                self.provider_user.id,
                "--filename",
                filename,
                stdout=DevNull(),
            )
            with open(filename, "rb") as fh:
                document = PdfReader(fh)
                self.assertEqual(document.metadata["/Author"], str(self.provider_user))
                self.assertEqual(len(document.pages), 2)
                self.assertIsNone(document.get_fields())
