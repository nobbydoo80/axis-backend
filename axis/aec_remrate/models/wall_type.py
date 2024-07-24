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


class WallType(models.Model):
    """Describe the walls"""

    wall_number = models.IntegerField(db_column="LWTWTNO", primary_key=True)
    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    composite_insulation_number = models.IntegerField(null=True, db_column="LWTCOMPNO", blank=True)
    continuous_insulation = models.FloatField(null=True, db_column="FWTCONTINS", blank=True)
    cavity_insulation = models.FloatField(null=True, db_column="FWTCVTYINS", blank=True)

    # -- Not Used --
    fwtstudwdt = models.FloatField(null=True, db_column="FWTSTUDWDT", blank=True)
    fwtstuddpt = models.FloatField(null=True, db_column="FWTSTUDDPT", blank=True)
    fwtstudspg = models.FloatField(null=True, db_column="FWTSTUDSPG", blank=True)
    fwtgypthk = models.FloatField(null=True, db_column="FWTGYPTHK", blank=True)
    fwtcinsthk = models.FloatField(null=True, db_column="FWTCINSTHK", blank=True)
    fwtblckins = models.FloatField(null=True, db_column="FWTBLCKINS", blank=True)
    nwtcntntyp = models.FloatField(null=True, db_column="NWTCNTNTYP", blank=True)
    bwtqfvalid = models.FloatField(null=True, db_column="BWTQFVALID", blank=True)
    fwtff = models.FloatField(null=True, db_column="FWTFF", blank=True)
    bwtdfltff = models.IntegerField(null=True, db_column="BWTDFLTFF", blank=True)
    swtnote = models.CharField(max_length=765, db_column="SWTNOTE", blank=True)
    nwtinsgrde = models.IntegerField(null=True, db_column="NWTINSGRDE", blank=True)

    class Meta:
        db_table = "WallType"
        managed = False
