"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..strings import (
    HOME_TYPES,
    HOME_LEVEL_TYPES,
    FOUNDATION_TYPES,
    THERMAL_BOUNDARY_TYPES,
    CRAWL_SPACE_TYPES,
)
from ..utils import compare_sets

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuildingInfo(models.Model):
    """Building Info"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    volume = models.FloatField(null=True, db_column="fBIVolume")
    conditioned_area = models.FloatField(null=True, db_column="fBIACond")
    type = models.IntegerField(null=True, db_column="nBIHType", choices=HOME_TYPES)
    house_level_type = models.IntegerField(
        null=True, db_column="nBILType", choices=HOME_LEVEL_TYPES
    )
    number_stories = models.IntegerField(null=True, db_column="nBIStories")
    foundation_type = models.IntegerField(null=True, db_column="nBIFType", choices=FOUNDATION_TYPES)
    number_bedrooms = models.IntegerField(null=True, db_column="nBIBeds")
    num_units = models.IntegerField(null=True, db_column="nBIUnits")
    rating_number = models.CharField(max_length=93, db_column="sBIRateNo")
    crawl_space_type = models.IntegerField(
        null=True, db_column="nBICType", choices=CRAWL_SPACE_TYPES
    )
    year_built = models.IntegerField(null=True, db_column="nBIYearBlt", blank=True)
    thermal_boundary = models.IntegerField(
        null=True, db_column="nBIThBndry", choices=THERMAL_BOUNDARY_TYPES
    )
    number_stories_including_conditioned_basement = models.IntegerField(
        null=True, db_column="nBIStoryWCB"
    )
    total_number_of_stories = models.IntegerField(null=True, db_column="nBITotalStories")

    foundation_within_infiltration_volume = models.BooleanField(
        null=True, db_column="NBIINFLTVOL", blank=True, help_text="Is Foundation in Infilt Volume"
    )

    def __str__(self):
        return "{} {} {} bedroom {} family".format(
            self.year_built,
            self.get_type_display(),
            self.number_bedrooms,
            self.get_house_level_type_display(),
        )

    @property
    def pretty_volume(self):
        """Nicely formatted volume"""
        if self.volume:
            return int(round(self.volume))
        return "-"

    @property
    def pretty_conditioned_area(self):
        """Nicely formatted area"""
        if self.conditioned_area:
            return int(round(self.conditioned_area))
        return "-"

    @property
    def pretty_housing_type(self):
        """Nicely formated housing type"""
        return self.get_type_display()

    def compare_to_home_status(self, home_status, **kwargs):
        """Compare building info to a home status"""
        match_items = [
            (
                self.conditioned_area,
                home_status.floorplan.square_footage,
                float,
                "Floorplan: Square Footage",
            ),
        ]
        for attr, kw in [(self.number_bedrooms, "number_bedrooms"), (self.volume, "volume")]:
            if kwargs.get(kw):
                value, label = kwargs.get(kw)
                match_items.append((attr, value, int, "Checklist: {}".format(label)))

        if kwargs.get("allowed_housing_type") is not None:
            match_items.append(
                (
                    self.type in kwargs.get("allowed_housing_type")[0],
                    True,
                    bool,
                    kwargs.get("allowed_housing_type")[1],
                    "error",
                )
            )

        if kwargs.get("allowed_foundation_type") is not None:
            match_items.append(
                (
                    self.foundation_type in kwargs.get("allowed_foundation_type")[0],
                    True,
                    bool,
                    kwargs.get("allowed_foundation_type")[1],
                    "error",
                )
            )

        if self.foundation_type == 3 and kwargs.get("enclosed_thermal_boundary") is not None:
            match_items.append(
                (
                    self.thermal_boundary in kwargs.get("enclosed_thermal_boundary")[0],
                    True,
                    bool,
                    kwargs.get("enclosed_thermal_boundary")[1],
                    "error",
                )
            )

        if self.foundation_type == 6 and kwargs.get("more_than_one_thermal_boundary") is not None:
            match_items.append(
                (
                    self.thermal_boundary in kwargs.get("more_than_one_thermal_boundary")[0],
                    True,
                    bool,
                    kwargs.get("more_than_one_thermal_boundary")[1],
                    "error",
                )
            )

        return compare_sets(match_items)

    @property
    def ashrae_64p2_2010_mechanical_ventillation_target(self):  # pylint: disable=invalid-name
        """ASHRAE 64.2 Ventilation target"""
        return (self.number_bedrooms + 1) * 7.5 + (self.conditioned_area * 0.01)
