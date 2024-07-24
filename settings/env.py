__author__ = "Steven K"
__date__ = "10/29/19 15:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import os

import environ

SITE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
env_file = os.path.join(SITE_ROOT, ".env")

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=str,
    GOOGLE_MAPS_API_KEY=str,
    GOOGLE_MAPS_CLIENT_ID=str,
    ZENDESK_API_TOKEN=str,
    FIELD_ENCRYPTION_KEY=str,
    EPA_USERNAME=str,
    EPA_PASSWORD=str,
    HES_API_KEY=str,
)

environ.Env.read_env(env_file=env_file)
