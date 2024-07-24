"""service.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:06"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.db import models
from django_fsm import FSMField

from axis.rpc.managers import RPCServiceQuerySet


class RPCService(models.Model):
    """
    RPC Service that handling connection
    """

    ON_STATE = "on"
    OFF_STATE = "off"

    STATE_CHOICES = ((ON_STATE, "On"), (OFF_STATE, "Off"))

    vm = models.ForeignKey("RPCVirtualMachine", on_delete=models.CASCADE)

    host = models.CharField(max_length=255)
    port = models.IntegerField()

    state = FSMField(choices=STATE_CHOICES, default=OFF_STATE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RPCServiceQuerySet.as_manager()

    def __str__(self):
        return f"RPC Service({self.get_state_display()}) - ({self.vm})"

    class Meta:
        ordering = ("-created_at",)
