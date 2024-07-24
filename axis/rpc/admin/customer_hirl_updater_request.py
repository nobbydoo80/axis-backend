# -*- coding: utf-8 -*-
"""customer_hirl_updater_request.py: """

__author__ = "Artem Hruzd"
__date__ = "11/21/2022 16:06"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib import admin
from django.contrib.admin.decorators import register

from axis.rpc.models import HIRLRPCUpdaterRequest


@register(HIRLRPCUpdaterRequest)
class HIRLRPCUpdaterRequestAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "rpc_session")
    search_fields = ("id", "user__first_name", "user__last_name")
    list_display = ("id", "user", "state", "rpc_session", "created_at")

    readonly_fields = ("result",)
