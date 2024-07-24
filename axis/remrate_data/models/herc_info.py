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


class HercInfo(models.Model):
    """HercInfo - Unknown"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    user_set_item_in_herc = models.CharField(max_length=765, db_column="sHIUsrItem")
    criteria_or_recommendation = models.CharField(max_length=765, db_column="sHIITMTYPE")
