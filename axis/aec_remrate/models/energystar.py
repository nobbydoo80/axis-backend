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


class ENERGYSTAR(models.Model):
    """Results of ENERGYSTAR data"""

    result_number = models.IntegerField(db_column="lBldgRunNo", verbose_name="Key to building run")
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True)
    passes_energy_star_v2 = models.BooleanField(db_column="BESTARV2", default=False)
    passes_energy_star_v2p5 = models.BooleanField(db_column="BESTARV25", default=False)
    energy_star_v2p5_pv_score = models.FloatField(db_column="FV25HERSPV", blank=True, null=True)
    energy_star_v2p5_hers_score = models.FloatField(db_column="FV25HERS", blank=True, null=True)
    energy_star_v2p5_hers_saf_score = models.FloatField(
        db_column="FV25HERSSA", blank=True, null=True
    )
    energy_star_v2p5_hers_saf = models.FloatField(db_column="FV25SZADJF", blank=True, null=True)

    passes_energy_star_v3 = models.BooleanField(db_column="BESTARV3", default=False)
    energy_star_v3_pv_score = models.FloatField(db_column="FV3HERSPV", blank=True, null=True)
    energy_star_v3_hers_score = models.FloatField(db_column="FV3HERS", blank=True, null=True)
    energy_star_v3_hers_saf_score = models.FloatField(db_column="FV3HERSSA", blank=True, null=True)
    energy_star_v3_hers_saf = models.FloatField(db_column="FV3SZADJF", blank=True, null=True)

    passes_energy_star_v3_hi = models.BooleanField(db_column="BESTARV3HI", default=False)
    energy_star_v3_hi_pv_score = models.FloatField(db_column="FV3HIHERSPV", blank=True, null=True)
    energy_star_v3_hi_hers_score = models.FloatField(db_column="FV3HIHERS", blank=True, null=True)
    energy_star_v3_hi_hers_saf_score = models.FloatField(
        db_column="FV3HIHERSSA", blank=True, null=True
    )
    energy_star_v3_hi_hers_saf = models.FloatField(db_column="FV3HISZADJF", blank=True, null=True)

    passes_energy_star_v3p1 = models.BooleanField(db_column="BESTARV31", default=False)
    energy_star_v3p1_pv_score = models.FloatField(db_column="FV31HERSPV", blank=True, null=True)
    energy_star_v3p1_hers_score = models.FloatField(db_column="FV31HERS", blank=True, null=True)
    energy_star_v3p1_hers_saf_score = models.FloatField(
        db_column="FV31HERSSA", blank=True, null=True
    )
    energy_star_v3p1_hers_saf = models.FloatField(db_column="FV31SZADJF", blank=True, null=True)

    passes_energy_star_v3p2 = models.BooleanField(db_column="BESTARV32W", default=False)
    energy_star_v3p2_pv_score = models.FloatField(db_column="FV32WHERSPV", blank=True, null=True)
    energy_star_v3p2_whers_score = models.FloatField(db_column="FV32WHERS", blank=True, null=True)
    energy_star_v3p2_whers_saf_score = models.FloatField(
        db_column="FV32WHERSSA", blank=True, null=True
    )
    energy_star_v3p2_whers_saf = models.FloatField(db_column="FV32WSZADJF", blank=True, null=True)

    passes_doe_zero = models.BooleanField(db_column="BDOEPROGRAM", default=False)
    doe_zero_hers_score = models.FloatField(db_column="FDOEHERS", blank=True, null=True)
    doe_zero_saf_score = models.FloatField(db_column="FDOEHERSSA", blank=True, null=True)

    passes_energy_star_v1p0_mf = models.BooleanField(null=True, db_column="bESTARV10MF", blank=True)
    energy_star_v1p0_mf_pv_score = models.FloatField(db_column="FV10MFHERSPV", blank=True)
    energy_star_v1p0_mf_hers_index = models.FloatField(db_column="FV10MFHERS", blank=True)

    passes_energy_star_v1p1_mf = models.BooleanField(null=True, db_column="BESTARV11MF", blank=True)
    energy_star_v1p1_mf_pv_score = models.FloatField(db_column="FV11MFHERSPV", blank=True)
    energy_star_v1p1_mf_hers_index = models.FloatField(db_column="FV11MFHERS", blank=True)

    passes_energy_star_v1p2_mf = models.BooleanField(null=True, db_column="BESTARV12MF", blank=True)
    energy_star_v1p2_mf_pv_score = models.FloatField(db_column="FV12MFHERSPV", blank=True)
    energy_star_v1p2_mf_hers_index = models.FloatField(db_column="FV12MFHERS", blank=True)

    class Meta:
        db_table = "ENERGYSTAR"
        managed = False
