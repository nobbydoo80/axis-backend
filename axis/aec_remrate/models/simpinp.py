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


class Simpinp(models.Model):
    """Simplified Input"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    lbldgno = models.IntegerField(db_column="LBLDGNO")
    nsihsetype = models.FloatField(null=True, db_column="NSIHSETYPE", blank=True)
    nsifndtype = models.FloatField(null=True, db_column="NSIFNDTYPE", blank=True)
    fsifndpesl = models.FloatField(null=True, db_column="FSIFNDPESL", blank=True)
    fsifndpeoc = models.FloatField(null=True, db_column="FSIFNDPEOC", blank=True)
    fsifndpeec = models.FloatField(null=True, db_column="FSIFNDPEEC", blank=True)
    fsifndpehc = models.FloatField(null=True, db_column="FSIFNDPEHC", blank=True)
    fsifndpeuf = models.FloatField(null=True, db_column="FSIFNDPEUF", blank=True)
    fsifndpehf = models.FloatField(null=True, db_column="FSIFNDPEHF", blank=True)
    fsifndpeuw = models.FloatField(null=True, db_column="FSIFNDPEUW", blank=True)
    fsifndpehw = models.FloatField(null=True, db_column="FSIFNDPEHW", blank=True)
    fsicflarea = models.FloatField(null=True, db_column="FSICFLAREA", blank=True)
    nsibedrms = models.FloatField(null=True, db_column="NSIBEDRMS", blank=True)
    fsipflarhb = models.FloatField(null=True, db_column="FSIPFLARHB", blank=True)
    fsipflarfl = models.FloatField(null=True, db_column="FSIPFLARFL", blank=True)
    fsipflarml = models.FloatField(null=True, db_column="FSIPFLARML", blank=True)
    fsipflarsl = models.FloatField(null=True, db_column="FSIPFLARSL", blank=True)
    fsipflartl = models.FloatField(null=True, db_column="FSIPFLARTL", blank=True)
    nsinocrnhb = models.FloatField(null=True, db_column="NSINOCRNHB", blank=True)
    nsinocrnfl = models.FloatField(null=True, db_column="NSINOCRNFL", blank=True)
    nsinocrnml = models.FloatField(null=True, db_column="NSINOCRNML", blank=True)
    nsinocrnsl = models.FloatField(null=True, db_column="NSINOCRNSL", blank=True)
    nsinocrntl = models.FloatField(null=True, db_column="NSINOCRNTL", blank=True)
    fsipoabohb = models.FloatField(null=True, db_column="FSIPOABOHB", blank=True)
    fsipoabofl = models.FloatField(null=True, db_column="FSIPOABOFL", blank=True)
    fsipoaboml = models.FloatField(null=True, db_column="FSIPOABOML", blank=True)
    fsipoabosl = models.FloatField(null=True, db_column="FSIPOABOSL", blank=True)
    fsipoabotl = models.FloatField(null=True, db_column="FSIPOABOTL", blank=True)
    fsiceilhhb = models.FloatField(null=True, db_column="FSICEILHHB", blank=True)
    fsiceilhfl = models.FloatField(null=True, db_column="FSICEILHFL", blank=True)
    fsiceilhml = models.FloatField(null=True, db_column="FSICEILHML", blank=True)
    fsiceilhsl = models.FloatField(null=True, db_column="FSICEILHSL", blank=True)
    fsiceilhtl = models.FloatField(null=True, db_column="FSICEILHTL", blank=True)
    fsipogrge = models.FloatField(null=True, db_column="FSIPOGRGE", blank=True)
    fsipcathhb = models.FloatField(null=True, db_column="FSIPCATHHB", blank=True)
    fsipcathfl = models.FloatField(null=True, db_column="FSIPCATHFL", blank=True)
    fsipcathml = models.FloatField(null=True, db_column="FSIPCATHML", blank=True)
    fsipcathsl = models.FloatField(null=True, db_column="FSIPCATHSL", blank=True)
    fsipcathtl = models.FloatField(null=True, db_column="FSIPCATHTL", blank=True)
    fsiinfrate = models.FloatField(null=True, db_column="FSIINFRATE", blank=True)
    nsiinfmtyp = models.FloatField(null=True, db_column="NSIINFMTYP", blank=True)
    nsiinfunit = models.FloatField(null=True, db_column="NSIINFUNIT", blank=True)
    nsinodoors = models.FloatField(null=True, db_column="NSINODOORS", blank=True)
    fsislbdbmt = models.FloatField(null=True, db_column="FSISLBDBMT", blank=True)
    fslbd1l = models.FloatField(null=True, db_column="FSLBD1L", blank=True)
    lsiclgt1no = models.FloatField(null=True, db_column="LSICLGT1NO", blank=True)
    lsiclgt2no = models.FloatField(null=True, db_column="LSICLGT2NO", blank=True)
    lsiwalt1no = models.FloatField(null=True, db_column="LSIWALT1NO", blank=True)
    lsiwalt2no = models.FloatField(null=True, db_column="LSIWALT2NO", blank=True)
    lsifndwtno = models.FloatField(null=True, db_column="LSIFNDWTNO", blank=True)
    lsiflrtyno = models.FloatField(null=True, db_column="LSIFLRTYNO", blank=True)
    lsidortyno = models.FloatField(null=True, db_column="LSIDORTYNO", blank=True)
    lsislbtyno = models.FloatField(null=True, db_column="LSISLBTYNO", blank=True)
    ssirateno = models.CharField(max_length=93, db_column="SSIRATENO", blank=True)
    fsiboxlen = models.FloatField(null=True, db_column="FSIBOXLEN", blank=True)
    fsiboxwid = models.FloatField(null=True, db_column="FSIBOXWID", blank=True)
    fsiboxhgt = models.FloatField(null=True, db_column="FSIBOXHGT", blank=True)
    nsilvabgar = models.FloatField(null=True, db_column="NSILVABGAR", blank=True)

    class Meta:
        db_table = "SimpInp"
        managed = False
