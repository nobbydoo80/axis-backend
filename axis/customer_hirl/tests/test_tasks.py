"""tasks.py: """

__author__ = "Artem Hruzd"
__date__ = "06/11/2020 13:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.contrib.auth import get_user_model


User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")
