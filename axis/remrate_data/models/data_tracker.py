"""RemRate Models suitable for use by Axis """


import datetime
import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DataTracker(models.Model):
    """Tracks the status of a simulation as it moves over the trigger."""

    STATUS = (
        (-1, "Data Have Building"),
        (0, "Data Have Simulation and Building"),
        (1, "Available for use"),
    )

    _result_number = models.IntegerField(db_column="lBldgRunNo", blank=True, null=True)
    _building_number = models.IntegerField(db_column="lBldgNo", blank=True, null=True)

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE, blank=True, null=True)
    building = models.ForeignKey("Building", on_delete=models.CASCADE, blank=True, null=True)

    version = models.CharField(max_length=12)
    db_major_version = models.IntegerField()
    db_minor_version = models.IntegerField()

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    remrate_user = models.ForeignKey(
        "remrate.RemRateUser", blank=True, null=True, on_delete=models.SET_NULL
    )
    user_host = models.CharField(max_length=128, blank=True, null=True)
    created_on = models.DateTimeField(default=datetime.datetime.now, editable=False)
    last_update = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=-2, choices=STATUS)
