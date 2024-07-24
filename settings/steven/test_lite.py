"""test.py: Django """


from .test import *

__author__ = "Steven Klass"
__date__ = "11/05/18 15:48 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"MIGRATE": False},
    },
}

SILENCED_SYSTEM_CHECKS = [
    "captcha.recaptcha_test_key_error",
]
