"""site.py - Axis"""

__author__ = "Steven K"
__date__ = "9/1/21 12:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from simulation.models import WaterHeater, DistributionSystem, Heater
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    DistributionSystemType,
)
from simulation.tests.factories import simulation_factory

from axis.company.tests.factories import (
    builder_organization_factory,
    rater_organization_factory,
    eep_organization_factory,
)
from axis.customer_eto.api_v3.serializers.project_tracker.site import (
    SiteSerializer,
    SitePropertySerializer,
    SiteTechnologySerializer,
    SiteProvidersSerializer,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.factories import floorplan_with_simulation_factory
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import home_factory

log = logging.getLogger(__name__)


class TestSiteSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")

        cls.eto = eep_organization_factory(slug="eto", is_customer=True, name="ETO", city=cls.city)

        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )

        cls.eep_program = basic_eep_program_factory(slug="eto-2020", owner=cls.eto)
        cls.home = home_factory(
            subdivision__city=cls.city, subdivision__builder_org=cls.builder_company
        )

        floorplan = floorplan_with_simulation_factory(
            owner=cls.rater_company, simulation__photovoltaic_count=1
        )

        cls.home_status = EEPProgramHomeStatus.objects.create(
            id=5555,
            eep_program=cls.eep_program,
            home=cls.home,
            company=cls.rater_company,
            floorplan=floorplan,
        )
        cls.project_tracker = FastTrackSubmission.objects.create(
            id=9999, home_status=cls.home_status
        )

    def test_site_structure(self):
        serializer = SiteSerializer(instance=self.project_tracker)
        data = serializer.to_representation(self.project_tracker)

        self.assertEqual(data["SiteType"], "STRUCTURE")
        self.assertEqual(data["SiteMarket"], "SINGLEFAM")
        self.assertEqual(type(data["SiteProperties"]), dict)
        self.assertEqual(type(data["SiteProperties"]["Properties"]), dict)
        self.assertEqual(type(data["SiteProperties"]["Properties"]["Property"]), list)
        self.assertEqual(len(data["SiteProperties"]["Properties"]["Property"]), 4)
        self.assertEqual(type(data["SiteTechnologies"]), dict)
        self.assertEqual(type(data["SiteTechnologies"]["Technology"]), list)

        self.assertEqual(type(data["ServiceProviders"]), dict)
        self.assertEqual(type(data["Associations"]), dict)
        self.assertEqual(type(data["Associations"]["Projects"]["Project"]), dict)
        self.assertEqual(
            data["Associations"]["Projects"]["Project"]["@ID"], self.project_tracker.home_status.id
        )
        self.assertEqual(
            type(data["Associations"]["Projects"]["Project"]["Measures"]["Measure"]), list
        )

    def test_site_property_serializer(self):
        serializer = SitePropertySerializer(instance=self.project_tracker)
        data = serializer.to_representation(self.project_tracker)

        self.assertIn("Properties", data)
        self.assertIn("Property", data["Properties"])
        self.assertEqual(len(data["Properties"]["Property"]), 4)

        simulation = self.home_status.floorplan.simulation
        data = {x["Name"]: x["Value"] for x in data["Properties"]["Property"]}
        self.assertEqual(data["YRBLT"], simulation.project.construction_year)
        self.assertEqual(data["AREA"], str(int(round(simulation.conditioned_area, 0))))
        self.assertEqual(data["NUMFLRS"], simulation.floors_on_or_above_grade)
        self.assertEqual(data["FOUNDATION"], simulation.foundation_type.label)

    def test_site_technology_serializer_air_conditioner(self):
        simulation = simulation_factory(
            company=self.rater_company,
            heater_count=0,
            air_conditioner_count=1,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.update(simulation=simulation)
        serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
        data = serializer.to_representation(FastTrackSubmission.objects.get())
        self.assertIn("Technology", data)
        self.assertEqual(len(data["Technology"]), 1)
        data = data["Technology"][0]
        self.assertEqual(data["@ID"], "1")
        self.assertEqual(data["Code"], "ACCENTRAL")

    def test_site_technology_serializer_water(self):
        simulation = simulation_factory(
            company=self.rater_company,
            heater_count=0,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=1,
            water_heater__fuel=FuelType.NATURAL_GAS,
            water_heater__style=WaterHeaterStyle.CONVENTIONAL,
            water_heater__efficiency=0.9,
        )
        Floorplan.objects.update(simulation=simulation)

        with self.subTest("Conventional Gas Water Heater"):
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertIn("Technology", data)
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "GASDHWSTR")

        with self.subTest("Tankless Gas Water Heater"):
            WaterHeater.objects.all().update(style=WaterHeaterStyle.TANKLESS)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "GASDHWTNKLS")

        with self.subTest("Conventional Electric Water Heater"):
            WaterHeater.objects.all().update(
                style=WaterHeaterStyle.CONVENTIONAL, fuel=FuelType.ELECTRIC
            )
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "ELEDHWSTR")

        with self.subTest("Tankless Electric Water Heater"):
            WaterHeater.objects.all().update(
                style=WaterHeaterStyle.TANKLESS, fuel=FuelType.ELECTRIC
            )
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "ELEDHWTNKLS")

        with self.subTest("Air Source Heat Pump Water Heater"):
            WaterHeater.objects.all().update(style=WaterHeaterStyle.AIR_SOURCE_HEAT_PUMP)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "DHWHP")

        with self.subTest("Ground Source Heat Pump Water Heater"):
            WaterHeater.objects.all().update(style=WaterHeaterStyle.GROUND_SOURCE_HEAT_PUMP)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "ELEDHW")

        with self.subTest("Oil Water Heater"):
            WaterHeater.objects.all().update(style=WaterHeaterStyle.CONVENTIONAL, fuel=FuelType.OIL)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "OILDHW")

        with self.subTest("Propane Water Heater"):
            WaterHeater.objects.all().update(fuel=FuelType.PROPANE)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "PROPDHW")

    def test_site_technology_serializer_heating(self):
        simulation = simulation_factory(
            company=self.rater_company,
            heater_count=1,
            heater__fuel=FuelType.NATURAL_GAS,
            distribution_system__system_type=DistributionSystemType.FORCED_AIR,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.update(simulation=simulation)

        with self.subTest("Conventional Gas Forced Air Heater"):
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertIn("Technology", data)
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "GASFURN")

        with self.subTest("Gas Hydronic Heater"):
            DistributionSystem.objects.all().update(system_type=DistributionSystemType.HYDRONIC)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "GASCFRADHEAT")

        with self.subTest("Gas Ductless Heater"):
            DistributionSystem.objects.all().update(system_type=DistributionSystemType.DUCTLESS)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "GASFIREPLC")

        with self.subTest("Electric Forced air Heater"):
            Heater.objects.all().update(fuel=FuelType.ELECTRIC)
            DistributionSystem.objects.all().update(system_type=DistributionSystemType.FORCED_AIR)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "ELEFURN")

        with self.subTest("Electric Baseboard Heater"):
            DistributionSystem.objects.all().update(system_type=DistributionSystemType.RADIANT)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "BASEBOARD")

        with self.subTest("Electric Radiant Heater"):
            DistributionSystem.objects.all().update(system_type=DistributionSystemType.HYDRONIC)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "ELERADIANT")

        with self.subTest("Oil Heater"):
            Heater.objects.all().update(fuel=FuelType.OIL)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "OILHEAT")

        with self.subTest("Propane Heater"):
            Heater.objects.all().update(fuel=FuelType.PROPANE)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "PROPHEAT")

        with self.subTest("Wood Heater"):
            Heater.objects.all().update(fuel=FuelType.WOOD)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "WOODHEAT")

    def test_site_technology_serializer_ashp(self):
        simulation = simulation_factory(
            company=self.rater_company,
            heater_count=0,
            air_conditioner_count=0,
            air_source_heat_pump_count=1,
            distribution_system__system_type=DistributionSystemType.FORCED_AIR,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.update(simulation=simulation)

        with self.subTest("Ducted ASHP"):
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertIn("Technology", data)
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "HPDUCTED")

        with self.subTest("Ductless ASHP"):
            DistributionSystem.objects.all().update(system_type=DistributionSystemType.DUCTLESS)
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "HPDUCTLESS")

    def test_site_technology_serializer_gshp(self):
        simulation = simulation_factory(
            company=self.rater_company,
            heater_count=0,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=1,
            water_heater_count=0,
        )
        Floorplan.objects.update(simulation=simulation)

        with self.subTest("GSHP"):
            serializer = SiteTechnologySerializer(instance=FastTrackSubmission.objects.get())
            data = serializer.to_representation(FastTrackSubmission.objects.get())
            self.assertIn("Technology", data)
            self.assertEqual(len(data["Technology"]), 1)
            self.assertEqual(data["Technology"][0]["Code"], "HPGRNDSRC")

    def test_site_providers_serializer(self):
        context = {"gas_utility_code": "FOO", "electric_utility_code": "BAZ"}

        serializer = SiteProvidersSerializer(
            instance=FastTrackSubmission.objects.get(), context=context
        )
        data = serializer.to_representation(FastTrackSubmission.objects.get())
        self.assertIn("ServiceProviders", data)
        self.assertEqual(len(data["ServiceProviders"]["ProviderInfo"]), 2)
        self.assertEqual(data["ServiceProviders"]["ProviderInfo"][0]["Service"], "ELE")
        self.assertEqual(
            data["ServiceProviders"]["ProviderInfo"][0]["Provider"],
            context["electric_utility_code"],
        )
        self.assertEqual(data["ServiceProviders"]["ProviderInfo"][1]["Service"], "GAS")
        self.assertEqual(
            data["ServiceProviders"]["ProviderInfo"][1]["Provider"], context["gas_utility_code"]
        )
