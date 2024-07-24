"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import CeilingTypeManager
from ..strings import STYLE, INS_TYPES, QUICKFILL_TYPES, INSULATION_GRADES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CeilingType(models.Model):
    """These are the ceiling types which are used by the roof."""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    composite_type = models.ForeignKey("CompositeType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_ceiling_number = models.IntegerField(db_column="lCTCTNo")
    gypsum_thickness = models.FloatField(null=True, db_column="fCTGypThk")
    rafter_width = models.FloatField(null=True, db_column="fCTRftrWdt")
    rafter_height = models.FloatField(null=True, db_column="fCTRftrHgt")
    rafter_spacing = models.FloatField(null=True, db_column="fCTRftrSpc")
    continuous_insulation = models.FloatField(null=True, db_column="fCTContIns")
    cavity_insulation = models.FloatField(null=True, db_column="fCTCvtyIns")
    cavity_insulation_thickness = models.FloatField(null=True, db_column="fCTCInsThk")
    style = models.IntegerField(choices=STYLE, db_column="nCTCeilTyp", default=1)
    _composite_type_number = models.IntegerField(db_column="lCTCompNo")
    quick_fill = models.BooleanField(db_column="bCTQFValid", default=False)
    insulation_type = models.IntegerField(choices=INS_TYPES, db_column="NCTINSTYP", default=1)
    unrestricted_depth = models.FloatField(null=True, db_column="FCTUNRDEP")
    unrestricted_rvalue = models.FloatField(null=True, db_column="FCTUNRRVL")
    ceiling_width = models.FloatField(null=True, db_column="FCTCLGWID")
    ceiling_rise = models.FloatField(null=True, db_column="FCTCLGRSE")
    truss_height = models.FloatField(null=True, db_column="FCTTRSHGT")
    heel_height = models.FloatField(null=True, db_column="FCTHELHGT")
    ventilation_space = models.FloatField(null=True, db_column="FCTVNTSPC")
    quick_fill_type = models.IntegerField(choices=QUICKFILL_TYPES, db_column="NCTQFTYP", default=0)
    framing_factor = models.FloatField(null=True, db_column="FCTFF")
    default_framing_factors = models.BooleanField(default=False, db_column="BCTDFLTFF")
    note = models.CharField(max_length=255, db_column="sCTNote", null=True, blank=True)
    insulation_grade = models.IntegerField(
        null=True, db_column="NCTINSGRDE", choices=INSULATION_GRADES
    )

    objects = CeilingTypeManager()

    def __str__(self):
        return "{}".format(self.composite_type)
