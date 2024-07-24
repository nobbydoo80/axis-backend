"""test_eto_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 15:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import random
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.models import Company
from axis.company.tests.factories import rater_organization_factory, builder_organization_factory
from axis.customer_eto.api_v3.serializers.calculators import EPSSimulation2021Serializer
from axis.customer_eto.api_v3.serializers.calculators.eps_2021 import (
    EPS2021CalculatorSerializer,
)
from axis.customer_eto.enumerations import (
    ClimateLocation,
    PrimaryHeatingEquipment2020,
    ElectricUtility,
    GasUtility,
    SmartThermostatBrands2020,
    Fireplace2020,
    GridHarmonization2020,
    SolarElements2020,
    AdditionalIncentives2020,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.strings import ETO_2021_CHECKSUMS
from axis.customer_eto.tests.program_checks.test_eto_2021 import ETO2021ProgramTestMixin
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.geographic.tests.factories import real_city_factory
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    WaterHeaterLiquidVolume,
    HotWaterEfficiencyUnit,
    HeatingEfficiencyUnit,
    SourceType,
    AnalysisType,
    FoundationType,
    MechanicalVentilationType,
    HeatingCoolingCapacityUnit,
    ResidenceType,
    VentilationRateUnit,
    DistributionSystemType,
    Location,
)
from simulation.models import Location as SimLocation
from simulation.models import Simulation

log = logging.getLogger(__name__)


class EPS2021SimulationSerializerTests(TestCase):
    """This will test out the simulation serializer"""

    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")

        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )
        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        cls.floorplan_factory_kwargs = dict(
            owner=cls.rater_company,
            use_udrh_simulation=True,
            simulation__pct_improvement=30.0,
            simulation__conditioned_area=2150.0,
            simulation__source_type=random.choice([SourceType.EKOTROPE, SourceType.REMRATE_SQL]),
            simulation__version="99.99.99",  # Works for both
            simulation__flavor="Rate",  # Works for both
            simulation__design_model=AnalysisType.OR_2021_ZONAL_DESIGN,
            simulation__reference_model=AnalysisType.OR_2021_ZONAL_REFERENCE,
            simulation__residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            simulation__location__climate_zone__zone="4",
            simulation__location__climate_zone__moisture_regime="C",
            simulation__location__weather_station="Eugene, OR",
            simulation__analysis__source_qualifier=ETO_2021_CHECKSUMS[1][0],  # Zonal!
            simulation__analysis__source_name=ETO_2021_CHECKSUMS[1][1],  # Zonal!
            simulation__heater__fuel=FuelType.NATURAL_GAS,
            simulation__heater__efficiency=0.891,
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
        floorplan_with_simulation_factory(**cls.floorplan_factory_kwargs)
        cls.simulation = Simulation.objects.get()

    def test_eps_simulation_serializer(self):
        serializer = EPSSimulation2021Serializer()
        data = serializer.to_representation(self.simulation)

        design = self.simulation.as_designed_analysis
        reference = self.simulation.reference_analysis

        self.assertIsNotNone(data["climate_location"])
        self.assertEqual(data["conditioned_area"], self.simulation.conditioned_area)
        self.assertEqual(
            data["percent_improvement"], design.get_percent_improvement_over(reference)
        )
        self.assertEqual(
            data["code_heating_therms"], reference.fuel_usages.all().gas_heating_consumption_therms
        )
        self.assertEqual(
            data["code_heating_kwh"], reference.fuel_usages.all().electric_heating_consumption_kwh
        )
        self.assertEqual(
            data["code_cooling_kwh"], reference.fuel_usages.all().electric_cooling_consumption_kwh
        )
        self.assertEqual(
            data["code_hot_water_therms"],
            reference.fuel_usages.all().gas_water_heating_consumption_therms,
        )
        self.assertEqual(
            data["code_hot_water_kwh"],
            reference.fuel_usages.all().electric_water_heating_consumption_kwh,
        )
        self.assertEqual(
            data["code_lights_and_appliance_therms"],
            reference.fuel_usages.all().gas_lighting_and_appliances_consumption_therms,
        )
        self.assertEqual(
            data["code_lights_and_appliance_kwh"],
            reference.fuel_usages.all().electric_lighting_and_appliances_consumption_kwh,
        )
        self.assertEqual(data["code_pv_kwh"], reference.summary.solar_generation_kwh)
        self.assertEqual(data["code_electric_cost"], reference.fuel_usages.all().electric_cost)
        self.assertEqual(data["code_gas_cost"], reference.fuel_usages.all().gas_cost)
        self.assertEqual(
            data["improved_heating_therms"], design.fuel_usages.all().gas_heating_consumption_therms
        )
        self.assertEqual(
            data["improved_heating_kwh"], design.fuel_usages.all().electric_heating_consumption_kwh
        )
        self.assertEqual(
            data["improved_cooling_kwh"], design.fuel_usages.all().electric_cooling_consumption_kwh
        )
        self.assertEqual(
            data["improved_hot_water_therms"],
            design.fuel_usages.all().gas_water_heating_consumption_therms,
        )
        self.assertEqual(
            data["improved_hot_water_kwh"],
            design.fuel_usages.all().electric_water_heating_consumption_kwh,
        )
        self.assertEqual(
            data["improved_lights_and_appliance_therms"],
            design.fuel_usages.all().gas_lighting_and_appliances_consumption_therms,
        )
        self.assertEqual(
            data["improved_lights_and_appliance_kwh"],
            design.fuel_usages.all().electric_lighting_and_appliances_consumption_kwh,
        )
        self.assertEqual(data["improved_pv_kwh"], design.summary.solar_generation_kwh)
        self.assertEqual(data["improved_electric_cost"], design.fuel_usages.all().electric_cost)
        self.assertEqual(data["improved_gas_cost"], design.fuel_usages.all().gas_cost)
        self.assertEqual(
            data["has_tankless_water_heater"],
            self.simulation.water_heaters.filter(style=WaterHeaterStyle.TANKLESS).exists(),
        )
        self.assertEqual(
            data["has_gas_hot_water"],
            self.simulation.water_heaters.filter(fuel=FuelType.NATURAL_GAS).exists(),
        )
        self.assertEqual(
            data["has_heat_pump_water_heater"], self.simulation.water_heaters.heat_pumps().exists()
        )
        self.assertEqual(data["hot_water_ef"], self.simulation.water_heaters.get().efficiency)
        self.assertEqual(
            data["has_gas_heater"],
            self.simulation.heaters.filter(fuel=FuelType.NATURAL_GAS).exists(),
        )
        self.assertEqual(data["gas_furnace_afue"], self.simulation.heaters.get().efficiency)
        self.assertEqual(data["has_ashp"], self.simulation.air_source_heat_pumps.exists())

    def test_climate_location(self):
        data = (
            ("Eugene, OR", ClimateLocation.EUGENE),
            ("North Bend, OR", ClimateLocation.NORTH_BEND),
            ("PORTLAND INTERNATIONAL AP, OR", ClimateLocation.PORTLAND),
            ("Pendleton, OR", ClimateLocation.PENDLETON),
            ("Astoria, OR", ClimateLocation.ASTORIA),
            ("Portland, OR", ClimateLocation.PORTLAND),
            ("EUGENE MAHLON SWEET ARPT [UO], OR", ClimateLocation.EUGENE),
            ("Salem, OR", ClimateLocation.SALEM),
            ("Redmond, OR", ClimateLocation.REDMOND),
            ("Burns, OR", ClimateLocation.BURNS),
            ("AURORA STATE, OR", ClimateLocation.PORTLAND),
            ("REDMOND ROBERTS FIELD, OR", ClimateLocation.REDMOND),
            ("Medford, OR", ClimateLocation.MEDFORD),
        )

        for input_data, expected in data:
            SimLocation.objects.all().update(weather_station=input_data)
            serializer = EPSSimulation2021Serializer(instance=Simulation.objects.get())
            data = serializer.to_representation(Simulation.objects.get())
            self.assertEqual(data["climate_location"], expected)


class ETO2021CalculatorAPITest(ETO2021ProgramTestMixin, APITestCase, CollectionRequestMixin):
    @classmethod
    def setUpTestData(cls):
        super(ETO2021CalculatorAPITest, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)
        cls.rater_company.update_permissions()

    def create(self, url, user, data=None, data_format="json"):
        """
        Return an object with the create action.
        """
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data=data, format=data_format)
        data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        return data

    def test_raw_calculator_api_post(self):
        """Test good data to Calculator"""
        data = self.default_program_data
        results = self.create(
            url=reverse_lazy("api_v3:eto_2021-calculator"),
            user=self.user,
            data=data,
        )

        for k, v in data.items():
            self.assertEqual(results["input"][k], v)

    def test_raw_calculator_api_fail_missing_data(self):
        """Test bad data to Calculator"""
        url = reverse_lazy("api_v3:eto_2021-calculator")

        data = self.default_program_data
        data.pop("climate_location")
        data.pop("conditioned_area")

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data=data, data_format="json")
        response_data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        self.assertEqual(len(response_data.get("errors").keys()), 2, response_data.get("errors"))

        self.assertEqual(
            set(response_data.get("errors").keys()), {"climate_location", "conditioned_area"}
        )

    def test_home_status_api_post_fail_no_data(self):
        url = reverse_lazy("api_v3:eto_2021-generate", kwargs={"pk": self.home_status.pk})

        Floorplan.objects.update(simulation=None)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        response_data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("errors", response_data)
        self.assertEqual(
            response_data["status"],
            "Input Error: 1 Simulation errors; 1 checklist response errors",
        )
        self.assertIn("simulation", response_data["errors"])
        self.assertEqual(len(response_data["errors"]["simulation"]), 1)
        self.assertIn("checklist_questions", response_data["errors"])
        self.assertEqual(len(response_data["errors"]["checklist_questions"]), 1)

    def test_electric_utility(self):
        electric_utility = self.home_status.home.get_electric_company()
        self.assertIsNotNone(electric_utility)
        serializer = EPS2021CalculatorSerializer()

        data = {
            "pacific-power": ElectricUtility.PACIFIC_POWER,
            "portland-electric": ElectricUtility.PORTLAND_GENERAL,
            "foo": ElectricUtility.NONE,
            None: ElectricUtility.NONE,
        }

        for slug, expected in data.items():
            if slug is not None:
                Company.objects.filter(id=electric_utility.id).update(slug=slug)
                company = Company.objects.get(id=electric_utility.id)
            else:
                company = None
            result = serializer.get_electric_utility(company)
            self.assertEqual(result, expected)

    def test_gas_utility(self):
        gas_utility = self.home_status.home.get_gas_company()
        self.assertIsNotNone(gas_utility)
        serializer = EPS2021CalculatorSerializer()

        data = {
            "nw-natural-gas": GasUtility.NW_NATURAL,
            "cascade-gas": GasUtility.CASCADE,
            "avista": GasUtility.AVISTA,
            "foo": GasUtility.NONE,
            None: GasUtility.NONE,
        }

        for slug, expected in data.items():
            if slug is not None:
                Company.objects.filter(id=gas_utility.id).update(slug=slug)
                company = Company.objects.get(id=gas_utility.id)
            else:
                company = None
            result = serializer.get_gas_utility(company)
            self.assertEqual(result, expected)

    def test_inputs(self):
        """Test out the inputs will traverse"""
        data = {
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.GAS_FURNACE,
            "smart-thermostat-brand": SmartThermostatBrands2020.BRYANT,
            "has-gas-fireplace": Fireplace2020.FE_60_69,
            "grid-harmonization-elements": GridHarmonization2020.ALL,
            "eto-additional-incentives": AdditionalIncentives2020.ENERGY_SMART,
            "solar-elements": SolarElements2020.SOLAR_PV,
            "ets-annual-etsa-kwh": "200",
        }
        self.add_bulk_answers(data=data, home_status=self.home_status)
        serializer = EPS2021CalculatorSerializer(data={"home_status": self.home_status.id})
        self.assertTrue(serializer.is_valid(raise_exception=True))

        self.assertEqual(
            serializer.calculator.primary_heating_class,
            PrimaryHeatingEquipment2020.GAS_FURNACE,
        )
        self.assertEqual(
            serializer.calculator.thermostat_brand,
            SmartThermostatBrands2020.BRYANT,
        )
        self.assertEqual(
            serializer.calculator.fireplace,
            Fireplace2020.FE_60_69,
        )
        self.assertEqual(
            serializer.calculator.grid_harmonization_elements,
            GridHarmonization2020.ALL,
        )
        self.assertEqual(
            serializer.calculator.eps_additional_incentives,
            AdditionalIncentives2020.ENERGY_SMART,
        )
        self.assertEqual(
            serializer.calculator.solar_elements,
            SolarElements2020.SOLAR_PV,
        )
        self.assertEqual(serializer.calculator.improved.pv_kwh, 200.0)

    def test_home_status_api_post_solid_data(self):
        url = reverse_lazy("api_v3:eto_2021-generate", kwargs={"pk": self.home_status.pk})

        self.add_collected_input(
            value=PrimaryHeatingEquipment2020.GAS_FURNACE.value,
            measure_id="primary-heating-equipment-type",
            home_status=self.home_status,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        # response_data = response.data
        # print(response_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        # We don't save it we simply want the calculator to verify our values.
        serializer = EPS2021CalculatorSerializer(data={"home_status": self.home_status.pk})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.to_internal_value(data={"home_status": self.home_status.pk})
        calculator = serializer.calculator

        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        fastrack_1 = FastTrackSubmission.objects.get()

        self.assertEqual(fastrack_1.home_status, self.home_status)

        self.assertEqual(fastrack_1.project_id, "")
        self.assertIsNone(fastrack_1.solar_project_id)

        self.assertGreater(fastrack_1.eps_score, 1)
        self.assertEqual(fastrack_1.eps_score, calculator.improved_calculations.eps_score)
        self.assertGreater(fastrack_1.eps_score_built_to_code_score, 1)
        self.assertEqual(
            fastrack_1.eps_score_built_to_code_score, calculator.code_calculations.code_eps_score
        )
        self.assertGreater(fastrack_1.percent_improvement, 0.01)
        self.assertEqual(
            fastrack_1.percent_improvement,
            round(calculator.improvement_data.floored_improvement_breakout.mbtu, 2),
        )
        self.assertGreater(fastrack_1.percent_improvement_kwh, 0.01)
        self.assertEqual(
            fastrack_1.percent_improvement_kwh,
            round(calculator.improvement_data.floored_improvement_breakout.kwh, 2),
        )
        self.assertGreater(fastrack_1.percent_improvement_therms, 0.01)
        self.assertEqual(
            fastrack_1.percent_improvement_therms,
            round(calculator.improvement_data.floored_improvement_breakout.therms, 2),
        )

        self.assertGreater(fastrack_1.builder_incentive, Decimal("1000.00"))
        self.assertEqual(fastrack_1.builder_incentive, calculator.incentives.builder_incentive)

        self.assertGreater(fastrack_1.rater_incentive, Decimal("299.00"))
        self.assertEqual(fastrack_1.rater_incentive, calculator.incentives.verifier_incentive)
        self.assertGreater(fastrack_1.carbon_score, 1)
        self.assertEqual(
            fastrack_1.carbon_score, round(calculator.improved_calculations.carbon_score, 1)
        )

        self.assertGreater(fastrack_1.carbon_built_to_code_score, 1)
        self.assertEqual(
            fastrack_1.carbon_built_to_code_score,
            round(calculator.code_calculations.code_carbon_score, 1),
        )
        self.assertGreater(fastrack_1.estimated_annual_energy_costs, Decimal("100.0"))
        self.assertEqual(
            round(float(fastrack_1.estimated_annual_energy_costs), 2),
            round(calculator.annual_cost, 2),
        )
        self.assertGreater(fastrack_1.estimated_monthly_energy_costs, Decimal("5.0"))
        self.assertEqual(
            round(float(fastrack_1.estimated_monthly_energy_costs), 2),
            round(calculator.monthly_cost, 2),
        )

        self.assertGreater(fastrack_1.estimated_annual_energy_costs_code, Decimal("0.1"))
        self.assertEqual(
            round(float(fastrack_1.estimated_annual_energy_costs_code), 2),
            round(calculator.annual_cost_code, 2),
        )
        self.assertGreater(fastrack_1.estimated_monthly_energy_costs_code, Decimal("0.1"))
        self.assertEqual(
            round(float(fastrack_1.estimated_monthly_energy_costs_code), 2),
            round(calculator.monthly_cost_code, 2),
        )

        self.assertGreater(fastrack_1.similar_size_eps_score, 1)
        self.assertEqual(
            fastrack_1.similar_size_eps_score, round(calculator.projected.similar_size_eps, 0)
        )
        self.assertGreater(fastrack_1.similar_size_carbon_score, 1)
        self.assertEqual(
            fastrack_1.similar_size_carbon_score, round(calculator.projected.similar_size_carbon, 1)
        )
        self.assertGreater(fastrack_1.builder_gas_incentive, Decimal("500.00"))
        self.assertEqual(
            round(float(fastrack_1.builder_electric_incentive), 2),
            round(calculator.incentives.builder_electric_incentive, 2),
        )
        self.assertGreater(fastrack_1.builder_electric_incentive, Decimal("100.00"))
        self.assertEqual(
            round(float(fastrack_1.builder_gas_incentive), 2),
            round(calculator.incentives.builder_gas_incentive, 2),
        )
        self.assertGreater(fastrack_1.rater_gas_incentive, Decimal("100.00"))
        self.assertEqual(
            round(float(fastrack_1.rater_gas_incentive), 2),
            round(calculator.incentives.verifier_gas_incentive, 2),
        )
        self.assertGreater(fastrack_1.rater_electric_incentive, Decimal("10.00"))
        self.assertEqual(
            round(float(fastrack_1.rater_electric_incentive), 2),
            round(calculator.incentives.verifier_electric_incentive, 2),
        )
        self.assertGreater(fastrack_1.therm_savings, Decimal("10.0"))
        self.assertEqual(
            round(float(fastrack_1.therm_savings), 2),
            round(calculator.improvement_data.savings.therms, 2),
        )
        self.assertGreater(fastrack_1.kwh_savings, Decimal("10.0"))
        self.assertEqual(
            round(float(fastrack_1.kwh_savings), 2),
            round(calculator.improvement_data.savings.kwh, 2),
        )
        self.assertGreater(fastrack_1.mbtu_savings, Decimal("2.00"))
        self.assertEqual(
            round(float(fastrack_1.mbtu_savings), 2),
            round(calculator.improvement_data.savings.mbtu, 2),
        )

        self.assertEqual(fastrack_1.eps_calculator_version, datetime.date(2021, 10, 1))

        self.assertIsNone(fastrack_1.original_builder_electric_incentive)
        self.assertIsNone(fastrack_1.original_builder_gas_incentive)
        self.assertIsNone(fastrack_1.original_builder_incentive)
        self.assertIsNone(fastrack_1.original_rater_electric_incentive)
        self.assertIsNone(fastrack_1.original_rater_gas_incentive)
        self.assertIsNone(fastrack_1.original_rater_incentive)
        self.assertIsNone(fastrack_1.payment_change_user)
        self.assertIsNone(fastrack_1.payment_change_datetime)
        self.assertIsNone(fastrack_1.payment_revision_comment)

        self.assertEqual(fastrack_1.net_zero_eps_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.energy_smart_homes_eps_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.net_zero_solar_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.energy_smart_homes_solar_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.original_net_zero_eps_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.original_energy_smart_homes_eps_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.original_net_zero_solar_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.original_energy_smart_homes_solar_incentive, Decimal("0.00"))

        # WA Code Credit
        self.assertEqual(fastrack_1.required_credits_to_meet_code, 0)
        self.assertEqual(fastrack_1.achieved_total_credits, 0)
        self.assertEqual(fastrack_1.eligible_gas_points, 0)
        self.assertEqual(fastrack_1.code_credit_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.thermostat_incentive, Decimal("0.00"))
        self.assertEqual(fastrack_1.fireplace_incentive, Decimal("0.00"))

        self.assertGreater(fastrack_1.electric_cost_per_month, Decimal("1.00"))
        self.assertEqual(
            round(float(fastrack_1.electric_cost_per_month), 2),
            round(calculator.improved.electric_cost / 12.0, 2),
        )
        self.assertGreater(fastrack_1.natural_gas_cost_per_month, Decimal("1.00"))
        self.assertEqual(
            round(float(fastrack_1.natural_gas_cost_per_month), 2),
            round(calculator.improved.gas_cost / 12.0, 2),
        )
        self.assertGreater(fastrack_1.improved_total_kwh, 0.0)
        self.assertEqual(
            fastrack_1.improved_total_kwh,
            calculator.improved.total_kwh,
        )
        self.assertGreater(fastrack_1.improved_total_therms, 0.0)
        self.assertEqual(
            fastrack_1.improved_total_therms,
            calculator.improved.total_therms,
        )
        self.assertEqual(fastrack_1.solar_hot_water_kwh, 0.0)
        self.assertEqual(
            fastrack_1.solar_hot_water_kwh,
            calculator.improved.solar_hot_water_kwh,
        )
        self.assertEqual(fastrack_1.solar_hot_water_therms, 0.0)
        self.assertEqual(
            fastrack_1.solar_hot_water_therms,
            calculator.improved.solar_hot_water_therms,
        )
        self.assertEqual(fastrack_1.pv_kwh, 0.0)
        self.assertEqual(
            fastrack_1.pv_kwh,
            calculator.improved.pv_kwh,
        )
        self.assertGreater(fastrack_1.projected_carbon_consumption_electric, 0.0)
        self.assertEqual(
            fastrack_1.projected_carbon_consumption_electric,
            calculator.projected.projected_carbon_consumption.electric_home_kwh
            + calculator.projected.projected_carbon_consumption.gas_home_kwh,
        )
        self.assertGreater(fastrack_1.projected_carbon_consumption_natural_gas, 0.0)
        self.assertEqual(
            fastrack_1.projected_carbon_consumption_natural_gas,
            calculator.projected.projected_carbon_consumption.gas_home_therms,
        )

        response = self.client.post(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
        )

        self.assertEqual(FastTrackSubmission.objects.count(), 1)
        FastTrackSubmission.objects.get()
