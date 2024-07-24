"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import (
    FOUNDATION_WALL_TYPES,
    FOUNDATION_WALL_STUD_TYPES,
    INSULATION_GRADES,
)

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FoundationWallType(models.Model):
    """Foundation Wall Types"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    wall_type_number = models.IntegerField(primary_key=True, db_column="LFWTWTNO")
    name = models.CharField(max_length=93, db_column="SFWTTYPE", blank=True)
    wall_type = models.IntegerField(null=True, db_column="NFWTTYPE", choices=FOUNDATION_WALL_TYPES)
    stud_type = models.IntegerField(
        null=True, db_column="NFWTSTDTYP", choices=FOUNDATION_WALL_STUD_TYPES
    )
    insulation_grade = models.IntegerField(
        null=True, db_column="NFWTINSGRD", choices=INSULATION_GRADES
    )

    # -- Not Used --
    ffwtmasthk = models.FloatField(null=True, db_column="FFWTMASTHK", blank=True)
    ffwtextins = models.FloatField(null=True, db_column="FFWTEXTINS", blank=True)
    ffwtexinst = models.FloatField(null=True, db_column="FFWTEXINST", blank=True)
    ffwtexinsb = models.FloatField(null=True, db_column="FFWTEXINSB", blank=True)
    nfwteinttp = models.FloatField(null=True, db_column="NFWTEINTTP", blank=True)
    nfwteinbtp = models.FloatField(null=True, db_column="NFWTEINBTP", blank=True)
    ffwtininct = models.FloatField(null=True, db_column="FFWTININCT", blank=True)
    ffwtininfc = models.FloatField(null=True, db_column="FFWTININFC", blank=True)
    ffwtininst = models.FloatField(null=True, db_column="FFWTININST", blank=True)
    ffwtininsb = models.FloatField(null=True, db_column="FFWTININSB", blank=True)
    nfwtiinttp = models.FloatField(null=True, db_column="NFWTIINTTP", blank=True)
    nfwtiinbtp = models.FloatField(null=True, db_column="NFWTIINBTP", blank=True)
    sfwtnote = models.CharField(max_length=765, db_column="SFWTNOTE", blank=True)

    class Meta:
        db_table = "FndwType"
        managed = False
