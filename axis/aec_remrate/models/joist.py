"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import JOIST_ABOVE_GRADE_WALL_LOCATIONS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Joist(models.Model):
    """Rim and Joist data"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=93, db_column="SZRJNAME", blank=True)
    area = models.FloatField(null=True, db_column="FRJAREA", blank=True)
    location = models.IntegerField(
        null=True, db_column="NRJLOC", choices=JOIST_ABOVE_GRADE_WALL_LOCATIONS, blank=True
    )
    rigid_insulation = models.FloatField(null=True, db_column="FRJCOINSUL", blank=True)
    batt_insulation = models.FloatField(null=True, db_column="FRJFRINSUL", blank=True)
    joist_spacing = models.FloatField(null=True, db_column="FRJSPACING", blank=True)
    u_value = models.FloatField(null=True, db_column="FRJUO", blank=True)
    insulation_thickness = models.FloatField(null=True, db_column="FRJINSULTH", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SRJRATENO", blank=True)
    insulation_grade = models.IntegerField(null=True, db_column="NRJINSGRDE", blank=True)

    class Meta:
        db_table = "Joist"
        managed = False
