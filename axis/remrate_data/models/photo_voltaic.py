"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import LOOP_TYPES, PV_ORIENTATION

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class PhotoVoltaic(models.Model):
    """PhotoVol - Photo Voltaics"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="sPVName", blank=True)
    type = models.IntegerField(null=True, choices=LOOP_TYPES, db_column="nPVColType")
    area = models.FloatField(null=True, db_column="fPVArea")
    peak_power = models.FloatField(null=True, db_column="fPVPower")
    tilt = models.FloatField(null=True, db_column="fPVTilt")
    orientation = models.IntegerField(null=True, choices=PV_ORIENTATION, db_column="nPVOr")
    inverter_efficiency = models.FloatField(null=True, db_column="fPVInvEff")
    rating_number = models.CharField(max_length=93, db_column="sPVRateNo", blank=True)
    number_bedrooms = models.IntegerField(blank=True, null=True, db_column="nPVNumBeds")

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        name = '"{}", '.format(self.name) if self.name else ""
        return "{}{} producing {} Watts over {:.2f} sq/ft".format(
            name, self.get_orientation_display(), self.peak_power, self.area
        )
