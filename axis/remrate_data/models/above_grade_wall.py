"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import AboveGradeWallManager
from ..strings import JOIST_ABOVE_GRADE_WALL_LOCATIONS, COLORS, ORIENTATION_CHOICES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AboveGradeWall(models.Model):
    """Above Grade Walls"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    type = models.ForeignKey("WallType", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=93, db_column="szAGName")
    gross_area = models.FloatField(null=True, db_column="fAGArea")
    location = models.IntegerField(db_column="nAGLoc", choices=JOIST_ABOVE_GRADE_WALL_LOCATIONS)
    color = models.IntegerField(choices=COLORS, db_column="nAGCol")
    u_value = models.FloatField(null=True, db_column="fAGUo")
    _wall_type_number = models.IntegerField(db_column="lAGWallTNo")
    rating_number = models.CharField(max_length=93, db_column="sAGRateNo", blank=True)

    objects = AboveGradeWallManager()

    def __str__(self):
        return '"{}" {}'.format(self.name, self.type)

    class Meta:
        ordering = ("simulation", "gross_area")

    def get_r_value(self):
        """Get the R-Value"""
        return "%.1f" % (1 / self.u_value)

    def is_shared_for_window(self, window):
        """Does this wall contain other shared windows with other orientations"""
        from .simulation import Simulation

        other_windows = (
            Simulation.objects.get(id=self.simulation_id)
            .window_set.filter(wall_number=window.wall_number)
            .exclude(orientation=window.orientation)
        )
        return other_windows.count()

    def get_windows(self):
        """Return windows"""
        for idx, wall in enumerate(self.simulation.abovegradewall_set.order_by("pk"), start=1):
            if wall.pk == self.pk:
                return self.simulation.window_set.filter(wall_number=idx)
        self.simulation.window_set.none()

    def get_orientations(self):
        """Gets the possible orientations"""
        values = self.get_windows().values_list("orientation", flat=True)
        return list(set([dict(ORIENTATION_CHOICES).get(x) for x in values]))

    @property
    def orientation(self):
        """If a wall has a singular orientation we can use that."""
        orientations = self.get_orientations()
        if len(orientations) == 1:
            return orientations[0]
