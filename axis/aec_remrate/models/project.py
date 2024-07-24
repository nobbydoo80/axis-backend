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


class Project(models.Model):
    """Input side Project Info"""

    result_number = models.IntegerField(null=True, db_column="LBLDGRUNNO", blank=True)
    building_number = models.IntegerField(db_column="LBLDGNO")
    name = models.CharField(max_length=153, db_column="SPIBLGNAME", blank=True)
    property_owner = models.CharField(max_length=93, db_column="SPIPOWNER", blank=True)
    property_address = models.CharField(max_length=93, db_column="SPISTREET", blank=True)
    property_city = models.CharField(max_length=93, db_column="SPICITY", blank=True)
    property_state = models.CharField(max_length=93, db_column="SPISTATE", blank=True)
    property_zip = models.CharField(max_length=93, db_column="SPIZIP", blank=True)
    property_phone = models.CharField(max_length=93, db_column="SPIPHONE", blank=True)
    builder_permit = models.CharField(max_length=93, db_column="SPIBLDRPRMT", blank=True)
    builder_name = models.CharField(max_length=93, db_column="SPIBUILDER", blank=True)
    builder_address = models.CharField(max_length=93, db_column="SPIBLDRSTR", blank=True)
    builder_address2 = models.CharField(max_length=93, db_column="SPIBLDRCTY", blank=True)
    builder_email = models.CharField(max_length=303, db_column="SPIBLDREML", blank=True)
    builder_phone = models.CharField(max_length=93, db_column="SPIBLDRPHO", blank=True)
    builder_model = models.CharField(max_length=153, db_column="SPIMODEL", blank=True)
    builder_development = models.CharField(max_length=93, db_column="SPIBLDRDEV", blank=True)
    rating_organization = models.CharField(max_length=93, db_column="SPIRATORG", blank=True)
    rating_organization_address = models.CharField(max_length=93, db_column="SPIRATSTR", blank=True)
    rating_organization_city = models.CharField(max_length=93, db_column="SPIRATCITY", blank=True)
    rating_organization_state = models.CharField(max_length=93, db_column="SPIRATST", blank=True)
    rating_organization_zip = models.CharField(max_length=93, db_column="SPIRATZIP", blank=True)
    rating_organization_phone = models.CharField(max_length=93, db_column="SPIRATPHON", blank=True)
    rating_organization_website = models.CharField(
        max_length=303, db_column="SPIRATWEB", blank=True
    )
    provider_id = models.CharField(max_length=93, db_column="SPIPRVDRID", blank=True)
    rater_name = models.CharField(max_length=93, db_column="SPIRATNAME", blank=True)
    rater_id = models.CharField(max_length=93, db_column="SPIRATERNO", blank=True)
    rater_email = models.CharField(max_length=303, db_column="SPIRATEMAL", blank=True)
    rating_date = models.CharField(max_length=93, db_column="SPIRATDATE", blank=True)
    rating_number = models.CharField(max_length=93, db_column="SPIRATNGNO", blank=True)
    rating_type = models.CharField(max_length=93, db_column="SPIRATTYPE", blank=True)
    rating_reason = models.CharField(max_length=93, db_column="SPIRATREAS", blank=True)
    rater_plan_inspector_one_name = models.CharField(
        max_length=93, db_column="SPIVER1NAME", blank=True
    )
    rater_plan_inspector_one_id = models.CharField(max_length=93, db_column="SPIVER1ID", blank=True)
    rater_plan_inspector_two_name = models.CharField(
        max_length=93, db_column="SPIVER2NAME", blank=True
    )
    rater_plan_inspector_two_id = models.CharField(max_length=93, db_column="SPIVER2ID", blank=True)
    rater_plan_inspector_three_name = models.CharField(
        max_length=93, db_column="SPIVER3NAME", blank=True
    )
    rater_plan_inspector_three_id = models.CharField(
        max_length=93, db_column="SPIVER3ID", blank=True
    )
    rater_plan_inspector_four_name = models.CharField(
        max_length=93, db_column="SPIVER4NAME", blank=True
    )
    rater_plan_inspector_four_id = models.CharField(
        max_length=93, db_column="SPIVER4ID", blank=True
    )
    sampleset_id = models.CharField(max_length=93, db_column="SPISAMSETID", blank=True)
    resnet_registry_id = models.CharField(max_length=153, db_column="SPIREGID", blank=True)
    resnet_registry_date = models.CharField(
        max_length=32, db_column="SPIREGDATE", null=True, blank=True
    )
    rating_permit_date = models.CharField(
        max_length=255, db_column="SPIPRMTDATE", null=True, blank=True
    )

    class Meta:
        db_table = "ProjInfo"
        managed = False
