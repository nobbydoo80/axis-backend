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


class EconomicParam(models.Model):
    """Economic Parameters"""

    result_number = models.IntegerField(null=True, db_column="LBldgRunNo", blank=True)
    lbldgno = models.IntegerField(db_column="LBldgNo")
    srateno = models.CharField(max_length=93, db_column="SRateNo", blank=True)
    nfsbaseline = models.IntegerField(null=True, db_column="NFSBaseline")
    sfsbldgname = models.CharField(max_length=255, null=True, db_column="SFSBldgName")
    fepimpcost = models.FloatField(null=True, db_column="fEPImpCost")
    fepimplife = models.FloatField(null=True, db_column="FEPImpLife")
    fepmortrat = models.FloatField(null=True, db_column="FEPMortRat")
    fepmortper = models.FloatField(null=True, db_column="FEPMortPer")
    fepdownpay = models.FloatField(null=True, db_column="FEPDownPay")
    fepappval = models.FloatField(null=True, db_column="FEPAppVal")
    fepinf = models.FloatField(null=True, db_column="FEPInf")
    fepdisrate = models.FloatField(null=True, db_column="FEPDisRate")
    fepeninf = models.FloatField(null=True, db_column="FEPEnInf")
    fepanalper = models.FloatField(null=True, db_column="FEPAnalPer")
    nepimplifed = models.IntegerField(null=True, db_column="NEPImpLifeD")
    nepmortratd = models.IntegerField(null=True, db_column="NEPMortRatD")
    nepmortperd = models.IntegerField(null=True, db_column="NEPMortPerD")
    nepdownpayd = models.IntegerField(null=True, db_column="NEPDownPayD")
    nepinfd = models.IntegerField(null=True, db_column="NEPInfD")
    nepdisrated = models.IntegerField(null=True, db_column="NEPDisRateD")
    nepeninfd = models.IntegerField(null=True, db_column="NEPEnInfD")
    nepanalperd = models.IntegerField(null=True, db_column="NEPAnalPerD")

    NEPDOECalc = models.IntegerField(null=True, db_column="NEPDOECalc")
    NEPCalcMthd = models.IntegerField(null=True, db_column="NEPCalcMthd")

    class Meta:
        db_table = "EconParam"
        managed = False
