# -*- coding: utf-8 -*-
"""session.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:36"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import models

from axis.core.managers.utils import queryset_user_is_authenticated


class RPCSessionQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self
