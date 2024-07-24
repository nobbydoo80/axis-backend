"""__init__.py: Django  package container"""

from ..development import *

__author__ = "Steven Klass"
__date__ = "10/10/18 11:48 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

DEBUG = True

TEMPLATE_DEBUG = False

MANAGERS = ADMINS = (("Steven Klass", "steve@pivotal.energy"),)
CONTACT_EMAILS = [
    "arti3d.artem@gmail.com",
]

for k, db in DATABASES.items():
    DATABASES[k]["HOST"] = "127.0.0.1"

DATABASES["default"]["HOST"] = "127.0.0.1"

USE_RDS_DB = env("USE_RDS_DB", default=None)
if USE_RDS_DB:
    for db in ["default", "remrate_ext", "customer_neea"]:
        if db in DATABASES:
            DATABASES[db]["HOST"] = "{}.cssjd9qk9ffi.us-west-2.rds.amazonaws.com".format(USE_RDS_DB)
            DATABASES[db]["USER"] = env("RDS_USER")
            DATABASES[db]["PASSWORD"] = env("RDS_PASSWORD")
            print(f"WARNING:  You are on {USE_RDS_DB} server")

    SERVER_TYPE = PRODUCTION_SERVER_TYPE


# del DATABASES['remrate_ext']
# del DATABASES['customer_neea']

# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "support@pivotalenergysolutions.com"
# EMAIL_HOST_PASSWORD = get_env_variable('AXIS_GMAIL_PASSWORD')
# EMAIL_USE_TLS = True


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = ""

# If you are not running rabbitMQ - Serialize it..
# WARNING DO NOT SIMPLY COMMENT THIS OUT!!
CELERY_TASK_ALWAYS_EAGER = CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_BEAT_SCHEDULE = {}

LOGGING["loggers"]["django.template"] = {"level": "INFO"}
LOGGING["loggers"]["django.utils.autoreload"] = {"level": "INFO"}

CUSTOMER_HIRL = {
    "ENROLLMENT_ENABLED": True,
    # verifier agreement
    "VERIFIER_AGREEMENT_ENROLLMENT_ENABLED": True,
    # project
    "HIRL_PROJECT_ENABLED": True,
    "VERIFIER_AGREEMENT_COUNTER_SIGNING_USERNAME": "NGBSadmin",
    "BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME": "NGBSadmin",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
}

if "test" in sys.argv:
    from .test import *
elif "compilefixtures" in sys.argv:
    from .compilefixtures import *


MESSAGING = {
    "HOST": "localhost:8080",
}

MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT = "8002"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 9999

DOE_HES_URL = "https://hesapi.labworks.org/st_api/serve"

DOCUSIGN_SANDBOX_MODE = True
