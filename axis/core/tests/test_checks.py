"""test_checks.py: """

__author__ = "Artem Hruzd"
__date__ = "07/25/2019 18:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.core.checks import Warning, Error
from django.test import TestCase, override_settings
from django.conf import settings

from axis.core.checks import (
    default_field_encryption_key_check,
    production_data_in_database_check,
)
from axis.core.tests.factories import rater_user_factory


class CheckTests(TestCase):
    @override_settings(FIELD_ENCRYPTION_KEY="nnnMOp6xF172kZGttkvZYb38ewR0-79O0ii_VzRYhWg=")
    def test_default_field_encryption_key_check_fail(self):
        errors = default_field_encryption_key_check()
        expected_errors = [
            Warning(
                "FIELD_ENCRYPTION_KEY settings variable is set to a default value",
                hint="Run ./manage.py generate_encryption_key and save the value to your .env",
                id="core.E004",
            )
        ]
        self.assertEqual(errors, expected_errors)

    @override_settings(FIELD_ENCRYPTION_KEY="4Ly8n5hwLxN0tEIxMYM1A5yY5aCIYGeoc5iMj5_HRpE=")
    def test_default_field_encryption_key_check_pass(self):
        errors = default_field_encryption_key_check()
        self.assertEqual(errors, [])

    @override_settings(SERVER_TYPE=settings.LOCALHOST_SERVER_TYPE)
    @override_settings(DEBUG=True)
    def test_production_data_in_database_check_pass(self):
        errors = production_data_in_database_check()
        self.assertEqual(errors, [])

    @override_settings(SERVER_TYPE=settings.LOCALHOST_SERVER_TYPE)
    @override_settings(DEBUG=True)
    def test_production_data_in_database_check_not_pass(self):
        emails = ["Matt@momentumidaho.com"]
        for email in emails:
            rater_user_factory(email=email)
        errors = production_data_in_database_check()
        expected_errors = [
            Error(
                f"Real emails: {emails} exist in development database. "
                f"Sanitize database from production data first.",
                hint=f"Use manage.py set_fake_emails command",
                id="core.E006",
            )
        ]
        self.assertEqual(errors, expected_errors)
