"""unit test for program specs gen"""


__author__ = "Johnny Fang"
__date__ = "02/12/19 7::55 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

import logging
import os
from datetime import datetime

from importlib import import_module

from axis.core.tests.testcases import AxisTestCase
from axis.core.tests.client import AxisClient
from axis.checklist.models import Question
from axis.eep_program.program_builder.base import ProgramBuilder
from axis.eep_program.management.commands.write_program import Command
from axis.eep_program.tests.mixins import ProgramSpecsGenFixtureMixin

log = logging.getLogger(__name__)


class ProgramSpecsGenTests(ProgramSpecsGenFixtureMixin, AxisTestCase):
    client_class = AxisClient
    DIR_PATH = "axis/eep_program/program_builder/"
    FILENAME = "program_generation_test"
    CLASS_NAME = "MyTestProgram"

    class SampleProgram(ProgramBuilder):
        CERTIFIER_SLUG = "neea"

        name = "Test program for Program Specs Gen"
        slug = "test-program"
        owner = CERTIFIER_SLUG
        simulation_type = None

    @classmethod
    def tearDownClass(cls):
        super(ProgramSpecsGenTests, cls).tearDownClass()
        filename = "generated_%s.py" % cls.FILENAME
        module_path = os.path.join(cls.DIR_PATH, filename)
        if os.path.exists(module_path):
            os.remove(module_path)
        else:
            log.info("The file does not exist")

    def create_program_file(self):
        command = Command()
        program = self.SampleProgram()
        program.slug = "test-program"
        program.class_name = self.CLASS_NAME
        expected_filename = "generated_%s.py" % self.FILENAME
        command.write_program_file(program, self.FILENAME, print_output=False)
        return expected_filename

    def test_create_file(self):
        """Test file gets created"""
        expected_filename = self.create_program_file()
        self.assertTrue(os.path.exists(os.path.join(self.DIR_PATH, expected_filename)))
        os.remove(os.path.join(self.DIR_PATH, expected_filename))

    def test_file_generated_class(self):
        """Test file gets generated with the correct class name and basic attrs"""
        base_filename = self.create_program_file()
        filename = base_filename.strip(".py")
        module_path = os.path.join(self.DIR_PATH, filename)
        module = module_path.replace("/", ".")
        program_class = getattr(import_module(module), self.CLASS_NAME, None)
        self.assertIsNotNone(program_class)
        base_program = self.SampleProgram()
        self.assertEqual(program_class.name, base_program.name)
        self.assertEqual(program_class.slug, base_program.slug)
        self.assertEqual(program_class.owner.lower(), base_program.owner.lower())
        os.remove(os.path.join(self.DIR_PATH, base_filename))


class ProgramSpecsGenAttributesTests(ProgramSpecsGenFixtureMixin, AxisTestCase):
    """This set of tests will focus on verifying the correctnes  of the output (structure and data)"""

    client_class = AxisClient

    DIR_PATH = "axis/eep_program/program_builder/"
    FILENAME = "my_test_file"
    CLASS_NAME = "MyTestProgram"

    class SampleProgram(ProgramBuilder):
        CERTIFIER_SLUG = "neea"

        name = "Test program for Program Specs Gen"
        slug = "test-program"
        owner = CERTIFIER_SLUG
        simulation_type = None
        program_start_date = datetime(2019, 1, 1)
        program_visibility_date = datetime(2019, 1, 1)

    @classmethod
    def setUpClass(cls):
        super(ProgramSpecsGenAttributesTests, cls).setUpClass()
        command = Command()
        program = cls.SampleProgram()
        program.slug = "test-program"
        program.class_name = cls.CLASS_NAME
        filename = "generated_%s.py" % cls.FILENAME
        module_name = filename.strip(".py")
        cls.filepath = command.write_program_file(program, cls.FILENAME, print_output=False)
        module_path = os.path.join(cls.DIR_PATH, module_name)
        module = import_module(module_path.replace("/", "."))
        cls.program_class = getattr(module, cls.CLASS_NAME, None)

    def tearDown(self):
        if self.filepath and os.path.exists(os.path.join(self.DIR_PATH, self.filepath)):
            os.remove(os.path.join(self.DIR_PATH, self.filepath))

    def test_measures_spec(self):
        """Test measures specs. for more info about the program used in this test look in the fixturecompilers.py"""
        program = self.program_class
        role = "rater"
        segment = "default"
        measures = program.measures

        file_measures = measures[role][segment]
        question_cnt = Question.objects.count()
        self.assertEqual(len(file_measures), question_cnt)
        question_slugs = list(Question.objects.values_list("slug", flat=True))
        self.assertEqual(set(file_measures), set(question_slugs))

    def test_texts_spec(self):
        """Test texts specs."""
        program = self.program_class
        role = "rater"
        texts = program.texts

        file_texts = texts[role]
        texts_keys = list(file_texts.keys())
        question_slugs = list(Question.objects.values_list("slug", flat=True))
        self.assertEqual(set(texts_keys), set(question_slugs))
        texts_values = list(file_texts.values())
        questions_text = list(Question.objects.values_list("question", flat=True))
        self.assertEqual(set(texts_values), set(questions_text))

    def test_description_spec(self):
        """Test descriptions specs"""
        program = self.program_class
        role = "rater"
        descriptions = program.descriptions

        file_descriptions = descriptions[role]
        descriptions_keys = file_descriptions.keys()
        question_slugs = list(Question.objects.values_list("slug", flat=True))
        self.assertEqual(set(descriptions_keys), set(question_slugs))
        descriptions_values = file_descriptions.values()
        questions_description = list(Question.objects.values_list("description", flat=True))
        self.assertEqual(set(descriptions_values), set(questions_description))

    def test_suggested_responses_spec(self):
        """Test suggested_responses specs"""
        program = self.program_class
        role = "rater"
        suggested_responses = program.suggested_responses

        file_suggested = suggested_responses[role]

        questions = Question.objects.all()
        expected_suggested = {}
        for question in questions:
            choices = tuple(question.question_choice.values_list("choice", flat=True))
            if choices:
                if choices not in expected_suggested:
                    expected_suggested[choices] = [question.slug]
                else:
                    expected_suggested[choices].append(question.slug)
        flat_list = [measure for sublist in file_suggested.values() for measure in sublist]
        flat_expected_list = [
            measure for sublist in expected_suggested.values() for measure in sublist
        ]
        self.assertEqual(file_suggested.keys(), expected_suggested.keys())
        self.assertEqual(flat_list, flat_expected_list)

    def test_instrument_types_spec(self):
        """Test instrument_types specs"""
        program = self.program_class
        instrument_types = program.instrument_types

        questions = Question.objects.all()
        expected_instrument_types = {}
        for question in questions:
            q_type = question.type
            if q_type in ["date", "integer", "float"]:
                if q_type not in expected_instrument_types:
                    expected_instrument_types[q_type] = [question.slug]
                else:
                    expected_instrument_types[q_type].append(question.slug)
        flat_list = [measure for sublist in instrument_types.values() for measure in sublist]
        flat_types_list = [
            measure for sublist in expected_instrument_types.values() for measure in sublist
        ]
        self.assertEqual(instrument_types.keys(), expected_instrument_types.keys())
        self.assertEqual(flat_list, flat_types_list)

    def test_suggested_response_flags(self):
        """Test suggested_response_flags specs"""
        program = self.program_class
        role = "rater"
        suggested_response_flags = program.suggested_response_flags

        questions = Question.objects.all()
        expected_response_flags = {}
        for question in questions:
            choices_flags = list(
                question.question_choice.values_list(
                    "choice", "document_required", "photo_required", "comment_required"
                )
            )
            if choices_flags:
                for choice_flag in choices_flags:
                    choice = choice_flag[0]
                    is_document_required = choice_flag[1]
                    is_photo_required = choice_flag[2]
                    is_comment_required = choice_flag[3]
                    if is_comment_required or is_photo_required or is_document_required:
                        if question.slug not in expected_response_flags:
                            expected_response_flags[question.slug] = {}
                        question_choice = expected_response_flags[question.slug]
                        if choice not in question_choice:
                            question_choice[choice] = {}
                        if is_document_required:
                            question_choice[choice]["document_required"] = True
                        if is_comment_required:
                            question_choice[choice]["comment_required"] = True
                        if is_photo_required:
                            question_choice[choice]["photo_required"] = True

        self.assertEqual(suggested_response_flags[role].keys(), expected_response_flags.keys())
        for choice_key in suggested_response_flags[role].keys():
            self.assertEqual(
                suggested_response_flags[role][choice_key].keys(),
                expected_response_flags[choice_key].keys(),
            )
            suggested_choice_keys = suggested_response_flags[role][choice_key]
            for key in expected_response_flags[choice_key].keys():
                self.assertEqual(
                    expected_response_flags[choice_key][key].keys(),
                    suggested_choice_keys[key].keys(),
                )
                self.assertEqual(
                    list(expected_response_flags[choice_key][key].values()),
                    list(suggested_choice_keys[key].values()),
                )
