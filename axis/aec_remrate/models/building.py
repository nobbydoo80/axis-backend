"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Building(models.Model):
    """The building Table"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(primary_key=True, db_column="LBLDGNO")
    filename = models.CharField(max_length=765, db_column="SBUBLDGNAM", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SBURATENO", blank=True)
    building_input_type = models.IntegerField(null=True, db_column="NBUBLGTYPE", blank=True)
    ceiling_attic_ro = models.FloatField(null=True, db_column="FCEILATRO", blank=True)
    ceiling_attic_area = models.FloatField(null=True, db_column="FCEILATAR", blank=True)
    ceiling_cathedral_ro = models.FloatField(null=True, db_column="FCEILCARO", blank=True)
    ceiling_cathedral_area = models.FloatField(null=True, db_column="FCEILCAAR", blank=True)
    above_ground_wall_conditioned_to_outdoor_ro = models.FloatField(
        null=True, db_column="FAGWCORO", blank=True
    )
    above_ground_wall_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FAGWCOAR", blank=True
    )
    above_ground_wall_buffer_to_outdoor_ro = models.FloatField(
        null=True, db_column="FAGWBORO", blank=True
    )
    above_ground_wall_buffer_to_outdoor_area = models.FloatField(
        null=True, db_column="FAGWBOAR", blank=True
    )
    joist_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="FJOICORO", blank=True)
    joist_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FJOICOAR", blank=True
    )
    joist_buffer_to_outdoor_ro = models.FloatField(null=True, db_column="FJOIBORO", blank=True)
    joist_buffer_to_outdoor_area = models.FloatField(null=True, db_column="FJOIBOAR", blank=True)
    foundation_walls_conditioned_to_outdoor_ro = models.FloatField(
        null=True, db_column="FFNDCORO", blank=True
    )
    foundation_walls_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FFNDCOAR", blank=True
    )
    foundation_walls_buffer_to_outdoor_ro = models.FloatField(
        null=True, db_column="FFNDBORO", blank=True
    )
    foundation_walls_buffer_to_outdoor_area = models.FloatField(
        null=True, db_column="FFNDBOAR", blank=True
    )
    frame_floor_conditioned_to_outdoor_ro = models.FloatField(
        null=True, db_column="FFRFCARO", blank=True
    )
    frame_floor_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FFRFCAAR", blank=True
    )
    window_conditioned_to_outdoor_ro = models.FloatField(
        null=True, db_column="FWINCORO", blank=True
    )
    window_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FWINCOAR", blank=True
    )
    skylight_conditioned_to_outdoor_ro = models.FloatField(
        null=True, db_column="FSKYCORO", blank=True
    )
    skylight_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FSKYCOAR", blank=True
    )
    door_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="FDORCORO", blank=True)
    door_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="FDORCOAR", blank=True
    )
    added_mass_drywall_thickness = models.FloatField(null=True, db_column="FAMTHDRY", blank=True)
    window_wall_ratio = models.FloatField(null=True, db_column="FWINWALL", blank=True)
    window_floor_ratio = models.FloatField(null=True, db_column="FWINFLOOR", blank=True)
    comments = models.TextField(db_column="sNotes", blank=True)

    dominant_flat_ceiling = models.CharField(
        max_length=255, db_column="SCEILATDOM", blank=True, null=True
    )
    dominant_sealed_attic_ceiling = models.CharField(
        max_length=255, db_column="SCEILSADOM", blank=True, null=True
    )
    dominant_cathedral_ceiling = models.CharField(
        max_length=255, db_column="SCEILCADOM", blank=True, null=True
    )
    dominant_above_grade_wall = models.CharField(
        max_length=255, db_column="SAGWDOM", blank=True, null=True
    )
    dominant_foundation_wall = models.CharField(
        max_length=255, db_column="SFNDWDOM", blank=True, null=True
    )
    dominant_slab = models.CharField(max_length=255, db_column="SSLABDOM", blank=True, null=True)
    dominant_frame_floor = models.CharField(
        max_length=255, db_column="SFRFDOM", blank=True, null=True
    )
    dominant_window = models.CharField(max_length=255, db_column="SWINDOM", blank=True, null=True)
    dominant_duct_leakage = models.CharField(
        max_length=255, db_column="SDUCTDOM", blank=True, null=True
    )
    dominant_heating = models.CharField(max_length=255, db_column="SHTGDOM", blank=True, null=True)
    dominant_cooling = models.CharField(max_length=255, db_column="SCLGDOM", blank=True, null=True)
    dominant_hot_water = models.CharField(
        max_length=255, db_column="SDHWDOM", blank=True, null=True
    )

    class Meta:
        db_table = "Building"
        managed = False

    def __str__(self):
        return self.filename
