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


class WindowType(models.Model):
    """WndwType - Window Types"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_window_type_number = models.IntegerField(db_column="lWDTWinNo")
    name = models.CharField(max_length=93, db_column="sWDTType", blank=True)
    shgc = models.FloatField(null=True, db_column="fWDTSHGC")
    u_value = models.FloatField(null=True, db_column="fWDTUValue")
    note = models.CharField(max_length=765, db_column="sWDTNote", blank=True)

    def __str__(self):
        return '"{}" U={}'.format(self.name, self.u_value)
