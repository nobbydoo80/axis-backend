"""heat_pump.py - Axis"""

__author__ = "Steven K"
__date__ = "10/30/20 11:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import (
    CoolingEfficiencyUnit,
    HeatingEfficiencyUnit,
    HeatingCoolingCapacityUnit,
)
from simulation.tests.factories import mechanical_equipment_factory

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics import eto_simulation_heat_pump_model_characteristics
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class HeatPumpAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.complete_sim = self.complete.floorplan.simulation

    def get_equipment_heat_pump(self, custom=False):
        data = {
            "input": {
                "hspf": "13.6",
                "seer": "18",
                "brand_name": "Mitsubishi",
                "capacity_17f_kbtuh": "21.4",
                "capacity_47f_kbtuh": "30",
                "indoor_model_number": "SVZ-KP30NA",
                "outdoor_model_number": "SUZ-KA30NA2",
                "cooling_capacity_kbtuh": "27",
            }
        }
        if custom:
            data["is_custom"] = True
        return data

    def get_primary_heating_equipment_type(self, hp_type=None):
        value = "Other Electric"
        if hp_type == "ashp":
            value = "Electric Heat Pump \u2013 Air Source Ducted"
        if hp_type == "ashp":
            value = "Electric Heat Pump \u2013 Ground Source"
        return {"input": value}

    def test_eto_simulation_heat_pump_model_characteristics_ashp(self):
        self.assertEqual(self.complete_sim.air_source_heat_pumps.count(), 0)
        self.assertEqual(self.complete_sim.ground_source_heat_pumps.count(), 0)

        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("ashp"),
        )

        # No heat pump in simulation
        self.assertEqual(len(data.keys()), 2)
        self.assertIn("model_heat_pump_characteristics", data)
        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 1)

        # Clean
        mechanical_equipment_factory(
            self.complete_sim,
            equipment_type="air_source_heat_pump",
            heating_efficiency=13.6,
            heating_efficiency_unit=HeatingEfficiencyUnit.HSPF,
            cooling_efficiency=18.0,
            cooling_efficiency_unit=CoolingEfficiencyUnit.SEER,
            heating_capacity_17f=21.4,
            heating_capacity_47f=30.0,
            cooling_capacity=27.0,
            capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            heating_percent_served=100,
            cooling_percent_served=100,
        )

        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("ashp"),
        )

        self.assertEqual(len(data.keys()), 2)
        self.assertIn("model_heat_pump_characteristics", data)
        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 0)
        self.assertEqual(len(data["model_heat_pump_cooling_characteristics"]["warnings"]), 0)

    def test_eto_simulation_heat_pump_model_characteristics_ashp_bad(self):
        self.assertEqual(self.complete_sim.air_source_heat_pumps.count(), 0)
        self.assertEqual(self.complete_sim.ground_source_heat_pumps.count(), 0)

        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("ashp"),
        )

        # No heat pump in simulation
        self.assertEqual(len(data.keys()), 2)
        self.assertIn("model_heat_pump_characteristics", data)
        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 1)

        # Get as much to flag as possible
        mechanical_equipment_factory(
            self.complete_sim,
            equipment_type="air_source_heat_pump",
            as_dfhp=False,
            heating_efficiency=3.6,
            heating_efficiency_unit=HeatingEfficiencyUnit.AFUE,
            cooling_efficiency=40.0,
            cooling_efficiency_unit=CoolingEfficiencyUnit.COP,
            heating_capacity_17f=10.4,
            heating_capacity_47f=5.0,
            cooling_capacity=4.0,
            capacity_unit=HeatingCoolingCapacityUnit.KW,  # BTUH?
            heating_percent_served=100,
            cooling_percent_served=100,
        )

        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("ashp"),
        )
        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 3)
        self.assertEqual(len(data["model_heat_pump_cooling_characteristics"]["warnings"]), 4)

    def test_eto_simulation_heat_pump_model_characteristics_gshp(self):
        self.assertEqual(self.complete_sim.ground_source_heat_pumps.count(), 0)

        self.assertEqual(self.complete_sim.air_source_heat_pumps.count(), 0)
        self.assertEqual(self.complete_sim.ground_source_heat_pumps.count(), 0)

        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("gshp"),
        )

        # No heat pump in simulation
        self.assertEqual(len(data.keys()), 2)
        self.assertIn("model_heat_pump_characteristics", data)
        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 1)

        # Clean
        mechanical_equipment_factory(
            self.complete_sim,
            equipment_type="ground_source_heat_pump",
            heating_efficiency=13.6,
            heating_efficiency_unit=HeatingEfficiencyUnit.HSPF,
            cooling_efficiency=18.0,
            cooling_efficiency_unit=CoolingEfficiencyUnit.SEER,
            heating_capacity=30,
            cooling_capacity=27.0,
            capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            heating_percent_served=100,
            cooling_percent_served=100,
        )
        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("gshp"),
        )
        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 0)
        self.assertEqual(len(data["model_heat_pump_cooling_characteristics"]["warnings"]), 0)

    def test_eto_simulation_heat_pump_model_characteristics_gshp_bad(self):
        self.assertEqual(self.complete_sim.ground_source_heat_pumps.count(), 0)

        self.assertEqual(self.complete_sim.air_source_heat_pumps.count(), 0)
        self.assertEqual(self.complete_sim.ground_source_heat_pumps.count(), 0)

        # Get the rest of it to flag out
        mechanical_equipment_factory(
            self.complete_sim,
            equipment_type="ground_source_heat_pump",
            heating_efficiency=93.6,
            heating_efficiency_unit=HeatingEfficiencyUnit.HSPF,
            cooling_efficiency=2.0,
            cooling_efficiency_unit=CoolingEfficiencyUnit.SEER,
            heating_capacity=30,
            cooling_capacity=27.0,
            capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            heating_percent_served=100,
            cooling_percent_served=100,
        )

        data = eto_simulation_heat_pump_model_characteristics(
            self.complete_sim.id,
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type("gshp"),
        )

        self.assertEqual(len(data["model_heat_pump_characteristics"]["warnings"]), 1)
        self.assertEqual(len(data["model_heat_pump_cooling_characteristics"]["warnings"]), 1)


# def get_answer_set(measures, user_role='rater'):
#     import random
#     from django_input_collection.models import CollectionInstrument
#     from axis.checklist.models import CollectedInput
#     custom_measure = random.choice(measures)
#     result = {}
#     for idx, measure_id in enumerate(measures):
#         instruments = CollectionInstrument.objects.filter(measure_id=measure_id)
#         _values = CollectedInput.objects.filter(instrument__in=instruments, user_role=user_role)
#         values = list(_values.values_list('data', flat=True))
#         if not len(values):
#             print("Nothing found for %s" % measure_id)
#             continue
#         if measure_id == custom_measure:
#             values = [x for x in values if x.get('hints', {}).get('is_custom')]
#             if not len(values):
#                 print("Skipping custom %s none found" % measure_id)
#             values = list(_values.values_list('data', flat=True))
#         else:
#             values = [x for x in values if not x.get('hints', {}).get('is_custom')]
#
#         result[measure_id] = random.choice(values)
#     print(result)
#     return result
