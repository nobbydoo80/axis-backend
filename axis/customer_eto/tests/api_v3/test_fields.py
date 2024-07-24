"""fields.py - Axis"""

__author__ = "Steven K"
__date__ = "9/29/21 16:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase
from rest_framework import serializers

from axis.customer_eto.api_v3.fields import CappedIntegerCommaField, CappedCommaFloatField
from axis.customer_eto.api_v3.serializers.fields import EnumField
from axis.customer_eto.enumerations import SmartThermostatBrands2020

log = logging.getLogger(__name__)


class FieldValuesTests(TestCase):
    """Shamelessly re-implemented from how DRF tests Fields"""

    valid_inputs = {}
    invalid_inputs = {}
    outputs = {}
    field_class = None

    def test_valid_inputs(self):
        for input_value, expected_output in self.valid_inputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                self.assertEqual(self.field_class().run_validation(input_value), expected_output)

    def test_invalid_inputs(self):
        for input_value, expected_failure in self.invalid_inputs.items():
            with self.subTest(f"Invalid Input value {input_value} -> {expected_failure}"):
                self.assertRaises(
                    serializers.ValidationError, self.field_class().run_validation, input_value
                )

    def test_outputs(self):
        for output_value, expected_output in self.outputs.items():
            with self.subTest(f"output value {output_value} -> {expected_output}"):
                self.assertEqual(
                    self.field_class().to_representation(output_value), expected_output
                )


class TestCappedIntegerCommaField(FieldValuesTests):
    valid_inputs = {
        "1": 1,
        "1.25": 1,
        "1.89": 2,
        "0": 0,
        "1,000": 1000,
        "-1,000": -1000,
        1: 1,
        1.99: 2,
        0: 0,
        1.0: 1,
        1.89: 2,
        0.0: 0,
        "1,000.00": 1000,
        "-1,000.00": -1000,
    }

    invalid_inputs = {
        "abc": ["A valid number is required."],
    }
    outputs = {
        "1": "1",
        "0": "0",
        "1000": "1,000",
        "123": "123",
        "-123": "-123",
        "1.25": "1",
        "1.99": "2",
        1: "1",
        1000: "1,000",
        -1000: "-1,000",
        0: "0",
        1.0: "1",
        1.25: "1",
        1.99: "2",
        0.0: "0",
        1000.0: "1,000",
        -1000.0: "-1,000",
    }
    field_class = CappedIntegerCommaField

    minimum_value = 0
    valid_minimum_inputs = {
        "1": 1,
        "0": 0,
        "-1000": 0,
        1: 1,
        1001: 1001,
        -1000: 0,
    }
    valid_minimum_outputs = {
        1: "1",
        1001: "1,001",
        -1000: "0",
    }

    maximum_value = 1000
    valid_maximum_inputs = {
        "-1": -1,
        "1001": 1000,
        -1: -1,
        1001: 1000,
    }
    valid_maximum_outputs = {
        "-1": "-1",
        "1001": "1,000",
        -1: "-1",
        1001: "1,000",
    }
    prefix = "€"
    suffix = "!"

    def test_minimum_acceptable_value_inputs(self):
        for input_value, expected_output in self.valid_minimum_inputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                field = self.field_class(minimum_acceptable_value=self.minimum_value)
                self.assertEqual(field.run_validation(input_value), expected_output)

    def test_minimum_acceptable_value_outputs(self):
        for input_value, expected_output in self.valid_minimum_outputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                field = self.field_class(minimum_acceptable_value=self.minimum_value)
                print(field)
                self.assertEqual(field.to_representation(input_value), expected_output)

    def test_maximum_acceptable_value_inputs(self):
        for input_value, expected_output in self.valid_maximum_inputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                field = self.field_class(maximum_acceptable_value=self.maximum_value)
                self.assertEqual(field.run_validation(input_value), expected_output)

    def test_maximum_acceptable_value_outputs(self):
        for input_value, expected_output in self.valid_maximum_outputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                field = self.field_class(maximum_acceptable_value=self.maximum_value)
                self.assertEqual(field.to_representation(input_value), expected_output)

    def test_valid_inputs_prefix(self):
        for input_value, expected_output in self.valid_inputs.items():
            with self.subTest(f"Input value {self.prefix}{input_value} -> {expected_output}"):
                field = self.field_class(prefix=self.prefix)
                input_value = f"{self.prefix}{input_value}"
                self.assertEqual(field.run_validation(input_value), expected_output)

    def test_prefix_outputs(self):
        for output_value, expected_output in self.outputs.items():
            with self.subTest(f"output value {output_value} -> {self.prefix}{expected_output}"):
                field = self.field_class(prefix=self.prefix)
                expected_output = f"{self.prefix}{expected_output}"
                self.assertEqual(field.to_representation(output_value), expected_output)

    def test_valid_inputs_suffix(self):
        for input_value, expected_output in self.valid_inputs.items():
            with self.subTest(f"Input value {input_value}{self.suffix} -> {expected_output}"):
                field = self.field_class(suffix=self.suffix)
                input_value = f"{input_value}{self.suffix}"
                self.assertEqual(field.run_validation(input_value), expected_output)

    def test_suffix_outputs(self):
        for output_value, expected_output in self.outputs.items():
            with self.subTest(f"output value {output_value} -> {expected_output}{self.suffix}"):
                field = self.field_class(suffix=self.suffix)
                expected_output = f"{expected_output}{self.suffix}"
                self.assertEqual(field.to_representation(output_value), expected_output)


class TestCappedCommaFloatField(TestCappedIntegerCommaField):
    valid_inputs = {
        "1": 1.0,
        "0": 0,
        "1,000": 1000.0,
        "-1,000": -1000.0,
        "1.25": 1.25,
        1: 1.0,
        0: 0,
        1.25: 1.25,
        0.0: 0.0,
        "1,000.00": 1000.0,
        "-1,000.00": -1000.0,
    }

    invalid_inputs = {
        "abc": ["A valid number is required."],
    }
    outputs = {
        "1": "1.0",
        "0": "0.0",
        "1000": "1,000.0",
        "1.25": "1.25",
        "-123": "-123.0",
        1: "1.0",
        1000: "1,000.0",
        -1000: "-1,000",
        0: "0.0",
        1.25: "1.25",
        0.0: "0.0",
        1000.0: "1,000.0",
        -1000.0: "-1,000.0",
    }
    field_class = CappedCommaFloatField

    minimum_value = 0
    valid_minimum_inputs = {
        "1": 1.0,
        "0": 0.0,
        "1.25": 1.25,
        "-1000": 0.0,
        1.25: 1.25,
        1001: 1001,
        -1000: 0.0,
    }
    valid_minimum_outputs = {
        1: "1.0",
        1001: "1,001.0",
        -1000: "0.0",
    }

    maximum_value = 1000
    valid_maximum_inputs = {
        "-1": -1.0,
        "1001": 1000.0,
        "1.25": 1.25,
        -1: -1.0,
        1001: 1000.0,
    }
    valid_maximum_outputs = {
        "-1": "-1.0",
        "1.25": "1.25",
        "1001": "1,000.0",
        -1: "-1.0",
        1.25: "1.25",
        1001: "1,000.0",
    }

    prefix = "€"

    valid_parens_inputs = {
        "(1)": -1.0,
        "1001": 1001.0,
        "(1.25)": -1.25,
        -1: -1.0,
        1001: 1001.0,
    }
    valid_parens_outputs = {
        "-1": "(1.0)",
        "1.25": "1.25",
        -1: "(1.0)",
        1.25: "1.25",
        -1001.2: "(1,001.2)",
    }

    valid_percent_inputs = {
        "1%": 0.01,
        "100.2%": 1.002,
        "-1%": -0.01,
        "99%": 0.99,
    }
    valid_percent_outputs = {
        "0.1": "10.000000%",
        "1.25": "125.000000%",
        -0.01: "-1.000000%",
        0.25: "25.000000%",
        125: "12,500.000000%",
    }

    def test_valid_inputs_parens(self):
        for input_value, expected_output in self.valid_parens_inputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                field = self.field_class(represent_negatives_as_paren=True)
                self.assertEqual(field.run_validation(input_value), expected_output)

    def test_parens_outputs(self):
        for output_value, expected_output in self.valid_parens_outputs.items():
            with self.subTest(f"output value {output_value} -> {expected_output}"):
                field = self.field_class(represent_negatives_as_paren=True)
                self.assertEqual(field.to_representation(output_value), expected_output)

    def test_valid_inputs_percent(self):
        for input_value, expected_output in self.valid_percent_inputs.items():
            with self.subTest(f"Input value {input_value} -> {expected_output}"):
                field = self.field_class(represent_percent=True)
                self.assertEqual(field.run_validation(input_value), expected_output)

    def test_percent_outputs(self):
        for output_value, expected_output in self.valid_percent_outputs.items():
            with self.subTest(f"output value {output_value} -> {expected_output}"):
                field = self.field_class(represent_percent=True)
                self.assertEqual(field.to_representation(output_value), expected_output)

    def test_percent_outputs_with_round(self):
        for output_value, expected_output in self.valid_percent_outputs.items():
            expected_output = expected_output.replace(".000000", "")
            with self.subTest(f"output value {output_value} -> {expected_output}"):
                field = self.field_class(represent_percent=True, round_value=0)
                self.assertEqual(field.to_representation(output_value), expected_output)


class TestEnumFieldTestCase(TestCase):
    def test_case_insensitive_enum(self):
        """Test to verify case-insensitive value."""
        field = EnumField(SmartThermostatBrands2020)
        self.assertEqual(
            field.to_internal_value(SmartThermostatBrands2020.ECOBEE4.value),
            SmartThermostatBrands2020.ECOBEE4,
        )
        self.assertEqual(
            field.to_internal_value(SmartThermostatBrands2020.ECOBEE4.value.lower()),
            SmartThermostatBrands2020.ECOBEE4,
        )
        self.assertEqual(
            field.to_internal_value(SmartThermostatBrands2020.ECOBEE4.value.upper()),
            SmartThermostatBrands2020.ECOBEE4,
        )
        self.assertEqual(
            field.to_internal_value(SmartThermostatBrands2020.ECOBEE4),
            SmartThermostatBrands2020.ECOBEE4,
        )
