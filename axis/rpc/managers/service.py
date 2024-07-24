# -*- coding: utf-8 -*-
"""service.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:36"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import models
from django.db.models import Q


class RPCServiceQuerySet(models.QuerySet):
    def free(self):
        from axis.rpc.models import RPCSession

        return self.exclude(rpcsession__state=RPCSession.IN_PROGRESS_STATE)
