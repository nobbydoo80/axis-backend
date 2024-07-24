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


class Mandreq(models.Model):
    """Mandatory Requirements"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    nmriecc04 = models.IntegerField(null=True, db_column="NMRIECC04", blank=True)
    nmriecc06 = models.IntegerField(null=True, db_column="NMRIECC06", blank=True)
    nmriecc09 = models.IntegerField(null=True, db_column="NMRIECC09", blank=True)
    nmresv2tbc = models.IntegerField(null=True, db_column="NMRESV2TBC", blank=True)
    nmresv2prd = models.IntegerField(null=True, db_column="NMRESV2PRD", blank=True)
    nmresv3tec = models.IntegerField(null=True, db_column="NMRESV3TEC", blank=True)
    nmresv3hc = models.IntegerField(null=True, db_column="NMRESV3HC", blank=True)
    nmresv3hr = models.IntegerField(null=True, db_column="NMRESV3HR", blank=True)
    nmresv3wm = models.IntegerField(null=True, db_column="NMRESV3WM", blank=True)
    nmresv3ap = models.IntegerField(null=True, db_column="NMRESV3AP", blank=True)
    nmresv3rf = models.IntegerField(null=True, db_column="NMRESV3RF", blank=True)
    nmresv3cf = models.IntegerField(null=True, db_column="NMRESV3CF", blank=True)
    nmresv3ef = models.IntegerField(null=True, db_column="NMRESV3EF", blank=True)
    nmresv3dw = models.IntegerField(null=True, db_column="NMRESV3DW", blank=True)
    nmresv3nrf = models.IntegerField(null=True, db_column="NMRESV3NRF", blank=True)
    nmresv3ncf = models.IntegerField(null=True, db_column="NMRESV3NCF", blank=True)
    nmresv3nef = models.IntegerField(null=True, db_column="NMRESV3NEF", blank=True)
    nmresv3ndw = models.IntegerField(null=True, db_column="NMRESV3NDW", blank=True)
    smrrateno = models.CharField(max_length=93, db_column="SMRRATENO", blank=True)
    nmrieccny = models.IntegerField(null=True, db_column="NMRIECCNY", blank=True)
    nmresv3saf = models.IntegerField(null=True, db_column="nMRESV3SAF", blank=True)
    fmresv3bfa = models.FloatField(null=True, db_column="fMRESV3BFA", blank=True)
    nmresv3nbb = models.IntegerField(null=True, db_column="nMRESV3NBB", blank=True)
    nmriecc12 = models.IntegerField(null=True, db_column="NMRIECC12", blank=True)
    meets_florida_requirements = models.BooleanField(null=True, blank=True, db_column="NMRFLORIDA")
    energy_star_v3_slab_exempt = models.BooleanField(null=True, blank=True, db_column="NMRESV3SLAB")
    NMRIECC15 = models.BooleanField(null=True, blank=True, db_column="NMRIECC15")
    energy_star_version_to_qualify = models.CharField(
        null=True, max_length=31, db_column="SMRESQUAL4", blank=True
    )

    NMRIECC18 = models.IntegerField(null=True, db_column="NMRIECC18", blank=True)
    NMRIECCMI = models.IntegerField(null=True, db_column="NMRIECCMI", blank=True)

    NMRESMFWSHR = models.IntegerField(null=True, db_column="NMRESMFWSHR", blank=True)
    NMRESMFDRYR = models.IntegerField(null=True, db_column="NMRESMFDRYR", blank=True)
    NMRESMFWIN = models.IntegerField(null=True, db_column="NMRESMFWIN", blank=True)
    NMRIECCNC = models.IntegerField(null=True, db_column="NMRIECCNC", blank=True)
    verified_ngbs_2015 = models.IntegerField(null=True, db_column="nMRNGBS15", blank=True)
    verified_iecc21 = models.BooleanField(null=True, db_column="NMRIECC21", blank=True)

    class Meta:
        db_table = "MandReq"
        managed = False
