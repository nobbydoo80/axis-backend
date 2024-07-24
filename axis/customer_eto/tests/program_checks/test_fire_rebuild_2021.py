"""test_fire_rebuild_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "12/1/21 11:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


import logging
import random

from django.core import management

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
from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
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
    YesNo,
)
from axis.customer_eto.models import ETOAccount
from axis.customer_eto.strings import ETO_FIRE_2021_CHECKSUMS
from axis.eep_program.models import EEPProgram
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import Home
from axis.home.tests.factories import (
    home_factory,
    eep_program_custom_home_status_factory,
)
from axis.qa.models import QARequirement
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships


log = logging.getLogger(__name__)


def get_fire_default_answers():
    return {
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
        "fire-rebuild-qualification": YesNo.YES,
        "fire-resilience-bonus": FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
        "building-window-triple-pane-u-value": 0.2,
        "building-fire-exterior-insulation-type": "Superior Fire Suppression stuff",
    }


class FireRebuild2021ProgramTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Beavercreek", "OR")

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
            "eto-fire-2021",
            "--warn_only",
            "--no_close_dates",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-fire-2021")

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

        sim_v = random.choice([(SourceType.EKOTROPE, "3.0.0"), (SourceType.REMRATE_SQL, "15.7.1")])

        cls.floorplan_factory_kwargs = dict(
            owner=cls.rater_company,
            use_udrh_simulation=True,
            simulation__pct_improvement=25.0,
            simulation__conditioned_area=2150.0,
            simulation__source_type=sim_v[0],
            simulation__version=sim_v[1],
            simulation__flavor="Rate",  # Works for both
            simulation__design_model=AnalysisType.OR_2022_ZONAL_DESIGN,
            simulation__reference_model=AnalysisType.OR_2022_ZONAL_REFERENCE,
            simulation__residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            simulation__location__climate_zone__zone="4",
            simulation__location__climate_zone__moisture_regime="C",
            simulation__location__weather_station="Eugene, OR",
            simulation__analysis__source_qualifier=ETO_FIRE_2021_CHECKSUMS[1][0],  # Zonal!
            simulation__analysis__source_name=ETO_FIRE_2021_CHECKSUMS[1][1],  # Zonal!
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
            simulation__slabs_count=1,
            simulation__foundation_wall_count=0,
            simulation__frame_floor_count=0,
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
            "us_state": PNWUSStates.OR.value,
            "climate_location": ClimateLocation.PORTLAND.value,
            "primary_heating_class": PrimaryHeatingEquipment2020.GAS_BOILER.value,
            "conditioned_area": 2500,
            "electric_utility": ElectricUtility.PACIFIC_POWER.value,
            "gas_utility": GasUtility.NW_NATURAL.value,
            "fireplace": Fireplace2020.FE_50_59.value,
            "fire_rebuild_qualification": YesNo.YES.value,
            "fire_resilience_bonus": FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC.value,
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

    @property
    def default_answers(self):
        return get_fire_default_answers()


class FireRebuild2021CompleteTestMixin(FireRebuild2021ProgramTestMixin):
    """This provide a complete ready for certification test"""

    @classmethod
    def setUpTestData(cls):
        super(FireRebuild2021CompleteTestMixin, cls).setUpTestData()

        collection_request = CollectionRequestMixin()
        collection_request.add_bulk_answers(get_fire_default_answers(), home_status=cls.home_status)
        annotation = AnnotationMixin()
        annotation.add_annotation(
            content="foo", type_slug="hpxml_gbr_id", content_object=cls.home_status
        )


class FireRebuild2021ProgramBase(
    FireRebuild2021CompleteTestMixin,
    CollectionRequestMixin,
    AnnotationMixin,
    AxisTestCase,
):
    """Fire Rebuild 2021 Base - Don't really add checks to this"""

    def test_setup(self):
        """Make sure that our test data works."""
        from axis.geographic.models import City
        from axis.home.models import EEPProgramHomeStatus
        from axis.company.models import Company

        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(EEPProgram.objects.count(), 2)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        self.assertEqual(
            Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).count(), 1
        )
        self.assertEqual(Company.objects.filter(company_type=Company.RATER_COMPANY_TYPE).count(), 1)
        self.assertEqual(
            Company.objects.filter(company_type=Company.PROVIDER_COMPANY_TYPE).count(),
            1,
        )

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_fire_rebuild_qualification(self):
        self.remove_collected_input("fire-rebuild-qualification", home_status=self.home_status)
        self.add_collected_input(
            value=YesNo.NO,
            measure_id="fire-rebuild-qualification",
            home_status=self.home_status,
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1, missing_checks)

        self.remove_collected_input(
            measure_id="fire-rebuild-qualification", home_status=self.home_status
        )
        self.add_collected_input(
            value=YesNo.YES,
            measure_id="fire-rebuild-qualification",
            home_status=self.home_status,
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_fire_resilience_bonus(self):
        self.remove_collected_input("fire-resilience-bonus", home_status=self.home_status)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)

        self.add_collected_input(
            value=FireResilienceBonus.RIGID_INSULATION,
            measure_id="fire-resilience-bonus",
            home_status=self.home_status,
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

    def test_program_checks(self):
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

        Home.objects.all().update(state="WA")
        self.home_status.refresh_from_db()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertIn(
            "Home is not eligible for the program - only OR homes qualify",
            str(missing_checks),
        )
