"""password_validation.py: Contains additional checks for Django Auth password validation"""


import re

from django.core.exceptions import ValidationError

__author__ = "Artem Hruzd"
__date__ = "07/16/2019 20:53"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class HasLowerCaseValidator:
    def __init__(self):
        self.message = "The password must contain at least one lowercase character."

    def validate(self, password, user=None):
        if re.search(r"[a-z]", password) is None:
            raise ValidationError(self.message, code="missing_lower_case")

    def get_help_text(self):
        return self.message


class HasUpperCaseValidator:
    def __init__(self):
        self.message = "The password must contain at least one uppercase character."

    def validate(self, password, user=None):
        if re.search(r"[A-Z]", password) is None:
            raise ValidationError(self.message, code="missing_upper_case")

    def get_help_text(self):
        return self.message


class HasNumberValidator:
    def __init__(self):
        self.message = "The password must contain at least one numeric character."

    def validate(self, password, user=None):
        if re.search(r"[0-9]", password) is None:
            raise ValidationError(self.message, code="missing_numeric")

    def get_help_text(self):
        return self.message
