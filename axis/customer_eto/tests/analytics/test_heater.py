"""heater.py - Axis"""

__author__ = "Steven K"
__date__ = "10/30/20 15:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import HeatingEfficiencyUnit, HeatingCoolingCapacityUnit, AuxEnergyUnit
from simulation.models import Heater

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics.heater import eto_simulation_heater_model_characteristics
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class HeaterAnalyticsTests(ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.complete_sim = self.complete.floorplan.simulation

    def get_equipment_furnace(self, custom=False):
        data = {
            "input": {
                "ecm": "N",
                "afue": "92.1",
                "brand_name": "Bryant",
                "eae_kwh_yr": "649",
                "model_number": "912SC48060S17*",
                "capacity_mbtuh": "56",
            }
        }
        if custom:
            data["is_custom"] = True
        return data

    def get_primary_heating_equipment_type(self, hp_type=None):
        return {"input": "Gas Furnace"}

    def test_eto_simulation_heater_model_characteristics(self):
        equip_ids = self.simulation.mechanical_equipment.filter(heater__isnull=False)
        heaters = Heater.objects.filter(id__in=equip_ids.values_list("heater_id", flat=True))
        heaters.update(
            capacity=56,
            capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            efficiency=92.1,
            efficiency_unit=HeatingEfficiencyUnit.AFUE,
            auxiliary_electric_capacity=649,
            auxiliary_electric_unit=AuxEnergyUnit.EAE,
        )
        data = eto_simulation_heater_model_characteristics(
            self.simulation.id,
            self.get_equipment_furnace(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data.keys()), 1)
        self.assertIn("model_heater_characteristics", data)
        self.assertEqual(len(data["model_heater_characteristics"]["warnings"]), 0)

        # We had a bug where we'd end up with an exception for heaters without distribution
        heaters.first().mechanical.heating_distribution_systems.all().delete()
        data = eto_simulation_heater_model_characteristics(
            self.simulation.id,
            self.get_equipment_furnace(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data.keys()), 1)
        self.assertIn("model_heater_characteristics", data)
        self.assertEqual(len(data["model_heater_characteristics"]["warnings"]), 0)

    def test_eto_simulation_heater_model_characteristics_units(self):
        """Check the units are in play"""

        equip_ids = self.simulation.mechanical_equipment.filter(heater__isnull=False)
        Heater.objects.filter(id__in=equip_ids.values_list("heater_id", flat=True)).update(
            capacity=0.056,
            capacity_unit=HeatingCoolingCapacityUnit.KW,  # BTUH
            efficiency=92.1,
            efficiency_unit=HeatingEfficiencyUnit.ADJUSTED_EFFICIENCY,
            auxiliary_electric_capacity=649,
            auxiliary_electric_unit=AuxEnergyUnit.KWH_YEAR,
        )
        data = eto_simulation_heater_model_characteristics(
            self.simulation.id,
            self.get_equipment_furnace(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data.keys()), 1)
        self.assertIn("model_heater_characteristics", data)
        self.assertEqual(len(data["model_heater_characteristics"]["warnings"]), 2)

    def test_eto_simulation_heater_model_characteristics_values(self):
        """Check the values when the right units are in play"""
        equip_ids = self.simulation.mechanical_equipment.filter(heater__isnull=False)
        Heater.objects.filter(id__in=equip_ids.values_list("heater_id", flat=True)).update(
            capacity=55.1,
            capacity_unit=HeatingCoolingCapacityUnit.KW,
            efficiency=93.1,
            efficiency_unit=HeatingEfficiencyUnit.AFUE,
            auxiliary_electric_capacity=650,
            auxiliary_electric_unit=AuxEnergyUnit.EAE,
        )
        data = eto_simulation_heater_model_characteristics(
            self.simulation.id,
            self.get_equipment_furnace(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data.keys()), 1)
        self.assertIn("model_heater_characteristics", data)
        self.assertEqual(len(data["model_heater_characteristics"]["warnings"]), 3)
