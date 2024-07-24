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


class GeneralMechanicalEquipment(models.Model):
    """General Mechanical Equipment"""

    equipment_number = models.IntegerField(primary_key=True, db_column="LEIEINO")
    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    heating_set_point = models.FloatField(null=True, db_column="FEIHSETPNT", blank=True)
    cooling_set_point = models.FloatField(null=True, db_column="FEICSETPNT", blank=True)
    setback_thermostat = models.IntegerField(
        null=True, db_column="NEISBTHRM", choices=((1, True), (2, False)), blank=True
    )
    setup_thermostat = models.IntegerField(
        null=True, db_column="NEISUTHRM", choices=((1, True), (2, False)), blank=True
    )
    # -- Not Used ---
    neiventtyp = models.FloatField(null=True, db_column="NEIVENTTYP", blank=True)
    neisbsch = models.FloatField(null=True, db_column="NEISBSCH", blank=True)
    feisbtemp = models.FloatField(null=True, db_column="FEISBTEMP", blank=True)
    neiductloc = models.FloatField(null=True, db_column="NEIDUCTLOC", blank=True)
    neiductlo2 = models.FloatField(null=True, db_column="NEIDUCTLO2", blank=True)
    neiductlo3 = models.FloatField(null=True, db_column="NEIDUCTLO3", blank=True)
    feiductins = models.FloatField(null=True, db_column="FEIDUCTINS", blank=True)
    feiductin2 = models.FloatField(null=True, db_column="FEIDUCTIN2", blank=True)
    feiductin3 = models.FloatField(null=True, db_column="FEIDUCTIN3", blank=True)
    feiductsup = models.FloatField(null=True, db_column="FEIDUCTSUP", blank=True)
    feiductsu2 = models.FloatField(null=True, db_column="FEIDUCTSU2", blank=True)
    feiductsu3 = models.FloatField(null=True, db_column="FEIDUCTSU3", blank=True)
    feiductret = models.FloatField(null=True, db_column="FEIDUCTRET", blank=True)
    feiductre2 = models.FloatField(null=True, db_column="FEIDUCTRE2", blank=True)
    feiductre3 = models.FloatField(null=True, db_column="FEIDUCTRE3", blank=True)
    neiductlk = models.FloatField(null=True, db_column="NEIDUCTLK", blank=True)
    neidtunits = models.IntegerField(null=True, db_column="NEIDTUNITS", blank=True)
    feidtlkage = models.FloatField(null=True, db_column="FEIDTLKAGE", blank=True)
    neidtqual = models.IntegerField(null=True, db_column="NEIDTQUAL", blank=True)
    seirateno = models.CharField(max_length=93, db_column="SEIRATENO", blank=True)

    capacity_weighting_heating = models.IntegerField(
        null=True, db_column="nEIHTGCAPWT", blank=True, verbose_name="Capacity Weighting Heating"
    )
    capacity_weighting_cooling = models.IntegerField(
        null=True, db_column="nEICLGCAPWT", blank=True, verbose_name="Capacity Weighting Cooling"
    )
    capacity_weighting_hot_water = models.IntegerField(
        null=True, db_column="nEIDHWCAPWT", blank=True, verbose_name="Capacity Weighting Hot Water"
    )
    capacity_weighting_dehumidifier = models.BooleanField(
        null=True, db_column="nEIDHUCAPWT", verbose_name="Capacity Weighting Dehumidifier"
    )

    feiwhfflow = models.FloatField(null=True, db_column="fEIWHFFlow", blank=True)
    feiwhfwatts = models.FloatField(null=True, db_column="FEIWHFWatts", blank=True)

    class Meta:
        db_table = "Equip"
        managed = False
