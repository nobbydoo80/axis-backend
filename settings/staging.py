"""staging.py: Django settings"""

from .base import *

__author__ = "Steven Klass"
__date__ = "1/24/13 10:45 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

SITE_ID = 4

SERVER_TYPE = STAGING_SERVER_TYPE

ALLOWED_HOSTS = [
    "staging.pivotalenergy.net",
    "staging.neea.pivotalenergy.net",
    "staging.homeinnovation.pivotalenergy.net",
    "staging.pivotalenergysolutions.com",
    "staging.pivotal.energy",
    "staging.greenquery.com",
    "127.0.0.1",
]

if os.environ.get("AWS_PUBLIC_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ.get("AWS_PUBLIC_HOSTNAME"))
if os.environ.get("AWS_INTERNAL_IP"):
    ALLOWED_HOSTS.append(os.environ.get("AWS_INTERNAL_IP"))

CELERY_BROKER_VHOST = SERVER_TYPE
CELERY_BROKER_URL = "amqp://{0}:{1}@{2}:{3}/{4}".format(
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOST,
    CELERY_BROKER_PORT,
    CELERY_BROKER_VHOST,
)

drop_tasks = [
    "Send BPA daily certification email",
    "Send daily certification email",
    "Send pending daily certification email",
    "Send daily admin certification email",
    "Send daily QA correction required",
    "Send daily QA daily fail review",
    "Send Monthly BPA Report",
    "Send digest email",
    "Pull HIRL database",
    "Docusign Home Innovation Signing Update",
    "Docusign Home Innovation Counter-Signing Update",
    "Update ETO Builder Permit DocuSign Status",
    "Update ETO Builder Occupancy DocuSign Status",
    "Update GBR Registry past items",
]

for k, v in CELERY_BEAT_SCHEDULE.items():
    if k in drop_tasks:
        CELERY_BEAT_SCHEDULE[k]["enabled"] = False

AWS_STORAGE_BUCKET_NAME = "assets.pivotalenergy.net"

DEFAULT_FILE_STORAGE = "s3_folder_storage.s3.DefaultStorage"
DEFAULT_S3_PATH = "media-{}".format(SERVER_TYPE)

# s3_folder_storage.s3.StaticStorage
#   -> inherits S3BotoStorage from storages.backends.s3boto3.S3Boto3Storage
STATICFILES_STORAGE = "s3_folder_storage.s3.StaticStorage"

STATIC_S3_PATH = "static/{}".format(SERVER_TYPE)

MEDIA_ROOT = "/%s/" % DEFAULT_S3_PATH
MEDIA_URL = "//s3.amazonaws.com/%s/media/" % AWS_STORAGE_BUCKET_NAME

STATIC_ROOT = "/%s/" % STATIC_S3_PATH
STATIC_URL = "//s3.amazonaws.com/%s/static/%s/" % (AWS_STORAGE_BUCKET_NAME, SERVER_TYPE)

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

DEFAULT_FROM_EMAIL = "'AXIS ({})'<noreply-{}@pivotalenergysolutions.com>".format(
    SERVER_TYPE.capitalize(), SERVER_TYPE
)
SERVER_EMAIL = "'AXIS ({}) Issue'<noreply-{}@pivotalenergysolutions.com>".format(
    SERVER_TYPE.capitalize(), SERVER_TYPE
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": [
            "pivotal.2j7eps.0001.usw2.cache.amazonaws.com:11211",
            "pivotal.2j7eps.0001.usw2.cache.amazonaws.com:11211",
        ],
        "KEY_PREFIX": SERVER_TYPE,
    },
    "collectfast": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": [
            "pivotal.2j7eps.0001.usw2.cache.amazonaws.com:11211",
            "pivotal.2j7eps.0001.usw2.cache.amazonaws.com:11211",
        ],
        "KEY_PREFIX": "statics-fast-{}".format(SERVER_TYPE),
        "TIMEOUT": 3600 * 24,
    },
}

COLLECTFAST_STRATEGY = "collectfast.strategies.boto3.Boto3Strategy"
COLLECTFAST_CACHE = "collectfast"

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

for db in ["default", "remrate_ext", "customer_neea"]:
    DATABASES[db]["HOST"] = "{}.cssjd9qk9ffi.us-west-2.rds.amazonaws.com".format(SERVER_TYPE)

_logfile_log = os.path.basename(LOGGING["handlers"]["logfile"].get("filename"))
log_name = os.path.join(os.sep, "var", "log", "django", _logfile_log)

_json_logfile_log = os.path.basename(LOGGING["handlers"]["json"].get("filename"))
json_log_name = os.path.join(os.sep, "var", "log", "django", _json_logfile_log)

LOGGING["handlers"]["logfile"]["filename"] = log_name
LOGGING["handlers"]["json"]["filename"] = json_log_name

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["handlers"] = ["logfile", "json"]
    if logger in [
        "django.db.backends",
        "django.template",
        "django.request",
        "appsearch",
        "django_states",
        "requests",
        "axis.core.technology.register_signals",
        "boto3",
        "botocore",
        "s3transfer",
        "urllib3",
        "PIL",
    ]:
        continue
    if logger in ["celery", "amqp", "kombu"]:
        LOGGING["loggers"][logger]["level"] = "WARNING"
        continue
    LOGGING["loggers"][logger]["level"] = "INFO"

DOCUSIGN_SANDBOX_MODE = True

# Tensor registration
REGISTRATION_OPEN = False

CORS_ORIGIN_WHITELIST = [
    "https://staging.pivotalenergy.net",
    "http://dev.pivotalenergy.net",
]
