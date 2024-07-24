"""serializers.py - axis"""

__author__ = "Steven K"
__date__ = "1/10/23 09:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from django.apps import apps

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.filehandling.models import CustomerDocument
from axis.home.models import Home, EEPProgramHomeStatus
from simulation.enumerations import PvCapacity

log = logging.getLogger(__name__)
gbp_app = apps.get_app_config("gbr")


class GBRHomeSerializer(serializers.ModelSerializer):
    """Endpoint https://sandbox.greenbuildingregistry.com/api/properties

    Customer wanted to use as-entered addresses."""

    address_line_1 = serializers.SerializerMethodField()
    address_line_2 = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    postal_code = serializers.SerializerMethodField()
    building_type = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = (
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "postal_code",
            "building_type",
        )

    def get_address_line_1(self, obj: Home) -> str:
        return obj.get_home_address_display_parts(raw=True).street_line1

    def get_address_line_2(self, obj: Home) -> str:
        return obj.get_home_address_display_parts(raw=True).street_line2

    def get_city(self, obj: Home) -> str:
        return obj.get_home_address_display_parts(raw=True, include_city_state_zip=True).city

    def get_state(self, obj: Home) -> str:
        return obj.get_home_address_display_parts(raw=True, include_city_state_zip=True).state

    def get_postal_code(self, obj: Home) -> str:
        return obj.get_home_address_display_parts(raw=True, include_city_state_zip=True).zipcode

    def get_building_type(self, obj: Home) -> str:
        if obj.is_multi_family:
            return "multifamily"
        return "residential"


class GBRHomeStatusEPSSerializer(serializers.ModelSerializer):
    """Endpoint https://sandbox.greenbuildingregistry.com/api/assessments/{abbr}"""

    gbr_id = serializers.CharField(source="home.gbr.gbr_id")
    certification_number = serializers.SerializerMethodField()
    date = serializers.CharField(source="certification_date")
    score = serializers.CharField(source="fasttracksubmission.eps_score")
    source = serializers.SerializerMethodField()
    report_url = serializers.SerializerMethodField()
    expiration_date = serializers.SerializerMethodField()
    conditioned_floor_area = serializers.IntegerField(
        source="floorplan.simulation.conditioned_area"
    )
    annual_generated = serializers.SerializerMethodField()
    capacity = serializers.SerializerMethodField()
    year_installed = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "gbr_id",
            "certification_number",
            "date",
            "score",
            "source",
            "report_url",
            "expiration_date",
            "conditioned_floor_area",
            "annual_generated",
            "capacity",
            "year_installed",
        )

    def get_source(self, obj: EEPProgramHomeStatus) -> str:
        return "AXIS"

    def get_certification_number(self, obj: EEPProgramHomeStatus) -> str:
        return f"{obj.pk:0>6}"

    def get_report_url(self, obj: EEPProgramHomeStatus) -> str | None:
        existing = CustomerDocument.objects.filter(
            document__icontains="eps",
            content_type=ContentType.objects.get_for_model(obj.home),
            object_id=obj.home.pk,
            login_required=False,
        ).first()
        if existing:
            server_protocol = "https" if not settings.DEBUG else "http"
            server_host = "axis" if settings.SERVER_TYPE == "production" else settings.SERVER_TYPE
            server = "{}://{}.pivotalenergy.net".format(server_protocol, server_host)
            return server + existing.get_preview_link()

    def get_expiration_date(self, obj: EEPProgramHomeStatus) -> str:
        return (
            str(obj.certification_date + datetime.timedelta(days=1095))
            if obj.certification_date
            else str(datetime.date.today())
        )

    def get_annual_generated(self, obj: EEPProgramHomeStatus) -> int:
        if not obj.floorplan.simulation.photovoltaics.exists():
            return None
        context = {"user__company": obj.company}
        collector = ExcelChecklistCollector(obj.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        checklist = {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

        return int(
            checklist.get("ets-annual-etsa-kwh") or checklist.get("non-ets-annual-pv-watts") or 0
        )

    def get_capacity(self, obj: EEPProgramHomeStatus) -> int:
        if not obj.floorplan.simulation.photovoltaics.exists():
            return None
        total = 0
        simulation = obj.floorplan.simulation
        values = simulation.photovoltaics.all().values_list("capacity", "capacity_units")
        for cap, unit in values:
            if unit == PvCapacity.KWDC.value:
                total += cap
            elif unit == PvCapacity.WATT.value:
                total += cap / 1000.0
        return int(round(total, 0))

    def get_year_installed(self, obj: EEPProgramHomeStatus) -> str:
        if not obj.floorplan.simulation.photovoltaics.exists():
            return None
        return obj.floorplan.simulation.project.construction_year
