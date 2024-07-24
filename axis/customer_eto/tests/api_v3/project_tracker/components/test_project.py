"""project.py - Axis"""

__author__ = "Steven K"
__date__ = "8/27/21 09:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import json
import logging
import random

from django.test import TestCase
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    HeatingEfficiencyUnit,
    CoolingEfficiencyUnit,
    DistributionSystemType,
    HeatingCoolingCapacityUnit,
)
from simulation.tests.factories import simulation_factory

from axis.company.tests.factories import (
    eep_organization_factory,
    rater_organization_factory,
    builder_organization_factory,
)
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.floorplan.models import Floorplan
from axis.floorplan.tests.factories import floorplan_with_simulation_factory, floorplan_factory
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus, Home
from axis.home.tests.factories import home_factory
from .....api_v3.serializers.project_tracker.project import ProjectSerializer
from axis.customer_eto.api_v3.serializers.project_tracker.attributes import (
    ProjectAttributeSerializer,
)
from axis.customer_eto.api_v3.serializers.project_tracker.measures import MeasureSerializer
from .....api_v3.viewsets.project_tracker import home_subtype_str_dict
from .....calculator.eps_2021.base import HomeSubType
from .....eep_programs.eto_2022 import SolarElements2022
from .....eep_programs.washington_code_credit import WACCFuelType
from .....enumerations import YesNo
from .....models import FastTrackSubmission

log = logging.getLogger(__name__)


class TestProjectSerializer(TestCase):
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

    def test_project_structure(self):
        with self.subTest("ENH Projects"):
            serializer = ProjectSerializer(instance=self.project_tracker)
            data = serializer.to_representation(self.project_tracker)

            self.assertEqual(data["@ID"], str(self.home_status.id))
            self.assertEqual(data["Track"], "T00000000099")
            self.assertEqual(data["Phase"], "PENDING")
            self.assertEqual(data["Type"], "WHH")
            self.assertEqual(data["Program"], "ENH")
            self.assertEqual(
                data["Title"],
                self.home_status.home.get_home_address_display(include_lot_number=False, raw=True),
            )
            self.assertEqual(data["Notes"], "")
            self.assertEqual(type(data["ExternalReferences"]["ExternalReference"]), list)
            self.assertEqual(data["ExternalReferences"]["ExternalReference"][0]["Type"], "0041")
            self.assertEqual(
                data["ExternalReferences"]["ExternalReference"][0]["Value"],
                str(self.home_status.id),
            )
            self.assertEqual(data["ExternalReferences"]["ExternalReference"][1]["Type"], "0040")
            self.assertEqual(
                data["ExternalReferences"]["ExternalReference"][1]["Value"], "1732596E"
            )

            self.assertEqual(type(data["Attributes"]["Attribute"]), list)
            self.assertEqual(type(data["Measures"]["Measure"]), list)

        with self.subTest("SLE Projects"):
            serializer = ProjectSerializer(
                instance=self.project_tracker, context={"project_type": "SLE"}
            )
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["Program"], "SLE")
            self.assertEqual(data["Track"], "T00000000189")
            self.assertEqual(data["Type"], "SLERES")
            self.assertEqual(data["SubType"], "ENH")
            self.assertEqual(data["Phase"], "PAYMENT")

    def test_eps_attribute_structure(self):
        context = {
            "annual_cost_electric": 493.09,
            "annual_cost_gas": 46.877,
            "carbon_score": 3.514,
            "code_carbon_score": 4.448,
            "code_carbon_similar": 10.595,
            "eto_path": "Pathway 2",
            "home_config": "Gas Heat - Gas DHW",
            "code_eps_score": 59.009,
            "eps_similar": 120.890,
            "total_kwh": 3087.857,
            "total_therms": 313.112,
            "estimated_annual_cost": 539.971,
            "eps_score": 46.617,
            "estimated_monthly_cost": 44.997,
            "percentage_improvement": 21.0,
            "fire_rebuild_qualification": YesNo.YES.value,
            "solar_elements": SolarElements2022.SOLAR_PV,
        }

        serializer = ProjectAttributeSerializer(instance=self.project_tracker, context=context)
        data = serializer.to_representation(self.project_tracker)
        self.assertIn("Attributes", data)
        self.assertIn("Attribute", data["Attributes"])
        data = data["Attributes"]["Attribute"]

        self.assertEqual(len(data), 18)

        data = {x["Name"]: x["Value"] for x in data}
        self.assertEqual(data["ANNUALCOSTELEC"], 493.09)
        self.assertEqual(data["ANNUALCOSTGAS"], 46.877)
        self.assertEqual(data["CARBONSCORE"], 3.514)
        self.assertEqual(data["CRBNSCCODE"], 4.448)
        self.assertEqual(data["CARBONSIMILAR"], 10.595)
        self.assertEqual(data["DVLPMNTNMED"], self.home.subdivision.name)
        self.assertEqual(data["ETOPATH"], "Pathway 2")
        self.assertEqual(data["HOMECONFIG"], "Gas Heat - Gas DHW")
        self.assertEqual(data["PROJSOLAR"], "SOLARPV")
        self.assertEqual(data["EPSCODE"], 59.009)
        self.assertEqual(data["EPSSMILIARHOME"], 120.89)
        self.assertEqual(data["ESTANNKWH"], 3087.857)
        self.assertEqual(data["ESTANNTHERM"], 313.112)
        self.assertEqual(data["ESTAVGENCOST"], 539.971)
        self.assertEqual(data["FINALSCORE"], 46.617)
        self.assertEqual(data["MONTHAVG"], 44.997)
        self.assertEqual(data["PCTIMPROV"], "21.0")
        self.assertEqual(data["RESDISASTER"], "20WF")

    def test_wcc_attribute_structure(self):
        self.home_status.floorplan = None
        self.home_status.save()
        self.eep_program.slug = "washington-code-credit"
        self.eep_program.save()

        context = {"water_heater_fuel": WACCFuelType.ELECTRIC.value}

        serializer = ProjectAttributeSerializer(instance=self.project_tracker, context=context)
        data = serializer.to_representation(self.project_tracker)
        data = data["Attributes"]["Attribute"]

        self.assertEqual(len(data), 4)
        data = {x["Name"]: x["Value"] for x in data}
        self.assertEqual(data["DVLPMNTNMED"], self.home.subdivision.name)
        self.assertEqual(data["HOMECONFIG"], "Gas Heat - Ele DHW")
        self.assertEqual(data["DVLPMNTNMED"], self.home.subdivision.name)
        self.assertEqual(data["HOMECONFIG"], "Gas Heat - Ele DHW")

    def test_sub_types(self):
        with self.subTest("No Data"):
            for subtype in [HomeSubType.GHGW, HomeSubType.GHEW, HomeSubType.EHEW, HomeSubType.EHGW]:
                context = {
                    "electric_utility_code": None,
                    "gas_utility_code": None,
                    "home_config": home_subtype_str_dict[subtype],
                }
                serializer = ProjectSerializer(instance=self.project_tracker, context=context)
                data = serializer.to_representation(self.project_tracker)
                self.assertTrue("SubType" not in data)

        with self.subTest("Electric Partial Territory"):
            context = {
                "electric_utility_code": "PGE",
                "gas_utility_code": None,
                "home_config": home_subtype_str_dict[HomeSubType.GHGW],
            }

            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertTrue("SubType" not in data)

            context["home_config"] = home_subtype_str_dict[HomeSubType.EHEW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "9ET-EE")

            context["home_config"] = home_subtype_str_dict[HomeSubType.EHGW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "10ET-EG")

            context["home_config"] = home_subtype_str_dict[HomeSubType.GHEW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertTrue("SubType" not in data)

        with self.subTest("Gas Partial Territory"):
            context = {
                "electric_utility_code": None,
                "gas_utility_code": "NWN",
                "home_config": home_subtype_str_dict[HomeSubType.GHGW],
            }

            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "5GT-GG")

            context["home_config"] = home_subtype_str_dict[HomeSubType.EHEW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertTrue("SubType" not in data)

            context["home_config"] = home_subtype_str_dict[HomeSubType.EHGW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertTrue("SubType" not in data)

            context["home_config"] = home_subtype_str_dict[HomeSubType.GHEW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "6GT-GE")

        with self.subTest("Full Territory"):
            context = {
                "electric_utility_code": "PAC",
                "gas_utility_code": "NWN",
                "home_config": home_subtype_str_dict[HomeSubType.GHGW],
            }

            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "1FT-GG")

            context["home_config"] = home_subtype_str_dict[HomeSubType.EHEW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "3FT-EE")

            context["home_config"] = home_subtype_str_dict[HomeSubType.EHGW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "4FT-EG")

            context["home_config"] = home_subtype_str_dict[HomeSubType.GHEW]
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "2FT-GE")

        with self.subTest("SLE"):
            context = {
                "electric_utility_code": None,
                "gas_utility_code": None,
                "home_config": home_subtype_str_dict[HomeSubType.EHEW],
                "project_type": "SLE",
            }
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "ENH")

        with self.subTest("WA"):
            context = {
                "electric_utility_code": "PAC",
                "gas_utility_code": "NWN",
                "home_config": home_subtype_str_dict[HomeSubType.EHEW],
            }
            Home.objects.filter(id=self.project_tracker.home_status.home_id).update(state="WA")
            self.project_tracker.refresh_from_db()
            serializer = ProjectSerializer(instance=self.project_tracker, context=context)
            data = serializer.to_representation(self.project_tracker)
            self.assertEqual(data["SubType"], "WAEPS")


class TestMeasureSerializer(TestCase):
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

        floorplan = floorplan_factory(owner=cls.rater_company)

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
        future = datetime.datetime.now() + datetime.timedelta(days=180)
        cls.install_date = future.strftime("%Y-%m-%d")

    def test_eps_water_heater_measures(self):
        context = {
            "water_heater_brand": "water_heater_brand",
            "water_heater_model": "water_heater_model",
            "water_heater_heat_pump_sn": "water_heater_heat_pump_sn",
            "water_heater_gas_sn": "water_heater_gas_sn",
            "water_heater_tankless_sn": "water_heater_tankless_sn",
            "electric_load_profile": "electric_load_profile",
            "gas_load_profile": "gas_load_profile",
        }

        # HPWH
        with self.subTest("HPWH Testing"):
            simulation = simulation_factory(
                heater_count=0,
                air_conditioner_count=0,
                air_source_heat_pump_count=0,
                ground_source_heat_pump_count=0,
                water_heater_count=1,
                water_heater__fuel=FuelType.ELECTRIC,
                water_heater__style=WaterHeaterStyle.AIR_SOURCE_HEAT_PUMP,
                water_heater__efficiency=1.2,
            )
            Floorplan.objects.update(simulation=simulation)

            water_heater = simulation.water_heaters.get()
            self.assertTrue(water_heater.is_heat_pump())
            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )

            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
            data = serializer.data["Measures"]["Measure"][0]
            self.assertEqual(data["LoadProfile"]["kwh"], context["electric_load_profile"])
            self.assertEqual(data["LoadProfile"]["Therm"], context["gas_load_profile"])
            self.assertEqual(data["@ID"], 1)
            self.assertEqual(data["Code"], "WHEPS")
            self.assertEqual(data["Quantity"], 1)
            self.assertEqual(data["InstallDate"], self.install_date)
            self.assertEqual(data["Cost"], 0)
            self.assertEqual(data["Incentive"], "0.00")

            self.assertEqual(len(data["Attributes"]["Attribute"]), 8)
            data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
            self.assertEqual(data["ENFACT"], water_heater.efficiency)
            self.assertEqual(data["MANUFACTURER"], "water_heater_brand")
            self.assertEqual(data["MODEL"], "water_heater_model")
            self.assertEqual(data["SN"], "water_heater_heat_pump_sn")
            self.assertEqual(data["DHWTYPE"], "Heat Pump")
            self.assertEqual(data["FUELTYPE"], "Electric")
            location = water_heater.mechanicals.get().get_location_display()
            self.assertEqual(data["LOCATION"], location)
            self.assertEqual(data["TANKSIZE"], water_heater.tank_size)

        with self.subTest("Gas Conventional"):
            simulation = simulation_factory(
                heater_count=0,
                air_conditioner_count=0,
                air_source_heat_pump_count=0,
                ground_source_heat_pump_count=0,
                water_heater_count=1,
                water_heater__fuel=FuelType.NATURAL_GAS,
                water_heater__style=WaterHeaterStyle.CONVENTIONAL,
                water_heater__efficiency=0.8,
            )
            Floorplan.objects.all().update(simulation=simulation)
            water_heater = simulation.water_heaters.get()
            self.assertFalse(water_heater.is_heat_pump())
            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
            data = serializer.data["Measures"]["Measure"][0]
            self.assertEqual(data["@ID"], 1)
            self.assertEqual(data["Code"], "WHEPS")
            self.assertEqual(data["Quantity"], 1)
            self.assertEqual(data["InstallDate"], self.install_date)
            self.assertEqual(data["Cost"], 0)
            self.assertEqual(data["Incentive"], "0.00")

            self.assertEqual(len(data["Attributes"]["Attribute"]), 8)
            data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
            self.assertEqual(data["ENFACT"], water_heater.efficiency)
            self.assertEqual(data["MANUFACTURER"], "water_heater_brand")
            self.assertEqual(data["MODEL"], "water_heater_model")
            self.assertEqual(data["SN"], "water_heater_gas_sn")
            self.assertEqual(data["DHWTYPE"], "Storage")
            self.assertEqual(data["FUELTYPE"], "Gas")
            location = water_heater.mechanicals.get().get_location_display()
            self.assertEqual(data["LOCATION"], location)
            self.assertEqual(data["TANKSIZE"], water_heater.tank_size)

        with self.subTest("Gas Tankless"):
            simulation = simulation_factory(
                heater_count=0,
                air_conditioner_count=0,
                air_source_heat_pump_count=0,
                ground_source_heat_pump_count=0,
                water_heater_count=1,
                water_heater__fuel=FuelType.NATURAL_GAS,
                water_heater__style=WaterHeaterStyle.TANKLESS,
                water_heater__efficiency=0.8,
                water_heater__tank_size=0.0,
            )
            Floorplan.objects.all().update(simulation=simulation)
            water_heater = simulation.water_heaters.get()
            self.assertFalse(water_heater.is_heat_pump())
            serializer = MeasureSerializer(
                instance=FastTrackSubmission.objects.get(), context=context
            )
            self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
            data = serializer.data["Measures"]["Measure"][0]
            self.assertEqual(data["@ID"], 1)
            self.assertEqual(data["Code"], "WHEPS")
            self.assertEqual(data["Quantity"], 1)
            self.assertEqual(data["InstallDate"], self.install_date)
            self.assertEqual(data["Cost"], 0)
            self.assertEqual(data["Incentive"], "0.00")

            self.assertEqual(len(data["Attributes"]["Attribute"]), 8)
            data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
            self.assertEqual(data["ENFACT"], water_heater.efficiency)
            self.assertEqual(data["MANUFACTURER"], "water_heater_brand")
            self.assertEqual(data["MODEL"], "water_heater_model")
            self.assertEqual(data["SN"], "water_heater_tankless_sn")
            self.assertEqual(data["DHWTYPE"], "Tankless")
            self.assertEqual(data["FUELTYPE"], "Gas")
            location = water_heater.mechanicals.get().get_location_display()
            self.assertEqual(data["LOCATION"], location)
            self.assertEqual(data["TANKSIZE"], water_heater.tank_size)

    def test_eps_heater_measures(self):
        context = {
            "primary_heating_type": random.choice(["Gas Furnace", "Other Gas"]),
            "furnace_brand": "furnace_brand",
            "furnace_model": "furnace_model",
        }
        simulation = simulation_factory(
            heater_count=1,
            heater__fuel=FuelType.NATURAL_GAS,
            heater__efficiency=33.33,
            heater__efficiency_unit=HeatingEfficiencyUnit.AFUE,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.all().update(simulation=simulation)
        heater = simulation.heaters.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "GASFFURNEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 3)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["AFUE"], heater.efficiency)
        self.assertEqual(data["MANUFACTURER"], "furnace_brand")
        self.assertEqual(data["MODEL"], "furnace_model")

    def test_eps_heat_pump_measures(self):
        context = {
            "primary_heating_type": "heat PUMPER",
            "heat_pump_brand": "heat_pump_brand",
            "heat_pump_model": "heat_pump_model",
            "heat_pump_sn": "heat_pump_sn",
        }
        simulation = simulation_factory(
            heater_count=0,
            air_conditioner_count=0,
            air_source_heat_pump_count=1,
            air_source_heat_pump__heating_efficiency_unit=HeatingEfficiencyUnit.HSPF,
            air_source_heat_pump__heating_efficiency=12.2,
            air_source_heat_pump__capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            air_source_heat_pump__heating_capacity_47f=19.2,
            air_source_heat_pump__cooling_efficiency_unit=CoolingEfficiencyUnit.SEER,
            air_source_heat_pump__cooling_efficiency=31.7,
            distribution_system__system_type=DistributionSystemType.FORCED_AIR,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.all().update(simulation=simulation)
        heater = simulation.air_source_heat_pumps.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "HPEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 8)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["HPTYPE"], "Ducted")
        self.assertEqual(data["HSPF"], heater.heating_efficiency)
        self.assertEqual(data["MANUFACTURER"], "heat_pump_brand")
        self.assertEqual(data["MODEL"], "heat_pump_model")
        self.assertEqual(data["SEER"], heater.cooling_efficiency)
        self.assertEqual(data["BACKUPHEAT"], "Electric")
        self.assertEqual(data["HEATCAP"], heater.heating_capacity)
        self.assertEqual(data["SN"], "heat_pump_sn")

    def test_eps_heat_pump_ductless_measures(self):
        context = {
            "primary_heating_type": "heat PUMPER",
            "heat_pump_brand": "heat_pump_brand",
            "heat_pump_model": "heat_pump_model",
            "heat_pump_sn": "heat_pump_sn",
        }
        simulation = simulation_factory(
            heater_count=0,
            air_conditioner_count=0,
            air_source_heat_pump_count=1,
            air_source_heat_pump__heating_efficiency_unit=HeatingEfficiencyUnit.HSPF,
            air_source_heat_pump__heating_efficiency=12.2,
            air_source_heat_pump__capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            air_source_heat_pump__heating_capacity_47f=19.2,
            air_source_heat_pump__cooling_efficiency_unit=CoolingEfficiencyUnit.SEER,
            air_source_heat_pump__cooling_efficiency=31.7,
            distribution_system__system_type=DistributionSystemType.DUCTLESS,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.all().update(simulation=simulation)
        heater = simulation.air_source_heat_pumps.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "HPEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 8)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["HPTYPE"], "DHP")
        self.assertEqual(data["HSPF"], heater.heating_efficiency)
        self.assertEqual(data["MANUFACTURER"], "heat_pump_brand")
        self.assertEqual(data["MODEL"], "heat_pump_model")
        self.assertEqual(data["SEER"], heater.cooling_efficiency)
        self.assertEqual(data["BACKUPHEAT"], "Electric")
        self.assertEqual(data["HEATCAP"], heater.heating_capacity)
        self.assertEqual(data["SN"], "heat_pump_sn")

    def test_eps_ground_source_heat_pump_measures(self):
        context = {
            "primary_heating_type": "heat PUMPER",
            "heat_pump_brand": "heat_pump_brand",
            "heat_pump_model": "heat_pump_model",
            "heat_pump_sn": "heat_pump_sn",
        }
        simulation = simulation_factory(
            heater_count=0,
            air_conditioner_count=0,
            ground_source_heat_pump_count=1,
            ground_source_heat_pump__heating_efficiency_unit=HeatingEfficiencyUnit.HSPF,
            ground_source_heat_pump__heating_efficiency=12.2,
            ground_source_heat_pump__capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            ground_source_heat_pump__heating_capacity=19.2,
            ground_source_heat_pump__cooling_efficiency_unit=CoolingEfficiencyUnit.SEER,
            ground_source_heat_pump__cooling_efficiency=31.7,
            air_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.all().update(simulation=simulation)
        heater = simulation.ground_source_heat_pumps.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "HPEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 8)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["HPTYPE"], "Geothermal")
        self.assertEqual(data["HSPF"], heater.heating_efficiency)
        self.assertEqual(data["MANUFACTURER"], "heat_pump_brand")
        self.assertEqual(data["MODEL"], "heat_pump_model")
        self.assertEqual(data["SEER"], heater.cooling_efficiency)
        self.assertEqual(data["BACKUPHEAT"], "Electric")
        self.assertEqual(data["HEATCAP"], heater.heating_capacity)
        self.assertEqual(data["SN"], "heat_pump_sn")

    def test_eps_fireplace_measures(self):
        context = {
            "primary_heating_type": "Gas Fireplace",
            "other_heater_type": "Gas Fireplace",
            "other_heater_brand": "other_heater_brand",
            "other_heater_model": "other_heater_model",
        }
        simulation = simulation_factory(
            heater_count=1,
            heater__fuel=FuelType.NATURAL_GAS,
            heater__efficiency=33.33,
            heater__efficiency_unit=HeatingEfficiencyUnit.AFUE,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.all().update(simulation=simulation)
        heater = simulation.heaters.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "NHFIREPLEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 3)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["AFUE"], heater.efficiency)
        self.assertEqual(data["MANUFACTURER"], "other_heater_brand")
        self.assertEqual(data["MODEL"], "other_heater_model")

    def test_heater_other_measures(self):
        context = {
            "primary_heating_type": "Other Electric",
            "other_heater_brand": "other_heater_brand",
            "other_heater_model": "other_heater_model",
        }
        simulation = simulation_factory(
            heater_count=1,
            heater__fuel=FuelType.NATURAL_GAS,
            heater__efficiency=33.33,
            heater__efficiency_unit=HeatingEfficiencyUnit.AFUE,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
        )
        Floorplan.objects.all().update(simulation=simulation)
        heater = simulation.heaters.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "HEATSYSEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 6)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["MANUFACTURER"], "other_heater_brand")
        self.assertEqual(data["MODEL"], "other_heater_model")
        self.assertEqual(data["EFFRATE"], heater.efficiency)
        self.assertEqual(data["FUELTYPE"], "Natural Gas")
        self.assertEqual(data["HEATCAP"], heater.capacity)
        self.assertEqual(data["HEATTYPE"], "Other Electric")

    def test_solar_measures(self):
        context = {"has_battery_storage": "Sure", "solar_kw_capacity": "5000"}
        simulation = simulation_factory(
            heater_count=0,
            air_conditioner_count=0,
            air_source_heat_pump_count=0,
            ground_source_heat_pump_count=0,
            water_heater_count=0,
            photovoltaic_count=1,
            photovoltaic__tilt=29.0,
            photovoltaic__azimuth=225.0,
            photovoltaic__capacity=1010.25,
        )
        Floorplan.objects.all().update(simulation=simulation)
        pv = simulation.photovoltaics.get()
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSSOLPV")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 5)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["ESTPRO"], pv.capacity)
        self.assertEqual(data["ORIENTATION"], "southwest")
        self.assertEqual(data["TILT"], pv.tilt)
        self.assertEqual(data["BATTERY"], "Sure")
        self.assertEqual(data["TOTALDCCAP"], context["solar_kw_capacity"])

    def test_SLE_EPSNZ_measure(self):
        "Test out the EPS Zero incentive"
        context = {
            # Calculator
            "percentage_therm_improvement": 10.2,
            "net_zero_eps_incentive": 125.21,
            # Questions
            "percentage_generation_kwh": 2500,
            "project_type": "SLE",
        }
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSNZ")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], f"{context['net_zero_eps_incentive']:.2f}")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 2)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["PERCENTGENERATION"], context["percentage_generation_kwh"])
        self.assertEqual(data["GASIMPROV"], context["percentage_therm_improvement"])

    def test_eps_smart_homes_measure(self):
        "Test out the EPS Zero incentive"
        context = {
            # Calculator
            "energy_smart_homes_eps_incentive": 125.21,
            # Questions
            "grid_harmonization_elements": "Energy smart homes – FOOBAR",
            "solar_elements": "SOMETHING",
        }
        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSESH")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], f'{context["energy_smart_homes_eps_incentive"]:.2f}')

        self.assertEqual(len(data["Attributes"]["Attribute"]), 2)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["ESHTYPE"], "FOOBAR")
        self.assertEqual(data["SOLARTYPE"], context["solar_elements"])

    def test_eps_smart_thermostats(self):
        context = {
            "thermostat_brand": "Something really neat",
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "SMARTTHERMOEPS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")

        self.assertEqual(len(data["Attributes"]["Attribute"]), 1)
        data = {x["Name"]: x["Value"] for x in data["Attributes"]["Attribute"]}
        self.assertEqual(data["MANUFACTURER"], context["thermostat_brand"])

    def test_eps_verifier_electric_measure(self):
        context = {
            "verifier_electric_incentive": 9999.9999,
            "electric_life": 32,
            "electric_load_profile": "Something",
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)

        data = serializer.data["Measures"]["Measure"][0]

        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "CUSTEPSVERFELE")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)
        self.assertNotIn("Savings", data)
        self.assertEqual(data["Incentive"], "{:.2f}".format(context["verifier_electric_incentive"]))
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Life"], context["electric_life"])
        self.assertEqual(data["LoadProfile"]["kwh"], context["electric_load_profile"])
        self.assertEqual(data["LoadProfile"]["Therm"], "None - gas")

    def test_eps_verifier_gas_measure(self):
        context = {
            "verifier_gas_incentive": 200.90,
            "gas_life": 36,
            "gas_load_profile": "Gas Profile",
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)

        data = serializer.data["Measures"]["Measure"][0]
        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "CUSTEPSVERFGAS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)
        self.assertNotIn("Savings", data)
        self.assertEqual(data["Incentive"], "{:.2f}".format(context["verifier_gas_incentive"]))
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Life"], context["gas_life"])
        self.assertEqual(data["LoadProfile"]["kwh"], "None - ele")
        self.assertEqual(data["LoadProfile"]["Therm"], context["gas_load_profile"])

    def test_additional_incentive_measure(self):
        context = {
            "eto_additional_incentives": "Yes",
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)
        data = serializer.data["Measures"]["Measure"][0]

        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSSLRRDYPV")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Cost"], 0)
        self.assertEqual(data["Incentive"], "0.00")
        self.assertNotIn("Attributes", data)

    def test_eps_builder_electric_measure(self):
        context = {
            "builder_electric_incentive": 299.90,
            "electric_life": 32,
            "electric_load_profile": "Gas Profile",
            "kwh_savings": 10.9,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)

        data = serializer.data["Measures"]["Measure"][0]

        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSENHELE")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)

        self.assertEqual(data["Savings"]["kwh"], int(round(context["kwh_savings"])))
        self.assertEqual(data["Savings"]["Therm"], 0)
        self.assertEqual(data["Incentive"], "{:.2f}".format(context["builder_electric_incentive"]))
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Life"], context["electric_life"])
        self.assertEqual(data["LoadProfile"]["kwh"], context["electric_load_profile"])
        self.assertEqual(data["LoadProfile"]["Therm"], "None - gas")

    def test_eps_builder_gas_measure(self):
        context = {
            "builder_gas_incentive": 9999.9999,
            "gas_life": 32,
            "gas_load_profile": "Something",
            "therm_savings": 109.232,
        }

        serializer = MeasureSerializer(instance=FastTrackSubmission.objects.get(), context=context)
        self.assertEqual(len(serializer.data["Measures"]["Measure"]), 1)

        data = serializer.data["Measures"]["Measure"][0]

        self.assertEqual(data["@ID"], 1)
        self.assertEqual(data["Code"], "EPSENHGAS")
        self.assertEqual(data["Quantity"], 1)
        self.assertEqual(data["Cost"], 0)

        self.assertEqual(data["Savings"]["kwh"], 0)
        self.assertEqual(data["Savings"]["Therm"], int(round(context["therm_savings"])))
        self.assertEqual(data["Incentive"], "{:.2f}".format(context["builder_gas_incentive"]))
        self.assertEqual(data["InstallDate"], self.install_date)
        self.assertEqual(data["Life"], context["gas_life"])
        self.assertEqual(data["LoadProfile"]["kwh"], "None - ele")
        self.assertEqual(data["LoadProfile"]["Therm"], context["gas_load_profile"])
