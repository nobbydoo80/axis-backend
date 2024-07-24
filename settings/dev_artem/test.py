"""test.py: Django """

from ..test import *

__author__ = "Steven Klass"
__date__ = "10/10/18 11:48 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

CELERY_TASK_ALWAYS_EAGER = CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = True

DATABASES.pop("remrate_ext", None)
DATABASES.pop("customer_neea", None)
