"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import HOT_WATER_RECIRCULATION_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HotWaterDistribution(models.Model):
    """DHWDISTRIB - Hot Water Distribution"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_hot_water_distribution_number = models.IntegerField(db_column="lDhwDistNo")
    rating_number = models.CharField(max_length=93, db_column="sRateNo", blank=True)
    fix_low_flow = models.BooleanField(default=False, null=True, db_column="bFixLowFlow")
    hot_water_pipe_insulation = models.BooleanField(
        null=True, default=False, db_column="bDhwPipeIns"
    )
    recirculation_type = models.IntegerField(
        null=True, db_column="nRecircType", choices=HOT_WATER_RECIRCULATION_TYPES
    )

    max_fix_distribution = models.FloatField(null=True, db_column="fMaxFixDist")
    max_supply_return_distribution = models.FloatField(null=True, db_column="fSupRetDist")
    hot_water_pipe_length = models.FloatField(null=True, db_column="fPipeLenDhw")
    hot_water_pipe_recirculation_length = models.FloatField(null=True, db_column="fPipeLenRec")
    hot_water_recirculation_pump_power = models.FloatField(null=True, db_column="fRecPumpPwr")

    has_recirculation_pump = models.BooleanField(null=True, default=False, db_column="bHasDwhr")

    hot_water_recirculation_pump_efficiency = models.FloatField(null=True, db_column="fDwhrEff")

    hot_water_recirculation_pre_heat_cold = models.BooleanField(null=True, db_column="bDwhrPrehtC")
    hot_water_recirculation_pre_heat_hot = models.BooleanField(null=True, db_column="bDwhrPrehtH")

    number_shower_heads = models.IntegerField(null=True, db_column="nShwrheads")
    number_recirculation_shower_heads = models.IntegerField(null=True, db_column="nShwrToDwhr")

    flow_control_efficiency = models.IntegerField(null=True, db_column="fHwCtrlEff")

    number_homes_served = models.IntegerField(null=True, blank=True, db_column="nHomesServed")

    compactness_factor = models.FloatField(null=True, blank=True, db_column="fCompactFactor")
