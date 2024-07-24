"""Examine view-to-api collector"""


import logging

from rest_framework.response import Response

from ..collectors import ChecklistCollector, APICollectorMixin
from .. import methods as axis_methods
from . import methods
from . import serializers

__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class BootstrapAngularChecklistCollector(ChecklistCollector, APICollectorMixin):
    # Inject Examine base on cascading select methods
    method_mixins = {
        axis_methods.BaseCascadingSelectMethod: {
            "prefix": "Examine",
            "mixin": methods.ExamineCascadingSelectMethodMixin,
        },
    }

    type_methods = {
        "open": methods.TextBoxMethod,
        "integer": methods.NumberBoxMethod,
        "float": methods.DecimalBoxMethod,
        "date": methods.DateBoxMethod,
        "multiple-choice": methods.HorizontalStripSelectMethod,
    }

    serializer_classes = {
        "instrument": serializers.InstrumentSerializer,
        "input": serializers.InputInstrumentSerializer,
        "request": serializers.CollectionRequestSerializer,
    }

    def get_destroy_response(self, instrument):
        """Returns a new copy of the instrument and fresh version of conditional instruments."""
        serializer_class = self.get_serializer_class("instrument")

        # We send all conditional instruments instead of just activated ones so that we can
        # effectively deactivate instruments that were previously enabled.
        conditional_instruments = instrument.get_child_instruments()
        instruments = [instrument] + list(conditional_instruments)
        serializer = serializer_class(
            instance=instruments,
            many=True,
            context={
                "collector": self,
            },
        )

        return Response(serializer.data)

    def remove(self, instrument, instance):
        home_status = instance.home_status
        super(BootstrapAngularChecklistCollector, self).remove(instrument, instance)
        home_status.validate_references()
