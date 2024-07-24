"""views.py: Django community"""


import logging

from datatableview import datatables, helpers
from datatableview.helpers import link_to_model

from axis.relationship.utils import get_relationship_column_supplier


__author__ = "Autumn Valenta"
__date__ = "10/23/15 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CommunityListDatatable(datatables.Datatable):
    city_metro = datatables.TextColumn(
        "City (Metro)", sources=["city__name", "metro__name"], processor="get_city_metro_data"
    )
    associations = datatables.DisplayColumn("Associations", processor="_rel_callback")

    class Meta:
        columns = ["name", "city_metro", "cross_roads"]
        processors = {
            "name": helpers.link_to_model,
            "cross_roads": "get_cross_roads_data",
        }
        ordering = ["name"]

    def __init__(self, *args, **kwargs):
        super(CommunityListDatatable, self).__init__(*args, **kwargs)

        user = self.view.request.user
        self._rel_callback = get_relationship_column_supplier(user, "community", "community")

    def preload_record_data(self, obj):
        return {"attached": self.view._attached}

    def get_city_metro_data(self, obj, **kwargs):
        if obj.city and obj.metro:
            return "{} ({})".format(obj.city.name, obj.metro.name)
        elif obj.city:
            return obj.city.name
        return ""

    def get_cross_roads_data(self, obj, **kwargs):
        return "{}{}".format(obj.cross_roads, obj.get_address_designator())


class CommunitySubivisionListDatatable(datatables.Datatable):
    name = datatables.TextColumn(
        "Subdivision", sources=["name", "builder_name"], processor="get_subdivision_data"
    )
    builder_org = datatables.TextColumn(
        "Builder", sources=["builder_org__name"], processor="get_builder_org_data"
    )
    number_of_homes = datatables.IntegerColumn("Number of homes", processor="get_home_count_data")
    coordinates = datatables.TextColumn(
        "Coordinates", sources=["latitude", "longitude"], processor="get_coordinates_data"
    )

    class Meta:
        columns = ["name", "builder_org", "cross_roads", "coordinates"]
        ordering = ["name"]

    def get_subdivision_data(self, obj, *args, **kwargs):
        text = obj.name
        if obj.builder_name:
            text = "{} ({})".format(obj.name, obj.builder_name)
        return link_to_model(obj, text=text)

    def get_builder_org_data(self, obj, *args, **kwargs):
        return link_to_model(obj.builder_org)

    def get_home_count_data(self, obj, *args, **kwargs):
        return obj.home_set.count()

    def get_coordinates_data(self, obj, *args, **kwargs):
        return "(%s, %s)" % (obj.latitude, obj.longitude)
