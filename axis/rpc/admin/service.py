# -*- coding: utf-8 -*-
"""service.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:35"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import admin
from django.contrib.admin.decorators import register

from axis.rpc.models import RPCService


@register(RPCService)
class RPCServiceAdmin(admin.ModelAdmin):
    search_fields = ("id",)
    list_display = ("id", "state", "host", "port")