"""celery.py: Django """

import os
import sys

from celery import Celery
from celery.signals import setup_logging


__author__ = "Steven Klass"
__date__ = "8/8/13 7:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

label = "celery_beat" if "beat" in sys.argv else ""
label = "celery_worker" if "worker" in sys.argv else label
os.environ.setdefault("LOG_SUFFIX", label)


@setup_logging.connect
def pivotal_setup_logging(**kwargs):
    import logging.config
    from django.conf import settings

    config = settings.LOGGING.copy()
    config["disable_existing_loggers"] = True
    logging.config.dictConfigClass(config).configure()
    return True


celery_app = Celery("axis")

celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()
