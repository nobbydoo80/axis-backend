"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..models import Building
from ..utils import compare_sets

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Project(models.Model):
    """Project Info"""

    building = models.OneToOneField(
        Building,
        on_delete=models.CASCADE,
    )
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    name = models.CharField(max_length=153, db_column="sPIBlgName", blank=True, null=True)
    property_owner = models.CharField(max_length=93, db_column="sPIPOwner", blank=True, null=True)
    property_address = models.CharField(max_length=93, db_column="sPIStreet", blank=True, null=True)
    property_city = models.CharField(max_length=93, db_column="sPICity", blank=True, null=True)
    property_state = models.CharField(max_length=93, db_column="sPIState", blank=True, null=True)
    property_zip = models.CharField(max_length=93, db_column="sPIZip", blank=True, null=True)
    property_phone = models.CharField(max_length=93, db_column="sPIPhone", blank=True, null=True)
    builder_permit = models.CharField(max_length=93, db_column="sPIBldrPrmt", blank=True, null=True)
    builder_name = models.CharField(max_length=93, db_column="SPIBuilder", blank=True, null=True)
    builder_address = models.CharField(max_length=93, db_column="sPIBldrStr", blank=True, null=True)
    builder_address2 = models.CharField(
        max_length=93, db_column="sPIBldrCty", blank=True, null=True
    )
    builder_email = models.CharField(max_length=303, db_column="sPIBldrEml", blank=True, null=True)
    builder_phone = models.CharField(max_length=93, db_column="sPIBldrPho", blank=True, null=True)
    builder_model = models.CharField(max_length=153, db_column="sPIModel", blank=True, null=True)
    builder_development = models.CharField(
        max_length=93, db_column="sPIBldrDev", blank=True, null=True
    )
    rating_organization = models.CharField(
        max_length=93, db_column="sPIRatOrg", blank=True, null=True
    )
    rating_organization_address = models.CharField(
        max_length=93, db_column="sPIRatStr", blank=True, null=True
    )
    rating_organization_city = models.CharField(
        max_length=93, db_column="sPIRatCity", blank=True, null=True
    )
    rating_organization_state = models.CharField(
        max_length=93, db_column="sPIRatSt", blank=True, null=True
    )
    rating_organization_zip = models.CharField(
        max_length=93, db_column="sPIRatZip", blank=True, null=True
    )
    rating_organization_phone = models.CharField(
        max_length=93, db_column="sPIRatPhon", blank=True, null=True
    )
    rating_organization_website = models.CharField(
        max_length=303, db_column="sPIRatWeb", blank=True, null=True
    )
    provider_id = models.CharField(max_length=93, db_column="sPIPRVDRID", blank=True, null=True)
    rater_name = models.CharField(max_length=93, db_column="sPIRatName", blank=True, null=True)
    rater_id = models.CharField(max_length=93, db_column="sPIRaterNo", null=True, blank=True)
    rater_email = models.CharField(max_length=303, db_column="sPIRatEMal", blank=True, null=True)
    rating_date = models.CharField(max_length=93, db_column="sPIRatDate", blank=True, null=True)
    rating_number = models.CharField(max_length=93, db_column="sPIRatngNo", blank=True, null=True)
    rating_type = models.CharField(max_length=93, db_column="sPIRatType", blank=True, null=True)
    rating_reason = models.CharField(max_length=93, db_column="sPIRatReas", blank=True, null=True)
    rater_plan_inspector_one_name = models.CharField(
        max_length=93, db_column="sPIVer1Name", blank=True, null=True
    )
    rater_plan_inspector_one_id = models.CharField(
        max_length=93, db_column="sPIVer1ID", blank=True, null=True
    )
    rater_plan_inspector_two_name = models.CharField(
        max_length=93, db_column="sPIVer2Name", blank=True, null=True
    )
    rater_plan_inspector_two_id = models.CharField(
        max_length=93, db_column="sPIVer2ID", blank=True, null=True
    )
    rater_plan_inspector_three_name = models.CharField(
        max_length=93, db_column="sPIVer3Name", blank=True, null=True
    )
    rater_plan_inspector_three_id = models.CharField(
        max_length=93, db_column="sPIVer3ID", blank=True, null=True
    )
    rater_plan_inspector_four_name = models.CharField(
        max_length=93, db_column="sPIVer4Name", blank=True, null=True
    )
    rater_plan_inspector_four_id = models.CharField(
        max_length=93, db_column="sPIVer4ID", blank=True, null=True
    )
    sampleset_id = models.CharField(max_length=93, db_column="SPISAMSETID", blank=True, null=True)
    resnet_registry_id = models.CharField(
        max_length=153, db_column="sPIREGID", null=True, blank=True
    )
    resnet_registry_date = models.CharField(
        max_length=32, db_column="sPIRegDate", null=True, blank=True
    )
    rating_permit_date = models.CharField(
        max_length=32, db_column="sPIPrmtDate", null=True, blank=True
    )

    def __str__(self):
        return '"{}" {} {} {} ({})'.format(
            self.name,
            self.property_owner,
            self.property_address,
            self.property_city,
            self.resnet_registry_id,
        )

    def compare_to_home_status(self, home_status, **_unused):
        """Compares this to home status data"""

        try:
            builder = home_status.home.get_builder().name
        except AttributeError:
            builder = None

        try:
            subdivision = home_status.home.subdivision.name or ""
        except AttributeError:
            subdivision = None

        match_items = [
            (self.builder_name, builder, str, "Home: Builder"),
            (self.property_city, home_status.home.city.name, str, "Home: City"),
            (self.property_state, home_status.home.state, str, "Home: State"),
            (self.property_zip, home_status.home.zipcode, str, "Home: ZIP code"),
            (self.builder_development, subdivision, str, "Subdivision: Name"),
            (self.name, home_status.floorplan.name, str, "Floorplan: Model name"),
        ]
        return compare_sets(match_items)
