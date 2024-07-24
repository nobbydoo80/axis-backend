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


class Roof(models.Model):
    """Input Ties a ceiling type to a home."""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    ceiling_type = models.IntegerField(db_column="LROCEILTNO")
    name = models.CharField(max_length=31, db_column="SZRONAME", null=True)
    color = models.IntegerField(
        choices=((0, "Reflective"), (1, "Light"), (2, "Medium"), (3, "Dark")), db_column="NROCOL"
    )
    area = models.FloatField(db_column="FROAREA", null=True)
    clay_or_concrete = models.IntegerField(choices=((1, True), (2, False)), db_column="NROCLAY")
    sub_tile_ventilation = models.IntegerField(choices=((1, True), (2, False)), db_column="NROVENT")
    radiant_barrier = models.IntegerField(choices=((1, True), (2, False)), db_column="NRORADBAR")
    style = models.IntegerField(choices=((1, "Vaulted"), (2, "Attic")), db_column="NROTYPE")
    u_value = models.FloatField(db_column="FROUO")
    rating_number = models.CharField(max_length=93, db_column="SRORATENO", blank=True)
    sealed_attic_roof_area = models.FloatField(null=True, db_column="FROROOFAREA", blank=True)

    class Meta:
        db_table = "Roof"
        managed = False
