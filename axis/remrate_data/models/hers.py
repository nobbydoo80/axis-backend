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


class HERS(models.Model):
    """HERS Result information"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo", verbose_name="Key to building run")
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True, null=True)

    score = models.FloatField(
        db_column="fHERSScor", blank=True, null=True, verbose_name="Hers Rating"
    )
    total_cost = models.FloatField(
        db_column="fHERSCost",
        blank=True,
        null=True,
        verbose_name="Hers Rating Cost",
    )
    stars = models.FloatField(
        db_column="fHERSStars",
        blank=True,
        null=True,
        verbose_name="Hers Star Rating",
    )
    reference_heating_consumption = models.FloatField(
        db_column="fHERSRHCn",
        blank=True,
        null=True,
        verbose_name="HERS Reference Heating Consumption",
    )
    reference_cooling_consumption = models.FloatField(
        db_column="fHERSRCCn",
        blank=True,
        null=True,
        verbose_name="HERS Reference Cooling Consumption",
    )
    reference_hot_water_consumption = models.FloatField(
        db_column="fHERSRDCN",
        blank=True,
        null=True,
        verbose_name="HERS Reference Hot Water Consumption",
    )
    reference_lights_appliance_consumption = models.FloatField(
        db_column="fHERSRLACn",
        blank=True,
        null=True,
        verbose_name="HERS Reference Lights and Appliance Consumption",
    )
    reference_photo_voltaic_consumption = models.FloatField(
        db_column="fHERSRPVCn",
        blank=True,
        null=True,
        verbose_name="HERS Reference Photo Voltaic Consumption",
    )
    reference_total_consumption = models.FloatField(
        db_column="fHERSRTCn",
        blank=True,
        null=True,
        verbose_name="HERS Reference Total Consumption",
    )
    designed_heating_consumption = models.FloatField(
        db_column="fHERSDHCn",
        blank=True,
        null=True,
        verbose_name="HERS Designed Heating Consumption",
    )
    designed_cooling_consumption = models.FloatField(
        db_column="fHERSDCCn",
        blank=True,
        null=True,
        verbose_name="HERS Designed Cooling Consumption",
    )
    designed_hot_water_consumption = models.FloatField(
        db_column="fHERSDDCN",
        blank=True,
        null=True,
        verbose_name="HERS Designed Hot Water Consumption",
    )
    designed_lights_appliance_consumption = models.FloatField(
        db_column="fHERSDLACn",
        blank=True,
        null=True,
        verbose_name="HERS Designed Lights and Appliance Consumption",
    )
    designed_photo_voltaic_consumption = models.FloatField(
        db_column="fHERSDPVCn",
        blank=True,
        null=True,
        verbose_name="HERS Designed Photo Voltaic Consumption",
    )
    designed_total_consumption = models.FloatField(
        db_column="fHERSDTCn", blank=True, null=True, verbose_name="HERS Designed Total Consumption"
    )
    ny_score = models.FloatField(
        db_column="FNYHERS", blank=True, null=True, verbose_name="NY HERS Score"
    )
    passes_2005_epact_tax_credit = models.BooleanField(
        null=True, default=False, db_column="bTaxCredit", verbose_name="2005 EPAct Tax Credit"
    )
    hers_130_savings = models.FloatField(
        db_column="FHERS130", blank=True, null=True, verbose_name="HERS 130 savings"
    )

    worst_case_orientation = models.IntegerField(
        db_column="NBADORIENT",
        blank=True,
        null=True,
        verbose_name="Worse orientation (0, 90, 180, 270) -1 is indeterminate",
    )
