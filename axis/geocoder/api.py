"""admin.py: Django geocoder"""
import json

from django.conf import settings

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Geocode

__author__ = "Peter Landry"
__date__ = "12/4/13 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Peter Landry",
]


class GeocodeViewSet(viewsets.ReadOnlyModelViewSet):
    model = Geocode
    queryset = model.objects.all()

    @action(detail=False)
    def matches(self, request, **kwargs):
        data = request.query_params.dict()
        if data.get("city", "").startswith("{") and data.get("city", "").endswith("}"):
            data["city"] = str(json.loads(data.get("city")).get("id"))
        matches = Geocode.objects.get_matches(**data)
        addrs = []
        data = {"matches": []}

        for response in matches:
            addr = response.broker.place.formatted_address

            if request.user.is_superuser or settings.DEBUG:
                addr = "[{}] {}".format(response.get_engine_display(), addr)
            if addr not in addrs:
                data["matches"].append(
                    {
                        "response": response.id,
                        "address": addr,
                    }
                )
                addrs.append(addr)

        return Response(data)
