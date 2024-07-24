"""api.py: Django reso"""


import json
import logging
from io import StringIO
from string import Template

from lxml import etree
from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import permissions, serializers, viewsets, renderers
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response

from axis.geographic.models import City, County
from axis.reso.RESO.data_models.reso import RESO1p4EDMX
from axis.reso.models import ResoHome, ResoGreenVerification
from axis.reso.odata.strings import (
    service_xml,
    data_systems_xml,
    BASE_URL,
    LAST_UPDATED,
    TRANSPORT_VERSION,
    TZ_OFFSET,
    NOW,
    DATA_DICTIONARY_VERSION,
    data_systems_json,
    metadata_xml,
)

__author__ = "Steven Klass"
__date__ = "7/23/17 10:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RESOAtomRenderer(renderers.BaseRenderer):
    media_type = "text/xml"
    format = "atom"

    def render(self, data, media_type=None, renderer_context=None):
        return etree.tostring(data, pretty_print=True)


class ServiceViewSet(viewsets.GenericViewSet):
    """
    Lists all RESO services this API Provides for.

        /

        /$metadata


    """

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication, TokenHasScope)

    def retrieve(self, _request, *_args, **_kwargs):
        """
        In conjunction with 2.3.2 this
        """
        with open(service_xml) as f:
            xml = f.read()
        tree = etree.parse(StringIO(xml))
        return Response(tree)

    def metadata(self, request, *_args, **_kwargs):
        """
        Formatted according to the RESO Web API Document v 1.0.2 Appendix 2 Section 3.
        """

        if "JSONRenderer" in "%s" % request.accepted_renderer:
            data = {"Error": "Only `atom` or `api` formats are allowed for $metatdata"}
        else:
            with open(metadata_xml) as f:
                xml = f.read()
            tree = etree.parse(StringIO(xml))
            return Response(tree)

        return Response(data)


class DataServicesViewSet(viewsets.GenericViewSet):
    """
    DataServices the RESO API Provides for.

    /('NAME') A single data system

    """

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication, TokenHasScope)

    def retrieve(self, request, *_args, **_kwargs):
        """
        Returns a Services
        """
        if "JSONRenderer" in "%s" % request.accepted_renderer:
            with open(data_systems_json) as f:
                data = Template(f.read())

            data = data.substitute(
                base_url=BASE_URL,
                last_updated=LAST_UPDATED,
                transport_version=TRANSPORT_VERSION,
                data_dictionary_version=DATA_DICTIONARY_VERSION,
                now=NOW,
                tzoffset=TZ_OFFSET,
            )

            data = json.loads(data)

        else:
            with open(data_systems_xml) as f:
                data = Template(f.read())

            data = data.substitute(
                base_url=BASE_URL,
                last_updated=LAST_UPDATED,
                transport_version=TRANSPORT_VERSION,
                data_dictionary_version=DATA_DICTIONARY_VERSION,
                now=NOW,
                tzoffset=TZ_OFFSET,
            )

            data = etree.parse(StringIO(data))
        return Response(data)

    def metadata(self, request, *_args, **_kwargs):
        """
        Returns metadata for Services
        """
        if "JSONRenderer" in "%s" % request.accepted_renderer:
            data = {"Error": "Only `atom` or `api` formats are allowed for $metatdata"}
        else:
            reso = RESO1p4EDMX()
            data = reso.data

        return Response(data)

    def reso(self, request, *args, **kwargs):
        """
        Returns metadata for Services
        """
        # return Response(datasystems.atom)

    def reso_metadata(self, request, *_args, **_kwargs):
        """
        Returns the same meta data for the single system definition.
        """
        if "JSONRenderer" in "%s" % request.accepted_renderer:
            data = {"Error": "Only `atom` or `api` formats are allowed for $metatdata"}
        else:
            reso = RESO1p4EDMX()
            data = reso.data

        return Response(data)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class CountySerializer(serializers.ModelSerializer):
    county_type = serializers.SerializerMethodField()
    climate_zone = serializers.SerializerMethodField()
    metro = serializers.SerializerMethodField()

    class Meta:
        model = County
        fields = (
            "id",
            "name",
            "state",
            "county_fips",
            "county_type",
            "legal_statistical_area_description",
            "ansi_code",
            "land_area_meters",
            "water_area_meters",
            "latitude",
            "longitude",
            "metro",
            "climate_zone",
        )

    def get_county_type(self, obj):
        return obj.get_county_type_display()

    def get_climate_zone(self, obj):
        return "{}".format(obj.climate_zone)

    def get_metro(self, obj):
        return "{}".format(obj.metro)


class GreenVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResoGreenVerification
        fields = (
            "GreenBuildingVerificationType",
            "GreenVerificationBody",
            "GreenVerificationDate",
            "GreenVerificationMetric",
            "GreenVerificationRating",
            "GreenVerificationSource",
            "GreenVerificationStatus",
            "GreenVerificationURL",
        )


class ResoHomeSerializer(serializers.ModelSerializer):
    GreenVerification = GreenVerificationSerializer(many=True)
    GreenBuildingVerificationType = serializers.SerializerMethodField()
    City = CitySerializer()
    CountyOrParish = CountySerializer()

    class Meta:
        model = ResoHome
        fields = (
            "ListingKeyNumeric",
            "AboveGradeFinishedArea",
            "AboveGradeFinishedAreaSource",
            "AboveGradeFinishedAreaUnits",
            "AddressLine1",
            "AddressLine2",
            "Basement",
            "BuilderModel",
            "BuilderName",
            "BuildingAreaTotal",
            "BuildingAreaSource",
            "BuildingAreaUnits",
            "City",
            "CountyOrParish",
            "Cooling",
            "CoolingYN",
            "ElectricExpense",
            "ElectricYN" "GasExpense",
            "GasYN" "GreenBuildingVerificationType",
            "Heating",
            "HeatingYN",
            "Latitude",
            "Longitude",
            "PostalCode",
            "StateOrProvince",
            "Stories",
            "StoriesTotal",
            "SubdivisionName",
            "YearBuilt",
            "YearBuiltSource",
            "GreenVerification",
        )

    def get_GreenBuildingVerificationType(self, obj):
        return eval(obj.GreenBuildingVerificationType)


class ResoHomeViewSet(viewsets.ReadOnlyModelViewSet):
    """

    RESO Property Listing


    """

    queryset = ResoHome.objects.all()
    serializer_class = ResoHomeSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication, TokenHasScope)
