"""test_encrypted_field.py: Django """


import os

from django.core import management
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

import cryptography.fernet
import logging

from .. import fields


__author__ = "Steven K"
__date__ = "11/29/2019 10:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class TestEncryptedFieldSettings(TestCase):
    def setUp(self):
        self.key1 = cryptography.fernet.Fernet.generate_key()
        self.key2 = cryptography.fernet.Fernet.generate_key()

    def test_settings(self):
        with self.settings(FIELD_ENCRYPTION_KEY=self.key1):
            fields.get_crypter()

    def test_settings_tuple(self):
        with self.settings(
            FIELD_ENCRYPTION_KEY=(
                self.key1,
                self.key2,
            )
        ):
            fields.get_crypter()

    def test_settings_list(self):
        with self.settings(
            FIELD_ENCRYPTION_KEY=[
                self.key1,
                self.key2,
            ]
        ):
            fields.get_crypter()

    def test_settings_empty(self):
        with self.settings(FIELD_ENCRYPTION_KEY=None):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=""):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=[]):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(FIELD_ENCRYPTION_KEY=tuple()):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

    def test_settings_bad(self):
        with self.settings(FIELD_ENCRYPTION_KEY=self.key1[:5]):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(
            FIELD_ENCRYPTION_KEY=(
                self.key1[:5],
                self.key2,
            )
        ):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

        with self.settings(
            FIELD_ENCRYPTION_KEY=[
                self.key1[:5],
                self.key2[:5],
            ]
        ):
            self.assertRaises(ImproperlyConfigured, fields.get_crypter)

    def test_management_function(self):
        """Test the management command"""
        with open(os.devnull, "w") as stdout:
            with self.settings(FIELD_ENCRYPTION_KEY=self.key1):
                management.call_command("generate_encryption_key", stdout=stdout, stderr=stdout)
