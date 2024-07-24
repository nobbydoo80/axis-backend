"""api.py: Geographic"""


from django.db.models import Count

from rest_framework import viewsets

from axis.core.pagination import AxisPageNumberPagination
from .models import Metro, City, County, ClimateZone
from .serializers import MetroSerializer, CitySerializer, CountySerializer, ClimateZoneSerializer

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class LongerPagePagination(AxisPageNumberPagination):
    page_size = 50


class UnrestrictedMetroViewSet(viewsets.ReadOnlyModelViewSet):
    model = Metro
    queryset = model.objects.all()
    serializer_class = MetroSerializer


class MetroViewSet(UnrestrictedMetroViewSet):
    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user)


class UnrestrictedCityViewSet(viewsets.ReadOnlyModelViewSet):
    model = City
    queryset = model.objects.all()
    serializer_class = CitySerializer
    pagination_class = LongerPagePagination


class CityViewSet(UnrestrictedCityViewSet):
    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user)


class SimpleCityViewSet(viewsets.ReadOnlyModelViewSet):
    model = City
    queryset = model.objects.none()

    def filter_queryset(self, queryset):
        queryset = City.objects.filter_by_user(self.request.user)

        grouped_queryset = (
            queryset.order_by().values("name", "county__state").annotate(n=Count("county__state"))
        )
        return grouped_queryset


class UnrestrictedCountyViewSet(viewsets.ReadOnlyModelViewSet):
    model = County
    queryset = model.objects.all()
    serializer_class = CountySerializer


class CountyViewSet(UnrestrictedCountyViewSet):
    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user)


class ClimateZoneViewSet(viewsets.ReadOnlyModelViewSet):
    model = ClimateZone
    queryset = model.objects.all()
    serializer_class = ClimateZoneSerializer
