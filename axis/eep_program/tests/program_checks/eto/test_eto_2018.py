"""eto_2018.py: Django """

import logging
from unittest import mock

from django.contrib.auth import get_user_model

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.home.models import EEPProgramHomeStatus, Home

__author__ = "Steven K"
__date__ = "12/17/2019 13:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
User = get_user_model()


class EEPProgramETO2018ProgramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for ETO 2018 eep_program"""

    client_class = AxisClient

    def test_get_eto_2018_no_multifamily_failing_status_for_multifamily_home(self):
        """Test for get_eto_2018_no_multifamily. home is multifamily. expected Failing Status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        Home.objects.filter(id=home_status.home.id).update(is_multi_family=True)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.home.is_multi_family)
        kwargs = {"home_edit_url": "home_edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertFalse(result.status)
        self.assertEqual("Home must not be designated as multifamily.", result.message)

    def test_get_eto_2018_no_multifamily_no_floorplan(self):
        """
        Test for get_eto_2018_no_multifamily. passed home_status argument has NO floorplan.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        self.assertFalse(home_status.home.is_multi_family)
        kwargs = {"home_edit_url": "home_edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertIsNone(result)

    def test_get_eto_2018_no_multifamily_rem_not_multifamily(self):
        """
        Test for get_eto_2018_no_multifamily. passed home_status argument has floorplan & remrate,
        but building type is NOT "Multi-family, whole building" or building_type != 6
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.home.is_multi_family)
        kwargs = {"home_edit_url": "home_edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertIsNone(result)

    def test_get_eto_2018_no_multifamily_rem_multifamily(self):
        """
        Test for get_eto_2018_no_multifamily. passed home_status argument has floorplan & remrate,
        but building type is "Multi-family, whole building" or building_type == 6
        expected back Failing Status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__building_info__type": 6}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.home.is_multi_family)
        kwargs = {"edit_url": "edit_url"}
        result = eep_program.get_eto_no_multifamily(home_status.home, home_status, **kwargs)
        self.assertIsNotNone(result)
        self.assertEqual("REM building type must not be designated as multifamily.", result.message)

    def test_get_eto_2018_oven_fuel_type_no_floorplan(self):
        """Test for get_eto_2018_oven_fuel_type. home_status has NO floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_oven_fuel_type(
            home_status.home, home_status, "", **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_oven_fuel_type_no_remrate_target(self):
        """Test get_eto_2018_oven_fuel_type. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_oven_fuel_type(
            home_status.home, home_status, "", **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_oven_fuel_type_no_heating_equipment_type(self):
        """
        Test for get_eto_2018_oven_fuel_type. input_values (dict) is empty. input values is expected
        to have 'primary-heating-equipment-type' as a key. Expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.home.is_multi_family)
        input_values = {}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_oven_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_oven_fuel_type_wrong_heating_type_category(self):
        """Test for get_eto_2018_oven_fuel_type. floorplan.remrate_target contains building info,
        we care about the lightsandappliance.oven_fuel this relates to the heating_type category:
        1  # FUEL_TYPES: "Natural gas"
        4  # FUEL_TYPES: "Electric"
        for this test case oven_fuel values is 2
        and heating_type_category NOT in [1, 4]
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        oven_fuel = floorplan.remrate_target.building.lightsandappliance.oven_fuel
        self.assertNotIn(oven_fuel, [1, 4])
        input_values = {"primary-heating-equipment-type": "Heat pump"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_oven_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertFalse(result.status)
        self.assertIn("does not match primary heating fuel", result.message)

    def test_get_eto_2018_oven_fuel_type_heating_type_gas(self):
        """Test for get_eto_2018_oven_fuel_type. floorplan.remrate_target contains building info,
        we care about the lightsandappliance.oven_fuel this relates to the heating_type category:
        1  # FUEL_TYPES: "Natural gas"
        4  # FUEL_TYPES: "Electric"
        for this test case oven_fuel values is 1  and heating_type_category IN [1, 4]
        primary-heating-equipment-type = 'Other Gas'
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__lightsandappliance__oven_fuel": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        oven_fuel = floorplan.remrate_target.building.lightsandappliance.oven_fuel
        self.assertEqual(oven_fuel, 1)
        input_values = {"primary-heating-equipment-type": "Other Gas"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_oven_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_oven_fuel_type_heating_type_electric(self):
        """Test for get_eto_2018_oven_fuel_type. floorplan.remrate_target contains building info,
        we care about the lightsandappliance.oven_fuel this relates to the heating_type category:
        1  # FUEL_TYPES: "Natural gas"
        4  # FUEL_TYPES: "Electric"
        for this test case oven_fuel values is 4  and heating_type_category IN [1, 4]
        primary-heating-equipment-type =  'Other Electric'
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {"remrate_target__lightsandappliance__oven_fuel": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        oven_fuel = floorplan.remrate_target.building.lightsandappliance.oven_fuel
        self.assertEqual(oven_fuel, 4)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_oven_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_dryer_attributes(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is conditioned i.e. equals 1
        AND
        dryer_fuel in primary_heating_fuel i.e. Dryer fuel does match checklist answer
        for primary heating fuel
        categories of fuel represented in the 2018 primary heating { 1-3: gas, 4: electric}
        AND
        lights_and_appliance clothes_dryer_energy_factor is 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 1,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 4,
            "remrate_target__lightsandappliance__clothes_dryer_energy_factor": 3.01,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertEqual(dryer_location, 1)
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertEqual(dryer_energy_factor, 3.01)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_dryer_attributes_no_floorplan(self):
        """Test for get_eto_2018_dryer_attributes. home_status has NO floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, "", **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_dryer_attributes_no_remrate_target(self):
        """Test get_eto_2018_dryer_attributes. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, "", **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_2018_dryer_attributes_no_primary_heating_equipment(self):
        """
        Test for get_eto_2018_dryer_attributes. input_values (dict) which SHOULD contain
        'primary-heating-equipment-type', for this test case is empty.
        lights_and_appliance's (floorplan.remrate_target) clothes_dryer_location is 1
        lights_and_appliance clothes_dryer_energy_factor is NOT 3.01
        Result expected back Failing status.
        by having an empty 'input_values' we simply are ignoring fuel checks. i.e. it would NOT
        affect the result
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        dryer_location = floorplan.remrate_target.building.lightsandappliance.clothes_dryer_location
        self.assertEqual(dryer_location, 1)
        dryer_ef = floorplan.remrate_target.building.lightsandappliance.clothes_dryer_energy_factor
        self.assertNotEqual(dryer_ef, 3.01)

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("EF must be 3.01", result.message)

    def test_get_eto_2018_dryer_attributes_incorrect_rem_values_1(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is conditioned i.e. equal 1
        AND
        dryer_fuel not in primary_heating_fuel i.e. Dryer fuel does NOT match checklist answer
        for primary heating fuel
        AND
        lights_and_appliance clothes_dryer_energy_factor is NOT 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 1,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 1,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertEqual(dryer_location, 1)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        # check clothes_dryer_fuel !=4, type 4 represents Electric fuel types, we want a mismatch
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertNotEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertNotEqual(dryer_energy_factor, 3.01)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Incorrect REM values", result.message)
        self.assertTrue(result.show_data)
        self.assertNotIn("Location must be conditioned", result.data)
        self.assertIn("must match checklist answer for primary heating fuel", result.data)
        self.assertIn("EF must be 3.01", result.data)

    def test_get_eto_2018_dryer_attributes_incorrect_rem_values_2(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is NOT conditioned i.e. NOT equal 1
        AND
        dryer_fuel not in primary_heating_fuel i.e. Dryer fuel does NOT match checklist answer
        for primary heating fuel
        AND
        lights_and_appliance clothes_dryer_energy_factor is NOT 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 2,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 1,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertNotEqual(dryer_location, 1)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        # check clothes_dryer_fuel !=4, type 4 represents Electric fuel types, we want a mismatch
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertNotEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertNotEqual(dryer_energy_factor, 3.01)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Incorrect REM values", result.message)
        self.assertTrue(result.show_data)
        self.assertIn("Location must be conditioned", result.data)
        self.assertIn("must match checklist answer for primary heating fuel", result.data)
        self.assertIn("EF must be 3.01", result.data)

    def test_get_eto_2018_dryer_attributes_incorrect_rem_values_3(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is NOT conditioned i.e. NOT equal 1
        AND
        dryer_fuel not in primary_heating_fuel i.e. Dryer fuel does NOT match checklist answer
        for primary heating fuel
        AND
        lights_and_appliance clothes_dryer_energy_factor is 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 1,
            "remrate_target__lightsandappliance__clothes_dryer_location": 2,
            "remrate_target__lightsandappliance__clothes_dryer_energy_factor": 3.01,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertNotEqual(dryer_location, 1)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        # check clothes_dryer_fuel !=4, type 4 represents Electric fuel types, we want a mismatch
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertNotEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertEqual(dryer_energy_factor, 3.01)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Incorrect REM values", result.message)
        self.assertTrue(result.show_data)
        self.assertIn("Location must be conditioned", result.data)
        self.assertIn("must match checklist answer for primary heating fuel", result.data)
        self.assertNotIn("EF must be 3.01", result.data)

    def test_get_eto_2018_dryer_attributes_incorrect_rem_values_4(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is NOT conditioned i.e. NOT equal 1
        AND
        dryer_fuel not in primary_heating_fuel i.e. Dryer fuel does NOT match checklist answer
        for primary heating fuel
        AND
        lights_and_appliance clothes_dryer_energy_factor is NOT 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 2,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 4,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertNotEqual(dryer_location, 1)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertNotEqual(dryer_energy_factor, 3.01)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Incorrect REM values", result.message)
        self.assertTrue(result.show_data)
        self.assertIn("Location must be conditioned", result.data)
        self.assertNotIn("must match checklist answer for primary heating fuel", result.data)
        self.assertIn("EF must be 3.01", result.data)

    def test_get_eto_2018_dryer_attributes_dryer_loc_not_conditioned(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is NOT conditioned i.e. NOT equal 1
        AND
        dryer_fuel in primary_heating_fuel i.e. Dryer fuel does match checklist answer
        for primary heating fuel
        categories of fuel represented in the 2018 primary heating { 1-3: gas, 4: electric}
        AND
        lights_and_appliance clothes_dryer_energy_factor is 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 2,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 4,
            "remrate_target__lightsandappliance__clothes_dryer_energy_factor": 3.01,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertNotEqual(dryer_location, 1)
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertEqual(dryer_energy_factor, 3.01)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Location must be conditioned", result.message)
        self.assertFalse(result.show_data)

    def test_get_eto_2018_dryer_attributes_dryer_fuel_mismatch(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is conditioned i.e. equals 1
        AND
        dryer_fuel NOT in primary_heating_fuel i.e. Dryer fuel does match checklist answer
        for primary heating fuel
        categories of fuel represented in the 2018 primary heating { 1-3: gas, 4: electric}
        AND
        lights_and_appliance clothes_dryer_energy_factor is 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 1,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 3,
            "remrate_target__lightsandappliance__clothes_dryer_energy_factor": 3.01,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertEqual(dryer_location, 1)
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertNotEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertEqual(dryer_energy_factor, 3.01)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("must match checklist answer for primary heating fuel", result.message)
        self.assertFalse(result.show_data)

    def test_get_eto_2018_dryer_attributes_wrong_efficiency_fuel(self):
        """
        Test for get_eto_2018_dryer_attributes. lights_and_appliance's (floorplan.remrate_target)
        clothes_dryer_location is conditioned i.e. equals 1
        AND
        dryer_fuel in primary_heating_fuel i.e. Dryer fuel does match checklist answer
        for primary heating fuel
        categories of fuel represented in the 2018 primary heating { 1-3: gas, 4: electric}
        AND
        lights_and_appliance clothes_dryer_energy_factor is NOT 3.01
        Result expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        kwargs = {
            "remrate_target__lightsandappliance__clothes_dryer_location": 1,
            "remrate_target__lightsandappliance__clothes_dryer_fuel": 4,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        remrate = floorplan.remrate_target
        dryer_location = remrate.lightsandappliance.clothes_dryer_location
        self.assertEqual(dryer_location, 1)
        dryer_fuel = remrate.lightsandappliance.clothes_dryer_fuel
        self.assertEqual(dryer_fuel, 4)
        dryer_energy_factor = remrate.lightsandappliance.clothes_dryer_energy_factor
        self.assertNotEqual(dryer_energy_factor, 3.01)
        input_values = {"primary-heating-equipment-type": "Other Electric"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_2018_dryer_attributes(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("EF must be 3.01", result.message)
        self.assertFalse(result.show_data)

    @mock.patch("axis.home.utils.get_eps_data")
    def test_get_eto_builder_incentive_status_unable_to_calculate_eps(self, get_eps_data):
        """Test for get_eto_builder_incentive_status"""

        from axis.customer_eto.calculator.eps.base import EPSInputException

        get_eps_data.side_effect = EPSInputException("something")
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_legacy_builder_incentive_status(home_status, "edit_utl")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Unable to calculate EPS", result.message)
        self.assertIsNone(result.url)

    @mock.patch("axis.home.utils.get_eps_data")
    def test_get_eto_builder_incentive_status_builder_incentive_too_low(self, get_eps_data):
        """Test for get_eto_builder_incentive_status"""
        data = {"builder_incentive": 0.0}
        get_eps_data.return_value = data
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_legacy_builder_incentive_status(home_status, "edit_utl")
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn(
            "Project must meet EPS % above code requirements and receive service from an "
            "Energy Trust utility",
            result.message,
        )
        self.assertEqual(result.url, "edit_utl")

    def test_get_eto_primary_heating_fuel_type_no_floorplan(self):
        """Test for get_eto_primary_heating_fuel_type. home_status has NO floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, "", **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_primary_heating_fuel_type_no_remrate_target(self):
        """Test get_eto_primary_heating_fuel_type. home_status' floorplan has no remrate target.
        expected result None
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, "", **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_primary_heating_fuel_type_no_heating_equipment_type(self):
        """
        Test for get_eto_primary_heating_fuel_type. input_values (dict) is empty.
        input values is expected to have 'primary-heating-equipment-type' as a key.
        Expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        floorplan = floorplan_with_remrate_factory()
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_primary_heating_fuel_type_heating_fuel_mismatch_1(self):
        """
        Test for get_eto_primary_heating_fuel_type.
        input_values (dict) =  'primary-heating-equipment-type': 'Heat Pump'
        primary heating fuel = 1 i.e. 'Natural gas'
        heating_type = input_values['primary-heating-equipment-type']
        heating_type does NOT contain 'Gas' and != 'Dual Fuel Heat Pump'
        Expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Heat Pump"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        simulation = floorplan.remrate_target
        oven_fuel_name = simulation.building.lightsandappliance.get_oven_fuel_display()
        msg_string = (
            "Primary heating fuel '{rem_fuel}' does not match checklist answer for "
            "primary heating fuel '{checklist_fuel}'"
        )
        msg = msg_string.format(
            rem_fuel=oven_fuel_name, checklist_fuel=input_values["primary-heating-equipment-type"]
        )
        self.assertEqual(msg, result.message)

    def test_get_eto_primary_heating_fuel_type_heating_fuel_mismatch_2(self):
        """
        Test for get_eto_primary_heating_fuel_type.
        input_values (dict) =  'primary-heating-equipment-type': 'Heat Pump'
        primary heating fuel = 4 i.e. 'Electric'
        heating_type = input_values['primary-heating-equipment-type']
        heating_type does NOT contain 'Electric' and != 'Dual Fuel Heat Pump'
        Expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2, "remrate_target__heating__fuel_type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Heat Pump"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        simulation = floorplan.remrate_target
        oven_fuel_name = simulation.building.lightsandappliance.get_oven_fuel_display()
        msg_string = (
            "Primary heating fuel '{rem_fuel}' does not match checklist answer for "
            "primary heating fuel '{checklist_fuel}'"
        )
        msg = msg_string.format(
            rem_fuel=oven_fuel_name, checklist_fuel=input_values["primary-heating-equipment-type"]
        )
        self.assertEqual(msg, result.message)

    def test_get_eto_primary_heating_fuel_type_no_issue_1(self):
        """
        Test for get_eto_primary_heating_fuel_type. heating_type contains 'Electric'
        AND primary_heating_fuel in ['Electric']
        """
        kwargs = {"remrate_target__heating__type": 2, "remrate_target__heating__fuel_type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Electric Resistance"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_primary_heating_fuel_type_no_issue_2(self):
        """
        Test for get_eto_primary_heating_fuel_type. heating_type contains 'Gas'
        AND primary_heating_fuel in ['Natural gas', 'Propane', 'Fuel oil']
        """
        kwargs = {"remrate_target__heating__type": 3, "remrate_target__heating__fuel_type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = {"primary-heating-equipment-type": "Gas Furnace"}
        kwargs = {"checklist_url": "checklist_url"}
        result = eep_program.get_eto_primary_heating_fuel_type(
            home_status.home, home_status, input_values, **kwargs
        )
        self.assertIsNone(result)

    def test_get_eto_percent_improvement_oregon_wrong_home_state(self):
        """
        Test get_eto_percent_improvement_oregon.
        home's state must be 'OR' otherwise expect None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertIsNone(result)

    def test_get_eto_percent_improvement_oregon_unable_to_calculate_eps(self):
        """
        Test get_eto_percent_improvement_oregon. we are trying to calculate improvement, but
        we are not supplying the data required, therefore status Failed!
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        Home.objects.filter(id=home_status.home.id).update(state="OR")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("OR", home_status.home.state)
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertFalse(result.status)
        self.assertIsNotNone(result.data)
        msg = "Unable to calculate EPS"
        self.assertEqual(msg, result.message)
        self.assertIsNone(result.url)

    def test_get_eto_percent_improvement_oregon_calculate_eps_failing_status(self):
        """
        Test get_eto_percent_improvement_oregon. we are trying to calculate improvement. The form it
        uses has 4 required fields:
        [simulation, us_state(home_status.home.state), heat_type(), program(eep_program)]
        """
        from axis.company.models import Company
        from axis.checklist.tests.factories import question_factory, answer_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        Company.objects.filter(id=eep_program.owner.id).update(slug="eto")
        simulation_kwargs = {
            "use_udrh_simulation": True,
            "remrate_target__site__site_label": "portland",
            "remrate_target__percent_improvement": 0.01,
        }
        floorplan = floorplan_with_remrate_factory(**simulation_kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        questions_slug = [
            "eto-primary_heat_type",
            "eto-eto_pathway",
            "eto-water_heater_ef",
            "eto-water_heater_heat_type",
        ]
        answers = ["Dual Fuel Heat Pump", "Pathway 1", "2", "Tankless"]
        for i, slug in enumerate(questions_slug):
            q_kwargs = {"slug": slug}
            question = question_factory(**q_kwargs)
            user = User.objects.filter(company__name="EEP3").first()
            a_kwargs = {"answer": answers[i]}
            answer_factory(question, home_status.home, user, **a_kwargs)

        Home.objects.filter(id=home_status.home.id).update(state="OR")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("OR", home_status.home.state)
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertFalse(result.status)
        msg = "Home is below {min_pct}% improvement and cannot be certified.".format(
            min_pct=int(8.0)
        )
        self.assertEqual(msg, result.message)
        self.assertIsNotNone(result.data)

    def test_get_eto_percent_improvement_oregon_calculate_eps_warning_status(self):
        """
        Test get_eto_percent_improvement_oregon. we are trying to calculate improvement. The form it
        uses has 4 required fields:
        [simulation, us_state(home_status.home.state), heat_type(), program(eep_program)]
        """
        from axis.company.models import Company
        from axis.checklist.tests.factories import question_factory, answer_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        Company.objects.filter(id=eep_program.owner.id).update(slug="eto")
        simulation_kwargs = {
            "use_udrh_simulation": True,
            "remrate_target__site__site_label": "portland",
            "remrate_target__percent_improvement": 0.09,
        }
        floorplan = floorplan_with_remrate_factory(**simulation_kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        questions_slug = [
            "eto-primary_heat_type",
            "eto-eto_pathway",
            "eto-water_heater_ef",
            "eto-water_heater_heat_type",
        ]
        answers = ["Dual Fuel Heat Pump", "Pathway 1", "2", "Tankless"]
        for i, slug in enumerate(questions_slug):
            q_kwargs = {"slug": slug}
            question = question_factory(**q_kwargs)
            user = User.objects.filter(company__name="EEP3").first()
            a_kwargs = {"answer": answers[i]}
            answer_factory(question, home_status.home, user, **a_kwargs)

        Home.objects.filter(id=home_status.home.id).update(state="OR")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("OR", home_status.home.state)
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertFalse(result.status)
        msg = (
            "Home is below 10% improvement. QA will determine if home qualifies under Path 1 "
            "requirements."
        )
        self.assertEqual(msg, result.message)
        self.assertIsNotNone(result.data)

    def test_get_eto_percent_improvement_oregon_calculate_eps_passing_status(self):
        """
        Test get_eto_percent_improvement_oregon. we are trying to calculate improvement. The form it
        uses has 4 required fields:
        [simulation, us_state(home_status.home.state), heat_type(), program(eep_program)]
        """
        from axis.company.models import Company
        from axis.checklist.tests.factories import question_factory, answer_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        Company.objects.filter(id=eep_program.owner.id).update(slug="eto")
        simulation_kwargs = {
            "use_udrh_simulation": True,
            "remrate_target__site__site_label": "portland",
        }
        floorplan = floorplan_with_remrate_factory(**simulation_kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        questions_slug = [
            "eto-primary_heat_type",
            "eto-eto_pathway",
            "eto-water_heater_ef",
            "eto-water_heater_heat_type",
        ]
        answers = ["Dual Fuel Heat Pump", "Pathway 1", "2", "Tankless"]
        for i, slug in enumerate(questions_slug):
            q_kwargs = {"slug": slug}
            question = question_factory(**q_kwargs)
            user = User.objects.filter(company__name="EEP3").first()
            a_kwargs = {"answer": answers[i]}
            answer_factory(question, home_status.home, user, **a_kwargs)

        Home.objects.filter(id=home_status.home.id).update(state="OR")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("OR", home_status.home.state)
        result = eep_program.get_eto_percent_improvement_oregon(home_status.home, home_status)
        self.assertTrue(result.status)
        self.assertIsNotNone(result.data)

    def test_get_eto_percent_improvement_washington_wrong_state(self):
        """Test for get_eto_percent_improvement_washington. home's state is NOT 'WA'"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_percent_improvement_washington(
            home_status.home, home_status, ""
        )
        self.assertIsNone(result)

    @mock.patch("axis.home.utils.get_eps_data")
    def test_get_eto_percent_improvement_washington_unable_to_calculate_eps(self, get_eps_data):
        """Test for get_eto_builder_incentive_status"""

        from axis.customer_eto.calculator.eps.base import EPSInputException

        get_eps_data.side_effect = EPSInputException("something")
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_eto_percent_improvement_washington(
            home_status.home, home_status, ""
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn("Unable to calculate EPS", result.message)
        self.assertIsNone(result.url)

    def test_get_eto_percent_improvement_washington_improvement_failure(self):
        """
        Test get_eto_percent_improvement_washington. we are trying to calculate improvement.
        The form it uses has 4 required fields:
        [simulation, us_state(home_status.home.state), heat_type(), program(eep_program)]
        """
        from axis.company.models import Company
        from axis.checklist.tests.factories import question_factory, answer_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        Company.objects.filter(id=eep_program.owner.id).update(slug="eto")
        simulation_kwargs = {
            "use_udrh_simulation": True,
            "remrate_target__site__site_label": "portland",
            "remrate_target__percent_improvement": 0.01,
        }
        floorplan = floorplan_with_remrate_factory(**simulation_kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        questions_slug = [
            "eto-primary_heat_type",
            "eto-eto_pathway",
            "eto-water_heater_ef",
            "eto-water_heater_heat_type",
        ]
        answers = ["Dual Fuel Heat Pump", "Pathway 1", "2", "Tankless"]
        for i, slug in enumerate(questions_slug):
            q_kwargs = {"slug": slug}
            question = question_factory(**q_kwargs)
            user = User.objects.filter(company__name="EEP3").first()
            a_kwargs = {"answer": answers[i]}
            answer_factory(question, home_status.home, user, **a_kwargs)

        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("WA", home_status.home.state)
        input_values = {"primary-heating-equipment-type": ""}
        result = eep_program.get_eto_percent_improvement_washington(
            home_status.home, home_status, input_values
        )
        self.assertFalse(result.status)
        msg = "Home is below {min_pct}% improvement and cannot be certified.".format(
            min_pct=int(10.0)
        )
        self.assertEqual(msg, result.message)
        self.assertIsNotNone(result.data)

    def test_get_eto_percent_improvement_washington_calculate_eps_passing_status(self):
        """
        Test get_eto_percent_improvement_washington. we are trying to calculate improvement.
        The form it uses has 4 required fields:
        [simulation, us_state(home_status.home.state), heat_type(), program(eep_program)]
        """
        from axis.company.models import Company
        from axis.checklist.tests.factories import question_factory, answer_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        Company.objects.filter(id=eep_program.owner.id).update(slug="eto")
        simulation_kwargs = {
            "use_udrh_simulation": True,
            "remrate_target__site__site_label": "portland",
            "remrate_target__percent_improvement": 0.01,
        }
        floorplan = floorplan_with_remrate_factory(**simulation_kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        questions_slug = [
            "eto-primary_heat_type",
            "eto-eto_pathway",
            "eto-water_heater_ef",
            "eto-water_heater_heat_type",
        ]
        answers = ["Dual Fuel Heat Pump", "Pathway 1", "2", "Tankless"]
        for i, slug in enumerate(questions_slug):
            q_kwargs = {"slug": slug}
            question = question_factory(**q_kwargs)
            user = User.objects.filter(company__name="EEP3").first()
            a_kwargs = {"answer": answers[i]}
            answer_factory(question, home_status.home, user, **a_kwargs)

        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("WA", home_status.home.state)
        input_values = {"primary-heating-equipment-type": "Electric Resistance"}
        result = eep_program.get_eto_percent_improvement_washington(
            home_status.home, home_status, input_values
        )
        self.assertTrue(result.status)
        self.assertIsNotNone(result.data)

    def test_get_eto_percent_improvement_washington_calculate_eps_passing_status_2(self):
        """
        Test get_eto_percent_improvement_washington. we are trying to calculate improvement.
        The form it uses has 4 required fields:
        [simulation, us_state(home_status.home.state), heat_type(), program(eep_program)]
        """
        from axis.company.models import Company
        from axis.checklist.tests.factories import question_factory, answer_factory

        EEPProgram.objects.filter(owner__name="EEP3").update(slug="eto")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        Company.objects.filter(id=eep_program.owner.id).update(slug="eto")
        simulation_kwargs = {
            "use_udrh_simulation": True,
            "remrate_target__site__site_label": "portland",
        }
        floorplan = floorplan_with_remrate_factory(**simulation_kwargs)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        questions_slug = [
            "eto-primary_heat_type",
            "eto-eto_pathway",
            "eto-water_heater_ef",
            "eto-water_heater_heat_type",
        ]
        answers = ["Dual Fuel Heat Pump", "Pathway 1", "2", "Tankless"]
        for i, slug in enumerate(questions_slug):
            q_kwargs = {"slug": slug}
            question = question_factory(**q_kwargs)
            user = User.objects.filter(company__name="EEP3").first()
            a_kwargs = {"answer": answers[i]}
            answer_factory(question, home_status.home, user, **a_kwargs)

        Home.objects.filter(id=home_status.home.id).update(state="WA")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertEqual("WA", home_status.home.state)
        input_values = {}
        result = eep_program.get_eto_percent_improvement_washington(
            home_status.home, home_status, input_values
        )
        self.assertTrue(result.status)
        self.assertIsNotNone(result.data)
