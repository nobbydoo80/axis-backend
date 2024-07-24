"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    FLOOR_COVERINGS,
    QUICKFILL_TYPES,
    INSULATION_LOCATIONS,
    INSULATION_GRADES,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FloorType(models.Model):
    """Framed Floor Types"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    composite_type = models.ForeignKey("CompositeType", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_floor_type_number = models.IntegerField(db_column="lFTFTNo")
    joist_width = models.FloatField(null=True, db_column="fFTJstWdt")
    joist_height = models.FloatField(null=True, db_column="fFTJstHgt")
    joist_spacing = models.FloatField(null=True, db_column="fFTJstSpg")
    continuous_insulation = models.FloatField(null=True, db_column="fFTContIns")
    cavity_insulation = models.FloatField(null=True, db_column="fFTCvtyIns")
    cavity_insulation_thickness = models.FloatField(null=True, db_column="fFTCInsThk")
    floor_covering = models.IntegerField(null=True, db_column="nFTCovType", choices=FLOOR_COVERINGS)
    _composite_type_number = models.IntegerField(db_column="nFTTCTNo")
    quick_fill = models.BooleanField(db_column="bFTQFValid", default=False)
    quick_fill_type = models.IntegerField(choices=QUICKFILL_TYPES, db_column="NFTQFTYPE")
    floor_width = models.FloatField(null=True, db_column="FFTFLRWID")
    outrigger_width = models.FloatField(null=True, db_column="FFTOUTWID")
    batt_thickness = models.FloatField(null=True, db_column="FFTBATTHK")
    batt_r_value = models.FloatField(null=True, db_column="FFTBATRVL")
    blanket_thickness = models.FloatField(null=True, db_column="FFTBLKTHK")
    blanket_r_value = models.FloatField(null=True, db_column="FFTBLKRVL")
    center_insulation_config = models.IntegerField(
        db_column="NFTCNTINS", choices=INSULATION_LOCATIONS
    )
    outrigger_insulation_config = models.IntegerField(
        db_column="NFTOUTINS", choices=INSULATION_LOCATIONS
    )
    framing_factor = models.FloatField(null=True, db_column="FFTFF")
    default_framing_factors = models.BooleanField(default=False, db_column="BFTDFLTFF")
    note = models.CharField(max_length=765, db_column="SFTNOTE", blank=True)
    insulation_grade = models.IntegerField(
        null=True, db_column="nFTInsGrde", choices=INSULATION_GRADES
    )

    def __str__(self):
        return "{}".format(self.composite_type)
