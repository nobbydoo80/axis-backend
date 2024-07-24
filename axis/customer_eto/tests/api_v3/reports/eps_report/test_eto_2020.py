"""test_eto_2020.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 15:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import random
from functools import cached_property
from io import BytesIO

from PyPDF2 import PdfReader
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    WaterHeaterLiquidVolume,
    HotWaterEfficiencyUnit,
    HeatingEfficiencyUnit,
    DistributionSystemType,
    SourceType,
    Location,
    MechanicalVentilationType,
    AnalysisType,
    ResidenceType,
    HeatingCoolingCapacityUnit,
    VentilationRateUnit,
    CostUnit,
)
from simulation.tests.factories import reference_and_design_analysis_simulation_factory

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.tests.factories import rater_organization_factory
from axis.core.tests.factories import rater_admin_factory
from axis.customer_eto.api_v3.serializers.reports.eps_report.eto_2020 import EPSReport2020Serializer
from axis.customer_eto.api_v3.serializers.reports.eps_report.simulation import (
    EPSReport2020SimulationSerializer,
)
from axis.customer_eto.enumerations import PrimaryHeatingEquipment2020
from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data
from axis.customer_eto.models import FastTrackSubmission, ETOAccount
from axis.customer_eto.strings import ETO_2020_CHECKSUMS
from axis.customer_eto.tests.program_checks.test_eto_2020 import ETO2020ProgramTestMixin
from axis.eep_program.models import EEPProgram
from axis.geographic.tests.factories import real_city_factory

log = logging.getLogger(__name__)


class TestEPSReport2020SimulationSerializer(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")
        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )
        rater_admin_factory(company=cls.rater_company, username="eto_rater_admin")

        cls.simulation_kwargs = dict(
            company=cls.rater_company,
            pct_improvement=21.0,
            conditioned_area=2150.0,
            source_type=random.choice([SourceType.EKOTROPE, SourceType.REMRATE_SQL]),
            version="99.99.99",  # Works for both
            flavor="Rate",  # Works for both
            design_model=AnalysisType.OR_2020_ZONAL_DESIGN,
            reference_model=AnalysisType.OR_2020_ZONAL_REFERENCE,
            residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            location__climate_zone__zone="4",
            location__climate_zone__moisture_regime="C",
            location__weather_station="Eugene",
            analysis__source_qualifier=ETO_2020_CHECKSUMS[1][0],  # Zonal!
            analysis__source_name=ETO_2020_CHECKSUMS[1][1],  # Zonal!
            heater__fuel=FuelType.ELECTRIC,
            heater__efficiency_unit=HeatingEfficiencyUnit.AFUE,
            heater__capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            water_heater__style=WaterHeaterStyle.CONVENTIONAL,
            water_heater__fuel=FuelType.ELECTRIC,
            water_heater__efficiency=0.92,
            water_heater__efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
            water_heater__tank_units=WaterHeaterLiquidVolume.GALLON,
            mechanical_ventilation__type=MechanicalVentilationType.SUPPLY_ONLY,
            mechanical_ventilation__hour_per_day=24.0,
            mechanical_ventilation__ventilation_rate=3500.0,
            mechanical_ventilation__ventilation_rate_unit=VentilationRateUnit.CFM,
            distribution_system__system_type=DistributionSystemType.RADIANT,
            appliances__refrigerator_consumption=700,
            appliances__refrigerator_location=Location.CONDITIONED_SPACE,
            appliances__dishwasher_consumption=300,
            appliances__clothes_washer_efficiency=0.5,
            appliances__clothes_washer_label_electric_consumption=500,
            appliances__clothes_dryer_efficiency=2.5,
            appliances__clothes_dryer_location=Location.CONDITIONED_SPACE,
            appliances__clothes_dryer_fuel=FuelType.ELECTRIC,
            appliances__oven_fuel=FuelType.ELECTRIC,
            air_conditioner_count=0,
            utility_rate_fuel__electric={"name": "PAC-Jan2021"},
            utility_rate_fuel__natural_gas={"name": "NWN_OR-Jan2021"},
        )

        cls.simulation = reference_and_design_analysis_simulation_factory(**cls.simulation_kwargs)

    def test_conditioned_area(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        self.assertEqual(
            serializer.data["conditioned_area"],
            int(self.simulation.conditioned_area),
        )

    def test_construction_year(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        self.assertEqual(
            serializer.data["construction_year"],
            self.simulation.project.construction_year,
        )

    def test_electric_unit_cost(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        rate = self.simulation.utility_rates.get(fuel=FuelType.ELECTRIC)
        value = rate.seasonal_rates.first().block_rates.first().cost
        value = value / 100.0 if rate.cost_units == CostUnit.USC else value
        self.assertEqual(
            serializer.data["electric_unit_cost"],
            value,
        )

    def test_gas_unit_cost(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        try:
            rate = self.simulation.utility_rates.get(fuel=FuelType.NATURAL_GAS)
            value = rate.seasonal_rates.first().block_rates.first().cost
            value = value / 100.0 if rate.cost_units == CostUnit.USC else value
        except (AttributeError, ObjectDoesNotExist):
            value = 0.0
        self.assertEqual(
            serializer.data["gas_unit_cost"],
            value,
        )

    def test_insulated_walls(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        wall = self.simulation.above_grade_walls.all().get_dominant_by_r_value()
        if wall:
            cavity = wall.type.cavity_insulation_r_value or 0.0
            continuous = wall.type.continuous_insulation_r_value or 0.0
            value = cavity + continuous
            self.assertEqual(
                serializer.data["insulated_walls"],
                f"R-{value:.0f}",
            )
        else:
            self.assertEqual(serializer.data["insulated_walls"], "")

    def test_insulated_floors(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        floor = self.simulation.frame_floors.all().get_dominant_by_r_value()
        if floor:
            cavity = floor.type.cavity_insulation_r_value or 0.0
            continuous = floor.type.continuous_insulation_r_value or 0.0
            value = cavity + continuous
        else:
            value = self.simulation.slabs.all().dominant_underslab_r_value
        self.assertEqual(
            serializer.data["insulated_floors"],
            f"R-{value:.0f}",
        )

    def test_efficient_windows(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        value = self.simulation.windows.all().dominant_u_value
        self.assertEqual(serializer.data["efficient_windows"], f"U-{value:.2f}")

    def test_efficient_lighting(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        value = self.simulation.lights.interior_led_percent
        self.assertEqual(serializer.data["efficient_lighting"], f"{value:.1f} %")

    def test_water_heater_efficiency(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        dominant = self.simulation.mechanical_equipment.dominant_water_heating_equipment.equipment
        value = f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}"
        self.assertEqual(serializer.data["water_heater_efficiency"], value)

    def test_heating_efficiency(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        dominant = self.simulation.mechanical_equipment.dominant_heating_equipment.equipment
        value = f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}"
        self.assertEqual(serializer.data["heating_efficiency"], value)

    def test_envelope_tightness(self):
        serializer = EPSReport2020SimulationSerializer(instance=self.simulation)
        value = (
            f"{self.simulation.infiltration.infiltration_value:.2f}"
            f" {self.simulation.infiltration.get_infiltration_unit_display()}"
        )
        self.assertEqual(serializer.data["envelope_tightness"], value)


class TestEPSViewSet2020(ETO2020ProgramTestMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestEPSViewSet2020, cls).setUpTestData()
        from axis.core.tests.factories import rater_user_factory

        cls.user = rater_user_factory(company=cls.rater_company)
        # Generate Fasttrack Data
        collection_request = CollectionRequestMixin()
        answers = {
            "primary-heating-equipment-type": PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
            "ceiling-r-value": 99.2,
        }
        collection_request.add_bulk_answers(answers, home_status=cls.home_status)

        _errors = get_legacy_calculation_data(cls.home_status, return_errors=True)
        cls.project_tracker = FastTrackSubmission.objects.get()

    def test_eto_2020_report_generation(self):
        url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        document = PdfReader(BytesIO(response.content))

        address = self.home_status.home.get_home_address_display(
            include_city_state_zip=True, include_lot_number=False
        )

        self.assertEqual(document.metadata["/Title"], address)
        self.assertEqual(document.metadata["/Author"], self.user.get_full_name())
        self.assertEqual(len(document.pages), 2)
        self.assertIsNone(document.get_fields())

    def test_eto_2021_report_generation(self):
        url = reverse_lazy("api_v3:eps_report-report", kwargs={"pk": self.home_status.pk})
        EEPProgram.objects.filter(slug="eto-2020").update(slug="eto-2021")
        self.assertEqual(EEPProgram.objects.filter(slug="eto-2021").count(), 1)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        document = PdfReader(BytesIO(response.content))

        address = self.home_status.home.get_home_address_display(
            include_city_state_zip=True, include_lot_number=False
        )

        self.assertEqual(document.metadata["/Title"], address)
        self.assertEqual(document.metadata["/Author"], self.user.get_full_name())
        self.assertEqual(len(document.pages), 2)
        self.assertIsNone(document.get_fields())

    def test_calculator_core_data(self):
        """Verify the Core serializer info is present"""
        serializer = EPSReport2020Serializer(instance=self.project_tracker)
        data = serializer.data
        self.assertIsNotNone(data)

        with self.subTest("Home / Home Status Elements"):
            self.assertIn(self.home_status.home.street_line1, data["street_line"])
            self.assertEqual(self.home_status.home.city.name, data["city"])
            self.assertEqual(self.home_status.home.state, data["state"])
            self.assertEqual(self.home_status.home.zipcode, data["zipcode"])

        with self.subTest("Rater"):
            self.assertEqual(str(self.home_status.company), data["rater"])

        with self.subTest("Electric"):
            self.assertEqual(str(self.home_status.get_electric_company()), data["electric_utility"])

        with self.subTest("Gas"):
            self.assertEqual(str(self.home_status.get_gas_company()), data["gas_utility"])

    def test_serializer_floorplan_type(self):
        serializer = EPSReport2020Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("PRELIMINARY", serializer.data["floorplan_type"])
        self.assertEqual(None, serializer.data["eps_issue_date"])

        self.home_status.certification_date = datetime.date.today()
        self.home_status.save()
        serializer = EPSReport2020Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("OFFICIAL", serializer.data["floorplan_type"])
        self.assertEqual(
            str(self.home_status.certification_date), serializer.data["eps_issue_date"]
        )

    def test_serializer_rater_ccb(self):
        serializer = EPSReport2020Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual(self.home_status.home.state, "OR")
        self.assertIsNotNone(self.rater_eto_account.ccb_number)
        self.assertIn(self.rater_eto_account.ccb_number, serializer.data["rater_ccb"])

        from axis.home.models import Home

        Home.objects.all().update(state="WA")
        serializer = EPSReport2020Serializer(instance=FastTrackSubmission.objects.get())
        self.assertEqual("", serializer.data["rater_ccb"])

        Home.objects.all().update(state="OR")
        ETOAccount.objects.all().update(ccb_number=None)
        serializer = EPSReport2020Serializer(instance=FastTrackSubmission.objects.get())
        self.assertIn("--", serializer.data["rater_ccb"])

    def test_serializer_simulation_components(self):
        from simulation.models import FrameFloorType

        FrameFloorType.objects.all().update(
            cavity_insulation_r_value=5.0, continuous_insulation_r_value=2.0
        )
        serializer = EPSReport2020Serializer(instance=self.project_tracker)
        simulation = FastTrackSubmission.objects.get().home_status.floorplan.simulation
        with self.subTest("Simulation Year"):
            self.assertEqual(serializer.data["year"], simulation.project.construction_year)
        with self.subTest("Simulation SQ Footage"):
            self.assertEqual(
                serializer.data["square_footage"], f"{round(simulation.conditioned_area):,}"
            )
        with self.subTest("Unit Costs"):
            rate = simulation.utility_rates.get(fuel=FuelType.ELECTRIC)
            try:
                self.assertEqual(
                    serializer.data["kwh_cost"],
                    f"${rate.seasonal_rates.first().block_rates.first().cost:,.2f}",
                )
            except AssertionError:
                # Cent conversion
                self.assertEqual(
                    serializer.data["kwh_cost"],
                    f"${rate.seasonal_rates.first().block_rates.first().cost/100.0:,.2f}",
                )

            rate = simulation.utility_rates.get(fuel=FuelType.NATURAL_GAS)
            try:
                self.assertEqual(
                    serializer.data["therm_cost"],
                    f"${rate.seasonal_rates.first().block_rates.first().cost:,.2f}",
                )
            except AssertionError:
                # Cent conversion
                self.assertEqual(
                    serializer.data["therm_cost"],
                    f"${rate.seasonal_rates.first().block_rates.first().cost/100.0:,.2f}",
                )

        with self.subTest("Insulated Walls"):
            dominant = simulation.above_grade_walls.all().get_dominant_by_r_value()
            if dominant:
                cavity = dominant.type.cavity_insulation_r_value or 0.0
                continous = dominant.type.continuous_insulation_r_value or 0.0
                self.assertEqual(f"R-{cavity + continous:.0f}", serializer.data["insulated_walls"])
        with self.subTest("Insulated Floors"):
            dominant = simulation.frame_floors.all().get_dominant_by_r_value()
            value = 0.0
            if dominant:
                cavity = dominant.type.cavity_insulation_r_value or 0.0
                continous = dominant.type.continuous_insulation_r_value or 0.0
                value = cavity + continous
                self.assertEqual(value, 7.0)  # Sent from above.
            if value == 0.0:
                value = simulation.slabs.all().dominant_underslab_r_value or 0.0
            value = f"R-{value:.0f}" if value != 0.0 else ""
            self.assertEqual(value, serializer.data["insulated_floors"])
        with self.subTest("Efficiency Windows"):
            value = simulation.windows.all().dominant_u_value
            self.assertEqual(f"U-{value:.2f}", serializer.data["efficient_windows"])
        with self.subTest("Efficient Lighting"):
            value = simulation.lights.interior_led_percent
            self.assertEqual(f"{value:.1f} %", serializer.data["efficient_lighting"])
        with self.subTest("Water Heater"):
            dominant = simulation.mechanical_equipment.dominant_water_heating_equipment.equipment
            self.assertEqual(
                f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}",
                serializer.data["water_heater"],
            )
        with self.subTest("Heater"):
            dominant = simulation.mechanical_equipment.dominant_heating_equipment.equipment
            self.assertEqual(
                f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}",
                serializer.data["space_heating"],
            )
        with self.subTest("Envelope Tightness"):
            self.assertEqual(
                f"{simulation.infiltration.infiltration_value:.2f} "
                f"{simulation.infiltration.get_infiltration_unit_display()}",
                serializer.data["envelope_tightness"],
            )

    def test_fastrack_model_backed_data(self):
        defaults = {
            "solar_hot_water_kwh": 1,
            "pv_kwh": 1,
            "solar_hot_water_therms": 1,
            "improved_total_kwh": 10,
            "improved_total_therms": 5,
            "projected_carbon_consumption_electric": 17,
            "projected_carbon_consumption_natural_gas": 13,
            "electric_cost_per_month": 10.0,
            "natural_gas_cost_per_month": 25.0,
        }
        FastTrackSubmission.objects.update(**defaults)
        serializer = EPSReport2020Serializer(instance=FastTrackSubmission.objects.get())

        self.assertEqual(serializer.data["electric_kwhs"], str(defaults["improved_total_kwh"]))
        self.assertEqual(serializer.data["net_electric_kwhs"], "8")
        self.assertEqual(serializer.data["total_electric_kwhs"], "12")
        self.assertEqual(
            serializer.data["natural_gas_therms"], str(defaults["improved_total_therms"])
        )
        self.assertEqual(serializer.data["total_natural_gas_therms"], "6")
        self.assertEqual(
            serializer.data["electric_tons_per_year"],
            float(defaults["projected_carbon_consumption_electric"]),
        )
        self.assertEqual(
            serializer.data["natural_gas_tons_per_year"],
            float(defaults["projected_carbon_consumption_natural_gas"]),
        )
        self.assertEqual(
            serializer.data["electric_per_month"],
            str(round(defaults["electric_cost_per_month"])),
        )
        self.assertEqual(
            serializer.data["natural_gas_per_month"],
            str(round(defaults["natural_gas_cost_per_month"])),
        )

    @cached_property
    def _answers(self):
        context = {"user__company": self.home_status.company}
        collector = ExcelChecklistCollector(self.home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    def test_checklist_responses(self):
        serializer = EPSReport2020Serializer(instance=self.project_tracker)

        with self.subTest("Ceiling R-Value"):
            self.assertIn("ceiling-r-value", self._answers)
            ans = self._answers["ceiling-r-value"]
            self.assertEqual(
                f"R-{float(ans):.0f}",
                serializer.data["insulated_ceiling"],
            )
