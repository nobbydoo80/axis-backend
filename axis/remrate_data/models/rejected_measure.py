"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import REJECTION_REASONS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RejectedMeasure(models.Model):
    """RejMeas"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    cost_rate = models.ForeignKey("CostRate", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_rejected_measure_number = models.IntegerField(unique=True, db_column="lRMRMNo")
    _cost_rate_number = models.IntegerField(db_column="lRMCRNo")
    _parent = models.IntegerField(null=True, db_column="lRMParNo")
    is_multiple_measures = models.BooleanField(default=False, db_column="nRMMult")
    component_name = models.CharField(max_length=153, db_column="sRMComp", blank=True)
    existing_measure_name = models.CharField(max_length=153, db_column="sRMExist", blank=True)
    proposed_measure_name = models.CharField(max_length=153, db_column="sRMProp", blank=True)
    treatment_name = models.CharField(max_length=363, db_column="sRMTreat", blank=True)
    treatment_description = models.CharField(max_length=363, db_column="sRMTreatD", blank=True)
    treatment_life = models.FloatField(null=True, db_column="fRMLife", blank=True)
    treatment_cost = models.FloatField(null=True, db_column="fRMCost", blank=True)
    rejection_type = models.IntegerField(
        null=True, db_column="nRMRejReas", choices=REJECTION_REASONS
    )
    rejection_reason = models.CharField(max_length=153, db_column="sRMRejReas", blank=True)
