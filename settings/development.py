"""development.py: Django settings"""

from .base import *  # noqa

__author__ = "Steven Klass"
__date__ = "1/24/13 10:58 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

DEBUG = True
FRONTEND = {
    "FRONTEND_DEPLOY_URL": "app/",
    # Use this one for common dev experience:
    "FRONTEND_HOST": "s3.amazonaws.com/assets.pivotalenergy.net/static/axis-frontend/dev/",
    # Use this one for serving files straight from a local ng serve:
    # NOTE: You must also launch Chrome with --disable-web-security to avoid CORS.
    # Run `bin/chrome-cross-origin` to relaunch it for you.
    # 'FRONTEND_HOST': 'localhost:4200/',
}

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove("axis.customer_eto.apps.CustomerETOConfig")
INSTALLED_APPS.append("axis.customer_eto.apps.UserTestingConfig")

CRISPY_FAIL_SILENTLY = not DEBUG
MANAGERS = ADMINS = ()
ALLOWED_HOSTS = INTERNAL_IPS = (
    "127.0.0.1",
    "0.0.0.0",  # nosec
    "localhost",
    "host.docker.internal",
)

SITE_ID = 1

SERVER_TYPE = LOCALHOST_SERVER_TYPE

# If you are not running rabbitMQ - Serialize it..
CELERY_ALWAYS_EAGER = CELERY_TASK_EAGER_PROPAGATES = True

# Should only be needed for testing.
DEFAULT_FROM_EMAIL = "'AXIS (Dev)'<noreply-dev@pivotalenergysolutions.com>"
SERVER_EMAIL = "'AXIS (Dev) Issue'<noreply-dev@pivotalenergysolutions.com>"

DEFAULT_HOST = "localhost"

# Support routing dev email requests through own gmail account.
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

EMAIL_USE_TLS = True

# TEMPLATES[0]['OPTIONS']['string_if_invalid'] = '__TEMPLATE_RENDER_ERROR__'

LOGGING["formatters"]["color"]["()"] = "colorlog.ColoredFormatter"
LOGGING["handlers"]["console"]["formatter"] = "color"
del LOGGING["handlers"]["mail_admins"]
del LOGGING["handlers"]["logfile"]


REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += ("rest_framework.renderers.BrowsableAPIRenderer",)

DOCUSIGN_SANDBOX_MODE = DEBUG

SILENCED_SYSTEM_CHECKS = [
    "captcha.recaptcha_test_key_error",
]

MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT = env(
    "PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT", default="8000"
)

CORS_ORIGIN_WHITELIST = [
    "http://dev.pivotalenergy.net",
    "http://localhost:4200",
    "http://localhost",
    "http://127.0.0.1",
]

# S3 media for a dev environment.  We'll dump any dev uploads to the staging server.
# from boto.s3.connection import OrdinaryCallingFormat
# AWS_STORAGE_BUCKET_NAME = 'assets.pivotalenergy.net'
# AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
# STATIC_S3_PATH = "static/staging"
# DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
# DEFAULT_S3_PATH = "media-staging"
# STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
# MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH  # Path from root of selected storage bucket
# MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
