"""tests.py - Axis"""
import io
import logging
import os

from django.core import management
from django.test import TestCase

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "1/28/21 08:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

BASE_TRIGGERS = os.path.abspath(os.path.dirname(__file__) + "/sql/triggers.sql")


class AECManagementTestCase(TestCase):
    def test_build_sql_triggers(self):
        output_file = "/tmp/test.sql"
        with open(os.devnull, "w") as stdout:
            management.call_command(
                "build_sql_triggers",
                "--output",
                output_file,
                "--no_update",
                stdout=stdout,
                stderr=stdout,
            )

        self.assertTrue(os.path.isfile(output_file))

        with io.open(BASE_TRIGGERS) as source:
            with io.open(output_file) as compare:
                self.assertEqual(list(source), list(compare))

        os.remove(output_file)
