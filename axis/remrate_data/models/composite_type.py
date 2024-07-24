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


class CompositeType(models.Model):
    """Defines a wall or ceiling cavity and it associated data"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_composite_type_number = models.IntegerField(db_column="lTCTTCTTNo")
    name = models.CharField(max_length=93, db_column="sTCTType", blank=True)
    quick_fill = models.BooleanField(db_column="nTCTQFVal", default=False)
    layer_1 = models.CharField(max_length=93, db_column="sTCTLNm1", blank=True)
    layer_2 = models.CharField(max_length=93, db_column="sTCTLNm2", blank=True)
    layer_3 = models.CharField(max_length=93, db_column="sTCTLNm3", blank=True)
    layer_4 = models.CharField(max_length=93, db_column="sTCTLNm4", blank=True)
    layer_5 = models.CharField(max_length=93, db_column="sTCTLNm5", blank=True)
    layer_6 = models.CharField(max_length=93, db_column="sTCTLNm6", blank=True)
    u_value = models.FloatField(null=True, db_column="fTCTUo", blank=True)

    def __str__(self):
        if self.u_value:
            return '"{}" U={}'.format(self.name, round(self.u_value, 3))
        return self.name
