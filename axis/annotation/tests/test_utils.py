"""test_utils.py - Axis"""

__author__ = "Steven K"
__date__ = "10/27/21 15:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import random
from collections import OrderedDict
import datetime

from axis.core.tests.testcases import AxisTestCase
from ..utils import (
    validate_annotation_type_content,
    validate_annotation_by_name,
    validate_annotations,
)
from ...company.tests.factories import eep_organization_factory
from ...eep_program.program_builder import ProgramBuilder
from ...filehandling.log_storage import LogStorage
from ...geographic.tests.factories import real_city_factory
from ..models import Type as AnnotationType

log = logging.getLogger(__name__)


class AnnotationUtilsTests(AxisTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Kennewick", "WA")

        cls.eto = eep_organization_factory(
            slug="eep", is_customer=True, name="EEP Organization", city=cls.city
        )

        cls.choices = ["Yes", "No", "Maybe", "Perhaps"]

        cls.unrelated_annotation_type = AnnotationType.objects.create(
            name="unrelated", data_type="open"
        )

        class TestProgram(ProgramBuilder):
            """This is a Test program"""

            slug = "program"
            name = "Fancy Program"
            owner = "eep"
            annotations = OrderedDict(
                (
                    (
                        "open-annotation",
                        {
                            "name": "Open annotation",
                            "data_type": "open",
                            "is_required": "True",
                        },
                    ),
                    (
                        "multiple-choice-annotation",
                        {
                            "name": "Multi-Choice Annotation",
                            "data_type": "multiple-choice",
                            "valid_multiplechoice_values": ",".join(cls.choices),
                            "is_required": "True",
                        },
                    ),
                    (
                        "integer-annotation",
                        {
                            "name": "Integer",
                            "data_type": "integer",
                            "is_required": "True",
                        },
                    ),
                    (
                        "float-annotation",
                        {
                            "name": "Float",
                            "data_type": "float",
                            "is_required": "True",
                        },
                    ),
                    (
                        "date-annotation",
                        {
                            "name": "Date",
                            "data_type": "date",
                            "is_required": "True",
                        },
                    ),
                )
            )

        cls.eep_program = TestProgram().build("rater")

    def setUp(self) -> None:
        self.log = LogStorage()

    def test_validate_annotation_type_content_open(self):
        annotation_type = AnnotationType.objects.get(slug="open-annotation")
        with self.subTest("Passing Data"):
            content = "X" * 500
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content)
        with self.subTest("Data too long"):
            content = "X" * 501
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], None)
            self.assertIn("maximum length of 500 characters", self.log.report_chronological()[-1])

    def test_validate_annotation_type_content_multiple_choice(self):
        annotation_type = AnnotationType.objects.get(slug="multiple-choice-annotation")
        with self.subTest("Passing Upper Data"):
            content = random.choice(self.choices)
            data = validate_annotation_type_content(annotation_type, content.upper(), log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content)
        with self.subTest("Passing Lower Data"):
            content = random.choice(self.choices)
            data = validate_annotation_type_content(annotation_type, content.lower(), log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content)
        with self.subTest("Failing"):
            content = "Yes,No"
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], None)
            self.assertIn("It must be one of", self.log.report_chronological()[-1])

    def test_validate_annotation_type_content_date(self):
        annotation_type = AnnotationType.objects.get(slug="date-annotation")
        with self.subTest("Passing date"):
            content = datetime.date.today()
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content.strftime("%m-%d-%Y"))
        with self.subTest("Passing string date"):
            content = "2021-10-27"
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], "10-27-2021")
        with self.subTest("Failing"):
            content = "yesterday"
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], None)
            self.assertIn("as a date", self.log.report_chronological()[-1])

    def test_validate_annotation_type_content_integer(self):
        annotation_type = AnnotationType.objects.get(slug="integer-annotation")
        with self.subTest("Passing Integer"):
            content = 500
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], str(content))
        with self.subTest("Passing Integer Str"):
            content = str(500)
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content)
        with self.subTest("Failing"):
            content = str(5.2)
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], None)
            self.assertIn("as a whole number", self.log.report_chronological()[-1])

    def test_validate_annotation_type_content_float(self):
        annotation_type = AnnotationType.objects.get(slug="float-annotation")
        with self.subTest("Passing Float"):
            content = -1.23
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], str(content))
        with self.subTest("Passing Float Str"):
            content = str(1.2e10)
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content)
        with self.subTest("Failing"):
            content = "10s"
            data = validate_annotation_type_content(annotation_type, content, log=self.log)
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], None)
            self.assertIn("as a decimal number", self.log.report_chronological()[-1])

    def test_validate_annotation_by_name(self):
        annotation_type = AnnotationType.objects.get(slug="open-annotation")
        with self.subTest("Passing Data"):
            content = "Something"
            data = validate_annotation_by_name(
                self.eep_program, annotation_type.name, content, log=self.log
            )
            self.assertEqual(data["type"], annotation_type)
            self.assertEqual(data["content"], content)
        with self.subTest("Unrelated"):
            data = validate_annotation_by_name(
                self.eep_program, self.unrelated_annotation_type.name, content, log=self.log
            )
            self.assertEqual(data, None)
            self.assertIn("is not recognized for the program", self.log.report_chronological()[-1])

    def test_validate_annotations(self):
        with self.subTest("Passing data"):
            annotations = [{"type": "open-annotation", "content": "Something"}]
            result = validate_annotations(self.eep_program, annotations, self.log)
            self.assertEqual(len(result), 1)
        with self.subTest("Invalid annotation type"):
            annotations = [{"type": "unrelated", "content": "Something"}]
            result = validate_annotations(self.eep_program, annotations, self.log)
            self.assertEqual(len(result), 0)
            self.assertIn("is not included in program", self.log.report_chronological()[-1])
        with self.subTest("Invalid Data Validation"):
            annotations = [{"type": "float-annotation", "content": "Something1"}]
            result = validate_annotations(self.eep_program, annotations, self.log)
            self.assertEqual(len(result), 0)
            self.assertIn("as a decimal number", self.log.report_chronological()[-1])
