"""test_wa_code_study.py: Django Washington Code Study Checks"""


import copy
import logging

from axis.core.tests.testcases import AxisTestCase
from axis.core.tests.client import AxisClient
from axis.annotation.models import Annotation
from axis.customer_neea.tests.mixins import WaCodeStudyProgramTestMixin
from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven K"
__date__ = "10/16/2019 12:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class EEPProgramWACodeStudyProgramChecksTests(WaCodeStudyProgramTestMixin, AxisTestCase):
    """Test for WA Code Stud eep_program"""

    client_class = AxisClient

    def setUp(self):
        """Convenience attrs"""
        super(EEPProgramWACodeStudyProgramChecksTests, self).setUp()
        self.program = EEPProgram.objects.first()
        self.home_status = EEPProgramHomeStatus.objects.first()
        self.check_data = dict(home_status=self.home_status, input_values={}, checklist_url="?")

    def test_dwelling_size(self):
        annotation = Annotation.objects.get(type__slug="dwelling-type")
        validation_check = self.program.get_wa_code_annotation_dwelling_status
        self.assertEqual(annotation.content, "Small Dwelling")

        _data = self.check_data.copy()
        result = validation_check(**_data)
        self.assertIsNone(result)

        _data.update({"input_values": {"home-size": "1000"}})
        result = validation_check(**_data)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

        _data.update({"input_values": {"home-size": "2000"}})
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.total_weight, 1)

        _data.update({"input_values": {"home-size": "6000"}})
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.total_weight, 1)

        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(
            content="Medium Dwelling"
        )
        _data.update({"input_values": {"home-size": "4000"}})
        result = validation_check(**_data)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(
            content="Large Dwelling"
        )
        _data.update({"input_values": {"home-size": "8000"}})
        result = validation_check(**_data)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

    def _test_option_1(self, source, validation_check):
        """This is a shared set of checks"""
        _data = copy.deepcopy(source)
        _data["input_values"].update(
            {
                "home-foundation-r-value": "9",
            }
        )
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

        _data = copy.deepcopy(source)
        _data["input_values"].update(
            {
                "home-floor-r-value": "37.0",
            }
        )
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

        _data = copy.deepcopy(source)
        _data["input_values"].update({"home-window-u-value": ".29"})
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def test_option_1a(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-envelope")
        validation_check = self.program.get_wa_code_opt_1_status

        self.assertEqual(annotation.content, "1a")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 3)

        source.update(
            {
                "input_values": {
                    "foundation-type": "Slab on Grade",
                    "home-foundation-r-value": "12",
                    "home-floor-r-value": "39.0",
                    "home-window-u-value": ".27",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 3)
        self.assertEqual(result.total_weight, 3)

        self._test_option_1(source, validation_check)

    def test_option_1b(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-envelope")
        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(content="1b")
        validation_check = self.program.get_wa_code_opt_1_status

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 5)

        source.update(
            {
                "input_values": {
                    "foundation-type": "Slab on Grade",
                    "home-foundation-r-value": "12",
                    "home-floor-r-value": "39.0",
                    "home-window-u-value": ".24",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 5)
        self.assertEqual(result.total_weight, 5)

        self._test_option_1(source, validation_check)

    def test_option_1c(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-envelope")
        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(content="1c")
        validation_check = self.program.get_wa_code_opt_1_status

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 6)

        source.update(
            {
                "input_values": {
                    "foundation-type": "Slab on Grade",
                    "home-foundation-r-value": "12",
                    "home-floor-r-value": "39.0",
                    "home-window-u-value": ".21",
                    "meets-wa-code-ceiling-requirements": "Yes",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 6)
        self.assertEqual(result.total_weight, 6)

        self._test_option_1(source, validation_check)

        source["input_values"].update({"meets-wa-code-ceiling-requirements": "No"})
        result = validation_check(**source)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def test_option_1d(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-envelope")
        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(content="1d")
        validation_check = self.program.get_wa_code_opt_1_status

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

        source.update(
            {
                "input_values": {
                    "home-window-u-value": ".21",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 1)
        self.assertEqual(result.total_weight, 1)

        source["input_values"].update({"home-window-u-value": ".25"})
        result = validation_check(**source)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def _test_option_2(self, source, validation_check):
        _data = copy.deepcopy(source)
        _data["input_values"].update(
            {
                "home-infiltration-ach": "3.1",
            }
        )
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def test_option_2a(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-air-leakage")
        validation_check = self.program.get_wa_code_opt_2_status

        self.assertEqual(annotation.content, "2a")

        source = self.check_data.copy()

        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 2)

        source.update(
            {
                "input_values": {
                    "home-infiltration-ach": "2.9",
                    "home-ventilation-type": "High Efficiency Fan",
                    "home-ventilation-fan-rating": "0.35",
                }
            }
        )

        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 2)
        self.assertEqual(result.total_weight, 2)

        self._test_option_2(source, validation_check)

        _data = copy.deepcopy(source)
        _data["input_values"].update(
            {
                "home-ventilation-fan-rating": ".33",
            }
        )
        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def test_option_2b(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-air-leakage")
        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(content="2b")
        validation_check = self.program.get_wa_code_opt_2_status

        source = self.check_data.copy()

        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 2)

        source.update(
            {
                "input_values": {
                    "home-infiltration-ach": "1.7",
                    "home-ventilation-type": "HRV",
                    "home-ventilation-sensible-heat-recovery-rating": ".71",
                }
            }
        )

        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 2)

        self._test_option_2(source, validation_check)

        _data = copy.deepcopy(source)
        _data["input_values"].update(
            {
                "home-ventilation-sensible-heat-recovery-rating": ".69",
            }
        )

        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def test_option_2c(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-air-leakage")
        self.home_status.annotations.filter(type__slug=annotation.type.slug).update(content="2c")
        validation_check = self.program.get_wa_code_opt_2_status

        source = self.check_data.copy()

        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 2)

        source.update(
            {
                "input_values": {
                    "home-infiltration-ach": "1.4",
                    "home-ventilation-type": "HRV",
                    "home-ventilation-sensible-heat-recovery-rating": ".86",
                }
            }
        )

        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 2)

        self._test_option_2(source, validation_check)

        _data = copy.deepcopy(source)
        _data["input_values"].update(
            {
                "home-ventilation-sensible-heat-recovery-rating": ".75",
            }
        )

        result = validation_check(**_data)
        self.assertFalse(result.status)
        self.assertEqual(result.weight, 1)

    def test_option_3(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-hvac")
        validation_check = self.program.get_wa_code_opt_3_status

        self.assertEqual(annotation.content, "3a")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 2)

        source.update(
            {
                "input_values": {
                    "home-furnace-afue": "95",
                    "home-boiler-afue": "95",
                    "home-primary-heating": "Gas Furnace",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 2)
        self.assertEqual(result.total_weight, 2)

    def test_option_4(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-hvac-distribution")
        validation_check = self.program.get_wa_code_opt_4_status

        self.assertEqual(annotation.content, "4")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 4)

        source.update(
            {
                "input_values": {
                    "home-primary-heating": "Gas Furnace",
                    "home-duct-primary-location": "Conditioned Space",
                    "home-furnace-afue": "81",
                    "meets-wa-code-duct-requirements": "Yes",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 4)
        self.assertEqual(result.total_weight, 4)

    def test_option_5a(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-water-heating-5a")
        validation_check = self.program.get_wa_code_opt_5a_status

        self.assertEqual(annotation.content, "5a")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

        source.update(
            {
                "input_values": {
                    "showerhead-flow-rate": "1.5",
                    "kitchen-faucet-flow-rate": "1.5",
                    "bathroom-faucet-flow-rate": "0.9",
                    "meets-wa-code-shower-head-requirements": "Yes",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 4)
        self.assertEqual(result.total_weight, 4)

    def test_option_5bc(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-water-heating-5bc")
        validation_check = self.program.get_wa_code_opt_5bc_status

        self.assertEqual(annotation.content, "5c")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 4)

        source.update(
            {
                "input_values": {
                    "home-primary-hot-water-type": "Gas conventional",
                    "home-primary-hot-water-gas-ef": "0.91",
                    "home-primary-hot-water-hp-ef": "2.1",
                    "meets-wa-code-solar-water-requirements": "Yes",
                    "meets-neea-hp-requirements": "Yes",
                    "home-primary-heating": "Ground Source Heat Pump",
                    "home-gshp-cop": "3.4",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 4)
        self.assertEqual(result.total_weight, 4)

    def test_option_5d(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-water-heating-5d")
        validation_check = self.program.get_wa_code_opt_5d_status

        self.assertEqual(annotation.content, "5d")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

        source.update(
            {
                "input_values": {
                    "meets-wa-code-drain-water-requirements": "Yes",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 1)
        self.assertEqual(result.total_weight, 1)

    def test_option_6(self):
        annotation = Annotation.objects.get(type__slug="efficient-building-renewable-energy")
        validation_check = self.program.get_wa_code_opt_6_status

        self.assertEqual(annotation.content, "1")

        source = self.check_data.copy()
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.total_weight, 1)

        source.update(
            {
                "input_values": {
                    "meets-wa-code-energy-credit-option": "Yes",
                }
            }
        )
        result = validation_check(**source)
        self.assertTrue(result.status)
        self.assertEqual(result.weight, 1)
        self.assertEqual(result.total_weight, 1)
