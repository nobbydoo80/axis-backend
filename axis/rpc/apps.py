# -*- coding: utf-8 -*-
"""apps.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:00"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.conf import settings
from axis.core import technology

settings = getattr(settings, "RPC", {})


class RPYCConfig(technology.TechnologyAppConfig):
    name = "axis.rpc"
