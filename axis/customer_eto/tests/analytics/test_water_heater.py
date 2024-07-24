"""water_heater.py - Axis"""

__author__ = "Steven K"
__date__ = "11/2/20 14:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import (
    WaterHeaterStyle,
    HotWaterEfficiencyUnit,
    WaterHeaterLiquidVolume,
)
from simulation.models import WaterHeater

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics.water_heater import (
    eto_simulation_water_heater_model_characteristics,
)
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class WaterHeaterAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.complete_sim = self.complete.floorplan.simulation

    def get_equipment_water_heater(self):
        return {
            "input": {
                "capacity": "0",
                "brand_name": "Rinnai",
                "model_number": "RUCS75i (REU-KCM2528FFU-US)",
                "energy_factor": "0.93",
            }
        }

    def get_converted_equipment_water_heater(self):
        return {
            "input": {
                "uef_cce": "0.92",
                "capacity": "40",
                "brand_name": "A. O. Smith",
                "converted_ef": "0.93",
                "model_number": "ENT-40 1**",
                "energy_factor": "-",
            }
        }

    def test_eto_simulation_water_heater_model_characteristics_units(self):
        equip_ids = self.simulation.mechanical_equipment.filter(water_heater__isnull=False)
        WaterHeater.objects.filter(
            id__in=equip_ids.values_list("water_heater_id", flat=True)
        ).update(
            style=WaterHeaterStyle.TANKLESS,
            tank_size=0,
            tank_units="liter",
            efficiency=0.93,
            efficiency_unit=HotWaterEfficiencyUnit.UNIFORM_ENERGY_FACTOR,
        )

        data = eto_simulation_water_heater_model_characteristics(
            self.simulation.id, self.get_equipment_water_heater()
        )

        self.assertEqual(set(list(data.keys())), {"model_water_heater_characteristics"})
        self.assertEqual(len(data["model_water_heater_characteristics"]["warnings"]), 2)

    def test_eto_simulation_water_heater_model_characteristics_capacity(self):
        equip_ids = self.simulation.mechanical_equipment.filter(water_heater__isnull=False)
        WaterHeater.objects.filter(
            id__in=equip_ids.values_list("water_heater_id", flat=True)
        ).update(
            style=WaterHeaterStyle.CONVENTIONAL,
            tank_size=50,
            tank_units=WaterHeaterLiquidVolume.GALLON,
            efficiency=0.93,
            efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
        )

        data = eto_simulation_water_heater_model_characteristics(
            self.simulation.id, self.get_equipment_water_heater()
        )
        self.assertEqual(set(list(data.keys())), {"model_water_heater_characteristics"})
        self.assertEqual(len(data["model_water_heater_characteristics"]["warnings"]), 1)

    def test_eto_simulation_water_heater_model_characteristics_efficiency(self):
        equip_ids = self.simulation.mechanical_equipment.filter(water_heater__isnull=False)
        WaterHeater.objects.filter(
            id__in=equip_ids.values_list("water_heater_id", flat=True)
        ).update(
            style=WaterHeaterStyle.TANKLESS,
            tank_size=0.0,
            tank_units=WaterHeaterLiquidVolume.GALLON,
            efficiency=0.91,
            efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
        )

        data = eto_simulation_water_heater_model_characteristics(
            self.simulation.id, self.get_equipment_water_heater()
        )

        self.assertEqual(set(list(data.keys())), {"model_water_heater_characteristics"})
        self.assertEqual(len(data["model_water_heater_characteristics"]["warnings"]), 1)

    def test_eto_simulation_water_heater_model_characteristics_efficiency_converted_ef(self):
        equip_ids = self.simulation.mechanical_equipment.filter(water_heater__isnull=False)
        WaterHeater.objects.filter(
            id__in=equip_ids.values_list("water_heater_id", flat=True)
        ).update(
            style=WaterHeaterStyle.CONVENTIONAL,
            tank_size=40.0,
            tank_units=WaterHeaterLiquidVolume.GALLON,
            efficiency=0.91,
            efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
        )

        data = eto_simulation_water_heater_model_characteristics(
            self.simulation.id, self.get_converted_equipment_water_heater()
        )

        self.assertEqual(set(list(data.keys())), {"model_water_heater_characteristics"})
        self.assertEqual(len(data["model_water_heater_characteristics"]["warnings"]), 1)

    def test_eto_simulation_water_heater_model_characteristics(self):
        equip_ids = self.simulation.mechanical_equipment.filter(water_heater__isnull=False)
        WaterHeater.objects.filter(
            id__in=equip_ids.values_list("water_heater_id", flat=True)
        ).update(
            style=WaterHeaterStyle.TANKLESS,
            tank_size=0.0,
            tank_units=WaterHeaterLiquidVolume.GALLON,
            efficiency=0.93,
            efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
        )

        data = eto_simulation_water_heater_model_characteristics(
            self.simulation.id, self.get_equipment_water_heater()
        )

        self.assertEqual(set(list(data.keys())), {"model_water_heater_characteristics"})
        self.assertEqual(len(data["model_water_heater_characteristics"]["warnings"]), 0)
