"""ventilation.py - Axis"""


__author__ = "Steven K"
__date__ = "11/2/20 11:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.enumerations import MechanicalVentilationType, AuxEnergyUnit, VentilationRateUnit

from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.analytics.legacy_ventilation import (
    eto_simulation_ventilation_model_characteristics,
    get_ventilation_analytics,
)
from axis.customer_eto.tests.analytics.test_appliances import ETO2022ProgramAnalyticsTestMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class VentilationAnalyticsTests(
    ETO2022ProgramAnalyticsTestMixin, CollectionRequestMixin, AxisTestCase
):
    def setUp(self):
        self.complete = EEPProgramHomeStatus.objects.get(state="complete")
        self.home_status = EEPProgramHomeStatus.objects.exclude(state="complete").get()
        self.simulation = self.home_status.floorplan.simulation
        self.mechanical_ventilation_systems = self.simulation.mechanical_ventilation_systems.all()
        self.mechanical_ventilation = self.mechanical_ventilation_systems.get()
        self.complete_sim = self.complete.floorplan.simulation
        self.analysis = self.simulation.analyses.first().type

    def get_equipment_ventilation_exhaust(self, custom=False):
        return {
            "input": {
                "speed_cfm": "55",
                "brand_name": "Panasonic",
                "model_number": "FV0511VKS1",
                "input_power_watts": "72",
            }
        }

    def get_equipment_ventilation_balanced(self, custom=False):
        return {
            "input": {
                "asre": "68",
                "brand_name": "Broan",
                "model_number": "HRV80",
                "net_airflow_cfm": "55",
                "power_consumption_watts": "73",
            }
        }

    def get_equipment_furnace(self, custom=False):
        data = {
            "input": {
                "ecm": "N",
                "afue": "95",
                "brand_name": "American Standard",
                "eae_kwh_yr": "789",
                "model_number": "ADH1B065A9421**",
                "capacity_mbtuh": "57",
                "ventilation_fan_watts": "74",
            }
        }
        if custom:
            data["is_custom"] = True
        return data

    def get_equipment_heat_pump(self, custom=False):
        data = {
            "input": {
                "hspf": "11.7",
                "seer": "21.6",
                "motor_hp": "-",
                "brand_name": "Mitsubishi",
                "capacity_17f_kbtuh": "12.1",
                "capacity_47f_kbtuh": "18",
                "indoor_model_number": "NAXWST15A112A*",
                "outdoor_model_number": "MUZ-GL15NA***",
                "ventilation_fan_watts": "-",
                "cooling_capacity_kbtuh": "14",
            }
        }
        if custom:
            data["is_custom"] = True
        return data

    def get_primary_heating_equipment_type(self):
        return {"input": "Gas Furnace"}

    def test_eto_simulation_ventilation_model_characteristics_type(self):
        self.mechanical_ventilation_systems.update(type=MechanicalVentilationType.AIR_CYCLER)
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(set(list(data.keys())), {"model_ventilation_characteristics"})
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 1)

    def test_eto_simulation_ventilation_model_characteristics_consumption_unit(self):
        self.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.BALANCED, consumption_unit=AuxEnergyUnit.KWH_YEAR
        )
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(set(list(data.keys())), {"model_ventilation_characteristics"})
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 1)

    def test_eto_simulation_ventilation_model_characteristics_ventilation_rate_unit(self):
        self.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.BALANCED,
            consumption_unit=AuxEnergyUnit.WATT,
            # The VentilationRateUnit only supports one unit now (which is obviously a valid choice),
            # so we have to manually set an invalid unit instead of using an enum as we usually would
            ventilation_rate_unit="cmm",
        )
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(set(list(data.keys())), {"model_ventilation_characteristics"})
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 1)

    def test_eto_simulation_ventilation_model_characteristics_balanced(self):
        self.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.BALANCED,
            adjusted_sensible_recovery_efficiency=68.0,
            ventilation_rate=25.0,
            ventilation_rate_unit=VentilationRateUnit.CFM,
            consumption=25.0,
            consumption_unit=AuxEnergyUnit.WATT,
        )

        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 2)

        # Passing
        self.mechanical_ventilation_systems.update(
            ventilation_rate=55.0,
            consumption=73.0,
        )
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 0)

    def test_eto_simulation_ventilation_model_characteristics_exhaust(self):
        self.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.EXHAUST_ONLY,
            adjusted_sensible_recovery_efficiency=68.0,
            ventilation_rate=72.0,
            ventilation_rate_unit=VentilationRateUnit.CFM,
            consumption=55.0,
            consumption_unit=AuxEnergyUnit.WATT,
        )
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 2)

        # Passing
        self.mechanical_ventilation_systems.update(
            ventilation_rate=55.0,
            consumption=72.0,
        )
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 0)

    def test_eto_simulation_ventilation_model_characteristics_supply(self):
        self.mechanical_ventilation_systems.update(
            type=MechanicalVentilationType.SUPPLY_ONLY,
            ventilation_rate=55.0,
            ventilation_rate_unit=VentilationRateUnit.CFM,
            consumption_unit=AuxEnergyUnit.WATT,
        )
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 1)

        # Passing
        self.mechanical_ventilation_systems.update(consumption=74.0)
        data = eto_simulation_ventilation_model_characteristics(
            self.simulation.id,
            self.get_equipment_ventilation_exhaust(),
            self.get_equipment_ventilation_balanced(),
            self.get_equipment_furnace(),
            self.get_equipment_heat_pump(),
            self.get_primary_heating_equipment_type(),
        )
        self.assertEqual(len(data["model_ventilation_characteristics"]["warnings"]), 0)

    def test_get_ventilation_analytics(self):
        input_data = {
            "simulation_id": self.simulation.id,
            "similar_insulation_simulation_ids": [self.complete_sim.id],
            "analysis_type": self.analysis,
            "similar_insulation_simulation_last_18mo_ids": [self.complete_sim.id],
        }
        data = get_ventilation_analytics(**input_data)
        self.assertEqual(set(list(data.keys())), {"ventilation_watts", "ventilation_rate"})
