from ..development import LOGGING

__author__ = "Steven Klass"
__date__ = "10/10/18 11:48 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

CELERY_TASK_ALWAYS_EAGER = True

LOGGING["loggers"]["axis"] = {"handlers": ["console"], "level": "WARNING"}
LOGGING["loggers"][""] = {"handlers": ["console"], "level": "WARNING", "propagate": True}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
