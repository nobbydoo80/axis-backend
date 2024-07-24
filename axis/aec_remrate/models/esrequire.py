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


class Esrequire(models.Model):
    """ENERGY STAR Requirements"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    nesequip = models.IntegerField(null=True, db_column="NESEQUIP", blank=True)
    neswindow = models.IntegerField(null=True, db_column="NESWINDOW", blank=True)
    nesfixture = models.IntegerField(null=True, db_column="NESFIXTURE", blank=True)
    nesappli = models.IntegerField(null=True, db_column="NESAPPLI", blank=True)
    nesceilfan = models.IntegerField(null=True, db_column="NESCEILFAN", blank=True)
    nesventfan = models.IntegerField(null=True, db_column="NESVENTFAN", blank=True)
    naboverall = models.IntegerField(null=True, db_column="nABOVERALL", blank=True)
    nabgrbdjst = models.IntegerField(null=True, db_column="nABGRBDJST", blank=True)
    nabevbffls = models.IntegerField(null=True, db_column="nABEVBFFLS", blank=True)
    nabslabedg = models.IntegerField(null=True, db_column="nABSLABEDG", blank=True)
    nabbandjst = models.IntegerField(null=True, db_column="nABBANDJST", blank=True)
    nabthmlbrg = models.IntegerField(null=True, db_column="nABTHMLBRG", blank=True)
    nwlshwrtub = models.IntegerField(null=True, db_column="nWLSHWRTUB", blank=True)
    nwlfireplc = models.IntegerField(null=True, db_column="nWLFIREPLC", blank=True)
    nwlatcslpe = models.IntegerField(null=True, db_column="nWLATCSLPE", blank=True)
    nwlatcknee = models.IntegerField(null=True, db_column="nWLATCKNEE", blank=True)
    nwlskyshft = models.IntegerField(null=True, db_column="nWLSKYSHFT", blank=True)
    nwlporchrf = models.IntegerField(null=True, db_column="nWLPORCHRF", blank=True)
    nwlstrcase = models.IntegerField(null=True, db_column="nWLSTRCASE", blank=True)
    nwldouble = models.IntegerField(null=True, db_column="nWLDOUBLE", blank=True)
    nflrabvgrg = models.IntegerField(null=True, db_column="nFLRABVGRG", blank=True)
    nflrcantil = models.IntegerField(null=True, db_column="nFLRCANTIL", blank=True)
    nshaftduct = models.IntegerField(null=True, db_column="nSHAFTDUCT", blank=True)
    nshaftpipe = models.IntegerField(null=True, db_column="nSHAFTPIPE", blank=True)
    nshaftflue = models.IntegerField(null=True, db_column="nSHAFTFLUE", blank=True)
    natcaccpnl = models.IntegerField(null=True, db_column="nATCACCPNL", blank=True)
    natddstair = models.IntegerField(null=True, db_column="nATDDSTAIR", blank=True)
    nrfdrpsoft = models.IntegerField(null=True, db_column="nRFDRPSOFT", blank=True)
    nrfrecslgt = models.IntegerField(null=True, db_column="nRFRECSLGT", blank=True)
    nrfhomefan = models.IntegerField(null=True, db_column="nRFHOMEFAN", blank=True)
    ncwlbtwnut = models.IntegerField(null=True, db_column="nCWLBTWNUT", blank=True)
    srateno = models.CharField(max_length=93, db_column="SRATENO", blank=True)

    class Meta:
        db_table = "ESRequire"
        managed = False
