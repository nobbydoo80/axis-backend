"""generate_encryption_key.py: Django """


import logging

import cryptography.fernet
from django.core.management.base import BaseCommand

__author__ = "Steven K"
__date__ = "11/29/2019 10:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate a new Fernet encryption key
    Pulled from https://gitlab.com/lansharkconsulting/django/django-encrypted-model-fields/
    """

    help = "Generates a new Fernet encryption key"
    requires_system_checks = []

    def handle(self, *args, **options):
        key = cryptography.fernet.Fernet.generate_key()
        self.stdout.write(key.decode("utf-8"), ending="\n")
