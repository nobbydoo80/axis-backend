"""eto_2017.py: Django """


__author__ = "Steven K"
__date__ = "12/17/2019 13:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]
import logging

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram

from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class EEPProgramETO2017ProgramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for ETO 2017 eep_program"""

    client_class = AxisClient

    def test_get_eto_2017_answer_sets(self):
        """
        Test for get_eto_2017_answer_sets() required argument home_status is not being used
        but still required.
        eep_program's slug must = "eto-2017"
        input_values is a dictionary.
        this model function basically check for three measure_values.
        if any is missing it returns a Failing status.
        """
        # first lets update the slug
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2017")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        input_values = {
            "eto-slab_perimeter_r_value": 1,
            "eto-slab_under_insulation_r_value": 1,
            "eto-framed_floor_r_value": 1,
            "eto-flat_ceiling_r_value-2017": 1,
            "eto-vaulted_ceiling_r_value-2017": 1,
            "eto-primary_heat_afue": 1,
            "eto-primary_heat_hspf-2016": 1,
            "eto-primary_heat_cop-2016": 1,
        }

        result = eep_program.get_eto_2017_answer_sets("home_status", "checklist_url", input_values)
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertFalse(result.show_data)
        self.assertIsNone(result.data)
        self.assertIsNone(result.message)

    def test_get_eto_2017_answer_sets_missing_all_measure_values(self):
        """
        Test for get_eto_2017_answer_sets() required argument home_status is not being used
        but still required.
        eep_program's slug must = "eto-2017"
        input_values is a dictionary, in this case is empty which means we get back a failing status
        this model function basically check for three measure_values.
        if any is missing it returns a Failing status.
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2017")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        input_values = {}

        result = eep_program.get_eto_2017_answer_sets("home_status", "checklist_url", input_values)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertFalse(result.show_data)
        self.assertIsNone(result.data)
        self.assertIn("Floor or Slab Insulation R values", result.message)
        self.assertIn("Vaulted or Flat ceiling Insulation R values", result.message)
        self.assertIn("Heating AFUE, HSPF or COP values", result.message)

    def test_get_eto_2017_answer_sets_missing_floor_or_slab_insulation_values(self):
        """
        Test for get_eto_2017_answer_sets() required argument home_status is not being used
        but still required.
        eep_program's slug must = "eto-2017"
        input_values is a dictionary
        this model function basically check for three measure_values.
        if any is missing it returns a Failing status.
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2017")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        input_values = {
            "eto-flat_ceiling_r_value-2017": 1,
            "eto-vaulted_ceiling_r_value-2017": 1,
            "eto-primary_heat_afue": 1,
            "eto-primary_heat_hspf-2016": 1,
            "eto-primary_heat_cop-2016": 1,
        }

        result = eep_program.get_eto_2017_answer_sets("home_status", "checklist_url", input_values)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertFalse(result.show_data)
        self.assertIsNone(result.data)
        self.assertIn("Floor or Slab Insulation R values", result.message)

    def test_get_eto_2017_answer_sets_missing_vaulter_or_flat_insulation_values(self):
        """
        Test for get_eto_2017_answer_sets() required argument home_status is not being used
        but still required.
        eep_program's slug must = "eto-2017"
        input_values is a dictionary
        this model function basically check for three measure_values.
        if any is missing it returns a Failing status.
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2017")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        input_values = {
            "eto-slab_perimeter_r_value": 1,
            "eto-slab_under_insulation_r_value": 1,
            "eto-framed_floor_r_value": 1,
            "eto-primary_heat_afue": 1,
            "eto-primary_heat_hspf-2016": 1,
            "eto-primary_heat_cop-2016": 1,
        }

        result = eep_program.get_eto_2017_answer_sets("home_status", "checklist_url", input_values)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertFalse(result.show_data)
        self.assertIsNone(result.data)
        self.assertIn("Vaulted or Flat ceiling Insulation R values", result.message)

    def test_get_eto_2017_answer_sets_missing_heating_values(self):
        """
        Test for get_eto_2017_answer_sets() required argument home_status is not being used
        but still required.
        eep_program's slug must = "eto-2017"
        input_values is a dictionary, in this case is empty which means we get back a failing status
        this model function basically check for three measure_values.
        if any is missing it returns a Failing status.
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto-2017")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        input_values = {
            "eto-slab_perimeter_r_value": 1,
            "eto-slab_under_insulation_r_value": 1,
            "eto-framed_floor_r_value": 1,
            "eto-flat_ceiling_r_value-2017": 1,
            "eto-vaulted_ceiling_r_value-2017": 1,
        }

        result = eep_program.get_eto_2017_answer_sets("home_status", "checklist_url", input_values)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertFalse(result.show_data)
        self.assertIsNone(result.data)
        self.assertIn("Heating AFUE, HSPF or COP values", result.message)

    def test_get_eto_heat_pump_water_heater_status_no_floorplan(self):
        """Test for get_eto_heat_pump_water_heater_status. home_status has NO floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_eto_heat_pump_water_heater_status(
            home_status.home, home_status, "", ""
        )
        self.assertIsNone(result)

    def test_get_eto_heat_pump_water_heater_status_no_remrate_target(self):
        """Test get_eto_heat_pump_water_heater_status. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_heat_pump_water_heater_status(
            home_status.home, home_status, "", ""
        )
        self.assertIsNone(result)

    def test_get_eto_heat_pump_water_heater_status_does_not_apply(self):
        """Test get_eto_heat_pump_water_heater_status. home_status' floorplan has no heat pump
        equipment installed.
        expected result None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_heat_pump_water_heater_status(
            home_status.home, home_status, "", ""
        )
        self.assertIsNone(result)

    def test_get_eto_heat_pump_water_heater_status_passing(self):
        """Test get_eto_heat_pump_water_heater_status.
        expected result Passing Status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__hot_water__type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        heat_pump = floorplan.remrate_target.installedequipment_set.filter(
            hot_water_heater__type=4
        ).first()
        self.assertTrue(heat_pump)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        val = "answer"
        input_values = {"heat-pump-water-heater-serial-number": val}
        result = eep_program.get_eto_heat_pump_water_heater_status(
            home_status.home, home_status, "", input_values
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertEqual(result.data, val)

    def test_get_eto_heat_pump_water_heater_status_failing_status(self):
        """Test get_eto_heat_pump_water_heater_status.
        expected result None
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        home_status.state_history.filter(to_state="qa_pending").update(
            start_time=datetime.datetime(2018, 1, 1, tzinfo=datetime.timezone.utc)
        )
        kwargs = {"remrate_target__hot_water__type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        heat_pump = floorplan.remrate_target.installedequipment_set.filter(
            hot_water_heater__type=4
        ).first()
        self.assertTrue(heat_pump)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"heat-pump-water-heater-serial-number": ""}
        result = eep_program.get_eto_heat_pump_water_heater_status(
            home_status.home, home_status, "checklist_url", input_values
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.status)
        self.assertIn(
            "A serial number must be provided as a checklist answer when a heat pump "
            "water heater is present",
            result.message,
        )
        self.assertEqual(result.url, "checklist_url")
