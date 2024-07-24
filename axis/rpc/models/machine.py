"""machine.py: """

__author__ = "Artem Hruzd"
__date__ = "11/20/2022 19:17"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.db import models
from django_fsm import FSMField


class RPCVirtualMachine(models.Model):
    """
    Virtual machine configurations
    """

    ON_STATE = "on"
    OFF_STATE = "off"

    STATE_CHOICES = ((ON_STATE, "On"), (OFF_STATE, "Off"))

    name = models.CharField(max_length=255)
    rdp_file = models.FileField(
        null=True, blank=True, help_text=".rdp file to connect via Microsoft Remote Desktop"
    )
    rdp_password = models.TextField(
        blank=True, help_text="Password to connect via Microsoft Remote Desktop"
    )

    state = FSMField(choices=STATE_CHOICES, default=OFF_STATE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Virtual Machine"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Virtual Machine: {self.name} ({self.get_state_display()})"
