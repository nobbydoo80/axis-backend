"""report.py - Axis"""

__author__ = "Steven K"
__date__ = "9/30/21 08:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from collections import namedtuple
from functools import cached_property

from localflavor.us.us_states import US_STATES
from django.db.models import ObjectDoesNotExist
from rest_framework import serializers

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.customer_eto.api_v3.fields import (
    CappedIntegerCommaField,
    CappedCommaFloatField,
    CappedIntegerField,
    CappedFloatField,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class EPSReportBaseSerializer(serializers.Serializer):
    """These are the base fields for the EPS Report"""

    home_status = serializers.PrimaryKeyRelatedField(
        queryset=EEPProgramHomeStatus.objects.filter(eep_program__owner__slug="eto")
    )
    street_line = serializers.CharField(max_length=256)
    city = serializers.CharField(max_length=32)
    state = serializers.CharField(max_length=2)
    zipcode = serializers.CharField(max_length=16, allow_null=True)
    floorplan_type = serializers.ChoiceField(
        choices=["OFFICIAL", "PRELIMINARY"], default="PRELIMINARY"
    )

    rater = serializers.CharField(max_length=64)
    rater_ccb = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)

    estimated_monthly_energy_costs = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    estimated_average_annual_energy_cost = CappedIntegerCommaField(
        default=0, minimum_acceptable_value=0
    )
    year = serializers.IntegerField()
    square_footage = CappedIntegerCommaField()
    eps_issue_date = serializers.DateField(allow_null=True)

    electric_utility = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    gas_utility = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)

    electric_per_month = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    natural_gas_per_month = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)

    kwh_cost = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    therm_cost = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )

    solar = serializers.CharField(max_length=64)
    energy_score = serializers.IntegerField(default=0)

    net_electric_kwhs = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    electric_kwhs = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    natural_gas_therms = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    total_electric_kwhs = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    total_natural_gas_therms = CappedIntegerCommaField(default=0, minimum_acceptable_value=0)
    electric_tons_per_year = CappedFloatField(default=0, minimum_acceptable_value=0, round_value=1)
    natural_gas_tons_per_year = CappedFloatField(
        default=0, minimum_acceptable_value=0, round_value=1
    )

    insulated_ceiling = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    insulated_walls = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    insulated_floors = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    efficient_windows = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    efficient_lighting = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    water_heater = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    space_heating = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)
    envelope_tightness = serializers.CharField(max_length=64, allow_null=True, allow_blank=True)

    energy_consumption_score = CappedIntegerField(default=0)
    energy_consumption_similar_home = CappedIntegerField(default=0)
    energy_consumption_to_code = CappedIntegerField(default=0)
    carbon_footprint_score = CappedFloatField(default=0, round_value=1)
    carbon_footprint_similar_home = CappedFloatField(default=0, round_value=1)
    carbon_footprint_to_code = CappedFloatField(default=0, round_value=1)

    class Meta:
        fields = (
            "street_line",
            "city",
            "state",
            "zipcode",
            "floorplan_type",
            "rater",
            "rater_ccb",
            "estimated_monthly_energy_costs",
            "estimated_average_annual_energy_cost",
            "year",
            "square_footage",
            "eps_issue_date",
            "electric_utility",
            "gas_utility",
            "electric_per_month",
            "natural_gas_per_month",
            "kwh_cost",
            "therm_cost",
            "solar",
            "energy_score",
            "net_electric_kwhs",
            "electric_kwhs",
            "natural_gas_therms",
            "total_electric_kwhs",
            "total_natural_gas_therms",
            "electric_tons_per_year",
            "natural_gas_tons_per_year",
            "insulated_ceiling",
            "insulated_walls",
            "insulated_floors",
            "efficient_windows",
            "efficient_lighting",
            "water_heater",
            "space_heating",
            "envelope_tightness",
            "energy_consumption_score",
            "energy_consumption_similar_home",
            "energy_consumption_to_code",
            "carbon_footprint_score",
            "carbon_footprint_similar_home",
            "carbon_footprint_to_code",
        )

    def to_representation(self, data):
        """Generate out the EPS Report"""
        internal = super(EPSReportBaseSerializer, self).to_representation(data)
        internal["state_long"] = dict(US_STATES).get(internal["state"])
        internal["cond_state"] = internal["state"]
        internal["cond_state_long"] = internal["state_long"]
        if internal["state"] == "OR":
            internal["cond_state"] += " "
            internal["cond_state_long"] += " "
        return internal


class EPSReportCoreSerializer(serializers.ModelSerializer):
    street_line = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    zipcode = serializers.SerializerMethodField()
    floorplan_type = serializers.SerializerMethodField()

    rater = serializers.SerializerMethodField()
    rater_ccb = serializers.SerializerMethodField()

    estimated_monthly_energy_costs = serializers.ReadOnlyField()
    estimated_average_annual_energy_cost = serializers.ReadOnlyField(
        source="estimated_annual_energy_costs"
    )

    eps_issue_date = serializers.SerializerMethodField()

    electric_utility = serializers.SerializerMethodField()
    gas_utility = serializers.SerializerMethodField()

    electric_per_month = serializers.ReadOnlyField(source="electric_cost_per_month")
    natural_gas_per_month = serializers.ReadOnlyField(source="natural_gas_cost_per_month")

    solar = serializers.SerializerMethodField()
    energy_score = serializers.ReadOnlyField(source="eps_score")

    electric_kwhs = serializers.ReadOnlyField(source="improved_total_kwh")
    net_electric_kwhs = serializers.SerializerMethodField()
    total_electric_kwhs = serializers.SerializerMethodField()
    natural_gas_therms = serializers.ReadOnlyField(source="improved_total_therms")
    total_natural_gas_therms = serializers.SerializerMethodField()

    electric_tons_per_year = serializers.ReadOnlyField(
        source="projected_carbon_consumption_electric"
    )
    natural_gas_tons_per_year = serializers.ReadOnlyField(
        source="projected_carbon_consumption_natural_gas"
    )

    energy_consumption_score = serializers.ReadOnlyField(source="eps_score")
    energy_consumption_similar_home = serializers.ReadOnlyField(source="similar_size_eps_score")
    energy_consumption_to_code = serializers.ReadOnlyField(source="eps_score_built_to_code_score")
    carbon_footprint_score = serializers.ReadOnlyField(source="carbon_score")
    carbon_footprint_similar_home = serializers.ReadOnlyField(source="similar_size_carbon_score")
    carbon_footprint_to_code = serializers.ReadOnlyField(source="carbon_built_to_code_score")

    # Simulation / Checklist fields
    year = serializers.SerializerMethodField()
    square_footage = serializers.SerializerMethodField()

    kwh_cost = serializers.SerializerMethodField()
    therm_cost = serializers.SerializerMethodField()

    insulated_ceiling = serializers.SerializerMethodField()
    insulated_walls = serializers.SerializerMethodField()
    insulated_floors = serializers.SerializerMethodField()
    efficient_windows = serializers.SerializerMethodField()
    efficient_lighting = serializers.SerializerMethodField()
    water_heater = serializers.SerializerMethodField()
    space_heating = serializers.SerializerMethodField()
    envelope_tightness = serializers.SerializerMethodField()

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = (
            "id",
            "street_line",
            "city",
            "state",
            "zipcode",
            "floorplan_type",
            "rater",
            "rater_ccb",
            "estimated_monthly_energy_costs",
            "estimated_average_annual_energy_cost",
            "year",
            "square_footage",
            "eps_issue_date",
            "electric_utility",
            "gas_utility",
            "electric_per_month",
            "natural_gas_per_month",
            "kwh_cost",
            "therm_cost",
            "solar",
            "energy_score",
            "net_electric_kwhs",
            "electric_kwhs",
            "natural_gas_therms",
            "total_electric_kwhs",
            "total_natural_gas_therms",
            "electric_tons_per_year",
            "natural_gas_tons_per_year",
            "insulated_ceiling",
            "insulated_walls",
            "insulated_floors",
            "efficient_windows",
            "efficient_lighting",
            "water_heater",
            "space_heating",
            "envelope_tightness",
            "energy_consumption_score",
            "energy_consumption_similar_home",
            "energy_consumption_to_code",
            "carbon_footprint_score",
            "carbon_footprint_similar_home",
            "carbon_footprint_to_code",
        )
        read_only_fields = (
            "id",
            "street_line",
            "city",
            "state",
            "zipcode",
            "floorplan_type",
            "rater",
            "rater_ccb",
            "estimated_monthly_energy_costs",
            "estimated_average_annual_energy_cost",
            "year",
            "square_footage",
            "eps_issue_date",
            "electric_utility",
            "gas_utility",
            "electric_per_month",
            "natural_gas_per_month",
            "kwh_cost",
            "therm_cost",
            "solar",
            "energy_score",
            "net_electric_kwhs",
            "electric_kwhs",
            "natural_gas_therms",
            "total_electric_kwhs",
            "total_natural_gas_therms",
            "electric_tons_per_year",
            "natural_gas_tons_per_year",
            "insulated_ceiling",
            "insulated_walls",
            "insulated_floors",
            "efficient_windows",
            "efficient_lighting",
            "water_heater",
            "space_heating",
            "envelope_tightness",
            "energy_consumption_score",
            "energy_consumption_similar_home",
            "energy_consumption_to_code",
            "carbon_footprint_score",
            "carbon_footprint_similar_home",
            "carbon_footprint_to_code",
        )

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

    def get_rater(self, obj: FastTrackSubmission) -> str:
        return str(obj.home_status.company)

    def get_floorplan_type(self, _obj: FastTrackSubmission) -> str:
        home_status = self.instance.home_status
        if home_status.certification_date is not None:
            return "OFFICIAL"
        return "PRELIMINARY"

    def get_rater_ccb(self, obj: FastTrackSubmission) -> str:
        home_status = obj.home_status
        try:
            ccb = home_status.company.eto_account.ccb_number
            if ccb is None:
                ccb = "--"
        except ObjectDoesNotExist:
            ccb = "--"
        return f"<b>CCB #:</b> {ccb} <br/>" if home_status.home.state == "OR" else ""

    def get_solar(self, obj: FastTrackSubmission) -> str:
        solar = []
        if obj.solar_hot_water_kwh or obj.pv_kwh:
            solar_kwh = int(round(obj.solar_hot_water_kwh, 0))
            solar_kwh += int(round(obj.pv_kwh, 0))
            solar.append(f"Electric (kWh): {solar_kwh:,}")
        if obj.solar_hot_water_therms:
            solar_therms = int(round(obj.solar_hot_water_therms, 0))
            solar.append(f"Natural gas (therms): {solar_therms:,}")
        return ", ".join(solar) if solar else "No system"

    def get_net_electric_kwhs(self, obj: FastTrackSubmission) -> float:
        return obj.improved_total_kwh - obj.pv_kwh - obj.solar_hot_water_kwh

    def get_total_electric_kwhs(self, obj: FastTrackSubmission) -> float:
        return obj.improved_total_kwh + obj.pv_kwh + obj.solar_hot_water_kwh

    def get_total_natural_gas_therms(self, obj: FastTrackSubmission) -> float:
        return obj.improved_total_therms + obj.solar_hot_water_therms

    def get_eps_issue_date(self, obj: FastTrackSubmission) -> datetime.date:
        return obj.home_status.certification_date

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

    @cached_property
    def _checklist_answers(self) -> dict:
        home_status = self.instance.home_status
        context = {"user__company": home_status.company}
        collector = ExcelChecklistCollector(home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        data = {}
        for i in instrument_lookup:
            try:
                data[i.measure_id] = collector.get_data_display(i)
            except TypeError:
                pass
        return data

    def get_year(self, _obj: FastTrackSubmission) -> int:
        raise NotImplementedError

    def get_square_footage(self, _obj: FastTrackSubmission) -> int:
        raise NotImplementedError

    def get_kwh_cost(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_therm_cost(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_insulated_ceiling(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_insulated_walls(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_insulated_floors(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_efficient_windows(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_efficient_lighting(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_water_heater(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_space_heating(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def get_envelope_tightness(self, _obj: FastTrackSubmission) -> str:
        raise NotImplementedError

    def to_representation(self, instance: FastTrackSubmission):
        data = super(EPSReportCoreSerializer, self).to_representation(instance)
        data["home_status"] = instance.home_status.id
        serializer = EPSReportBaseSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return serializer.data
