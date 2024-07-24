"""test_eto_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "11/30/21 13:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random

from rest_framework.test import APITestCase

from axis.company.tests.factories import rater_organization_factory
from axis.core.tests.factories import rater_admin_factory
from axis.customer_eto.api_v3.serializers.reports.eps_report.simulation import (
    EPSReport2020SimulationSerializer,
    EPSReportSimulationSerializer,
    EPSReport2021SimulationSerializer,
)
from axis.customer_eto.strings import ETO_2021_CHECKSUMS
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
from simulation.models import Simulation
from simulation.tests.factories import analysis_factory

log = logging.getLogger(__name__)


class TestEPSReport2021SimulationSerializer(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")
        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )
        rater_admin_factory(company=cls.rater_company, username="eto_rater_admin")

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
            subdivision__city=cls.city,
            subdivision__name="Subdivision",
        )
        floorplan_with_simulation_factory(**cls.floorplan_factory_kwargs)
        cls.simulation = Simulation.objects.get()

    def test_multiple_analysis(self):
        """We found a bug with EPS reporting with Ekotrope is invovled."""
        analysis_factory(
            simulation=self.simulation,
            company=self.simulation.company,
            type=AnalysisType.OR_2020_ZONAL_DESIGN,
        )
        analysis_factory(
            simulation=self.simulation,
            company=self.simulation.company,
            type=AnalysisType.OR_2020_ZONAL_REFERENCE,
        )
        serializer = EPSReportSimulationSerializer(instance=self.simulation)
        self.assertRaises(ValueError, getattr, serializer, "data")

        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        expected = {
            "electric_per_month",
            "natural_gas_per_month",
            "conditioned_area",
            "construction_year",
            "electric_unit_cost",
            "gas_unit_cost",
            "insulated_walls",
            "insulated_floors",
            "efficient_windows",
            "efficient_lighting",
            "water_heater_efficiency",
            "heating_efficiency",
            "envelope_tightness",
            "pv_capacity_watts",
        }
        self.assertEqual(set(serializer.data.keys()), expected)

        serializer = EPSReport2021SimulationSerializer(instance=self.simulation)
        self.assertEqual(set(serializer.data.keys()), expected)
