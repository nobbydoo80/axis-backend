"""test.py: Django settings"""

__author__ = "Steven Klass"
__date__ = "1/24/13 11:12 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import datetime
import warnings

import geopy.geocoders.base
from django.utils.deprecation import RemovedInDjango50Warning, RemovedInNextVersionWarning

from axis.geocoder.adapters import CachedDataAdapter
from infrastructure.utils.logging_utils import github_system_warning, system_warning
from .base import *

# SITE_ID = 1 is important to use example.com Site in DynamicSiteDomainMiddleware
SITE_ID = 1

if os.environ.get("DB_TYPE") == "sqlite":
    print("Using Sqlite Backend!")
    for label, db in DATABASES.items():
        DATABASES[label] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "TEST": {"MIGRATE": False},
        }
elif os.environ.get("DB_TYPE") == "mariadb":
    print("Using MySQL Backend!")
    for label, db in DATABASES.items():
        DATABASES[label].update(
            {
                "HOST": "127.0.0.1",
                "PORT": "3306",
                "USER": env("DB_USER") or DATABASES[label]["USER"],
                "PASSWORD": env("DB_PASSWORD") or DATABASES[label]["USER"],
                "OPTIONS": {"sql_mode": "STRICT_TRANS_TABLES"},
            }
        )

DATABASE_ROUTERS = []

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Handle system warning as log messages

warnings.simplefilter("always")
old_showwarning = warnings.showwarning
warnings.filterwarnings("error", category=ResourceWarning, module="axis")
warnings.filterwarnings("error", category=RuntimeWarning, module="axis")
warnings.filterwarnings("error", category=DeprecationWarning, module="axis")
warnings.filterwarnings("error", category=PendingDeprecationWarning, module="axis")
warnings.filterwarnings("error", category=ImportWarning, module="axis")
warnings.filterwarnings("error", category=RemovedInNextVersionWarning, module="axis")
warnings.filterwarnings("error", category=RemovedInDjango50Warning, module="axis")
warnings.filterwarnings("error", category=RuntimeWarning, module="django")


LOGGING["handlers"]["console"]["level"] = os.environ.get("DEBUG_LEVEL", "WARNING")

if os.environ.get("CI"):  # Always set true for Github Actions
    LOGGING["handlers"]["console"]["formatter"] = "github_action"
    warnings.showwarning = github_system_warning
else:
    warnings.showwarning = system_warning

for logger in LOGGING["loggers"]:
    if logger == "py.warnings":
        LOGGING["loggers"][logger]["level"] = "WARNING"
    else:
        LOGGING["loggers"][logger]["level"] = "CRITICAL"
    LOGGING["loggers"][logger]["handlers"] = ["console"]
if "logfile" in LOGGING["handlers"]:
    LOGGING["handlers"]["logfile"]["filename"] = "/tmp/django.log"

CELERY_TASK_ALWAYS_EAGER = CELERY_TASK_EAGER_PROPAGATES = True
CELERYD_HIJACK_ROOT_LOGGER = True

SITE_ALIASES = {
    "0.0.0.0": 2,
    "testserver": 2,
    "example.com": 2,
}

GEOCODER_ELAPSED_TIME_TO_RECODE = 0.5

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework.authentication.BasicAuthentication",
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.TokenAuthentication",
    "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
]

REST_FRAMEWORK["UNICODE_JSON"] = False  # TODO:  Review Subdivision fails"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "select2_cache",
    },
}

SELECT2_CACHE_BACKEND = "select2"
DOCUSIGN_SANDBOX_MODE = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

USE_FAKE_HPXML = False

CUSTOMER_ETO = {
    "ETO_2021_WA_AVAILABLE_DATE": datetime.date(2021, 5, 1),
    "ETO_2021_NON_WA_AVAILABLE_DATE": datetime.date(2021, 6, 1),
    "LEGACY_EPS_REPORT_CUTOFF_DATE": datetime.date(2020, 1, 1),
}


# Use our cached data!!
geopy.geocoders.base.options.default_adapter_factory = CachedDataAdapter
