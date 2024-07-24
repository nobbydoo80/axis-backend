"""base.py: Django """

import os
import sys
from datetime import timedelta

import bleach
from celery.schedules import crontab

from .env import env

__author__ = "Steven Klass"
__date__ = "1/24/13 9:16 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Autumn Valenta"]

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

DEBUG = env("DEBUG")

# constants
PRODUCTION_SERVER_TYPE = "production"
BETA_SERVER_TYPE = "beta"
GAMMA_SERVER_TYPE = "gamma"
DEMO_SERVER_TYPE = "demo"
STAGING_SERVER_TYPE = "staging"
LOCALHOST_SERVER_TYPE = "dev"

SERVER_TYPE = None

ADMINS = (("Steven Klass", "sklass+axis_admin@pivotalenergysolutions.com"),)

MANAGERS = (
    ("Robert Burns", "rburns+axis_mgr@pivotalenergysolutions.com"),
    ("Steven Klass", "sklass+axis_mgr@pivotalenergysolutions.com"),
)

ALLOWED_HOSTS = []
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "axis",
        "USER": env("DB_USER", default=None)
        or env("MARIADB_USER", default=None)
        or env("MYSQL_USER", default=None),
        "PASSWORD": env("DB_PASSWORD", default=None)
        or env("MARIADB_PASSWORD", default=None)
        or env("MYSQL_PASSWORD", default=None),
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED",
        },
        "TEST": {
            "MIGRATE": False,
            "CHARSET": "utf8mb4",
            "COLLATION": "utf8mb4_unicode_520_ci",
        },
    },
    "remrate_ext": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "remrate",
        "USER": env("DB_USER", default=None)
        or env("MARIADB_USER", default=None)
        or env("MYSQL_USER", default=None),
        "PASSWORD": env("DB_PASSWORD", default=None)
        or env("MARIADB_PASSWORD", default=None)
        or env("MYSQL_PASSWORD", default=None),
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED",
        },
        "TEST": {
            "MIGRATE": False,
            "CHARSET": "utf8mb4",
            "COLLATION": "utf8mb4_unicode_520_ci",
        },
    },
    "customer_neea": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "neea_legacy",
        "USER": env("DB_USER", default=None)
        or env("MARIADB_USER", default=None)
        or env("MYSQL_USER", default=None),
        "PASSWORD": env("DB_PASSWORD", default=None)
        or env("MARIADB_PASSWORD", default=None)
        or env("MYSQL_PASSWORD", default=None),
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED",
        },
        "TEST": {
            "MIGRATE": False,
            "CHARSET": "utf8mb4",
            "COLLATION": "utf8mb4_unicode_520_ci",
        },
    },
}

DATABASE_ROUTERS = [
    "axis.aec_remrate.routers.RemrateRouter",
    "axis.customer_neea.routers.NEEARouter",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_FORMAT = "m/d/Y"
SHORT_DATE_FORMAT = DATE_FORMAT
SHORT_DATETIME_FORMAT = "m/d/Y H:i"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# NOTE:  This MUST be writeable by Apache!!
MEDIA_ROOT = os.path.abspath(SITE_ROOT + "/media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in axis' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(SITE_ROOT + "/static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(SITE_ROOT, "webpack/dist"),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env("SECRET_KEY")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(os.path.abspath("axis/aws"), "static"),
            os.path.join(os.path.abspath("axis/impersonate"), "templates"),
        ],
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                # Vanilla Django
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # Axis
                "axis.core.context_processors.menu",
                "axis.core.context_processors.current_build_number",
                "axis.core.context_processors.server_configuration",
                "axis.core.context_processors.map_api_keys",
                "axis.messaging.context_processors.websocket",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    }
]

TEST_RUNNER = "django.test.runner.DiscoverRunner"

MIDDLEWARE = (
    "corsheaders.middleware.CorsMiddleware",
    "axis.core.middleware.ExceptionUserInfoMiddleware",
    "axis.core.middleware.AxisSessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "axis.core.middleware.DynamicSiteDomainMiddleware",
    "axis.core.middleware.AxisAuthenticationMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "axis.core.middleware.AxisAuthenticationCookieMiddleware",
    "axis.core.middleware.UserPermissionsMiddleware",
    "axis.company.middleware.CompanyMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
)

ROOT_URLCONF = "urls"

# CACHES = {
#     'default': {
#         "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
#         'KEY_PREFIX': 'test',
#     }
# }


SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
MESSAGE_STORAGE = "axis.messaging.storage.MessagingStorage"
MESSAGE_LEVEL = 10  # debug

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "storages",
    "s3_folder_storage",
    "collectfast",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    "simple_history",
    "django_fsm",
    "django_states",
    "app_metrics",
    "django_select2",
    "crispy_forms",
    "localflavor",
    "bootstrap_templatetags",
    "django_input_collection.apps.InputConfig",
    "tensor_registration",
    "captcha",
    "analytics",
    "simulation",
    "waffle",
    # Could be third-party one day
    "axis.examine.apps.ExamineConfig",
    "axis.proto.apps.ProtoConfig",
    "axis.core.apps.CoreConfig",
    "axis.frontend.apps.FrontendConfig",
    "axis.aec_remrate.apps.AECREMRateConfig",  # Raw AecRemrateRemRate Data
    "axis.annotation.apps.AnnotationConfig",
    "axis.builder_agreement",
    "axis.certification.apps.CertificationConfig",
    "axis.checklist.apps.ChecklistConfig",
    "axis.community.apps.CommunityConfig",
    "axis.company.apps.CompanyConfig",
    "axis.customer_appraisal_institute.apps.CustomerAppraisalInstituteConfig",
    "axis.customer_aps.apps.CustomerAPSConfig",
    "axis.customer_earth_advantage.apps.CustomerEarthAdvantageConfig",
    "axis.customer_eto.apps.CustomerETOConfig",
    "axis.customer_hirl.apps.CustomerHIRLConfig",
    "axis.customer_neea.apps.CustomerNEEAConfig",
    "axis.customer_wsu.apps.CustomerWSUConfig",
    "axis.eep_program.apps.EEPProgramConfig",
    "axis.ekotrope.apps.EkotropeConfig",
    "axis.equipment.apps.EquipmentConfig",
    "axis.filehandling.apps.FilehandlingConfig",
    "axis.floorplan.apps.FloorplanConfig",
    "axis.geographic.apps.GeographicConfig",
    "axis.hes.apps.HESConfig",
    "axis.home.apps.HomeConfig",
    "axis.incentive_payment.apps.IncentivePaymentConfig",
    "axis.invoicing",
    "axis.qa.apps.QAConfig",
    "axis.relationship.apps.RelationshipConfig",
    "axis.remrate.apps.REMRateConfig",
    "axis.remrate_data.apps.REMRateDataConfig",
    "axis.report.apps.ReportConfig",
    "axis.resnet.apps.RESNETConfig",
    "axis.reso.apps.RESOConfig",
    "axis.sampleset.apps.SampleSetConfig",
    "axis.scheduling.apps.SchedulingConfig",
    "axis.subdivision.apps.SubdivisionConfig",
    "axis.search.apps.SearchConfig",
    "axis.geocoder.apps.GeocoderConfig",
    "axis.user_management.apps.UserManagementConfig",
    "axis.messaging.apps.MessagingConfig",
    "axis.rpc.apps.RPYCConfig",
    "axis.gbr.apps.GBRAppConfig",
    # The order here very much matters b/c we want to override some of the templates with our
    # own. So these still get loaded but these are loaded last.
    "django.contrib.admin",
    "django.contrib.flatpages",
    "appsearch",
    "datatableview",
    "impersonate",
    "rest_framework",
    "rest_framework.authtoken",
    "oauth2_provider",
    "django_filters",
    "drf_yasg",
)

CORS_URLS_REGEX = r"^.*$"  # Everything
CORS_ALLOW_CREDENTIALS = True  # Allows cookies to cross the connection
CORS_ORIGIN_WHITELIST = [
    "https://homeinnovation.pivotalenergy.net",
    "https://axis.pivotalenergy.net",
]

REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "axis.core.fields.AxisJSONRenderer",
        "axis.core.renderers.NoHTMLFormBrowsableAPIRenderer",
    ),
    "DEFAULT_METADATA_CLASS": "axis.core.api_v3.options.AxisMetadata",
    "DEFAULT_MODEL_SERIALIZATION_CLASS": "rest_framework.serializers.HyperlinkedModelSerializer",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "checklist": "250/min",
        "ipp": "250/min",
        "anon": "3000/day",
        "user": "3000/min",
    },
    "DEFAULT_PAGINATION_CLASS": "axis.core.pagination.AxisPageNumberPagination",
    "page_size": 20,
    "page_size_query_param": "page_size",
    "max_page_size": 100,
}

# drf-yasg settings
SWAGGER_SETTINGS = {
    "DEFAULT_GENERATOR_CLASS": "axis.core.api_v3.schema.AxisOpenAPISchemaGenerator",
    "DEFAULT_AUTO_SCHEMA_CLASS": "axis.core.api_v3.schema.AxisSchema",
    "LOGIN_URL": "/accounts/login/",
    "LOGOUT_URL": "/accounts/logout/",
    "DOC_EXPANSION": "none",
    "DEEP_LINKING": True,
    "SECURITY_DEFINITIONS": {
        "Bearer": {  # enable JWT Bearer token authentication
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
}

_LOG_SUFFIX = "_%s" % os.environ["LOG_SUFFIX"] if os.environ.get("LOG_SUFFIX") else ""

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s %(processName)s "
            "[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "color": {
            "format": "%(log_color)s[%(asctime)s] %(levelname)s %(task_id)s "
            "%(processName)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "log_colors": {
                "DEBUG": "white",
                "INFO": "cyan",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "white,bg_red",
            },
        },
        "json": {
            "()": "infrastructure.utils.JSONFormatter",
        },
        "github_action": {
            "()": "infrastructure.utils.GitHubActionFormatter",
        },
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "task_filter": {"()": "infrastructure.utils.TaskFilter"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": sys.stdout,
            "filters": ["task_filter"],
        },
        "logfile": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "django{}.log".format(_LOG_SUFFIX),
            "formatter": "standard",
            "backupCount": 5,
            "maxBytes": 5242880,  # (5MB)
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
            "filters": ["require_debug_false"],
        },
        "json": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/tmp/django{}.json".format(_LOG_SUFFIX),  # nosec
            "formatter": "json",
            "backupCount": 2,
            "maxBytes": 1024 * 1024 * 100,
            "filters": ["task_filter"],
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.template": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django_celery_beat": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "amqp": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "kombu": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "boto": {"handlers": ["console"], "level": "WARNING"},
        "boto3": {"handlers": ["console"], "level": "WARNING"},
        "botocore": {"handlers": ["console"], "level": "WARNING"},
        "s3transfer": {"handlers": ["console"], "level": "WARNING"},
        "urllib3": {"handlers": ["console"], "level": "WARNING"},
        "PIL": {"handlers": ["console"], "level": "WARNING"},
        "requests": {"handlers": ["console"], "level": "WARNING"},
        "multiprocessing": {"handlers": ["console"], "level": "WARNING"},
        "py.warnings": {"handlers": ["console"], "level": "WARNING"},
        "appsearch": {"handlers": ["console"], "level": "INFO"},
        "django_states": {"handlers": ["console"], "level": "INFO"},
        "analytics": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "simulation": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "axis": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "axis.core.technology.register_signals": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
        "": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}

# Django auth
LOGIN_REDIRECT_URL = "/"
AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 6,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "axis.core.password_validation.HasLowerCaseValidator",
    },
    {
        "NAME": "axis.core.password_validation.HasUpperCaseValidator",
    },
    {
        "NAME": "axis.core.password_validation.HasNumberValidator",
    },
]

INPUT_COLLECTEDINPUT_MODEL = "checklist.CollectedInput"
INPUT_BOUNDSUGGESTEDRESPONSE_MODEL = "checklist.AxisBoundSuggestedResponse"

AUTHENTICATION_BACKENDS = ("tensor_registration.backends.TensorModelBackend",)

ACCOUNT_ACTIVATION_DAYS = 7

SITE_ID = 1

FILE_UPLOAD_PERMISSIONS = 0o644

ZENDESK_URL = "http://support.pivotalenergysolutions.com"
ZENDESK_TOKEN = env("ZENDESK_TOKEN", default=None)
ZENDESK_SUBDOMAIN = "pivotalenergysolutions"
ZENDESK_SHARED_KEY = env("ZENDESK_SHARED_KEY", default="Not Provided").encode("utf-8")
ZENDESK_API_TOKEN = env("ZENDESK_API_TOKEN", default="Not Provided")
ZENDESK_AGENT_EMAIL = env("ZENDESK_DEFAULT_AGENT_EMAIL", default=None)
ZENDESK_AGENT_PASSWORD = env("ZENDESK_DEFAULT_AGENT_PASSWORD", default=None)

GOOGLE_ANALYTICS_CODE = env("GOOGLE_ANALYTICS_CODE", default=None)

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = ""

AWS_PRELOAD_METADATA = True
AWS_S3_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID", default=None)
AWS_S3_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY", default=None)
AWS_DEFAULT_ACL = "private"
if "collectstatic" in sys.argv:
    print("Setting Public Read")
    AWS_DEFAULT_ACL = "public-read"
    AWS_HEADERS = {
        "Cache-Control": "max-age=86400",
    }

AWS_REGION_NAME = "us-west-1"
AWS_ELASTIC_IP = None

GMAPI_MAPS_URL = "https://maps.google.com/maps/api/js?sensor=false"
GMAPI_STATIC_URL = "https://maps.google.com/maps/api/staticmap"

GOOGLE_MAPS_CLIENT_ID = env("GOOGLE_MAPS_CLIENT_ID", default=None)
GOOGLE_MAPS_API_KEY = env("GOOGLE_MAPS_API_KEY", default=None)

# django-recaptcha
# default is a test key provided by Google
RECAPTCHA_PUBLIC_KEY = env(
    "RECAPTCHA_PUBLIC_KEY", default=str("6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI")
)
RECAPTCHA_PRIVATE_KEY = env(
    "RECAPTCHA_PRIVATE_KEY", default=str("6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe")
)

BING_MAPS_API_KEY = env("BING_MAPS_API_KEY", default=None)
GEOCODER_ELAPSED_TIME_TO_RECODE = 60 * 3

# django-phonenumber-field
PHONENUMBER_DEFAULT_REGION = "US"
PHONENUMBER_DEFAULT_FORMAT = "NATIONAL"

EPA_USERNAME = env("EPA_USERNAME", default="None Provided")
EPA_PASSWORD = env("EPA_PASSWORD", default="None Provided")
EPA_BASE_URL = "https://www.energystar.gov/ws/homes/homes.cfc"

# RabbitMQ / Celery Settings
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_USER = env("RABBITMQ_USER", default=None) or env(
    "RABBITMQ_DEFAULT_USER", default="guest"
)
CELERY_BROKER_PASSWORD = env("RABBITMQ_PASSWORD", default=None) or env(
    "RABBITMQ_DEFAULT_PASS", default="guest"
)
CELERY_BROKER_HOST = env("RABBITMQ_HOST", default="172.31.6.98")
CELERY_BROKER_VHOST = env("RABBITMQ_DEFAULT_VHOST", default="axis")
CELERY_BROKER_PORT = "5672"

CELERY_BROKER_URL = "amqp://{0}:{1}@{2}:{3}/{4}".format(
    CELERY_BROKER_USER,
    CELERY_BROKER_PASSWORD,
    CELERY_BROKER_HOST,
    CELERY_BROKER_PORT,
    CELERY_BROKER_VHOST,
)

CELERY_BROKER_POOL_LIMIT = None  # https://github.com/celery/celery/issues/4226

CELERY_SEND_EVENTS = True
CELERY_TASK_TRACK_STARTED = True
CELERY_WORKER_CONCURRENCY = 8
CELERY_WORKER_PREFETCH_MULTIPLIER = 2
CELERY_TASK_TIME_LIMIT = 60 * 60 * 2  # Kill anything longer than 2 hours
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_ENABLE_UTC = True
CELERY_RESULT_EXTENDED = True  # See https://github.com/celery/django-celery-results/issues/334

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_EXPIRES = 60 * 60 * 2
CELERY_BEAT_SYNC_EVERY = 1
CELERY_EVENT_QUEUE_EXPIRES = 60  # Will delete all celeryev after 1 minute of no use

# CELERY_MAX_PREPARING = 1800

CELERY_TASK_ROUTES = {
    "axis.geocoder.tasks.get_responses": {"queue": "priority"},
}

CELERY_BEAT_SCHEDULE = {
    "Expire equipment sponsor status": {
        "task": "axis.equipment.tasks.equipment_status_expire_task",
        "schedule": crontab(hour="12", minute="00", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Expire training status": {
        "task": "axis.user_management.tasks.training_tasks.training_status_expire_task",
        "schedule": crontab(hour="12", minute="00", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Expire accreditation status warning": {
        "task": "axis.user_management.tasks.accreditation_tasks.accreditation_status_expire_notification_warning_task",
        "schedule": crontab(hour="12", minute="00", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Expire accreditation status": {
        "task": "axis.user_management.tasks.accreditation_tasks.accreditation_status_expire_task",
        "schedule": crontab(hour="12", minute="00", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Prune public REM/Rate® data": {
        "task": "axis.aec_remrate.tasks.prune_remrate_data",
        "schedule": crontab(hour="7", minute="0", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Prune failed REM/Rate® data": {
        "task": "axis.remrate_data.tasks.prune_failed_simulation_models",
        "schedule": crontab(hour="8", minute="0", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Finalize missing Simulations": {
        "task": "simulation.tasks.catch_not_replicated_and_finalize",
        "schedule": crontab(hour="8", minute="10", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Audit builder agreements": {
        "task": "axis.builder_agreement.tasks.audit_builder_agreements",
        "schedule": crontab(hour="1", minute="0", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Issue Reminder Notifications": {
        "task": "axis.certification.configs.trc.tasks.issue_reminder_notifications",
        "schedule": crontab(hour="7", minute="10", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Clear expired sessions": {
        "task": "axis.core.tasks.clear_expired_sessions",
        "schedule": crontab(hour="9", minute="15", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Aggregate metrics": {
        "task": "axis.core.tasks.aggregate_metrics",
        "schedule": crontab(hour="9", minute="30", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Cleanup celery tasks": {
        "task": "axis.core.tasks.cleanup_tasks",
        "schedule": 60.0 * 60.0 * 2,
        "options": {"expires": 60.0 * 90.0},
    },
    "Automatch APS metersets": {
        "task": "axis.customer_aps.tasks.update_metersets_task",
        "schedule": crontab(hour="8", minute="10", day_of_week="*"),
        "options": {"expires": 60.0 * 60 * 23.5},
    },
    "Send Monthly BPA Report": {
        "task": "axis.customer_neea.tasks.issue_monthly_bpa_utility_reports_to_bpa_utilities_task",
        "schedule": crontab(hour="10", minute="0", day_of_month="1"),
        "options": {
            "expires": 60 * 60 * 23 * 28,
            "max_retries": 2,
            "time_limit": 60.0 * 60.0 * 10,
        },
    },
    "Update EPA database": {
        "task": "axis.epa_registry.tasks.update_epa_database",
        "schedule": crontab(hour="8", minute="0", day_of_week="*"),
        "options": {
            "expires": 60 * 60 * 23,
            "max_retries": 2,
            "time_limit": 60.0 * 60.0 * 4,
        },
    },
    "Set abandoned homes": {
        "task": "axis.home.tasks.tasks.set_abandoned_homes_task",
        "schedule": crontab(hour="9", minute="20", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Send BPA daily certification email": {
        "task": "axis.home.tasks.tasks.new_bpa_certification_daily_email_task",
        "schedule": crontab(hour="7", minute="05", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Send pending daily certification email": {
        "task": "axis.home.tasks.tasks.pending_certification_daily_email_task",
        "schedule": crontab(hour="7", minute="05", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Send daily certification email": {
        "task": "axis.home.tasks.tasks.new_certification_daily_email_task",
        "schedule": crontab(hour="7", minute="05", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Send daily admin email": {
        "task": "axis.home.tasks.tasks.admin_daily_email_task",
        "schedule": crontab(hour="7", minute="05", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Associate Companies to homes": {
        "task": "axis.home.tasks.tasks.associate_nightly_companies_to_homestatuses",
        "schedule": crontab(hour="7", minute="10", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Audit missing incentive payments": {
        "task": "axis.incentive_payment.tasks.catch_missing_incentive_payments",
        "schedule": 60.0 * 60.0 * 3,
        "options": {
            "expires": 60 * 60 * 23.5,
            "store_errors_even_if_ignored": True,
            "ignore_result": True,
        },
    },
    "Send digest email": {
        "task": "axis.messaging.tasks.send_digest_email",
        "schedule": crontab(hour="4", minute="0", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Send daily QA correction required": {
        "task": "axis.qa.tasks.correction_required_daily_email",
        "schedule": crontab(hour="7", minute="10", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Send daily QA daily fail review": {
        "task": "axis.qa.tasks.qa_review_fail_daily_email",
        "schedule": crontab(hour="7", minute="05", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Assign Reference and Similar Simulations": {
        "task": "axis.remrate_data.tasks.assign_references_and_similar_simulation_models",
        "schedule": 60.0,
        "options": {"expires": 30.0},
    },
    "Update RESNET database": {
        "task": "axis.resnet.tasks.update_resnet_database",
        "schedule": crontab(hour="8", minute="10", day_of_week="*"),
        "options": {
            "expires": 60 * 60 * 23,
            "max_retries": 2,
            "time_limit": 60.0 * 5.0,
        },
    },
    "Update ETO Builder Permit DocuSign Status": {
        "task": "axis.customer_eto.tasks.docusign.poll_building_permits_docusign",
        "schedule": 60.0 * 30,
        "options": {"expires": 60.0 * 29},
    },
    "Update ETO Builder Occupancy DocuSign Status": {
        "task": "axis.customer_eto.tasks.docusign.poll_certificates_of_occupancy_docusign",
        "schedule": 60.0 * 30,
        "options": {"expires": 60.0 * 29},
    },
    "Collect Externally Influenced Analytics": {
        "task": "analytics.tasks.update_external_influencers",
        "schedule": crontab(hour="8", minute="00", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    # Customer HIRL Builder Agreement
    "Docusign Home Innovation Signing Update": {
        "task": "axis.customer_hirl.tasks.builder_agreements.update_signed_status_from_docusign_task",
        "schedule": 60.0 * 5,  # every 5 min
        "options": {"expires": 60.0 * 4},
    },
    "Docusign Home Innovation Counter-Signing Update": {
        "task": "axis.customer_hirl.tasks.builder_agreements.update_countersigned_status_from_docusign_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    "Docusign Home Innovation Extension Request Signing Update": {
        "task": "axis.customer_hirl.tasks.builder_agreements.update_extension_request_signed_status_from_docusign_task",
        "schedule": 60.0 * 5,  # every 5 min
        "options": {"expires": 60.0 * 4},
    },
    "Docusign Home Innovation Extension Request Counter-Signing Update": {
        "task": "axis.customer_hirl.tasks.builder_agreements."
        "update_countersigned_extension_request_agreement_status_from_docusign_task",
        "schedule": 60.0 * 5,  # every 5 min
        "options": {"expires": 60.0 * 4},
    },
    "Home Innovation Builder Agreement expire warning notification": {
        "task": "axis.customer_hirl.tasks.builder_agreements.builder_agreement_expire_notification_warning_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    "Home Innovation Builder Agreement expire": {
        "task": "axis.customer_hirl.tasks.builder_agreements.builder_agreement_expire_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    # Customer HIRL Verifier Agreement
    "Docusign Home Innovation Verifier Signing Update": {
        "task": "axis.customer_hirl.tasks.verifier_agreements.update_verifier_signed_status_from_docusign_task",
        "schedule": 60.0 * 5,  # every 5 min
        "options": {"expires": 60.0 * 4},
    },
    "Docusign Home Innovation Officer Signing Update": {
        "task": "axis.customer_hirl.tasks.verifier_agreements.update_officer_signed_status_from_docusign_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    "Docusign Home Innovation Verifier Counter-Signing Update": {
        "task": "axis.customer_hirl.tasks.verifier_agreements.update_verifier_countersigned_status_from_docusign_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    "Home Innovation Verifier Agreement expire warning notification": {
        "task": "axis.customer_hirl.tasks.verifier_agreements.verifier_agreement_expire_notification_warning_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    "Home Innovation Verifier Agreement expire": {
        "task": "axis.customer_hirl.tasks.verifier_agreements.verifier_agreement_expire_task",
        "schedule": 60.0 * 5,
        "options": {"expires": 60.0 * 4},
    },
    "Update GBR Registry past items": {
        "task": "axis.gbr.tasks.collect_missing_eto_gbr_registry_entries",
        "schedule": crontab(hour="6", minute="05", day_of_week="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    "Clean duplicate history": {
        "task": "axis.core.tasks.clean_all_duplicate_history_task",
        # run every month
        "schedule": crontab(hour="0", minute="0", day_of_week="1", day_of_month="*"),
        "options": {"expires": 60 * 60 * 23.5},
    },
    # Home Innovation Reports
    # "Home Innovation Homes Report": {
    #     "task": "axis.home.tasks.customer_hirl_homes_report.customer_hirl_homes_report_task",
    #     "schedule": crontab(hour="23", minute="59", day_of_week="*"),
    #     "options": {"expires": 60.0 * 4},
    # },
}

FIELD_ENCRYPTION_KEY = env(
    "FIELD_ENCRYPTION_KEY", default="nnnMOp6xF172kZGttkvZYb38ewR0-79O0ii_VzRYhWg="
)

DOCUSIGN_INTEGRATOR_KEY = env("DOCUSIGN_INTEGRATOR_KEY", default=None)
DOCUSIGN_ACCOUNT_ID = env("DOCUSIGN_ACCOUNT_ID", default=None)

DOCUSIGN_SANDBOX_MODE = DEBUG
DOCUSIGN_REDIRECT_URI = "https://axis.pivotalenergy.net"

# Django Hashid Field
# https://github.com/nshafer/django-hashid-field
# Never change this key. This will affect on all hash ID models
HASHID_FIELD_SALT = "zwdk8z0q&s4=t8e1i@c3f(lfe2lmf(ff^4u1$h0*l^y#+jmd^)"
HASHID_FIELD_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ1234567890"


# Home application
# Stats which have been abandoned will automatically fall into this.
HOME_ABANDON_EXPIRE_DAYS = 365

# Determine whether what type of checklist input collection show on home page
HOME_EEP_PROGRAM_LEGACY_CHECKLIST_NAMES = [
    "APS",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

IMPERSONATE_REQUIRE_SUPERUSER = True
# IMPERSONATE_REDIRECT_URL = "/index/"
IMPERSONATE_REDIRECT_FIELD_NAME = "next"

AUTO_RENDER_SELECT2_STATICS = False

CRISPY_TEMPLATE_PACK = "bootstrap3"
BOOTSTRAP_TEMPLATETAGS_STYLE = CRISPY_TEMPLATE_PACK

DATATABLEVIEW_MINIMUM_YEAR = 1900

# tensor_registration
CONTACT_EMAILS = [info[1] for info in MANAGERS]

# Their staging server info
FASTTRACK_API_ENDPOINT = (
    "https://services-stg.energytrust.org/etoimport/service.asmx"  # ?op=FTImportXML"
)
FASTTRACK_API_KEY = "B75A5170-8CCC-447B-AEC2-7C3DC55AC025"
FASTTRACK_API_PROGRAM_CODE = "0040"  # Assigned to use by FastTrack to identify us
FASTTRACK_IMPORT_CODE = "AXISEPSFULL"
ETO_VARIABLE_RATES = True

EKOTROPE_APP_ENDPOINT = "http://app.ekotrope.com/ekotrope/v1"
EKOTROPE_API_ENDPOINT = "http://api.ekotrope.com/api/v1"
EKOTROPE_API_USERNAME = "sklass"
EKOTROPE_API_PASSWORD = "steveTEMP"

RESNET_API_ENDPOINT = "https://brapiv2.resnet.us/post.asmx"
RESENT_API_USERNAME = "pivotal"
RESNET_API_PASSWORD = "energG2016!"
RESNET_API_DEBUG = True

DOE_HES_API_KEY = env("HES_API_KEY", default="HES_API_KEY_UNDEFINED")

NEEA_USE_NEW_CERTIFICATE = True
PROVIDER_HOME_BUILDERS_ASSOCIATION_OF_TRI_CITIES_USE_NEW_CERTIFICATE = True

APS_INCENTIVE_DETAILS = {
    "first_name": "DeeDee",
    "last_name": "Hessler",
    "employee_number": "Z11360",
    "extension": "81-3306",
}

SAMPLING_MAX_SIZE = 7

MESSAGING = {
    "HOST": "{HTTP_HOST}",
}
MESSAGING_SOCKET_AGE_LIMIT = timedelta(days=1)
MESSAGING_DUPLICATE_DEBOUNCE = timedelta(seconds=10)
MESSAGING_RENOTIFICATION_GRACE_PERIOD = timedelta(seconds=5)
MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_HOST = env(
    "MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_HOST", default="localhost"
)
MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT = env(
    "PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT", default="8002"
)

ALLOWED_TAGS = ["p"] + list(bleach.ALLOWED_TAGS)
ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES.update({"a": ["href", "title", "rel", "target"]})

HIRL_HOST = "192.40.230.129"
HIRL_PORT = 1433
HIRL_USERNAME = "userPivotal"
HIRL_PASSWORD = "a8Cf-67!335e31ada8"
HIRL_SERVER = "Johnson"
HIRL_DATABASE = "PivotalEnergySolutions"
HIRL_TABLE = "PivotalEnergySolutionsCertifications"

DATATABLEVIEW_CACHE_BACKEND = "default"
DATATABLEVIEW_DEFAULT_CACHE_TYPE = "pk_list"
DATATABLEVIEW_CACHE_KEY_HASH = True
DATATABLEVIEW_CACHE_KEY_HASH_LENGTH = 10

USER_PERMISSION_CACHE_DURATION = 15 * 60  # seconds
COMPANY_SPONSOR_INFO_CACHE_DURATION = 15 * 60  # seconds

OAUTH2_PROVIDER = {"SCOPES": {"read": "Read scope"}}
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "oauth2_provider.AccessToken"
OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2_provider.Application"
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "oauth2_provider.RefreshToken"
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "oauth2_provider.IDToken"

FRONTEND = {
    "FRONTEND_HOST": "{host}/app/",  # nginx will rewrite this to the s3 url
    "FRONTEND_DEPLOY_URL": "app/",
}

# Customer HIRL app
CUSTOMER_HIRL = {
    # hirl builder agreement
    "ENROLLMENT_ENABLED": True,
    # hirl verifier agreement
    "VERIFIER_AGREEMENT_ENROLLMENT_ENABLED": True,
    # hirl project
    "HIRL_PROJECT_ENABLED": True,
}
