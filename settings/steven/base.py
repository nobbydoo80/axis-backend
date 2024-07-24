"""__init__.py: Django  package container"""

import datetime
import warnings

from infrastructure.utils.logging_utils import system_warning
from ..development import *

__author__ = "Steven Klass"
__date__ = "10/10/18 11:48 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

MANAGERS = ADMINS = (("Steven Klass", "steve@pivotal.energy"),)
CONTACT_EMAILS = ["steve@pivotal.energy"]

ALLOWED_HOSTS = INTERNAL_IPS = (
    "127.0.0.1",
    "localhost",
    "host.docker.internal",
    "homeinnovation.pivotalenergy.local",
    "pivotalenergy.local",
    "testserver",
)

for k, db in DATABASES.items():
    DATABASES[k]["HOST"] = "127.0.0.1"

DATABASES["default"]["HOST"] = "127.0.0.1"

USE_RDS_DB = env("USE_RDS_DB", default=None)
_django_shell = (
    "shell" in " ".join(sys.argv)
    or "pydevconsole.py" in " ".join(sys.argv)
    # or "XXX" in " ".join(sys.argv)
)
if USE_RDS_DB and _django_shell:
    for db in ["default", "remrate_ext", "customer_neea"]:
        DATABASES[db]["HOST"] = "{}.cssjd9qk9ffi.us-west-2.rds.amazonaws.com".format(USE_RDS_DB)
        DATABASES[db]["USER"] = env("RDS_USER")
        DATABASES[db]["PASSWORD"] = env("RDS_PASSWORD")
        if DATABASES[db]["USER"].endswith("_ro"):
            print(f"WARNING:  You are on READ-ONLY {USE_RDS_DB} server")
        else:
            print(f"WARNING:  You are on {USE_RDS_DB} server and CAN EDIT!")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": ["127.0.0.1:11211"],
        "KEY_PREFIX": "dev",
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": ["127.0.0.1:11211"],
    },
}
# SELECT2_CACHE_BACKEND = 'select2'

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True

# If you are not running rabbitMQ - Serialize it..
# WARNING DO NOT SIMPLY COMMENT THIS OUT!!
CELERY_TASK_ALWAYS_EAGER = CELERY_TASK_EAGER_PROPAGATES = False
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

OPEN_STUDIO_PATH = "/Applications/OpenStudio-2.9.0"
ERI_PATH = "/Users/steven/Development/Pivotal/OpenStudio-ERI-0.6.0-beta"
OPEN_STUDIO_DEFAULT_VERSION = ERI_DEFAULT_VERSION = None

HIRL_HOST = "192.168.1.19"
HIRL_DATABASE = "NGBG"

warnings.simplefilter("once")
old_showwarning = warnings.showwarning
warnings.showwarning = system_warning

LOGGING["loggers"]["django.template"] = {"level": "INFO"}
LOGGING["loggers"]["boto3"] = {"level": "INFO"}
LOGGING["loggers"]["botocore"] = {"level": "INFO"}

if "test" in sys.argv:
    from .test import *
elif "compilefixtures" in sys.argv:
    from .compilefixtures import *

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
}
CUSTOMER_ETO = {
    "LEGACY_EPS_REPORT_CUTOFF_DATE": datetime.date(2020, 1, 1),
}

# VERBOSE_INPUT_DEBUGGING = True

# _SERVER_TYPE = 'production'
# from boto.s3.connection import OrdinaryCallingFormat
# AWS_STORAGE_BUCKET_NAME = 'assets.pivotalenergy.net'
# AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
# AWS_ELASTIC_IP = '52.38.23.209'
#
# DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
# DEFAULT_S3_PATH = 'media-{}'.format(_SERVER_TYPE)
#
# STATICFILES_STORAGE = 'axis.core.backends.CachedStaticStorage'
# STATIC_S3_PATH = 'static/{}'.format(_SERVER_TYPE)
#
# MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
# MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
#
# STATIC_ROOT = '/%s/' % STATIC_S3_PATH
# STATIC_URL = '//s3.amazonaws.com/%s/static/%s/' % (AWS_STORAGE_BUCKET_NAME, _SERVER_TYPE)
#
# ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
