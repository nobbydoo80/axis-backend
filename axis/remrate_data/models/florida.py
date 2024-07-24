"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Florida(models.Model):
    """Florida - Unknown"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    type = models.IntegerField(db_column="nType", blank=True)
    worst_case = models.IntegerField(db_column="nWorstCase", blank=True)
    permit_off = models.CharField(max_length=51, db_column="sPermitOff", blank=True)
    permit_number = models.CharField(max_length=51, db_column="sPermitNo", blank=True)
    juristdiction = models.CharField(max_length=51, db_column="sJurisdctn", blank=True)
    rating_number = models.CharField(max_length=31, db_column="sRateNo", blank=True)
