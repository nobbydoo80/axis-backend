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


class Doechallenge(models.Model):
    """DOE Challenge Home"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    sdcbldrid = models.CharField(max_length=93, db_column="SDCBLDRID", blank=True)
    ndcfenstrtn = models.IntegerField(null=True, db_column="NDCFENSTRTN", blank=True)
    ndcinsul = models.IntegerField(null=True, db_column="NDCINSUL", blank=True)
    ndcductloc = models.IntegerField(null=True, db_column="NDCDUCTLOC", blank=True)
    ndcappl = models.IntegerField(null=True, db_column="NDCAPPL", blank=True)
    ndclighting = models.IntegerField(db_column="NDCLIGHTING")
    ndcfaneff = models.IntegerField(null=True, db_column="NDCFANEFF", blank=True)
    ndcairqual = models.IntegerField(null=True, db_column="NDCAIRQUAL", blank=True)
    ndcsolare = models.IntegerField(null=True, db_column="NDCSOLARE", blank=True)
    ndcsolarhw = models.IntegerField(null=True, db_column="NDCSOLARHW", blank=True)
    ndcairplus = models.IntegerField(db_column="NDCAIRPLUS")
    ndcwtrsense = models.IntegerField(db_column="NDCWTRSENSE")
    ndcibhs = models.IntegerField(db_column="NDCIBHS")
    ndcmgmt = models.IntegerField(db_column="NDCMGMT")
    ndcwaiver = models.IntegerField(db_column="NDCWAIVER")
    sdcrateno = models.CharField(max_length=93, db_column="SDCRATENO", blank=True)
    verified_water_efficiency = models.IntegerField(null=True, db_column="NDCWATEREFF", blank=True)
    passive_home_certified = models.BooleanField(null=True, db_column="nDCPassiveHome", blank=True)

    class Meta:
        db_table = "DOEChallenge"
        managed = False
