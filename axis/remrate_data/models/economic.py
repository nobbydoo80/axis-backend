"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import IMPROVEMENT_CRITERIA

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Economic(models.Model):
    """Econ - Economic Improvements"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    cost_rate = models.ForeignKey("CostRate", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_economic_number = models.IntegerField(primary_key=True, db_column="lECECNo")
    _cost_rate_number = models.IntegerField(db_column="lECCRNo")
    installed_cost_of_improvements = models.FloatField(null=True, db_column="fECImpCst")
    cost_weighted_life_of_measure = models.FloatField(null=True, db_column="fECWtLife")
    mortgage_term = models.FloatField(null=True, db_column="nECMorTerm")
    mortgage_rate = models.FloatField(null=True, db_column="fECMorRate")
    present_value = models.FloatField(null=True, db_column="fECPVF")
    expected_annual_energy_savings = models.FloatField(null=True, db_column="fECSavTot")
    expected_annual_maintenance_costs = models.FloatField(null=True, db_column="fECMaint")
    expected_annual_savings = models.FloatField(null=True, db_column="fECNetSav")
    increased_annual_mortgage_costs = models.FloatField(null=True, db_column="fECMorCst")
    present_value_of_savings = models.FloatField(null=True, db_column="fECPVSav")
    improvement_raking_criteria = models.IntegerField(
        null=True, db_column="nECRankCr", choices=IMPROVEMENT_CRITERIA
    )
    improvement_ranking_cutoff = models.FloatField(null=True, db_column="fECCutoff")
    maximum_limit = models.FloatField(null=True, db_column="fECMaxLim")
    interacts_with_measures = models.BooleanField(default=False, db_column="nECMeasInt")
