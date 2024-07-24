"""RemRate Models suitable for use by Axis """

import datetime
import logging

from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from ..managers import BuildingManager
from ..strings import BUILDING_INPUT_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Building(models.Model):
    """The building Table"""

    SYNC_STATES = (
        (-1, "Data Inputed"),
        (0, "Data Ready for Task Server"),
        (-2, "Task Server Replication In-Progress"),
        (1, "Available for use"),
        (-3, "User removed"),
    )

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building_info = models.OneToOneField(
        "BuildingInfo", on_delete=models.CASCADE, blank=True, null=True
    )

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    remrate_user = models.ForeignKey(
        "remrate.RemRateUser", blank=True, null=True, on_delete=models.SET_NULL
    )
    user_host = models.CharField(max_length=128, blank=True, null=True)
    created_on = models.DateTimeField(default=datetime.datetime.now, editable=False)
    last_update = models.DateTimeField(auto_now=True)
    sync_status = models.IntegerField(default=-1, choices=SYNC_STATES)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_building_number = models.IntegerField(db_column="lBldgNo")
    filename = models.CharField(max_length=765, db_column="sBUBldgNam")
    rating_number = models.CharField(max_length=93, db_column="sBURateNo", blank=True)
    building_input_type = models.IntegerField(
        null=True, choices=BUILDING_INPUT_TYPES, db_column="nBUBlgType"
    )
    ceiling_attic_ro = models.FloatField(null=True, db_column="fCeilAtRo")
    ceiling_attic_area = models.FloatField(null=True, db_column="fCeilAtAr")
    ceiling_cathedral_ro = models.FloatField(null=True, db_column="fCeilCaRo")
    ceiling_cathedral_area = models.FloatField(null=True, db_column="fCeilCaAr")
    above_ground_wall_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fAGWCORo")
    above_ground_wall_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="fAGWCOAr"
    )
    above_ground_wall_buffer_to_outdoor_ro = models.FloatField(null=True, db_column="fAGWBORo")
    above_ground_wall_buffer_to_outdoor_area = models.FloatField(null=True, db_column="fAGWBOAr")
    joist_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fJoiCORo")
    joist_conditioned_to_outdoor_area = models.FloatField(null=True, db_column="fJoiCOAr")
    joist_buffer_to_outdoor_ro = models.FloatField(null=True, db_column="fJoiBORo")
    joist_buffer_to_outdoor_area = models.FloatField(null=True, db_column="fJoiBOAr")
    foundation_walls_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fFndCORo")
    foundation_walls_conditioned_to_outdoor_area = models.FloatField(
        null=True, db_column="fFndCOAr"
    )
    foundation_walls_buffer_to_outdoor_ro = models.FloatField(null=True, db_column="fFndBORo")
    foundation_walls_buffer_to_outdoor_area = models.FloatField(null=True, db_column="fFndBOAr")
    frame_floor_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fFrFCARo")
    frame_floor_conditioned_to_outdoor_area = models.FloatField(null=True, db_column="fFrFCAAr")
    window_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fWinCORo")
    window_conditioned_to_outdoor_area = models.FloatField(null=True, db_column="fWinCOAr")
    skylight_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fSkyCORo")
    skylight_conditioned_to_outdoor_area = models.FloatField(null=True, db_column="fSkyCOAr")
    door_conditioned_to_outdoor_ro = models.FloatField(null=True, db_column="fDorCORo")
    door_conditioned_to_outdoor_area = models.FloatField(null=True, db_column="fDorCOAr")
    added_mass_drywall_thickness = models.FloatField(null=True, db_column="fAMThDry")
    window_wall_ratio = models.FloatField(null=True, db_column="fWinWall", blank=True)
    window_floor_ratio = models.FloatField(null=True, db_column="fWinFloor", blank=True)

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

    note = models.TextField(db_column="sNotes", blank=True)

    objects = BuildingManager()

    class Meta:
        verbose_name = "REM/Rate Building"

    def __str__(self):
        return self.filename

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Ensure that we have an accurate created on date."""
        if not self.id and not self.created_on:
            self.created_on = now()
        return super(Building, self).save(force_insert, force_update, using, update_fields)

    def get_window_wall_ratio(self):
        """Get the window to wall ratio"""
        denominator = self.above_ground_wall_conditioned_to_outdoor_area
        denominator += self.joist_conditioned_to_outdoor_area
        denominator += self.foundation_walls_conditioned_to_outdoor_area
        denominator += self.door_conditioned_to_outdoor_area
        return self.window_conditioned_to_outdoor_area / denominator

    def get_absolute_url(self):
        """Return the url for this model"""
        return reverse("floorplan:input:remrate", kwargs={"pk": self.simulation.pk})
