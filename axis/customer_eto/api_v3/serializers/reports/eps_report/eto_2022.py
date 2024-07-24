"""eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "3/29/22 09:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from collections import namedtuple
from functools import cached_property

from rest_framework import serializers

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.customer_eto.api_v3.fields import (
    CappedIntegerCommaField,
    CappedIntegerField,
    CappedCommaFloatField,
)
from axis.customer_eto.models import FastTrackSubmission
from .eto_2018 import EPSReport2018Serializer
from .simulation import EPSReport2022SimulationSerializer, EPSReport2021SimulationSerializer

log = logging.getLogger(__name__)


class EPSReportLegacy2022Serializer(EPSReport2018Serializer):
    @cached_property
    def _simulation_data(self) -> dict:
        home_status = self.instance.home_status
        serializer = EPSReport2022SimulationSerializer(data=home_status.floorplan.simulation)
        return serializer.to_representation(home_status.floorplan.simulation)


class EPSReport2022BaseSerializer(serializers.Serializer):
    """Properly formats everything for our report.  While this has a lot of stuff from the Base
    we only need a limited subset of it."""

    street_line = serializers.CharField(max_length=48)
    city = serializers.CharField(max_length=32)
    state = serializers.CharField(max_length=2)
    zipcode = serializers.CharField(max_length=16, allow_null=True)

    year = serializers.CharField(max_length=4)
    square_footage = CappedIntegerCommaField()
    eps_issue_date = serializers.DateField(allow_null=True)

    rater = serializers.CharField(max_length=64)
    builder = serializers.CharField(max_length=64)
    electric_utility = serializers.CharField(max_length=64)
    gas_utility = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)

    energy_score = serializers.IntegerField(default=0)
    energy_consumption_similar_home = CappedIntegerField(default=0)
    energy_consumption_to_code = CappedIntegerField(default=0)

    estimated_monthly_energy_costs = CappedIntegerCommaField(
        default=0, minimum_acceptable_value=0, prefix="$"
    )
    estimated_monthly_energy_costs_code = CappedIntegerCommaField(
        default=0, minimum_acceptable_value=0, prefix="$"
    )
    electric_per_month = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    natural_gas_per_month = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    kwh_cost = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    therm_cost = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    total_electric_kwhs = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    total_natural_gas_therms = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)

    annual_savings = CappedIntegerCommaField(default=0, minimum_acceptable_value=0, prefix="$")
    thirty_year_savings = CappedIntegerCommaField(default=0, minimum_acceptable_value=0, prefix="$")

    solar_elements = serializers.CharField(max_length=64, allow_blank=True)
    electric_vehicle_type = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    storage_type = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)

    pv_watts = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    pv_capacity_watts = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    storage_capacity = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)

    class Meta:
        fields = (
            "street_line",
            "city",
            "state",
            "zipcode",
            "year",
            "square_footage",
            "eps_issue_date",
            "rater",
            "builder",
            "electric_utility",
            "gas_utility",
            "energy_score",
            "energy_consumption_similar_home",
            "energy_consumption_to_code",
            "estimated_monthly_energy_costs",
            "estimated_monthly_energy_costs_code",
            "electric_per_month",
            "natural_gas_per_month",
            "kwh_cost",
            "therm_cost",
            "total_electric_kwhs",
            "total_natural_gas_therms",
            "annual_savings",
            "thirty_year_savings",
            "solar_elements",
            "electric_vehicle_type",
            "storage_type",
            "pv_kwh",
            "pv_capacity_watts",
            "storage_capacity",
        )


class EPSReport2022Serializer(serializers.ModelSerializer):
    street_line = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    zipcode = serializers.SerializerMethodField()

    year = serializers.SerializerMethodField()
    square_footage = serializers.SerializerMethodField()

    eps_issue_date = serializers.SerializerMethodField()

    rater = serializers.SerializerMethodField()
    builder = serializers.SerializerMethodField()

    electric_utility = serializers.SerializerMethodField()
    gas_utility = serializers.SerializerMethodField(allow_null=True)

    energy_score = serializers.ReadOnlyField(source="eps_score")
    energy_consumption_similar_home = serializers.ReadOnlyField(source="similar_size_eps_score")
    energy_consumption_to_code = serializers.ReadOnlyField(source="eps_score_built_to_code_score")

    estimated_monthly_energy_costs = serializers.ReadOnlyField()
    estimated_monthly_energy_costs_code = serializers.ReadOnlyField()

    electric_per_month = serializers.ReadOnlyField(source="electric_cost_per_month")
    natural_gas_per_month = serializers.ReadOnlyField(source="natural_gas_cost_per_month")

    kwh_cost = serializers.SerializerMethodField()
    therm_cost = serializers.SerializerMethodField()

    total_electric_kwhs = serializers.SerializerMethodField()
    total_natural_gas_therms = serializers.ReadOnlyField(source="improved_total_therms")

    annual_savings = serializers.ReadOnlyField(source="estimated_annual_energy_savings_cost")
    thirty_year_savings = serializers.SerializerMethodField()
    solar_elements = serializers.SerializerMethodField()
    electric_vehicle_type = serializers.SerializerMethodField()
    storage_type = serializers.SerializerMethodField()
    pv_watts = serializers.SerializerMethodField()
    pv_capacity_watts = serializers.SerializerMethodField()
    storage_capacity = serializers.SerializerMethodField()

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission

        fields = (
            "street_line",
            "city",
            "state",
            "zipcode",
            "year",
            "square_footage",
            "eps_issue_date",
            "rater",
            "builder",
            "electric_utility",
            "gas_utility",
            "energy_score",
            "energy_consumption_similar_home",
            "energy_consumption_to_code",
            "estimated_monthly_energy_costs",
            "estimated_monthly_energy_costs_code",
            "electric_per_month",
            "natural_gas_per_month",
            "kwh_cost",
            "therm_cost",
            "total_electric_kwhs",
            "total_natural_gas_therms",
            "annual_savings",
            "thirty_year_savings",
            "solar_elements",
            "electric_vehicle_type",
            "storage_type",
            "pv_watts",
            "pv_capacity_watts",
            "storage_capacity",
        )
        read_only_fields = fields

    @cached_property
    def _simulation_data(self) -> dict:
        home_status = self.instance.home_status
        serializer = EPSReport2022SimulationSerializer(data=home_status.floorplan.simulation)
        if home_status.home.state == "WA":
            serializer = EPSReport2021SimulationSerializer(data=home_status.floorplan.simulation)
        return serializer.to_representation(home_status.floorplan.simulation)

    @cached_property
    def _checklist_answers(self) -> dict:
        home_status = self.instance.home_status
        context = {"user__company": home_status.company}
        collector = ExcelChecklistCollector(home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    @cached_property
    def _address(self) -> namedtuple:
        home_status = self.instance.home_status
        return home_status.home.get_home_address_display_parts(
            **{
                "company": home_status.company,
                "include_city_state_zip": True,
            }
        )

    def get_street_line(self, _obj: FastTrackSubmission) -> str:
        return self._address.street_line1

    def get_city(self, _obj: FastTrackSubmission) -> str:
        return self._address.city

    def get_state(self, _obj: FastTrackSubmission) -> str:
        return self._address.state

    def get_zipcode(self, _obj: FastTrackSubmission) -> str:
        return self._address.zipcode

    def get_year(self, _obj: FastTrackSubmission) -> int:
        return self._simulation_data.get("construction_year") or datetime.date.today().year

    def get_square_footage(self, _obj: FastTrackSubmission) -> int:
        return self._simulation_data.get("conditioned_area")

    def get_eps_issue_date(self, obj: FastTrackSubmission) -> datetime.date:
        return obj.home_status.certification_date

    def get_rater(self, obj: FastTrackSubmission) -> str:
        return str(obj.home_status.company)

    def get_builder(self, obj: FastTrackSubmission) -> str:
        return str(obj.home_status.home.get_builder())

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

    def get_kwh_cost(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("electric_unit_cost")

    def get_therm_cost(self, _obj: FastTrackSubmission) -> str:
        return self._simulation_data.get("gas_unit_cost")

    def get_total_electric_kwhs(self, obj: FastTrackSubmission) -> float:
        return obj.improved_total_kwh

    def get_thirty_year_savings(self, obj: FastTrackSubmission) -> float:
        return float(obj.estimated_annual_energy_savings_cost) * 30.0

    def get_solar_elements(self, _obj: FastTrackSubmission) -> str | None:
        return self._checklist_answers.get("solar-elements")

    def get_electric_vehicle_type(self, _obj: FastTrackSubmission) -> str | None:
        return self._checklist_answers.get("electric-vehicle-type")

    def get_storage_type(self, _obj: FastTrackSubmission) -> str | None:
        return self._checklist_answers.get("storage-type")

    def get_pv_watts(self, _obj: FastTrackSubmission) -> int:
        return int(
            self._checklist_answers.get("ets-annual-etsa-kwh")
            or self._checklist_answers.get("non-ets-annual-pv-watts")
            or 0
        )

    def get_pv_capacity_watts(self, _obj: FastTrackSubmission) -> float:
        return self._simulation_data.get("pv_capacity_watts", 0.0)

    def get_storage_capacity(self, _obj: FastTrackSubmission) -> int:
        return int(self._checklist_answers.get("storage-capacity") or 0)

    def to_representation(self, instance: FastTrackSubmission) -> dict:
        data = super(EPSReport2022Serializer, self).to_representation(instance)
        serializer = EPSReport2022BaseSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return serializer.data
