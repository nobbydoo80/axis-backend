"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import LEAKAGE_TYPES, LEAKAGE_UNITS

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DuctSystem(models.Model):
    """Duct Systems"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    duct_system_number = models.IntegerField(primary_key=True, db_column="LDSDSNO")
    name = models.CharField(max_length=93, db_column="SZDSNAME", blank=True)
    leakage_type = models.IntegerField(
        null=True, db_column="NDSDLEAKTY", blank=True, choices=LEAKAGE_TYPES
    )
    units = models.IntegerField(
        null=True, db_column="NDSDLEAKUN", blank=True, choices=LEAKAGE_UNITS
    )

    total_leakage = models.FloatField(null=True, db_column="FDSDLEAKTO", blank=True)
    supply_leakage = models.FloatField(null=True, db_column="FDSDLEAKSU", blank=True)
    return_leakage = models.FloatField(null=True, db_column="FDSDLEAKRE", blank=True)
    # -- Not used ---
    ldshtgno = models.IntegerField(null=True, db_column="LDSHTGNO", blank=True)
    ldsclgno = models.IntegerField(null=True, db_column="LDSCLGNO", blank=True)
    fdssuparea = models.FloatField(null=True, db_column="FDSSUPAREA", blank=True)
    fdsretarea = models.FloatField(null=True, db_column="FDSRETAREA", blank=True)
    ldsregis = models.IntegerField(null=True, db_column="LDSREGIS", blank=True)
    ldsdleaket = models.IntegerField(null=True, db_column="LDSDLEAKET", blank=True)
    sdsrateno = models.CharField(max_length=93, db_column="SDSRATENO", blank=True)
    ndsdleaktt = models.IntegerField(null=True, db_column="NDSDLEAKTT", blank=True)
    fdscfarea = models.FloatField(null=True, db_column="FDSCFAREA", blank=True)
    fdsdleakrto = models.FloatField(null=True, db_column="fDSDLEAKRTO", blank=True)
    ndsdleakrun = models.IntegerField(
        null=True, db_column="nDSDLeakRUN", blank=True, choices=LEAKAGE_UNITS
    )
    ndsdleaktex = models.IntegerField(null=True, db_column="NDSDLEAKTEX", blank=True)

    nDSInpType = models.IntegerField(null=True, db_column="nDSInpType", blank=True)
    nDSLtOType = models.IntegerField(null=True, db_column="nDSLtOType", blank=True)
    nDSIECCEx = models.IntegerField(null=True, db_column="nDSIECCEx", blank=True)
    nDSRESNETEx = models.IntegerField(null=True, db_column="nDSRESNETEx", blank=True)
    nDSESTAREx = models.IntegerField(null=True, db_column="nDSESTAREx", blank=True)
    fDSTestLtO = models.FloatField(null=True, db_column="fDSTestLtO", blank=True)
    fDSTestDL = models.FloatField(null=True, db_column="fDSTestDL", blank=True)

    no_building_cavities_used_as_ducts = models.BooleanField(
        null=True, db_column="nDSIsDucted", blank=True
    )
    leakage_test_type = models.IntegerField(db_column="nDSTestType", blank=True, null=True)

    distribution_system_efficiency = models.FloatField(null=True, db_column="fDSDSE", blank=True)

    class Meta:
        db_table = "DuctSystem"
        managed = False
