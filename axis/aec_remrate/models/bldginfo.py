"""Django AEC Models - Theses are the source data coming in on the rate database."""


import logging

from django.db import models

from axis.remrate_data.strings import (
    HOME_TYPES,
    HOME_LEVEL_TYPES,
    FOUNDATION_TYPES,
    THERMAL_BOUNDARY_TYPES,
)

__author__ = "Steven Klass"
__date__ = "06/09/2019 13:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Bldginfo(models.Model):
    """Building Info"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    volume = models.FloatField(null=True, db_column="FBIVOLUME", blank=True)
    conditioned_area = models.FloatField(null=True, db_column="FBIACOND", blank=True)
    type = models.IntegerField(null=True, db_column="NBIHTYPE", choices=HOME_TYPES, blank=True)
    house_level_type = models.IntegerField(
        null=True, db_column="NBILTYPE", choices=HOME_LEVEL_TYPES, blank=True
    )
    number_stories = models.IntegerField(null=True, db_column="NBISTORIES", blank=True)
    foundation_type = models.IntegerField(
        null=True, db_column="NBIFTYPE", choices=FOUNDATION_TYPES, blank=True
    )
    number_bedrooms = models.IntegerField(null=True, db_column="NBIBEDS", blank=True)
    num_units = models.IntegerField(null=True, db_column="NBIUNITS", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SBIRATENO", blank=True)
    crawl_space_type = models.IntegerField(null=True, db_column="NBICTYPE", blank=True)
    year_built = models.IntegerField(null=True, db_column="NBIYEARBLT", blank=True)
    thermal_boundary = models.IntegerField(
        null=True, db_column="NBITHBNDRY", choices=THERMAL_BOUNDARY_TYPES, blank=True
    )
    number_stories_including_conditioned_basement = models.IntegerField(
        null=True, db_column="NBISTORYWCB"
    )

    foundation_within_infiltration_volume = models.BooleanField(
        null=True, db_column="NBIINFLTVOL", blank=True
    )

    total_number_of_stories = models.IntegerField(
        null=True, db_column="nBITotalStories", blank=True
    )

    class Meta:
        db_table = "BldgInfo"
