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


class CostRate(models.Model):
    """CostRate - Cost Rate"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)

    _source_cost_rate_number = models.IntegerField(primary_key=True, db_column="lCRCRNo")
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    heating_cost_as_is = models.FloatField(null=True, db_column="fCRHtg")
    heating_costs_with_improvements = models.FloatField(null=True, db_column="fCRHtg2")
    heating_costs_savings = models.FloatField(null=True, db_column="fCRHtgSav")
    cooling_cost_as_is = models.FloatField(null=True, db_column="fCRClg")
    cooling_costs_with_improvements = models.FloatField(null=True, db_column="fCRClg2")
    cooling_costs_savings = models.FloatField(null=True, db_column="fCRClgSav")
    hot_water_cost_as_is = models.FloatField(null=True, db_column="fCRHW")
    hot_water_costs_with_improvements = models.FloatField(null=True, db_column="fCRHW2")
    hot_water_costs_savings = models.FloatField(null=True, db_column="fCRHWSav")
    lights_and_appliance_cost_as_is = models.FloatField(null=True, db_column="fCRLA")
    lights_and_appliance_costs_with_improvements = models.FloatField(null=True, db_column="fCRLA2")
    lights_and_appliance_costs_savings = models.FloatField(null=True, db_column="fCRLASav")
    service_cost_as_is = models.FloatField(null=True, db_column="fCRSC")
    service_costs_with_improvements = models.FloatField(null=True, db_column="fCRSC2")
    service_costs_savings = models.FloatField(null=True, db_column="fCRSCSav")
    total_cost_as_is = models.FloatField(null=True, db_column="fCRTot")
    total_costs_with_improvements = models.FloatField(null=True, db_column="fCRTot2")
    total_costs_savings = models.FloatField(null=True, db_column="fCRTotSav")
    rating_cost_as_is = models.FloatField(null=True, db_column="fCRRating")
    rating_costs_with_improvements = models.FloatField(null=True, db_column="fCRRating2")
    first_year_cash_flow = models.FloatField(null=True, db_column="fCR1YCF")
