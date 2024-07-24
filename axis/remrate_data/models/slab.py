"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import SlabManager

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..strings import SLAB_LOCATIONS

log = logging.getLogger(__name__)


class Slab(models.Model):
    """Slabs"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("SlabType", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szSFName", blank=True)
    area = models.FloatField(null=True, db_column="fSFArea")
    depth_below_grade = models.FloatField(null=True, db_column="fSFDep")
    full_perimeter = models.FloatField(null=True, db_column="fSFPer")
    exposed_perimeter = models.FloatField(null=True, db_column="fSFExPer")
    on_grade_perimeter = models.FloatField(null=True, db_column="fSFOnPer")
    _slab_type_number = models.IntegerField(db_column="lSFSlabTNo")
    rating_number = models.CharField(max_length=93, db_column="sSFRateNo", blank=True)
    location = models.IntegerField(
        null=True, blank=True, db_column="nSFLoc", choices=SLAB_LOCATIONS
    )
    objects = SlabManager()

    def __str__(self):
        return '"{}", {}'.format(self.name, self.type)

    class Meta:
        ordering = ("simulation", "area")
