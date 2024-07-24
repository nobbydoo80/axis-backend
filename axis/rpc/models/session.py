"""session.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:29"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import models
from django_fsm import FSMField

from axis.rpc.managers import RPCSessionQuerySet


class RPCSession(models.Model):
    """
    Script information that we are running on RPC VM machine via RPC Service
    """

    IN_PROGRESS_STATE = "in_progress"
    SUCCESS_STATE = "success"
    ERROR_STATE = "error"

    STATE_CHOICES = (
        (IN_PROGRESS_STATE, "In Progress"),
        (SUCCESS_STATE, "Success"),
        (ERROR_STATE, "Error"),
    )

    CUSTOMER_HIRL_UPDATER_SERVICE_TYPE = "customer_hirl_updater"

    SESSION_TYPE_CHOICES = ((CUSTOMER_HIRL_UPDATER_SERVICE_TYPE, "Customer HIRL Updater"),)

    service = models.ForeignKey("RPCService", on_delete=models.CASCADE)

    session_type = models.CharField(choices=SESSION_TYPE_CHOICES, max_length=255)

    state = FSMField(choices=STATE_CHOICES, default=IN_PROGRESS_STATE)

    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RPCSessionQuerySet.as_manager()

    def __str__(self):
        return f"RPC Session({self.get_state_display()}) {self.service}"

    class Meta:
        ordering = ("-created_at",)
