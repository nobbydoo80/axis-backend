"""Disambiguation extension (utilties)."""


from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

settings = getattr(settings, "HOME", {})


# pylint: disable=invalid-name
class DisambiguationConfig(technology.ExtensionConfig):
    """Empty config.  This module provides utilities to platform apps."""

    def import_certifications(self):
        print("ATTENTION: Define hook `app_config.import_certifications()` to allow imports.")
