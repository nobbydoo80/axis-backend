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


class HeatPath(models.Model):
    """Specifies the heat path"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    composite_type = models.ForeignKey("CompositeType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _composite_type_number = models.FloatField(db_column="lHPTCTTNo")
    name = models.CharField(max_length=93, db_column="sHPPthName", blank=True)
    area = models.FloatField(null=True, db_column="fHPPthArea")
    r_value = models.FloatField(null=True, db_column="fHPPthRVal")
    layer_1_r_value = models.FloatField(null=True, db_column="fHPLRval1", blank=True)
    layer_2_r_value = models.FloatField(null=True, db_column="fHPLRval2", blank=True)
    layer_3_r_value = models.FloatField(null=True, db_column="fHPLRval3", blank=True)
    layer_4_r_value = models.FloatField(null=True, db_column="fHPLRval4", blank=True)
    layer_5_r_value = models.FloatField(null=True, db_column="fHPLRval5", blank=True)
    layer_6_r_value = models.FloatField(null=True, db_column="fHPLRval6", blank=True)
    layer_7_r_value = models.FloatField(null=True, db_column="fHPLRval7", blank=True)
    layer_8_r_value = models.FloatField(null=True, db_column="fHPLRval8", blank=True)

    def __str__(self):
        if self.area:
            return '"{}" ({})'.format(self.name, round(self.area, 3))
        return self.name

    def total_layer_r_value(self) -> float:
        return sum([getattr(self, f"layer_{i}_r_value") for i in range(1, 9)])
