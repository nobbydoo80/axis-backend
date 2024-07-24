"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import RoofManager
from ..strings import ROOF_STYLE, TRUE_FALSE, COLORS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Roof(models.Model):
    """Ties a ceiling type to a home."""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("CeilingType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=31, db_column="szROName", null=True)
    area = models.FloatField(db_column="fROArea", null=True)
    style = models.IntegerField(choices=ROOF_STYLE, db_column="nROType")
    radiant_barrier = models.IntegerField(choices=TRUE_FALSE, db_column="nRORadBar")
    color = models.IntegerField(choices=COLORS, db_column="nROCol")
    _ceiling_number = models.IntegerField(db_column="lROCeilTNo")
    u_value = models.FloatField(db_column="fROUo")
    rating_number = models.CharField(max_length=93, db_column="sRORateNo", blank=True)
    clay_or_concrete = models.IntegerField(choices=TRUE_FALSE, db_column="nROClay")
    sub_tile_ventilation = models.IntegerField(choices=TRUE_FALSE, db_column="nROVent")
    sealed_attic_roof_area = models.FloatField(null=True, db_column="fRORoofArea", blank=True)

    objects = RoofManager()

    def __str__(self):
        return "{} (R={})".format(self.type, self.get_r_value())

    class Meta:
        ordering = ("simulation", "-area")

    def get_r_value(self):
        """Get the R-Value"""
        return "%.1f" % (1 / self.u_value)
