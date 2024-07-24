"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EconomicParameters(models.Model):
    """Economic Parameters"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    rating_number = models.CharField(max_length=93, db_column="sRateNo", blank=True)
    baseline = models.IntegerField(null=True, db_column="nFSBaseline")
    baseline_file = models.CharField(max_length=255, null=True, db_column="sFSBldgName")
    improvement_cost = models.FloatField(null=True, db_column="fEPImpCost")
    improvement_life = models.FloatField(null=True, db_column="fEPImpLife")
    mortgage_rate = models.FloatField(null=True, db_column="fEPMortRat")
    mortgate_period = models.FloatField(null=True, db_column="fEPMortPer")
    down_payment = models.FloatField(null=True, db_column="fEPDownPay")
    appraisal_value = models.FloatField(null=True, db_column="fEPAppVal")
    inflation = models.FloatField(null=True, db_column="fEPInf")
    discount_rate = models.FloatField(null=True, db_column="fEPDisRate")
    energy_inflation = models.FloatField(null=True, db_column="fEPEnInf")
    analysis_period = models.FloatField(null=True, db_column="fEPAnalPer")
    ImpLifeD = models.BooleanField(null=True, db_column="nEPImpLifeD")
    mortgage_rate_default = models.BooleanField(null=True, db_column="nEPMortRatD")
    mortgage_period_default = models.BooleanField(null=True, db_column="nEPMortPerD")
    down_payment_default = models.BooleanField(null=True, db_column="nEPDownPayD")
    inflation_default = models.BooleanField(null=True, db_column="nEPInfD")
    discount_rate_default = models.BooleanField(null=True, db_column="nEPDisRateD")
    energy_inflation_default = models.BooleanField(null=True, db_column="nEPEnInfD")
    analysis_period_default = models.BooleanField(null=True, db_column="nEPAnalPerD")
    use_doe_methodology = models.BooleanField(null=True, db_column="NEPDOECalc")
    calculation_methodology = models.IntegerField(null=True, db_column="NEPCalcMthd")
