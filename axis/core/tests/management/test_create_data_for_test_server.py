# -*- coding: utf-8 -*-
"""test_create_data_for_test_server.py: """

__author__ = "Artem Hruzd"
__date__ = "10/25/2022 22:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from io import StringIO

from django.conf import settings
from django.core.management import call_command, CommandError
from django.test import override_settings

from axis.core.tests.testcases import AxisTestCase


class CreateDataForTestServerCommandTests(AxisTestCase):
    @override_settings(SERVER_TYPE=settings.BETA_SERVER_TYPE)
    def test_run_on_beta_bob_customer_hirl_dataset(self):
        """
        We expect that command finished without errors.
        There are no reason to check what was created
        """

        call_command("create_data_for_test_server", "--dataset", "bob_customer_hirl")

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    def test_run_on_production(self):
        out = StringIO()
        with self.assertRaisesRegex(
            CommandError, expected_regex="Command is not available on production"
        ):
            call_command(
                "create_data_for_test_server",
                "--dataset",
                "bob_customer_hirl",
                verbosity=3,
                stdout=out,
                stderr=out,
            )
