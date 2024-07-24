"""test.py: Django """

from ..test import *

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
        "TEST": {
            "MIGRATE": False,
        },
    },
}

# DATABASES["default"]["OPTIONS"] = {
#     "init_command": "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; SET sql_mode='ONLY_FULL_GROUP_BY';",
# }

# DATABASES['default']['TEST'] = {
#     'NAME': 'test_axis',
# }

SILENCED_SYSTEM_CHECKS = [
    "captcha.recaptcha_test_key_error",
]

LOGGING["handlers"]["console"]["level"] = os.environ.get("DEBUG_LEVEL", "WARNING")
for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["level"] = "INFO"
    LOGGING["loggers"][logger]["handlers"] = ["console"]
