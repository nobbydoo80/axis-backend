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


class HERS(models.Model):
    """Resulting HERS information"""

    result_number = models.IntegerField(db_column="lBldgRunNo")
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True, null=True)

    score = models.FloatField(db_column="fHERSScor")
    total_cost = models.FloatField(db_column="fHERSCost")
    stars = models.FloatField(db_column="fHERSStars")
    reference_heating_consumption = models.FloatField(db_column="fHERSRHCn")
    reference_cooling_consumption = models.FloatField(db_column="fHERSRCCn")
    reference_hot_water_consumption = models.FloatField(db_column="fHERSRDCN")
    reference_lights_appliance_consumption = models.FloatField(db_column="fHERSRLACn")
    reference_photo_voltaic_consumption = models.FloatField(db_column="fHERSRPVCn")
    reference_total_consumption = models.FloatField(db_column="fHERSRTCn")
    designed_heating_consumption = models.FloatField(db_column="fHERSDHCn")
    designed_cooling_consumption = models.FloatField(db_column="fHERSDCCn")
    designed_hot_water_consumption = models.FloatField(db_column="fHERSDDCN")
    designed_lights_appliance_consumption = models.FloatField(db_column="fHERSDLACn")
    designed_photo_voltaic_consumption = models.FloatField(db_column="fHERSDPVCn")
    designed_total_consumption = models.FloatField(db_column="fHERSDTCn")

    ny_score = models.FloatField(db_column="FNYHERS")
    passes_2005_epact_tax_credit = models.BooleanField(
        null=True, default=False, db_column="bTaxCredit"
    )
    hers_130_savings = models.FloatField(null=True, db_column="FHERS130", blank=True)

    worst_case_orientation = models.IntegerField(db_column="NBADORIENT", blank=True, null=True)

    class Meta:
        db_table = "HERSCode"
        managed = False
