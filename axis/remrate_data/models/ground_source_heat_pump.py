"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import GSHP_PUMP_TYPES, FUEL_TYPES, PUMP_ENERGY_UNITS, GSHP_DISTRIBUTION_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GroundSourceHeatPump(models.Model):
    """GshpType - Ground Source Heat Pumps"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_ground_source_heat_pump_number = models.IntegerField(db_column="lGSTGSTNo")

    name = models.CharField(max_length=93, db_column="sGSTType", blank=True)
    type = models.IntegerField(db_column="nGSTType", null=True, choices=GSHP_PUMP_TYPES)
    fuel_type = models.IntegerField(db_column="nGSTFuel", choices=FUEL_TYPES, null=True)
    heating_coefficient_of_performance_70f = models.FloatField(null=True, db_column="fGSTHCOP70")
    heating_coefficient_of_performance_50f = models.FloatField(null=True, db_column="fGSTHCOP50")
    cooling_energy_efficiency_ratio_70f = models.FloatField(null=True, db_column="fGSTCEER70")
    cooling_energy_efficiency_ratio_50f = models.FloatField(null=True, db_column="fGSTCEER50")
    heating_capacity_70f = models.FloatField(null=True, db_column="fGSTHCap70")
    heating_capacity_50f = models.FloatField(null=True, db_column="fGSTHCap50")
    cooling_capacity_70f = models.FloatField(null=True, db_column="fGSTCCap70")
    cooling_capacity_50f = models.FloatField(null=True, db_column="fGSTCCap50")
    heating_coefficient_of_performance_32f = models.FloatField(null=True, db_column="fGSTHCOP32")
    heating_capacity_32f = models.FloatField(null=True, db_column="fGSTHCap32")
    cooling_energy_efficiency_ratio_77f = models.FloatField(null=True, db_column="fGSTCEER77")
    cooling_capacity_77f = models.FloatField(null=True, db_column="fGSTCCap77")
    sensible_heat_fraction = models.FloatField(null=True, db_column="fGSTSHF")
    fan_defaults = models.BooleanField(default=False, db_column="nGSTFanDef")
    is_desuperheater = models.BooleanField(default=False, db_column="nGSTDSHtr")
    note = models.CharField(max_length=765, db_column="sGSTNote", blank=True)
    backup_capacity = models.FloatField(null=True, db_column="fGSTBKUPCP", blank=True)
    fan_power = models.FloatField(null=True, db_column="fGSTFanPwr", blank=True)
    pump_energy = models.FloatField(null=True, db_column="fGSTPmpEng", blank=True)
    pump_energy_type = models.IntegerField(
        null=True, db_column="nGSTPmpEnT", choices=PUMP_ENERGY_UNITS
    )
    distribution_type = models.IntegerField(
        null=True, db_column="nGSTDbType", choices=GSHP_DISTRIBUTION_TYPES
    )

    def __str__(self):
        return '{}, "{}" {}/{} kBtuh ({})'.format(
            self.get_type_display(),
            self.name,
            self.heating_capacity_50f,
            self.cooling_capacity_50f,
            self.get_fuel_type_display(),
        )

    class Meta:
        ordering = ("simulation", "-heating_capacity_50f", "-cooling_capacity_50f")
