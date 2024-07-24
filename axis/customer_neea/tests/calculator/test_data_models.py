"""test_data_models.py - Axis"""

__author__ = "Steven K"
__date__ = "6/28/21 09:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from simulation.models import Simulation as Simulation

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea.rtf_calculator.calculator import NEEAV2Calculator
from axis.customer_neea.rtf_calculator.data_models.rem import RemModeledInputBase
from axis.customer_neea.rtf_calculator.data_models.simulation import SimulationModeledInputBase
from axis.customer_neea.tests.mixins import NEEAV2ProgramTestMixin
from axis.remrate_data.models import Simulation as RemSimulation

log = logging.getLogger(__name__)


class DataModelTests(NEEAV2ProgramTestMixin, AxisTestCase):
    """Test out data model data integrity between REM and Simulation Models"""

    client_class = AxisClient

    def setUp(self) -> None:
        self.rem_simulation = RemSimulation.objects.get(export_type=4)
        self.assertIn("As Is Building", self.rem_simulation.get_export_type_display())
        self.rem_reference_simulation = RemSimulation.objects.get(export_type=5)
        self.assertIn("Reference", self.rem_reference_simulation.get_export_type_display())
        self.simulation = Simulation.objects.get()

    @property
    def rem_modeled_design_data_model(self):
        return RemModeledInputBase(simulation=self.rem_simulation, is_improved=True)

    @property
    def rem_modeled_reference_data_model(self):
        return RemModeledInputBase(simulation=self.rem_reference_simulation, is_improved=False)

    @property
    def simulation_design_data_model(self):
        return SimulationModeledInputBase(simulation=self.simulation, is_improved=True)

    @property
    def simulation_reference_data_model(self):
        return SimulationModeledInputBase(simulation=self.simulation, is_improved=False)

    def test_heating_therms(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.heating_therms, sim.heating_therms)

        rem = self.rem_modeled_reference_data_model
        sim = self.simulation_reference_data_model
        self.assertEqual(rem.heating_therms, sim.heating_therms)

    def test_heating_kwh(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.heating_kwh, sim.heating_kwh)

        rem = self.rem_modeled_reference_data_model
        sim = self.simulation_reference_data_model
        self.assertEqual(rem.heating_kwh, sim.heating_kwh)

    def test_cooling_kwh(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.cooling_kwh, sim.cooling_kwh)

        rem = self.rem_modeled_reference_data_model
        sim = self.simulation_reference_data_model
        self.assertEqual(rem.cooling_kwh, sim.cooling_kwh)

    def test_total_consumption_therms(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.total_consumption_therms, sim.total_consumption_therms)

        rem = self.rem_modeled_reference_data_model
        sim = self.simulation_reference_data_model
        self.assertEqual(rem.total_consumption_therms, sim.total_consumption_therms)

    def test_total_consumption_kwh(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.total_consumption_kwh, sim.total_consumption_kwh)

        rem = self.rem_modeled_reference_data_model
        sim = self.simulation_reference_data_model
        self.assertEqual(rem.total_consumption_kwh, sim.total_consumption_kwh)

    def test_qty_heat_pump_water_heaters(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.qty_heat_pump_water_heaters, sim.qty_heat_pump_water_heaters)

    def test_primary_heating_type(self):
        """Note: These will be verbally different"""
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertIn("heater", rem.primary_heating_type.lower())
        self.assertIn("heater", sim.primary_heating_type.lower())

    def test_is_primary_heating_is_heat_pump(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.is_primary_heating_is_heat_pump, sim.is_primary_heating_is_heat_pump)

    def test_primary_cooling_type(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.primary_cooling_type.lower(), "air conditioner")
        self.assertEqual(sim.primary_cooling_type.lower(), "air conditioner")

    def test_primary_cooling_fuel(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.primary_cooling_fuel.lower(), sim.primary_cooling_fuel.lower())

    def test_primary_water_heating_type(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.primary_water_heating_type, sim.primary_water_heating_type)

    def test_clothes_dryer_fuel(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.clothes_dryer_fuel, sim.clothes_dryer_fuel)

    def test_square_footage(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.square_footage, sim.square_footage)

    def test_get_udrh_percent_improvement(self):
        rem = self.rem_modeled_design_data_model
        sim = self.simulation_design_data_model
        self.assertEqual(rem.get_udrh_percent_improvement(), sim.get_udrh_percent_improvement())

    def test_data_model_selector(self):
        from axis.home.models import EEPProgramHomeStatus

        # Copied blindly from axis.home.api.HomeStatusViewSet.rtf_calculator sans assertions
        instance = EEPProgramHomeStatus.objects.get()

        self.assertIsNotNone(instance.floorplan)
        self.assertIsNotNone(instance.floorplan.remrate_target)
        self.assertIsNotNone(instance.floorplan.simulation)

        answer_data = dict(instance.annotations.all().values_list("type__slug", "content"))
        answer_data = {k.replace("-", "_"): v for k, v in answer_data.items()}

        input_values = instance.get_input_values(user_role="rater")
        input_answers = {
            measure.replace("neea-", ""): value for measure, value in input_values.items()
        }

        answer_data.update(input_answers)
        sim_calculator = NEEAV2Calculator(home_status_id=instance.id, **answer_data)
        self.assertEqual(sim_calculator.improved_data.__class__.__name__, "NEEASimModeledInput")
        self.assertEqual(sim_calculator.code_data.__class__.__name__, "NEEASimModeledInput")
        sim_results = sim_calculator.result_data()

        answer_data = answer_data.copy()
        answer_data["force_rem_simulation"] = True
        rem_calculator = NEEAV2Calculator(home_status_id=instance.id, **answer_data)
        self.assertEqual(rem_calculator.improved_data.__class__.__name__, "NEEARemModeledInput")
        self.assertEqual(rem_calculator.code_data.__class__.__name__, "NEEARemModeledInput")
        rem_results = rem_calculator.result_data()

        for k, v in sim_results.items():
            if k in ["reports", "last_updated"]:
                continue
            self.assertEqual(rem_results[k], v)
