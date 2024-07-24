"""test_eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "2/23/22 09:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random
import datetime

from django.core import management
from django.urls import reverse

from axis.customer_eto.validations import get_eto_2022_simulation_validations
from axis.filehandling.models import CustomerDocument
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import certify_single_home
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
    AnalysisType,
    HeatingCoolingCapacityUnit,
    MechanicalVentilationType,
    VentilationRateUnit,
    CoolingSystemType,
    CoolingEfficiencyUnit,
    MechanicalSystemType,
    CostUnit,
)
from simulation.tests.factories import (
    mechanical_equipment_factory,
    distribution_factory,
)

from axis.annotation.tests.test_mixins import AnnotationMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.tests.factories import (
    eep_organization_factory,
    builder_organization_factory,
    utility_organization_factory,
)
from axis.core.tests.factories import (
    provider_admin_factory,
    rater_admin_factory,
    qa_admin_factory,
)
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.eep_programs.eto_2022 import (
    AdditionalElements2022,
    SmartThermostatBrands2022,
    SolarElements2022,
    ElectricCarElements2022,
    StorageElements2022,
    MechanicalVentilationSystemTypes,
    BalancedVentilationTypes,
)
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    PrimaryHeatingEquipment2020,
    Fireplace2020,
    YesNo,
    PNWUSStates,
    ClimateLocation,
    ElectricUtility,
    GasUtility,
)
from axis.customer_eto.models import ETOAccount
from axis.customer_eto.strings import ETO_2022_CHECKSUMS, ETO_2023_CHECKSUMS
from axis.eep_program.models import EEPProgram
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.geographic.tests.factories import real_city_factory
from axis.home.tests.factories import (
    eep_program_custom_home_status_factory,
    home_factory,
)
from axis.qa.models import QARequirement
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships

log = logging.getLogger(__name__)


class ETO2022ProgramTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Eugene", "OR")

        cls.eto = eep_organization_factory(slug="eto", is_customer=True, name="ETO", city=cls.city)

        cls.provider_user = provider_admin_factory(
            username="eto_provider_admin",
            company__slug="peci",
            company__name="EPS New Construction",
            company__is_customer=True,
            company__city=cls.city,
        )
        cls.provider_company = cls.provider_user.company

        cls.rater_user = rater_admin_factory(
            username="eto_rater_admin",
            company__slug="rater",
            company__name="RATER",
            company__is_customer=True,
            company__city=cls.city,
        )
        cls.rater_company = cls.rater_user.company
        ETOAccount.objects.create(
            company=cls.rater_company, account_number="123", ccb_number="95232"
        )

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        ETOAccount.objects.create(company=cls.builder_company, account_number="456")

        cls.electric_utility = utility_organization_factory(
            slug="pacific-power",
            is_customer=True,
            name="Pacific Power",
            city=cls.city,
            gas_provider=False,
            electricity_provider=True,
        )
        cls.gas_utility = utility_organization_factory(
            slug="nw-natural-gas",
            is_customer=True,
            name="NW Natural Gas",
            city=cls.city,
            gas_provider=True,
            electricity_provider=False,
        )

        management.call_command(
            "build_program", "-p", "eto-2022", "--no_close_dates", stdout=DevNull()
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-2022")

        cls.qa_user = qa_admin_factory(
            username="QA",
            company__slug="csg-qa",
            company__name="QA",
            company__is_customer=True,
            company__city=cls.city,
        )
        cls.qa_company = cls.qa_user.company
        QARequirement.objects.get_or_create(
            qa_company=cls.qa_company,
            coverage_pct=1,
            gate_certification=True,
            eep_program=cls.eep_program,
        )

        companies = [
            cls.eto,
            cls.provider_company,
            cls.rater_company,
            cls.qa_company,
            cls.builder_company,
            cls.electric_utility,
            cls.gas_utility,
        ]

        Relationship.objects.create_mutual_relationships(*companies)

        source_type = random.choice([SourceType.EKOTROPE, SourceType.REMRATE_SQL])
        design_model = AnalysisType.OR_2023_ZONAL_DESIGN
        reference_model = AnalysisType.OR_2023_ZONAL_REFERENCE
        version = "16.0.6"
        util_rate = "Jan2023"
        if source_type == SourceType.EKOTROPE:
            design_model = AnalysisType.OR_2022_ZONAL_DESIGN
            reference_model = AnalysisType.OR_2022_ZONAL_REFERENCE
            version = "3.1.1"
            util_rate = "Jan2022"

        cls.floorplan_factory_kwargs = dict(
            owner=cls.rater_company,
            use_udrh_simulation=True,
            simulation__pct_improvement=25.0,
            simulation__conditioned_area=2150.0,
            simulation__source_type=source_type,
            simulation__version=version,
            simulation__flavor="Rate",  # Works for both
            simulation__design_model=design_model,
            simulation__reference_model=reference_model,
            simulation__residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            simulation__frame_floor_count=1,
            simulation__frame_floor__exterior_location=Location.ENCLOSED_CRAWL,
            simulation__location__climate_zone__zone="4",
            simulation__location__climate_zone__moisture_regime="C",
            simulation__location__weather_station="Eugene, OR",
            simulation__analysis__source_qualifier=ETO_2023_CHECKSUMS[1][0],  # Zonal!
            simulation__analysis__source_name=ETO_2023_CHECKSUMS[1][1],  # Zonal!
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
            simulation__appliances__dishwasher_consumption=303,
            simulation__appliances__clothes_washer_efficiency=2.15,
            simulation__appliances__clothes_washer_label_electric_consumption=152,
            simulation__appliances__clothes_dryer_efficiency=2.5,
            simulation__appliances__clothes_dryer_location=Location.CONDITIONED_SPACE,
            simulation__appliances__clothes_dryer_fuel=FuelType.ELECTRIC,
            simulation__appliances__oven_fuel=FuelType.ELECTRIC,
            simulation__air_conditioner_count=0,
            simulation__utility_rate_fuel__electric={
                "name": f"PAC-{util_rate}",
                "cost_units": CostUnit.USD,
                "seasonal_rate__service_charge": 0.0,
                "seasonal_rate__block_rate__cost": 0.01123,
            },
            simulation__utility_rate_fuel__natural_gas={
                "name": f"NWN_OR-{util_rate}",
                "cost_units": CostUnit.USD,
                "seasonal_rate__service_charge": 0.0,
                "seasonal_rate__block_rate__cost": 1.0377,
            },
            simulation__project__construction_year=str(datetime.date.today().year),
            subdivision__builder_org=cls.builder_company,
            subdivision__city=cls.city,
            subdivision__name="Subdivision",
        )

        floorplan = floorplan_with_simulation_factory(**cls.floorplan_factory_kwargs)
        cls.simulation = floorplan.simulation

        assert str(floorplan.simulation.location.climate_zone) == "4C"
        assert str(floorplan.simulation.climate_zone) == "4C"

        cls.home_kwargs = {
            "street_line1": "854 West 27th Avenue",
            "street_line2": None,
            "city": cls.city,
            "zipcode": "97405",
        }

        cls.home = home_factory(
            subdivision=floorplan.subdivision_set.first(), geocode=True, **cls.home_kwargs
        )
        cls.home_status = eep_program_custom_home_status_factory(
            home=cls.home,
            floorplan=floorplan,
            eep_program=cls.eep_program,
            company=cls.rater_company,
        )

        rel_ele = create_or_update_spanning_relationships(
            cls.electric_utility, cls.home_status.home
        )[0][0]
        rel_gas = create_or_update_spanning_relationships(cls.gas_utility, cls.home_status.home)[0][
            0
        ]
        create_or_update_spanning_relationships(cls.qa_company, cls.home_status.home)
        create_or_update_spanning_relationships(cls.provider_company, cls.home_status.home)

        cls.home._generate_utility_type_hints(rel_gas, rel_ele)

        assert cls.home_status.get_electric_company().id == cls.electric_utility.pk
        assert cls.home_status.get_gas_company().id == cls.gas_utility.pk

    @property
    def default_program_data(self):
        data = {
            "us_state": PNWUSStates.OR.value,
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
            "improved_heating_therms": 23.3,
            "improved_heating_kwh": 1501.2,
            "improved_cooling_kwh": 2503.6,
            "improved_hot_water_therms": 25.2,
            "improved_hot_water_kwh": 1025.2,
            "improved_lights_and_appliance_therms": 5.2,
            "improved_lights_and_appliance_kwh": 1975.2,
            "improved_pv_kwh": 5,
            "electric_rate": 1.0332,
            "gas_rate": 1.2012,
        }
        return data.copy()


class ETO2022ProgramCompleteTestMixin(ETO2022ProgramTestMixin, AxisTestCase):
    """This provides a complete ready for certification test"""

    @classmethod
    def setUpTestData(cls):
        super(ETO2022ProgramCompleteTestMixin, cls).setUpTestData()

        collection_request = CollectionRequestMixin()
        cls.expected_answers = {
            "is-adu": YesNo.NO,
            "fire-rebuild-qualification": YesNo.NO,
            "builder-payment-redirected": YesNo.NO,
            "cobid-qualification": YesNo.NO,
            "eto-electric-elements": AdditionalElements2022.NO,
            "smart-thermostat-brand": SmartThermostatBrands2022.NEST,
            "has-gas-fireplace": Fireplace2020.NONE,
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            "equipment-water-heater": {"brand": "Brand", "model": "Model"},
            # These are simulation dependant
            "equipment-heating-other-type": PrimaryHeatingEquipment2020.OTHER_GAS,
            "equipment-heating-other-brand": "Brand",
            "equipment-heating-other-model-number": "Model",
            "equipment-ventilation-system-type": {
                "input": MechanicalVentilationSystemTypes.OTHER,
                "comment": "XX",
            },
        }
        collection_request.add_bulk_answers(cls.expected_answers, home_status=cls.home_status)
        annotation = AnnotationMixin()
        annotation.add_annotation(
            content="foo", type_slug="hpxml_gbr_id", content_object=cls.home_status
        )

        missing_checks = cls.home_status.report_eligibility_for_certification()
        if missing_checks:
            print(
                "** Warning! Failing ETO-2022 Certification Eligibility Requirements:\n  - "
                + "\n  - ".join(missing_checks)
                + "\n** End Warning\n"
            )

            questions = cls.home_status.get_unanswered_questions()
            measures = questions.values_list("measure", flat=True)
            if len(measures):
                print("Missing questions")
            for measure in measures:
                print(" * %s" % measure)


# class ETO2022ProgramCoreBehaviorsTests(AxisTestCase):
#     @classmethod
#     def setUpTestData(cls):
#         super(ETO2022ProgramCoreBehaviorsTests, cls).setUpTestData()
#         eep_organization_factory(slug="eto")
#         provider_organization_factory(slug="peci")
#         management.call_command("build_program", "-p", "eto-2022", "-r", "rater")
#         cls.eep_program = EEPProgram.objects.get(slug="eto-2022")
#
#     def test_conditions(self):
#         cr = self.eep_program.collection_request
#         instruments = cr.collectioninstrument_set.all()
#         with self.subTest("Solar Company"):
#             instrument = instruments.get(measure="solar-company")
#             self.assertEqual(instrument.test_requirement_type, "one-pass")
#             self.assertEqual(instrument.conditions.count(), 2)


class ETO2022ProgramTests(ETO2022ProgramCompleteTestMixin, CollectionRequestMixin, AxisTestCase):
    def test_missing_required_checklist_status(self):
        """Verify that you fail if you are missing required questions"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_redirect_cascade(self):
        """Redirect needs Payee"""
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("payee-company", missing)
        self.replace_collected_input("builder-payment-redirected", YesNo.YES)
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("payee-company", missing)

    def test_fire_rebuild_cascade(self):
        """Rebuild get bonus"""
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("fire-resilience-bonus", missing)
        self.replace_collected_input("fire-rebuild-qualification", YesNo.YES)
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("fire-resilience-bonus", missing)

        with self.subTest("Triple Window"):
            self.add_collected_input(
                value=FireResilienceBonus.TRIPLE_PANE,
                measure_id="fire-resilience-bonus",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("building-window-triple-pane-u-value", missing)

        with self.subTest("Exterior Insulation"):
            self.replace_collected_input(
                value=FireResilienceBonus.RIGID_INSULATION,
                measure_id="fire-resilience-bonus",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("building-fire-exterior-insulation-type", missing)

        with self.subTest("Both Insulation and Windows"):
            self.replace_collected_input(
                value=FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
                measure_id="fire-resilience-bonus",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("building-window-triple-pane-u-value", missing)
            self.assertIn("building-fire-exterior-insulation-type", missing)

    def test_cobid_cascade(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("cobid-qualification", missing)
        self.assertNotIn("cobid-type", missing)
        self.assertNotIn("cobid-registered", missing)
        self.replace_collected_input("cobid-qualification", YesNo.YES)
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("cobid-type", missing)
        self.assertIn("cobid-registered", missing)

    def test_electric_incentives(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("solar-elements", missing)
        self.assertNotIn("solar-company", missing)
        self.assertNotIn("electric-vehicle-type", missing)
        self.assertNotIn("storage-type", missing)

        with self.subTest("Solar Tests"):
            self.replace_collected_input(
                value=AdditionalElements2022.SOLAR,
                measure_id="eto-electric-elements",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("solar-elements", missing)
            self.assertNotIn("electric-vehicle-type", missing)
            self.assertNotIn("storage-type", missing)

        with self.subTest("EV Tests"):
            self.replace_collected_input(
                value=AdditionalElements2022.ELECTRIC_CAR,
                measure_id="eto-electric-elements",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("solar-elements", missing)
            self.assertNotIn("solar-company", missing)
            self.assertIn("electric-vehicle-type", missing)
            self.assertNotIn("storage-type", missing)

        with self.subTest("Storage Tests"):
            self.replace_collected_input(
                value=AdditionalElements2022.SOLAR_AND_STORAGE,
                measure_id="eto-electric-elements",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("solar-elements", missing)
            self.assertNotIn("electric-vehicle-type", missing)
            self.assertIn("storage-type", missing)

        with self.subTest("All Tests"):
            self.replace_collected_input(
                value=AdditionalElements2022.ALL,
                measure_id="eto-electric-elements",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("solar-elements", missing)
            self.assertIn("electric-vehicle-type", missing)
            self.assertIn("storage-type", missing)

    def test_solar_elements(self):
        self.replace_collected_input(
            value=AdditionalElements2022.SOLAR,
            measure_id="eto-electric-elements",
            home_status=self.home_status,
        )
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("solar-elements", missing)
        self.assertNotIn("ets-annual-etsa-kwh", missing)
        self.assertNotIn("solar-company", missing)
        self.assertNotIn("non-ets-annual-pv-watts", missing)
        self.assertNotIn("non-ets-dc-capacity-installed", missing)
        self.assertNotIn("non-ets-installer", missing)
        self.assertNotIn("non-ets-pv-panels-brand", missing)
        self.assertNotIn("non-ets-inverter-brand", missing)
        self.assertNotIn("non-ets-tsrf", missing)

        with self.subTest("Solar Ready"):
            self.add_collected_input(
                value=SolarElements2022.SOLAR_READY,
                measure_id="solar-elements",
                home_status=self.home_status,
            )
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("solar-elements", missing)
            self.assertNotIn("ets-annual-etsa-kwh", missing)
            self.assertNotIn("solar-company", missing)
            self.assertNotIn("non-ets-annual-pv-watts", missing)
            self.assertNotIn("non-ets-dc-capacity-installed", missing)
            self.assertNotIn("non-ets-installer", missing)
            self.assertNotIn("non-ets-pv-panels-brand", missing)
            self.assertNotIn("non-ets-inverter-brand", missing)
            self.assertNotIn("non-ets-tsrf", missing)

        for answer in [SolarElements2022.SOLAR_PV, SolarElements2022.NET_ZERO]:
            with self.subTest(f"ETO {answer.value}"):
                self.add_collected_input(
                    value=answer,
                    measure_id="solar-elements",
                    home_status=self.home_status,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertIn("solar-company", missing)
                self.assertIn("ets-annual-etsa-kwh", missing)
                self.assertNotIn("non-ets-annual-pv-watts", missing)
                self.assertNotIn("non-ets-dc-capacity-installed", missing)
                self.assertNotIn("non-ets-installer", missing)
                self.assertNotIn("non-ets-pv-panels-brand", missing)
                self.assertNotIn("non-ets-inverter-brand", missing)
                self.assertNotIn("non-ets-tsrf", missing)

        with self.subTest("Non ETO Solar"):
            self.add_collected_input(
                value=SolarElements2022.NON_ETO_SOLAR,
                measure_id="solar-elements",
                home_status=self.home_status,
            )
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("ets-annual-etsa-kwh", missing)
            self.assertNotIn("ets-annual-etsa-kwh", missing)
            self.assertIn("solar-company", missing)
            self.assertIn("non-ets-annual-pv-watts", missing)
            self.assertIn("non-ets-pv-panels-brand", missing)
            self.assertIn("non-ets-inverter-brand", missing)
            self.assertIn("non-ets-tsrf", missing)

    def test_ev_type(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("electric-vehicle-type", missing)
        self.assertNotIn("electric-vehicle-estar-level-2", missing)
        self.assertNotIn("electric-vehicle-charging-brand", missing)
        self.assertNotIn("electric-vehicle-charging-installer", missing)

        self.replace_collected_input(
            value=AdditionalElements2022.ELECTRIC_CAR,
            measure_id="eto-electric-elements",
            home_status=self.home_status,
        )
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("electric-vehicle-type", missing)
        self.assertNotIn("electric-vehicle-estar-level-2", missing)
        self.assertNotIn("electric-vehicle-charging-brand", missing)
        self.assertNotIn("electric-vehicle-charging-model", missing)
        self.assertNotIn("electric-vehicle-charging-installer", missing)
        with self.subTest("EV Type READT"):
            self.add_collected_input(
                value=ElectricCarElements2022.EV_READY,
                measure_id="electric-vehicle-type",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("electric-vehicle-estar-level-2", missing)
            self.assertNotIn("electric-vehicle-charging-brand", missing)
            self.assertNotIn("electric-vehicle-charging-model", missing)
            self.assertNotIn("electric-vehicle-charging-installer", missing)

        with self.subTest("EV Type Installed"):
            self.replace_collected_input(
                value=ElectricCarElements2022.EV_INSTALLED,
                measure_id="electric-vehicle-type",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("electric-vehicle-estar-level-2", missing)
            self.assertIn("electric-vehicle-charging-brand", missing)
            self.assertIn("electric-vehicle-charging-model", missing)
            self.assertIn("electric-vehicle-charging-installer", missing)

    def test_storage_type(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("storage-type", missing)
        self.assertNotIn("storage-capacity", missing)
        self.assertNotIn("storage-brand", missing)
        self.assertNotIn("storage-installer", missing)
        self.assertNotIn("storage-smart-panel", missing)
        self.assertNotIn("storage-smart-panel-brand", missing)

        self.replace_collected_input(
            value=AdditionalElements2022.SOLAR_AND_STORAGE,
            measure_id="eto-electric-elements",
            home_status=self.home_status,
        )
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("storage-type", missing)
        self.assertNotIn("storage-capacity", missing)
        self.assertNotIn("storage-brand", missing)
        self.assertNotIn("storage-installer", missing)
        self.assertNotIn("storage-smart-panel", missing)
        self.assertNotIn("storage-smart-panel-brand", missing)
        self.assertNotIn("storage-smart-panel-model", missing)

        with self.subTest("Storage Ready"):
            self.add_collected_input(
                value=StorageElements2022.STORAGE_READY,
                measure_id="storage-type",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("storage-capacity", missing)
            self.assertNotIn("storage-brand", missing)
            self.assertNotIn("storage-installer", missing)
            self.assertNotIn("storage-smart-panel", missing)
            self.assertNotIn("storage-smart-panel-brand", missing)
            self.assertNotIn("storage-smart-panel-model", missing)

        with self.subTest("Storage Installed"):
            self.add_collected_input(
                value=StorageElements2022.STORAGE_INSTALLED,
                measure_id="storage-type",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("storage-capacity", missing)
            self.assertIn("storage-brand", missing)
            self.assertIn("storage-installer", missing)
            self.assertIn("storage-smart-panel", missing)
            self.assertNotIn("storage-smart-panel-brand", missing)
            self.assertNotIn("storage-smart-panel-model", missing)

        with self.subTest("No Storage Smart Panel"):
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("storage-smart-panel", missing)
            self.assertNotIn("storage-smart-panel-brand", missing)
            self.add_collected_input(
                value=YesNo.NO,
                measure_id="storage-smart-panel",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("storage-smart-panel", missing)
            self.assertNotIn("storage-smart-panel-brand", missing)
            self.assertNotIn("storage-smart-panel-model", missing)

        with self.subTest("Storage Smart Panel"):
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("storage-smart-panel-brand", missing)
            self.replace_collected_input(
                value=YesNo.YES,
                measure_id="storage-smart-panel",
                home_status=self.home_status,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("storage-smart-panel-brand", missing)
            self.assertIn("storage-smart-panel-model", missing)

    def test_primary_heating_type(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("mini-split-indoor-heads-quantity", missing)
        self.replace_collected_input(
            value=PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED,
            measure_id="primary-heating-equipment-type",
            home_status=self.home_status,
        )
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("mini-split-indoor-heads-quantity", missing)

    def test_primary_heating_type_mini_split(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("mini-split-indoor-heads-quantity", missing)
        self.replace_collected_input(
            value=PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED,
            measure_id="primary-heating-equipment-type",
            home_status=self.home_status,
        )
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("mini-split-indoor-heads-quantity", missing)

    def test_simulation_gas_forced_air_heaters(self):
        simulation = self.home_status.floorplan.simulation
        self.assertEqual(simulation.gas_forced_air_heating.count(), 0)

        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-furnace", missing)
        self.assertNotIn("equipment-furnace-2", missing)

        with self.subTest("Single System"):
            simulation.hvac_distribution_systems.update(
                system_type=DistributionSystemType.FORCED_AIR
            )
            simulation.mechanical_equipment.heaters().update(fuel=FuelType.NATURAL_GAS)
            self.assertEqual(
                simulation.mechanical_equipment.primary_heating_equipment_system_type,
                MechanicalSystemType.FORCED_AIR_GAS_HEATER,
            )
            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.NONE,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-furnace", missing)
            self.assertNotIn("equipment-furnace-2", missing)

        with self.subTest("Two Systems"):
            equip = mechanical_equipment_factory(
                simulation=simulation,
                equipment_type="heater",
                fuel=FuelType.NATURAL_GAS,
                heating_percent_served=64.0,
            )
            distribution_factory(
                simulation=simulation,
                heating_system=equip,
                system_type=DistributionSystemType.FORCED_AIR,
            )
            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.FORCED_AIR_GAS_HEATER,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-furnace", missing)
            self.assertIn("equipment-furnace-2", missing)

    def test_simulation_air_source_heat_pumps(self):
        simulation = self.home_status.floorplan.simulation
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-heat-pump", missing)
        self.assertNotIn("equipment-heat-pump-2", missing)

        self.home_status.floorplan.simulation.hvac_distribution_systems.all().delete()
        self.home_status.floorplan.simulation.mechanical_equipment.first().delete()

        with self.subTest("Single System"):
            equip = mechanical_equipment_factory(
                simulation=simulation,
                equipment_type="air_source_heat_pump",
                as_dfhp=False,
                heating_percent_served=64.0,
            )
            distribution_factory(
                simulation=simulation,
                heating_system=equip,
                system_type=DistributionSystemType.FORCED_AIR,
            )
            self.assertEqual(
                simulation.mechanical_equipment.primary_heating_equipment_system_type,
                MechanicalSystemType.FORCED_AIR_ASHP,
            )
            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.NONE,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-heat-pump", missing)
            self.assertNotIn("equipment-heat-pump-2", missing)

        with self.subTest("Two Systems"):
            equip = mechanical_equipment_factory(
                simulation=simulation,
                equipment_type="air_source_heat_pump",
                as_dfhp=False,
                heating_percent_served=24.0,
            )
            distribution_factory(
                simulation=simulation,
                heating_system=equip,
                system_type=DistributionSystemType.DUCTLESS,
            )

            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.DUCTLESS_ASHP,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-heat-pump", missing)
            self.assertIn("equipment-heat-pump-2", missing)

    def test_simulation_dfhp(self):
        simulation = self.home_status.floorplan.simulation

        self.home_status.floorplan.simulation.hvac_distribution_systems.all().delete()
        self.home_status.floorplan.simulation.mechanical_equipment.first().delete()

        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-dfhp-brand", missing)
        self.assertNotIn("equipment-dfhp-outdoor-model", missing)
        self.assertNotIn("equipment-dfhp-indoor-model", missing)
        self.assertNotIn("equipment-dfhp-furnace-model", missing)
        self.assertNotIn("equipment-dfhp-brand-2", missing)
        self.assertNotIn("equipment-dfhp-outdoor-model-2", missing)
        self.assertNotIn("equipment-dfhp-indoor-model-2", missing)
        self.assertNotIn("equipment-dfhp-furnace-model-2", missing)

        with self.subTest("Single System"):
            equip = mechanical_equipment_factory(
                simulation=simulation,
                equipment_type="air_source_heat_pump",
                as_dfhp=True,
                heating_percent_served=64.0,
            )
            distribution_factory(
                simulation=simulation,
                heating_system=equip,
                system_type=DistributionSystemType.FORCED_AIR,
            )
            self.assertEqual(
                simulation.mechanical_equipment.primary_heating_equipment_system_type,
                MechanicalSystemType.FORCED_AIR_DFHP,
            )
            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.NONE,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-dfhp-brand", missing)
            self.assertIn("equipment-dfhp-outdoor-model", missing)
            self.assertIn("equipment-dfhp-indoor-model", missing)
            self.assertIn("equipment-dfhp-furnace-model", missing)
            self.assertNotIn("equipment-dfhp-brand-2", missing)
            self.assertNotIn("equipment-dfhp-outdoor-model-2", missing)
            self.assertNotIn("equipment-dfhp-indoor-model-2", missing)
            self.assertNotIn("equipment-dfhp-furnace-model-2", missing)

        with self.subTest("Two Systems"):
            equip = mechanical_equipment_factory(
                simulation=simulation,
                equipment_type="air_source_heat_pump",
                as_dfhp=True,
                heating_percent_served=25.0,
            )
            distribution_factory(
                simulation=simulation,
                heating_system=equip,
                system_type=DistributionSystemType.DUCTLESS,
            )
            self.assertEqual(
                simulation.mechanical_equipment.primary_heating_equipment_system_type,
                MechanicalSystemType.FORCED_AIR_DFHP,
            )
            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.DUCTLESS_DFHP,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-dfhp-brand-2", missing)
            self.assertIn("equipment-dfhp-outdoor-model-2", missing)
            self.assertIn("equipment-dfhp-indoor-model-2", missing)
            self.assertIn("equipment-dfhp-furnace-model-2", missing)

    def test_simulation_other_hvac(self):
        simulation = self.home_status.floorplan.simulation

        self.remove_collected_input(
            measure_id="equipment-heating-other-type", home_status=self.home_status
        )
        self.remove_collected_input(
            measure_id="equipment-heating-other-brand", home_status=self.home_status
        )
        self.remove_collected_input(
            measure_id="equipment-heating-other-model-number",
            home_status=self.home_status,
        )

        with self.subTest("Single System"):
            self.assertEqual(
                simulation.mechanical_equipment.primary_heating_equipment_system_type,
                MechanicalSystemType.RADIANT_ELECTRIC_HEATER,
            )
            self.assertEqual(
                simulation.mechanical_equipment.secondary_heating_equipment_system_type,
                MechanicalSystemType.NONE,
            )
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-heating-other-type", missing)
            self.assertIn("equipment-heating-other-brand", missing)
            self.assertIn("equipment-heating-other-model-number", missing)
            self.assertNotIn("equipment-heating-other-type-2", missing)
            self.assertNotIn("equipment-heating-other-brand-2", missing)
            self.assertNotIn("equipment-heating-other-model-number-2", missing)

        with self.subTest("Two Systems"):
            mechanical_equipment_factory(
                simulation=simulation,
                equipment_type="ground_source_heat_pump",
                heating_percent_served=25.0,
            )
            self.assertEqual(
                self.home_status.floorplan.simulation.gas_forced_air_heating.count(), 0
            )
            self.assertEqual(self.home_status.floorplan.simulation.air_source_heat_pumps.count(), 0)
            self.assertEqual(
                self.home_status.floorplan.simulation.non_air_source_heat_pump_heating.count(),
                2,
            )

            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-heating-other-type", missing)
            self.assertIn("equipment-heating-other-brand", missing)
            self.assertIn("equipment-heating-other-model-number", missing)
            self.assertIn("equipment-heating-other-type-2", missing)
            self.assertIn("equipment-heating-other-brand-2", missing)
            self.assertIn("equipment-heating-other-model-number-2", missing)

    def test_air_conditioner_system_type(self):
        """
        Test the simulation checks that will add new questions
        """
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-air-conditioner-brand", missing)
        self.assertNotIn("equipment-air-conditioner-model-number-outdoor", missing)
        self.assertNotIn("equipment-air-conditioner-model-number-outdoor", missing)
        self.assertFalse(self.home_status.floorplan.simulation.air_conditioners.exists())

        mechanical_equipment_factory(
            company=self.simulation.company,
            simulation=self.simulation,
            equipment_type="air_conditioner",
            system_type=CoolingSystemType.AIR_CONDITIONER,
            efficiency_unit=CoolingEfficiencyUnit.SEER,
            efficiency=12.99,
        )

        self.home_status.refresh_from_db()
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertTrue(self.home_status.floorplan.simulation.air_conditioners.exists())
        self.assertNotIn("equipment-air-conditioner-brand", missing)
        self.assertNotIn("equipment-air-conditioner-model-number-outdoor", missing)
        self.assertNotIn("equipment-air-conditioner-model-number-outdoor", missing)

        self.home_status.floorplan.simulation.air_conditioners.update(efficiency=13.01)

        self.home_status.refresh_from_db()
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertTrue(self.home_status.floorplan.simulation.air_conditioners.exists())
        self.assertIn("equipment-air-conditioner-brand", missing)
        self.assertIn("equipment-air-conditioner-model-number-outdoor", missing)
        self.assertIn("equipment-air-conditioner-model-number-outdoor", missing)

    def test_simulation_water_heater(self):
        water_heaters = self.home_status.floorplan.simulation.water_heaters
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-gas-tank-water-heater-serial-number", missing)
        self.assertNotIn("equipment-gas-tankless-water-heater-serial-number", missing)
        self.assertNotIn("equipment-heat-pump-water-heater-serial-number", missing)

        with self.subTest("Conventional Gas Test"):
            water_heaters.update(
                fuel=FuelType.NATURAL_GAS,
                style=WaterHeaterStyle.CONVENTIONAL,
                efficiency=0.89,
            )
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-gas-tank-water-heater-serial-number", missing)
            self.assertNotIn("equipment-gas-tankless-water-heater-serial-number", missing)
            self.assertNotIn("equipment-heat-pump-water-heater-serial-number", missing)

        with self.subTest("Conventional Gas Tankless Test"):
            water_heaters.update(
                fuel=FuelType.NATURAL_GAS,
                style=WaterHeaterStyle.TANKLESS,
                efficiency=0.89,
            )
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("equipment-gas-tank-water-heater-serial-number", missing)
            self.assertIn("equipment-gas-tankless-water-heater-serial-number", missing)
            self.assertNotIn("equipment-heat-pump-water-heater-serial-number", missing)

        with self.subTest("Heat Pump Water Heater Test"):
            water_heaters.update(
                fuel=FuelType.ELECTRIC,
                style=WaterHeaterStyle.AIR_SOURCE_HEAT_PUMP,
                efficiency=0.89,
            )
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("equipment-gas-tank-water-heater-serial-number", missing)
            self.assertNotIn("equipment-gas-tankless-water-heater-serial-number", missing)
            self.assertIn("equipment-heat-pump-water-heater-serial-number", missing)

        with self.subTest("Conventional HPWH Test"):
            water_heaters.update(
                fuel=FuelType.ELECTRIC,
                style=WaterHeaterStyle.CONVENTIONAL,
                efficiency=1.01,
            )
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("equipment-gas-tank-water-heater-serial-number", missing)
            self.assertNotIn("equipment-gas-tankless-water-heater-serial-number", missing)
            self.assertIn("equipment-heat-pump-water-heater-serial-number", missing)

    def test_ventilation_exhaust(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-balanced-ventilation-no-hr", missing)

        self.add_collected_input(
            measure_id="equipment-ventilation-system-type",
            value=MechanicalVentilationSystemTypes.BALANCED_NO_HR,
        )
        self.home_status.refresh_from_db()
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertIn("equipment-balanced-ventilation-no-hr", missing)
        self.assertNotIn("equipment-ventilation-exhaust", missing)
        self.assertNotIn("equipment-ventilation-supply-brand", missing)
        self.assertNotIn("equipment-ventilation-supply-model", missing)

        for answer in [
            BalancedVentilationTypes.INTERMITTENT,
            BalancedVentilationTypes.CONTINUOUS,
        ]:
            with self.subTest(f"Exhaust question - {answer!r}"):
                self.add_collected_input(
                    measure_id="equipment-balanced-ventilation-no-hr",
                    value=answer,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertIn("equipment-ventilation-exhaust", missing)

        for answer in [
            BalancedVentilationTypes.SECONDARY,
            BalancedVentilationTypes.STAND_ALONE,
        ]:
            with self.subTest(f"Exhaust / Brand / Mode question - {answer!r}"):
                self.add_collected_input(
                    measure_id="equipment-balanced-ventilation-no-hr",
                    value=answer,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertIn("equipment-ventilation-exhaust", missing)
                self.assertIn("equipment-ventilation-supply-brand", missing)
                self.assertIn("equipment-ventilation-supply-model", missing)

        for answer in [BalancedVentilationTypes.OTHER]:
            with self.subTest(f"With other - {answer!r}"):
                self.add_collected_input(
                    measure_id="equipment-balanced-ventilation-no-hr",
                    value=answer,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertNotIn("equipment-ventilation-supply-brand", missing)
                self.assertNotIn("equipment-ventilation-supply-model", missing)
                self.assertNotIn("equipment-ventilation-exhaust", missing)

    def test_ventilation_hrv_erv(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-ventilation-system-type", missing)
        self.assertNotIn("equipment-ventilation-spot-erv-count", missing)
        self.assertNotIn("equipment-ventilation-balanced", missing)
        self.assertNotIn("equipment-ventilation-hrv-erv", missing)
        self.assertNotIn("equipment-ventilation-exhaust", missing)

        for answer in [
            MechanicalVentilationSystemTypes.STAND_ALONE,
            MechanicalVentilationSystemTypes.INTEGRATED_HRV_ERV,
        ]:
            with self.subTest(f"ERV_HRV {answer!r}"):
                self.add_collected_input(
                    measure_id="equipment-ventilation-system-type",
                    value=answer,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertIn("equipment-ventilation-hrv-erv", missing)

        for answer in [MechanicalVentilationSystemTypes.SPOT]:
            with self.subTest(f"Spot Count {answer!r}"):
                self.add_collected_input(
                    measure_id="equipment-ventilation-system-type",
                    value=answer,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertIn("equipment-ventilation-spot-erv-count", missing)
                self.assertIn("equipment-ventilation-hrv-erv", missing)

        for answer in [MechanicalVentilationSystemTypes.WA_EXHAUST]:
            with self.subTest(f"WA Count {answer!r}"):
                self.add_collected_input(
                    measure_id="equipment-ventilation-system-type",
                    value=answer,
                )
                self.home_status.refresh_from_db()
                missing = self.get_unanswered_questions(self.home_status, measures_only=True)
                self.assertIn("equipment-ventilation-exhaust", missing)

    def test_appliances(self):
        missing = self.get_unanswered_questions(self.home_status, measures_only=True)
        self.assertNotIn("equipment-refrigerator", missing)
        self.assertNotIn("equipment-dishwasher", missing)
        self.assertNotIn("equipment-clothes-washer", missing)
        self.assertNotIn("equipment-clothes-dryer", missing)

        appliances = self.home_status.floorplan.simulation.appliances

        with self.subTest("Appliance Refrigerator"):
            appliances.refrigerator_consumption = 548.9
            appliances.save()
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-refrigerator", missing)

        with self.subTest("Appliance Dishwasher"):
            appliances.dishwasher_consumption = 301.9
            appliances.save()
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-dishwasher", missing)

        with self.subTest("Appliance Washing Machine"):
            appliances.clothes_washer_efficiency = 2.156
            appliances.save()
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertNotIn("equipment-clothes-washer", missing)

            appliances.clothes_washer_label_electric_consumption = 150.9
            appliances.save()
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-clothes-washer", missing)

        with self.subTest("Appliance Dryer"):
            appliances.clothes_dryer_efficiency = 2.801
            appliances.save()
            self.home_status.refresh_from_db()
            missing = self.get_unanswered_questions(self.home_status, measures_only=True)
            self.assertIn("equipment-clothes-dryer", missing)

    def test_get_min_max_simulation_version(self):
        """Tests that our minimum verision for Eko and REM work"""
        kwargs = {
            "simulation__source_type": SourceType.REMRATE_SQL,
            "simulation__flavor": "Rate",
            "simulation__version": "16.0.6",
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
        with self.subTest("Failing Minimum"):
            floorplan.simulation.version = "0.0.0"
            floorplan.simulation.save()

            home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
            result = self.home_status.eep_program.get_min_max_simulation_version(
                home_status, edit_url="foo"
            )
            self.assertFalse(result.status)
            self.assertIn("Simulation data must be REM ==", result.message)

        with self.subTest("Failing Maximum"):
            floorplan.simulation.source_type = SourceType.REMRATE_SQL
            floorplan.simulation.version = "16.1.0"
            floorplan.simulation.flavor = "Duh"
            floorplan.simulation.save()

            home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
            result = self.home_status.eep_program.get_min_max_simulation_version(
                home_status, edit_url="foo"
            )
            self.assertFalse(result.status)
            self.assertIn("Simulation data must be REM ==", result.message)

        with self.subTest("Failing Maximum Ekotrope"):
            floorplan.simulation.source_type = SourceType.EKOTROPE
            floorplan.simulation.version = "3.0.1"
            floorplan.simulation.flavor = "Duh"
            floorplan.simulation.save()

            home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
            result = self.home_status.eep_program.get_min_max_simulation_version(
                home_status, edit_url="foo"
            )
            self.assertFalse(result.status)
            self.assertIn("You gave Ekotrope 3.0.1", result.message)

    def test_get_floorplan_simulation_error_status(self):
        # Flesh out the chain
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)
        # Drill into the test
        result = self.home_status.get_floorplan_simulation_error_status()
        self.assertTrue(result.status)
        # Drill into the actual validations
        result = get_eto_2022_simulation_validations(self.home_status, self.simulation)
        self.assertEqual(result["errors"], [])

        ventilation = self.simulation.mechanical_ventilation_systems.get()
        initial = ventilation.hour_per_day
        ventilation.hour_per_day = 23.9
        ventilation.save()
        with self.subTest("Ventilation Failing 23.9 Rate"):
            result = get_eto_2022_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("must be 24hr/day or 4.5hr/day", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)

        ventilation.hour_per_day = 4.2
        ventilation.save()
        with self.subTest("Ventilation Failing 4.2 Rate"):
            result = get_eto_2022_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("must be 24hr/day or 4.5hr/day", result["errors"][0])
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 1)

        ventilation.hour_per_day = 4.5
        ventilation.save()
        with self.subTest("Ventilation Passing 4.5 Rate"):
            result = get_eto_2022_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 0)
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 0)

        ventilation.hour_per_day = initial
        ventilation.save()
        with self.subTest("Ventilation Passing 24 Rate"):
            result = get_eto_2022_simulation_validations(self.home_status, self.simulation)
            self.assertEqual(len(result["errors"]), 0)
            missing_checks = self.home_status.report_eligibility_for_certification()
            self.assertEqual(len(missing_checks), 0)

    def test_get_eto_builder_incentive_status(self):
        """Verify that you fail if you have too low of a pct improvement"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        floorplan_factory_kwargs = self.floorplan_factory_kwargs.copy()
        floorplan_factory_kwargs["simulation__pct_improvement"] = 0.09
        floorplan_factory_kwargs["simulation__name"] = "Too Low"
        floorplan = floorplan_with_simulation_factory(**floorplan_factory_kwargs)

        self.home_status.floorplan = floorplan
        self.home_status.save()

        home_status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        result = home_status.eep_program.get_eto_builder_incentive_status(home_status, "foo")
        self.assertFalse(result.status)
        self.assertIn("Project does not currently qualify for an incentive", result.message)

        missing_checks = home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertEqual(
            {"Project does not currently qualify for an incentive"}, set(missing_checks)
        )

    def test_collector_queries(self):
        url = reverse("apiv2:home-collectors", kwargs={"pk": self.home_status.home.pk})
        self.assertTrue(
            self.client.login(username=self.rater_user.username, password="password"),
        )

        # with self.assertNumQueries(1741):
        # with self.assertNumQueries(763):
        with self.assertNumQueries(676):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        _data = response.json()
        self.assertEqual(len(_data.keys()), 1)
        data = _data[list(_data.keys())[0]]  # Collection Request ID
        self.assertEqual(len(data.keys()), 2)  # Specification / Instruments


class ETO2022Certification(ETO2022ProgramCompleteTestMixin, AxisTestCase):
    def test_certification(self):
        """Make sure when we certify we get our document"""

        try:
            self.assertEqual(self.home_status.is_eligible_for_certification(), True)
        except AssertionError:
            import pprint

            for k, v in self.home_status.get_progress_analysis()["requirements"].items():
                if v["status"] is False:
                    print(k)
                    pprint.pprint(v)
            raise

        self.assertEqual(self.home_status.is_eligible_for_certification(), True)

        rater_admin = self.get_admin_user(company_type="rater")
        self.assertEqual(
            self.home_status.can_user_certify(rater_admin, perform_eligiblity_check=False),
            False,
        )

        provider_admin = self.user_model.objects.filter(
            company__slug="csg-qa", is_company_admin=True
        )[0]
        certify_single_home(
            provider_admin,
            self.home_status,
            datetime.datetime.today(),
            bypass_check=True,  # Skip Gating QA
        )

        status = EEPProgramHomeStatus.objects.get(id=self.home_status.id)
        self.assertIsNotNone(status.certification_date)
        self.assertEqual(status.state, "complete")

        doc = CustomerDocument.objects.get()
        self.assertIsNotNone(doc.filesize)
        self.assertIsNotNone(doc.description)
        self.assertIn("Final", doc.description)
