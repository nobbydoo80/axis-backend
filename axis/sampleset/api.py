"""models.py: Django sampleset API views"""


import logging
import uuid

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.core.utils import filter_integers
from .models import SampleSet, SampleSetHomeStatus
from .serializers import (
    SampleSetSerializer,
    SampleSetHomeStatusSerializer,
    SampleSetSummarySerializer,
)
from .utils import modify_sampleset

__author__ = "Autumn Valenta"
__date__ = "8/1/14 10:20 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSetViewSet(viewsets.ModelViewSet):
    model = SampleSet
    queryset = model.objects.all()
    serializer_class = SampleSetSerializer

    @action(detail=True)
    def summary(self, request, *args, **kwargs):
        """Returns data about a sampleset in a consolidated format for the UI."""
        obj = self.get_object()
        data = SampleSetSummarySerializer(obj).data
        return Response(data)

    @action(detail=False)
    def uuid(self, request, *args, **kwargs):
        """Return uuid for a blank Sample Set on front-end"""
        return Response(
            {
                "uuid": str(uuid.uuid4()),
            }
        )

    @action(detail=False)
    def analyze(self, request, *args, **kwargs):
        """
        Receives a collection of Test and Sampled homes, and returns status messages about the
        configuration.  No database modifications are made.
        """
        obj = self.model()
        test_id_list = list(filter_integers(request.query_params.getlist("test")))
        sampled_id_list = list(filter_integers(request.query_params.getlist("sampled")))
        data = modify_sampleset(
            obj, test_id_list, sampled_id_list, user=request.user, simulate=True
        )
        return Response(data)

    @action(detail=False, methods=["post", "put"])
    def commit(self, request, *args, **kwargs):
        """
        Requests a save operation on a sampleset with a set of item ids it should contain.
        SampleSetHomeStatus items will be implicitly removed from the sampleset's currently phase if
        the id is missing from the provided list.

        Correct usage of this endpoint may require multiple calls to store the configurations built
        in the frontend!
        """

        if request.method == "POST":
            obj = self.model(
                uuid=request.data.get("uuid"),
                alt_name=request.data.get("alt_name"),
                owner=request.user.company,
            )
        else:
            obj_id = request.data.get("sampleset")
            obj = get_object_or_404(self.get_queryset(), id=obj_id)
            obj.alt_name = request.data.get("alt_name")
            obj.save()

        test_id_list = list(filter_integers(list(request.data.get("test", []))))
        sampled_id_list = list(filter_integers(list(request.data.get("sampled", []))))

        data = modify_sampleset(
            obj, test_id_list, sampled_id_list, user=request.user, simulate=False
        )
        return Response(data)

    @action(detail=True, methods=["post"])
    def advance(self, request, *args, **kwargs):
        """Calling an advance method of SampleSet"""
        obj = self.get_object()
        obj.advance()
        return Response(status=status.HTTP_200_OK)


class SampleSetHomeStatusViewSet(viewsets.ModelViewSet):
    model = SampleSetHomeStatus
    queryset = model.objects.all().order_by("id")
    serializer_class = SampleSetHomeStatusSerializer
