"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "10/18/21 10:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import re
from collections import namedtuple
from functools import cached_property

from django.utils import formats
from rest_framework import serializers

from axis.checklist.collection.excel import ExcelChecklistCollector

from axis.customer_eto.eep_programs.washington_code_credit import (
    BuildingEnvelope,
    AirLeakageControl,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DWHR,
    EfficientWaterHeating,
    RenewableEnergy,
    Appliances,
)
from axis.customer_eto.models import FastTrackSubmission

log = logging.getLogger(__name__)


class WashingtonCodeCreditReportSerializer(serializers.ModelSerializer):
    """These are the base fields for the EPS Report"""

    address = serializers.SerializerMethodField()

    builder = serializers.SerializerMethodField()
    rater = serializers.SerializerMethodField()
    certification_date = serializers.SerializerMethodField()

    year_built = serializers.SerializerMethodField()
    square_footage = serializers.SerializerMethodField()

    electric_utility = serializers.SerializerMethodField()
    gas_utility = serializers.SerializerMethodField()

    envelope_option = serializers.SerializerMethodField()
    air_leakage_option = serializers.SerializerMethodField()
    hvac_option = serializers.SerializerMethodField()
    hvac_distribution_option = serializers.SerializerMethodField()
    dwhr_option = serializers.SerializerMethodField()
    water_heating_option = serializers.SerializerMethodField()
    renewable_electric_option = serializers.SerializerMethodField()
    appliance_option = serializers.SerializerMethodField()

    required_credits_to_meet_code = serializers.FloatField()
    achieved_total_credits = serializers.FloatField()
    eligible_gas_points = serializers.FloatField

    class Meta:
        model = FastTrackSubmission
        fields = (
            "address",
            "builder",
            "rater",
            "certification_date",
            "year_built",
            "square_footage",
            "electric_utility",
            "gas_utility",
            "envelope_option",
            "air_leakage_option",
            "hvac_option",
            "hvac_distribution_option",
            "dwhr_option",
            "water_heating_option",
            "renewable_electric_option",
            "appliance_option",
            "required_credits_to_meet_code",
            "achieved_total_credits",
            "eligible_gas_points",
        )
        read_only_fields = fields

    def get_address(self, obj: FastTrackSubmission) -> str:
        return obj.home_status.home.get_home_address_display(
            include_lot_number=False, include_city_state_zip=True
        )

    def get_builder(self, obj: FastTrackSubmission) -> str:
        return str(obj.home_status.home.get_builder())

    def get_rater(self, obj: FastTrackSubmission) -> str:
        return str(obj.home_status.company)

    def get_certification_date(self, obj: FastTrackSubmission) -> str:
        if obj.home_status.certification_date:
            return formats.date_format(obj.home_status.certification_date, "SHORT_DATE_FORMAT")
        return "Pending"

    def get_year_built(self, obj: FastTrackSubmission) -> str:
        if obj.home_status.certification_date:
            return str(obj.home_status.certification_date.year)
        return str(datetime.date.today().year)

    @cached_property
    def _checklist_answers(self) -> dict:
        home_status = self.instance.home_status
        context = {"user__company": home_status.company}
        collector = ExcelChecklistCollector(home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    @cached_property
    def _annotations(self) -> dict:
        home_status = self.instance.home_status
        required = home_status.eep_program.required_annotation_types.values_list("slug", flat=True)
        annotations = {v: "" for v in required}
        annotations.update(dict(home_status.annotations.all().values_list("type__slug", "content")))
        return annotations

    def get_square_footage(self, _obj: FastTrackSubmission) -> str:
        value = self._checklist_answers["wcc-conditioned_floor_area"]
        if value:
            return f"{int(value):,}"
        return ""

    def get_electric_utility(self, obj: FastTrackSubmission) -> str:
        value = obj.home_status.get_electric_company()
        if value:
            return str(value)
        return ""

    def get_gas_utility(self, obj: FastTrackSubmission) -> str:
        value = obj.home_status.get_gas_company()
        if value:
            return str(value)
        return ""

    def get_envelope_option(self, _obj: FastTrackSubmission) -> str:
        return BuildingEnvelope(self._annotations["wcc-envelope-option"])

    def get_air_leakage_option(self, _obj: FastTrackSubmission) -> str:
        return AirLeakageControl(self._annotations["wcc-air-leakage-option"])

    def get_hvac_option(self, _obj: FastTrackSubmission) -> str:
        return HighEfficiencyHVAC(self._annotations["wcc-hvac-option"])

    def get_hvac_distribution_option(self, _obj: FastTrackSubmission) -> str:
        return HighEfficiencyHVACDistribution(self._annotations["wcc-hvac-distribution-option"])

    def get_dwhr_option(self, _obj: FastTrackSubmission) -> str:
        return DWHR(self._annotations["wcc-dwhr-option"])

    def get_water_heating_option(self, _obj: FastTrackSubmission) -> str:
        return EfficientWaterHeating(self._annotations["wcc-water-heating-option"])

    def get_renewable_electric_option(self, _obj: FastTrackSubmission) -> str:
        return RenewableEnergy(self._annotations["wcc-renewable-electric-option"])

    def get_appliance_option(self, _obj: FastTrackSubmission) -> str:
        return Appliances(self._annotations["wcc-appliance-option"])
