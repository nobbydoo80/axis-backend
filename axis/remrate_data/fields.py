""" Fields definitions leveraging the Select2 tools. """


import logging

from django.utils import formats
from django.conf import settings

import pytz

from axis.core.fields import ApiModelSelect2Widget
from .api import SimulationViewSet, UnattachedSimulationViewSet

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SimulationChoiceWidget(ApiModelSelect2Widget):
    # permission_required =
    viewset_class = SimulationViewSet
    search_fields = [
        "building__project__name__icontains",
        "building__project__builder_development__icontains",
        "building__project__builder_name__icontains",
        "building__project__property_address__icontains",
        "building__filename__icontains",
    ]

    def label_from_instance(self, obj, request=None):
        date = obj.building.last_update or obj.building.created_on

        if request and request.user.is_authenticated:
            tz = request.user.timezone_preference
        else:
            tz = pytz.timezone(settings.TIME_ZONE)

        if date:
            date = date.astimezone(tz)
            created_on = "{date_string} {timezone!s}".format(
                date_string=formats.date_format(date, "SHORT_DATETIME_FORMAT"), timezone=tz
            )
        else:
            created_on = "-"

        if obj.export_type == 1:
            return (
                "Name: {obj.building.project.name}<br />"
                "Development: {obj.building.project.builder_development}<br />"
                "Builder: {obj.building.project.builder_name}<br />"
                "BLG File: {obj.building.filename}<br />"
                "Upload: {created_on}"
            ).format(obj=obj, created_on=created_on)
        return (
            "Name: {obj.building.project.name}<br />"
            "Development: {obj.building.project.builder_development}<br />"
            "Builder: {obj.building.project.builder_name}<br />"
            "BLG File: {obj.building.filename}<br />"
            "Upload: {created_on}<br />"
            "Type: {type}"
        ).format(obj=obj, created_on=created_on, type=obj.get_export_type_display())


class UnattachedSimulationChoiceWidget(SimulationChoiceWidget):
    viewset_class = UnattachedSimulationViewSet
