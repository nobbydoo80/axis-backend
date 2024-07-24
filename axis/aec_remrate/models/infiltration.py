"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import INFILTRATION_UNITS, INFILTRATION_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Infiltration(models.Model):
    """Infiltration"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    infiltration_number = models.IntegerField(null=True, db_column="LININFILNO", blank=True)
    heating_value = models.FloatField(null=True, db_column="FINHEATVAL", blank=True)
    cooling_value = models.FloatField(null=True, db_column="FINCOOLVAL", blank=True)
    units = models.FloatField(
        null=True, db_column="NINWHINFUN", choices=INFILTRATION_UNITS, blank=True
    )
    mechanical_vent_type = models.IntegerField(
        null=True, db_column="LINMVTYPE", choices=INFILTRATION_TYPES, blank=True
    )
    mechanical_vent_cfm = models.FloatField(null=True, db_column="FINMVRATE", blank=True)
    mechanical_vent_power = models.FloatField(null=True, db_column="FINMVFAN", blank=True)
    hours_per_day = models.FloatField(null=True, db_column="NINHRSDAY", blank=True)
    # -- Not Used --
    nintype = models.FloatField(null=True, db_column="NINTYPE", blank=True)
    finsreff = models.FloatField(null=True, db_column="FINSREFF", blank=True)
    sinrateno = models.CharField(max_length=93, db_column="SINRATENO", blank=True)
    fintreff = models.FloatField(null=True, db_column="FINTREFF", blank=True)
    ninverify = models.FloatField(null=True, db_column="NINVERIFY", blank=True)
    ninshltrcl = models.IntegerField(null=True, db_column="NINSHLTRCL", blank=True)
    ninclgvent = models.IntegerField(null=True, db_column="NINCLGVENT", blank=True)
    ecm_fan_motor = models.IntegerField(null=True, db_column="NINFANMOTOR")

    FINANNUAL = models.FloatField(null=True, db_column="FINANNUAL", blank=True)
    FINTESTED = models.FloatField(null=True, db_column="FINTESTED", blank=True)
    NINGDAIRXMF = models.IntegerField(null=True, db_column="NINGDAIRXMF", blank=True)

    NINNOMVMSRD = models.BooleanField(null=True, db_column="NINNOMVMSRD", blank=True)
    NINWATTDFLT = models.BooleanField(null=True, db_column="NINWATTDFLT", blank=True)

    class Meta:
        db_table = "Infilt"
        managed = False
