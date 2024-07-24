"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import WALL_TYPES, INSULATION_GRADES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class WallType(models.Model):
    """Describe the walls"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    composite_type = models.ForeignKey("CompositeType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_wall_type_number = models.IntegerField(db_column="lWTWTNo")
    stud_width = models.FloatField(null=True, db_column="fWTStudWdt")
    stud_depth = models.FloatField(null=True, db_column="fWTStudDpt")
    stud_spacing = models.FloatField(null=True, db_column="fWTStudSpg")
    gypsum_thickness = models.FloatField(null=True, db_column="fWTGypThk")
    continuous_insulation = models.FloatField(null=True, db_column="fWTContIns")
    cavity_insulation = models.FloatField(null=True, db_column="fWTCvtyIns")
    cavity_insulation_thickness = models.FloatField(null=True, db_column="fWTCInsThk")
    block_insulation = models.FloatField(null=True, db_column="fWTBlckIns")
    construction_type = models.FloatField(choices=WALL_TYPES, db_column="nWTCntnTyp", default=0)
    _composite_type_number = models.IntegerField(db_column="lWTCompNo")
    quick_fill = models.BooleanField(db_column="bWTQFValid", default=False)
    framing_factor = models.FloatField(null=True, db_column="fWTFF")
    default_framing_factors = models.BooleanField(default=False, db_column="bWTDFLTFF")
    note = models.CharField(null=True, max_length=255, db_column="sWTNote", blank=True)
    insulation_grade = models.IntegerField(
        null=True, db_column="nWTInsGrde", choices=INSULATION_GRADES
    )

    def __str__(self):
        return "{} {}".format(self.get_construction_type_display(), self.composite_type)
