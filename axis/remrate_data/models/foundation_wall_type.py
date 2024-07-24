"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    FOUNDATION_WALL_TYPES,
    FOUNDATION_WALL_STUD_TYPES,
    FOUNDATION_TYPE,
    INSULATION_GRADES,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FoundationWallType(models.Model):
    """Foundation Wall Types"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_foundation_wall_number = models.IntegerField(db_column="lFWTWTNo")
    name = models.CharField(max_length=93, db_column="sFWTType")
    wall_type = models.IntegerField(null=True, db_column="nFWTType", choices=FOUNDATION_WALL_TYPES)
    stud_type = models.IntegerField(
        null=True, db_column="nFWTStdTyp", choices=FOUNDATION_WALL_STUD_TYPES
    )
    masonry_thickness = models.FloatField(null=True, db_column="fFWTMasThk")
    exterior_insulation = models.FloatField(null=True, db_column="fFWTExtIns")
    exterior_insulation_top = models.FloatField(null=True, db_column="fFWTExInsT")
    exterior_insulation_bottom = models.FloatField(null=True, db_column="fFWTExInsB")
    exterior_insulation_top_type = models.FloatField(
        null=True, db_column="nFWTEInTTp", choices=FOUNDATION_TYPE
    )
    exterior_insulation_bottom_type = models.FloatField(
        null=True, db_column="nFWTEInBTp", choices=FOUNDATION_TYPE
    )
    rigid_insulation_r_value = models.FloatField(null=True, db_column="fFWTInInCt")
    batt_or_blown_insulation_r_value = models.FloatField(null=True, db_column="fFWTInInFC")
    interior_insulation_top = models.FloatField(null=True, db_column="fFWTInInsT")
    interior_insulation_bottom = models.FloatField(null=True, db_column="fFWTInInsB")
    interior_insulation_top_type = models.FloatField(
        null=True, db_column="nFWTIInTTp", choices=FOUNDATION_TYPE
    )
    interior_insulation_bottom_type = models.FloatField(
        null=True, db_column="nFWTIInBTp", choices=FOUNDATION_TYPE
    )
    note = models.CharField(null=True, max_length=765, db_column="sFWTNote", blank=True)
    insulation_grade = models.IntegerField(
        null=True, db_column="nFWTInsGrd", choices=INSULATION_GRADES
    )

    def __str__(self):
        return '"{}" {} {}'.format(
            self.name, self.get_wall_type_display(), self.get_stud_type_display()
        )
