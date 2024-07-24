"""dev_docker.py: Django settings"""

import logging
import socket
import warnings

from infrastructure.utils.logging_utils import system_warning

from .development import *

__author__ = "Steven Klass"
__date__ = "3/15/18 2:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

DOCKER_ENABLED = True  # This will correctly setup global_base.html
DEBUG = True

# Messaging won't work if DEBUG=False but everything else should.. see window.STATIC_URL (global_base.html)

CELERY_TASK_ALWAYS_EAGER = False

ALLOWED_HOSTS = INTERNAL_IPS = [
    "127.0.0.1",
    "0.0.0.0",  # nosec
    "localhost",
    "app",
    "dev.pivotalenergy.net",
    "neea.dev.pivotalenergy.net",
    "host.docker.internal",
]
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + "1"]

MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_HOST = "app"
MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT = "8000"

for k, db in DATABASES.items():
    DATABASES[k]["HOST"] = "db"
    DATABASES[k]["USER"] = env("MARIADB_USER")
    DATABASES[k]["PASSWORD"] = env("MARIADB_PASSWORD")

# See https://github.com/antonagestam/collectfast/issues/205
# STATICFILES_STORAGE = "django.core.files.storage.FileSystemStorage"
COLLECTFAST_STRATEGY = "collectfast.strategies.filesystem.FileSystemStrategy"
COLLECTFAST_CACHE = "collectfast"

# Setup for RabbitMQ
CELERY_BROKER_HOST = "rabbitmq"
CELERY_BROKER_PASSWORD = env("RABBITMQ_DEFAULT_PASS")
CELERY_BROKER_URL = "amqp://{0}:{1}@{2}:{3}/{4}".format(
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOST,
    CELERY_BROKER_PORT,
    CELERY_BROKER_VHOST,
)
CELERY_BEAT_SCHEDULE = {}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": [
            "memcached:11211",
            "memcached:11211",
        ],
    },
    "collectfast": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": [
            "memcached:11211",
            "memcached:11211",
        ],
        "KEY_PREFIX": "statics_fast",
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

warnings.simplefilter("always")
old_showwarning = warnings.showwarning
warnings.showwarning = system_warning

LOGGING["handlers"]["console"]["level"] = "DEBUG"

base_path = os.path.abspath(os.curdir)
if os.path.isdir(os.path.join(os.sep, "var", "log", "django")):
    base_path = os.path.join(os.sep, "var", "log", "django")
elif os.path.isdir(os.path.join(os.curdir, "..", "docker")):
    base_path = os.path.abspath(os.path.join(os.curdir, "..", "docker"))

LOGGING["formatters"]["standard"]["datefmt"] = "%Y-%m-%dT%H:%M:%S.00%z"
LOGGING["formatters"]["color"]["datefmt"] = "%Y-%m-%dT%H:%M:%S.00%z"
LOGGING["formatters"]["color"]["log_colors"] = {
    "DEBUG": "white",
    "INFO": "cyan",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "black,bg_red",
}

_base_fmt = "%(levelname)s %(processName)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
LOGGING["formatters"]["standard"]["format"] = "%(asctime)s - " + _base_fmt
LOGGING["formatters"]["color"]["format"] = "%(asctime)s - %(log_color)s" + _base_fmt

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["handlers"] = ["console"]
    if logger in [
        "django.db.backends",
        "django.template",
        "appsearch",
        "django_states",
        "requests",
        "axis.core.technology.register_signals",
    ]:
        continue
    if logger in ["celery", "amqp", "kombu"]:
        LOGGING["loggers"][logger]["level"] = "INFO"
        continue
    LOGGING["loggers"][logger]["level"] = "DEBUG"
