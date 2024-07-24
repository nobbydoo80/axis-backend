"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import INSULATION_GRADES, FLOOR_COVERINGS

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SlabType(models.Model):
    """Slab Types"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _source_slab_type_number = models.IntegerField(db_column="lSTSTNo")
    name = models.CharField(max_length=93, db_column="sSTType", blank=True)
    perimeter_r_value = models.FloatField(null=True, db_column="fSTPIns")
    under_slab_r_value = models.FloatField(null=True, db_column="fSTUIns")
    under_slab_width = models.FloatField(null=True, db_column="fSTFUWid")
    radiant_floor = models.IntegerField(
        null=True, db_column="nSTRadiant", choices=((1, True), (2, False))
    )
    perimeter_insulation_depth = models.FloatField(null=True, db_column="fSTPInsDep")
    note = models.CharField(max_length=765, db_column="sSTNote", blank=True)
    insulation_grade = models.IntegerField(
        null=True, db_column="nSTInsGrde", choices=INSULATION_GRADES
    )
    floor_covering = models.IntegerField(null=True, db_column="nSTFlrCvr", choices=FLOOR_COVERINGS)

    def __str__(self):
        return '"{}" R={}'.format(self.name, round(self.perimeter_r_value, 2))
