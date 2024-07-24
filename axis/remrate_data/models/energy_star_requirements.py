"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import ENERGYSTAR_REQ_CHOICES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EnergyStarRequirements(models.Model):
    """ENERGYSTAR Requirements"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")

    has_energystar_heating_cooling_equip = models.BooleanField(default=False, db_column="nESEQUIP")
    has_energystar_windows = models.IntegerField(db_column="nESWINDOW")
    has_energystar_fixtures = models.IntegerField(db_column="nESFIXTURE")
    has_energystar_appliances = models.IntegerField(db_column="nESAPPLI")
    has_energystar_ceiling_fans = models.IntegerField(db_column="nESCEILFAN")
    has_energystar_ventilation_fans = models.IntegerField(db_column="nESVENTFAN")
    air_barrier_overall = models.IntegerField(
        db_column="nABOVERALL", choices=ENERGYSTAR_REQ_CHOICES
    )
    air_barrier_garage_band_joist = models.IntegerField(
        db_column="nABGRBDJST", choices=ENERGYSTAR_REQ_CHOICES
    )
    air_barrier_attic_eve_baffles = models.IntegerField(
        db_column="nABEVBFFLS", choices=ENERGYSTAR_REQ_CHOICES
    )
    air_barrier_slab_edge_insulation = models.IntegerField(
        db_column="nABSLABEDG", choices=ENERGYSTAR_REQ_CHOICES
    )
    air_barrier_all_band_joist = models.IntegerField(
        db_column="nABBANDJST", choices=ENERGYSTAR_REQ_CHOICES
    )
    air_barrier_min_thermal_barrier = models.IntegerField(
        db_column="nABTHMLBRG", choices=ENERGYSTAR_REQ_CHOICES
    )
    wall_behind_shower_tub = models.IntegerField(
        db_column="nWLSHWRTUB", choices=ENERGYSTAR_REQ_CHOICES
    )
    wall_behind_fireplace = models.IntegerField(
        db_column="nWLFIREPLC", choices=ENERGYSTAR_REQ_CHOICES
    )
    wall_behind_insulation_attic_slopes = models.IntegerField(
        db_column="nWLATCSLPE", choices=ENERGYSTAR_REQ_CHOICES
    )
    wall_attic_knee = models.IntegerField(db_column="nWLATCKNEE", choices=ENERGYSTAR_REQ_CHOICES)
    wall_skylight_shaft = models.IntegerField(
        db_column="nWLSKYSHFT", choices=ENERGYSTAR_REQ_CHOICES
    )
    wall_ajoining_porch = models.IntegerField(
        db_column="nWLPORCHRF", choices=ENERGYSTAR_REQ_CHOICES
    )
    wall_staircase = models.IntegerField(db_column="nWLSTRCASE", choices=ENERGYSTAR_REQ_CHOICES)
    wall_double = models.IntegerField(db_column="nWLDOUBLE", choices=ENERGYSTAR_REQ_CHOICES)
    floor_above_garage = models.IntegerField(db_column="nFLRABVGRG", choices=ENERGYSTAR_REQ_CHOICES)
    floor_cantilevered = models.IntegerField(db_column="nFLRCANTIL", choices=ENERGYSTAR_REQ_CHOICES)
    shafts_duct = models.IntegerField(db_column="nSHAFTDUCT", choices=ENERGYSTAR_REQ_CHOICES)
    shafts_piping = models.IntegerField(db_column="nSHAFTPIPE", choices=ENERGYSTAR_REQ_CHOICES)
    shafts_flue = models.IntegerField(db_column="nSHAFTFLUE", choices=ENERGYSTAR_REQ_CHOICES)
    dropped_ceiling = models.IntegerField(db_column="nATCACCPNL", choices=ENERGYSTAR_REQ_CHOICES)
    fire_wall = models.IntegerField(db_column="nATDDSTAIR", choices=ENERGYSTAR_REQ_CHOICES)
    stair_framing = models.IntegerField(db_column="nRFDRPSOFT", choices=ENERGYSTAR_REQ_CHOICES)
    recess_lights = models.IntegerField(db_column="nRFRECSLGT", choices=ENERGYSTAR_REQ_CHOICES)
    house_fan = models.IntegerField(db_column="nRFHOMEFAN", choices=ENERGYSTAR_REQ_CHOICES)
    common_wall = models.IntegerField(db_column="nCWLBTWNUT", choices=ENERGYSTAR_REQ_CHOICES)
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True)
