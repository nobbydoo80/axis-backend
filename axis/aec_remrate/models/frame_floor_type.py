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


class FrameFloorType(models.Model):
    """Input Framed Floor Types"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    floor_type_number = models.IntegerField(db_column="LFTFTNO")
    composite_insulation_number = models.IntegerField(db_column="NFTTCTNO")
    continuous_insulation = models.FloatField(null=True, db_column="FFTCONTINS", blank=True)
    cavity_insulation = models.FloatField(null=True, db_column="FFTCVTYINS", blank=True)

    # -- Not Used --
    fftjstwdt = models.FloatField(null=True, db_column="FFTJSTWDT", blank=True)
    fftjsthgt = models.FloatField(null=True, db_column="FFTJSTHGT", blank=True)
    fftjstspg = models.FloatField(null=True, db_column="FFTJSTSPG", blank=True)
    fftcinsthk = models.FloatField(null=True, db_column="FFTCINSTHK", blank=True)
    nftcovtype = models.FloatField(null=True, db_column="NFTCOVTYPE", blank=True)
    bftqfvalid = models.FloatField(null=True, db_column="BFTQFVALID", blank=True)
    nftqftype = models.IntegerField(null=True, db_column="NFTQFTYPE", blank=True)
    fftflrwid = models.FloatField(null=True, db_column="FFTFLRWID", blank=True)
    fftoutwid = models.FloatField(null=True, db_column="FFTOUTWID", blank=True)
    fftbatthk = models.FloatField(null=True, db_column="FFTBATTHK", blank=True)
    fftbatrvl = models.FloatField(null=True, db_column="FFTBATRVL", blank=True)
    fftblkthk = models.FloatField(null=True, db_column="FFTBLKTHK", blank=True)
    fftblkrvl = models.FloatField(null=True, db_column="FFTBLKRVL", blank=True)
    nftcntins = models.IntegerField(null=True, db_column="NFTCNTINS", blank=True)
    nftoutins = models.IntegerField(null=True, db_column="NFTOUTINS", blank=True)
    fftff = models.FloatField(null=True, db_column="FFTFF", blank=True)
    bftdfltff = models.IntegerField(null=True, db_column="BFTDFLTFF", blank=True)
    sftnote = models.CharField(max_length=765, db_column="SFTNOTE", blank=True)
    nftinsgrde = models.IntegerField(null=True, db_column="NFTINSGRDE", blank=True)

    class Meta:
        db_table = "FlrType"
        managed = False
