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


class AcceptedMeasure(models.Model):
    """AccMeas - Unknown"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    cost_rate = models.ForeignKey("CostRate", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")

    _source_measure_number = models.IntegerField(unique=True, db_column="lAMAMNo")
    _cost_rate_number = models.IntegerField(db_column="lAMCRNo")
    _parent = models.IntegerField(null=True, db_column="lAMParNo")
    is_multiple_measures = models.BooleanField(default=False, db_column="nAMMult")
    component_name = models.CharField(max_length=153, db_column="sAMComp")
    existing_measure_name = models.CharField(max_length=153, db_column="sAMExist")
    proposed_measure_name = models.CharField(max_length=153, db_column="sAMProp")
    treatment_name = models.CharField(max_length=363, db_column="sAMTreat")
    treatment_description = models.CharField(max_length=363, db_column="sAMTreatD")
    treatment_life = models.FloatField(null=True, db_column="fAMLife")
    treatment_cost = models.FloatField(null=True, db_column="fAMCost")
    yearly_savings = models.FloatField(null=True, db_column="fAMYrSav")
    savings_to_investment_ratio = models.FloatField(null=True, db_column="fAMSIR")
    net_present_value_of_savings = models.FloatField(null=True, db_column="fAMPVSav")
    simple_payback = models.FloatField(null=True, db_column="fAMSP")
    rating = models.FloatField(null=True, db_column="fAMRating")
    first_year_cash_flow = models.FloatField(null=True, db_column="fAM1YCF")
