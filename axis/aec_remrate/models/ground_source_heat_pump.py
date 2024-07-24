"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import GS_PUMP_TYPES, FUEL_TYPES

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GroundSourceHeatPump(models.Model):
    """Ground Source Heat Pumps"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    ground_source_heat_pump_number = models.FloatField(null=True, db_column="LGSTGSTNO", blank=True)
    name = models.CharField(max_length=93, db_column="SGSTTYPE", blank=True)
    type = models.IntegerField(db_column="NGSTTYPE", null=True, choices=GS_PUMP_TYPES)
    fuel_type = models.IntegerField(db_column="NGSTFUEL", choices=FUEL_TYPES, null=True)
    heating_rated_output_capacity = models.FloatField(null=True, db_column="FGSTHCAP50", blank=True)
    cooling_rated_output_capacity = models.FloatField(null=True, db_column="FGSTCCAP50", blank=True)

    heating_cop_70 = models.FloatField(null=True, db_column="FGSTHCOP70", blank=True)
    cooling_eer_70 = models.FloatField(null=True, db_column="FGSTCEER70", blank=True)
    heating_cap_70 = models.FloatField(null=True, db_column="FGSTHCAP70", blank=True)
    cooling_cap_70 = models.FloatField(null=True, db_column="FGSTCCAP70", blank=True)

    # -- Not Used ---
    fgsthcop50 = models.FloatField(null=True, db_column="FGSTHCOP50", blank=True)
    fgstceer50 = models.FloatField(null=True, db_column="FGSTCEER50", blank=True)
    fgsthcop32 = models.FloatField(null=True, db_column="FGSTHCOP32", blank=True)
    fgsthcap32 = models.FloatField(null=True, db_column="FGSTHCAP32", blank=True)
    fgstceer77 = models.FloatField(null=True, db_column="FGSTCEER77", blank=True)
    fgstccap77 = models.FloatField(null=True, db_column="FGSTCCAP77", blank=True)
    fgstshf = models.FloatField(null=True, db_column="FGSTSHF", blank=True)
    ngstfandef = models.FloatField(null=True, db_column="NGSTFANDEF", blank=True)
    ngstdshtr = models.FloatField(null=True, db_column="NGSTDSHTR", blank=True)
    sgstnote = models.CharField(max_length=765, db_column="SGSTNOTE", blank=True)
    fgstbkupcp = models.FloatField(null=True, db_column="FGSTBKUPCP", blank=True)
    fgstfanpwr = models.FloatField(null=True, db_column="fGSTFANPWR", blank=True)
    fgstpmpeng = models.FloatField(null=True, db_column="fGSTPmpEng", blank=True)
    ngstpmpent = models.IntegerField(null=True, db_column="nGSTPmpEnT", blank=True)
    ngstdbtype = models.IntegerField(null=True, db_column="nGSTDbType", blank=True)

    class Meta:
        db_table = "GshpType"
        managed = False
