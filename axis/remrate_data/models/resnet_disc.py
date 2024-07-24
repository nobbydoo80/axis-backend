"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import RESNET_CHOICES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ResnetDisc(models.Model):
    """RESNET Questions"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    question_1 = models.BooleanField(null=True, db_column="nRDQ1", blank=True)
    question_2a = models.BooleanField(null=True, db_column="nRDQ2A", blank=True)
    question_2b = models.BooleanField(null=True, db_column="nRDQ2B", blank=True)
    question_2c = models.BooleanField(null=True, db_column="nRDQ2C", blank=True)
    question_2d = models.BooleanField(null=True, db_column="nRDQ2D", blank=True)
    question_2e = models.BooleanField(null=True, db_column="nRDQ2E", blank=True)
    question_2e_other = models.CharField(max_length=765, db_column="SRDQ2EOTHR", blank=True)
    question_3a = models.BooleanField(null=True, db_column="nRDQ3A", blank=True)
    question_3b = models.BooleanField(null=True, db_column="nRDQ3B", blank=True)
    question_3c = models.BooleanField(null=True, db_column="nRDQ3C", blank=True)
    question_4_hvac_installed = models.IntegerField(
        null=True, db_column="NRDQ4HVACI", blank=True, choices=RESNET_CHOICES
    )
    question_4_hvac_business = models.IntegerField(
        null=True, db_column="NRDQ4HVACB", blank=True, choices=RESNET_CHOICES
    )
    question_4_thermal_insulation_installed = models.IntegerField(
        null=True, db_column="NRDQ4THMLI", blank=True, choices=RESNET_CHOICES
    )
    question_4_thermal_insulation_business = models.IntegerField(
        null=True, db_column="NRDQ4THMLB", blank=True, choices=RESNET_CHOICES
    )
    question_4_air_sealing_installed = models.IntegerField(
        null=True, db_column="NRDQ4AIRSI", blank=True, choices=RESNET_CHOICES
    )
    question_4_air_sealing_business = models.IntegerField(
        null=True, db_column="NRDQ4AIRSB", blank=True, choices=RESNET_CHOICES
    )
    question_4_windows_installed = models.IntegerField(
        null=True, db_column="NRDQ4WINI", blank=True, choices=RESNET_CHOICES
    )
    question_4_windows_business = models.IntegerField(
        null=True, db_column="NRDQ4WINB", blank=True, choices=RESNET_CHOICES
    )
    question_4_appliance_installed = models.IntegerField(
        null=True, db_column="NRDQ4APPLI", blank=True, choices=RESNET_CHOICES
    )
    question_4_appliance_business = models.IntegerField(
        null=True, db_column="NRDQ4APPLB", blank=True, choices=RESNET_CHOICES
    )
    question_4_construction_installed = models.IntegerField(
        null=True, db_column="NRDQ4CNSTI", blank=True, choices=RESNET_CHOICES
    )
    question_4_construction_business = models.IntegerField(
        null=True, db_column="NRDQ4CNSTB", blank=True, choices=RESNET_CHOICES
    )
    question_4_other_installed = models.IntegerField(
        null=True, db_column="NRDQ4OTHRI", blank=True, choices=RESNET_CHOICES
    )
    question_4_other_business = models.IntegerField(
        null=True, db_column="NRDQ4OTHRB", blank=True, choices=RESNET_CHOICES
    )
    question_4_other = models.CharField(max_length=765, db_column="SRDQ4OTHR", blank=True)
    question_5_sampling = models.BooleanField(
        null=True, default=False, db_column="NRDQ5", blank=True
    )
    rating_number = models.CharField(max_length=93, db_column="sRateNo", blank=True)
