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


class ENERGYSTAR(models.Model):
    """ENERGYSTAR Requirements"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo", verbose_name="Key to building run")
    rating_number = models.CharField(max_length=93, db_column="SRATENO", blank=True, null=True)
    passes_energy_star_v2 = models.BooleanField(
        null=True, db_column="BESTARV2", default=False, verbose_name="Passes ENERGYSTAR v2.0"
    )

    passes_energy_star_v2p5 = models.BooleanField(
        null=True, db_column="BESTARV25", default=False, verbose_name="Passes ENERGYSTAR v2.5"
    )
    energy_star_v2p5_pv_score = models.FloatField(
        db_column="FV25HERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v2.5 photo voltaic adjusted HERS score",
    )
    energy_star_v2p5_hers_score = models.FloatField(
        db_column="FV25HERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v2.5 Reference Design HERS score",
    )
    energy_star_v2p5_hers_saf_score = models.FloatField(
        db_column="FV25HERSSA",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v2.5 size adjustment factor adjusted HERS score",
    )
    energy_star_v2p5_hers_saf = models.FloatField(
        db_column="FV25SZADJF",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v2.5 size adjustment factor",
    )

    passes_energy_star_v3 = models.BooleanField(
        null=True, db_column="BESTARV3", default=False, verbose_name="Passes ENERGYSTAR v3.0"
    )
    energy_star_v3_pv_score = models.FloatField(
        db_column="FV3HERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 photo voltaic adjusted HERS score",
    )
    energy_star_v3_hers_score = models.FloatField(
        db_column="FV3HERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 Reference Design HERS score",
    )
    energy_star_v3_hers_saf_score = models.FloatField(
        db_column="FV3HERSSA",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 size adjustment factor adjusted HERS score",
    )
    energy_star_v3_hers_saf = models.FloatField(
        db_column="FV3SZADJF",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 size adjustment factor",
    )

    passes_energy_star_v3_hi = models.BooleanField(
        null=True,
        db_column="BESTARV3HI",
        default=False,
        verbose_name="Passes ENERGYSTAR v3.0 Hawaii, Guam",
    )
    energy_star_v3_hi_pv_score = models.FloatField(
        db_column="FV3HIHERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 Hawaii, Guam photo voltaic adjusted HERS score",
    )
    energy_star_v3_hi_hers_score = models.FloatField(
        db_column="FV3HIHERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 Hawaii, Guam Reference Design HERS score",
    )
    energy_star_v3_hi_hers_saf_score = models.FloatField(
        db_column="FV3HIHERSSA",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 Hawaii, Guam size adjustment factor adjusted HERS score",
    )
    energy_star_v3_hi_hers_saf = models.FloatField(
        db_column="FV3HISZADJF",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.0 Hawaii, Guam size adjustment factor",
    )

    passes_energy_star_v3p1 = models.BooleanField(
        null=True, db_column="BESTARV31", default=False, verbose_name="Passes ENERGYSTAR v3.1"
    )
    energy_star_v3p1_pv_score = models.FloatField(
        db_column="FV31HERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.1 photo voltaic adjusted HERS score",
    )
    energy_star_v3p1_hers_score = models.FloatField(
        db_column="FV31HERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.1 Reference Design HERS score",
    )
    energy_star_v3p1_hers_saf_score = models.FloatField(
        db_column="FV31HERSSA",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.1 size adjustment factor adjusted HERS score",
    )
    energy_star_v3p1_hers_saf = models.FloatField(
        db_column="FV31SZADJF",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.1 size adjustment factor",
    )

    passes_energy_star_v3p2 = models.BooleanField(
        null=True,
        db_column="BESTARV32W",
        default=False,
        verbose_name="Passes ENERGYSTAR v3.2 Washington",
    )
    energy_star_v3p2_pv_score = models.FloatField(
        db_column="FV32WHERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.2 Washington photo voltaic adjusted HERS score",
    )
    energy_star_v3p2_whers_score = models.FloatField(
        db_column="FV32WHERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.2 Washington Reference Design HERS score",
    )
    energy_star_v3p2_whers_saf_score = models.FloatField(
        db_column="FV32WHERSSA",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.2 Washington size adjustment factor adjusted HERS score",
    )
    energy_star_v3p2_whers_saf = models.FloatField(
        db_column="FV32WSZADJF",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v3.2 Washington size adjustment factor",
    )

    passes_doe_zero = models.BooleanField(
        null=True,
        db_column="BDOEPROGRAM",
        default=False,
        verbose_name="Passes DOE Zero Energy Rated Home",
    )
    doe_zero_hers_score = models.FloatField(
        db_column="FDOEHERS",
        blank=True,
        null=True,
        verbose_name="DOE Zero Energy Rated Home Reference Design HERS score",
    )
    doe_zero_saf_score = models.FloatField(
        db_column="FDOEHERSSA",
        blank=True,
        null=True,
        verbose_name="DOE Zero Energy Rated Home size adjustment factor adjusted HERS score",
    )

    passes_energy_star_v1p0_mf = models.BooleanField(
        null=True,
        db_column="bESTARV10MF",
        blank=True,
        verbose_name="Meets Energy Star v1.0 Multi-Family NC",
    )
    energy_star_v1p0_mf_pv_score = models.FloatField(
        db_column="FV10MFHERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v1.0 Multi-Family NC - HERS PV Adjusted",
    )
    energy_star_v1p0_mf_hers_index = models.FloatField(
        db_column="FV10MFHERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v1.0 Multi-Family NC - HERS Index Target",
    )

    passes_energy_star_v1p1_mf = models.BooleanField(
        null=True,
        db_column="BESTARV11MF",
        blank=True,
        verbose_name="Meets Energy Star v1.1 Multi-Family NC",
    )
    energy_star_v1p1_mf_pv_score = models.FloatField(
        db_column="FV11MFHERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v1.1 Multi-Family NC - HERS PV Adjusted",
    )
    energy_star_v1p1_mf_hers_index = models.FloatField(
        db_column="FV11MFHERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v1.1 Multi-Family NC- HERS Index Target",
    )

    passes_energy_star_v1p2_mf = models.BooleanField(
        null=True,
        db_column="BESTARV12MF",
        blank=True,
        verbose_name="Meets Energy Star v1.2 Multi-Family NC",
    )
    energy_star_v1p2_mf_pv_score = models.FloatField(
        db_column="FV12MFHERSPV",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v1.2 Multi-Family NC - HERS PV Adjusted",
    )
    energy_star_v1p2_mf_hers_index = models.FloatField(
        db_column="FV12MFHERS",
        blank=True,
        null=True,
        verbose_name="ENERGYSTAR v1.2 Multi-Family NC- HERS Index Target",
    )
