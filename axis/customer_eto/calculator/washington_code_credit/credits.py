"""credits.py - Axis"""

__author__ = "Steven K"
__date__ = "8/13/21 15:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from functools import cached_property
from tabulate import tabulate

from axis.customer_eto.calculator.washington_code_credit.constants.defaults import (
    BUILDING_ENVELOPE_OPTIONS,
    AIR_LEAKAGE,
    HVAC,
    HVAC_DISTRIBUTION,
    DRAIN_WATER_HEAT_RECOVER,
    HOT_WATER,
    RENEWABLES,
    APPLIANCES,
)

log = logging.getLogger(__name__)


class Credits:
    def __init__(
        self,
        envelope_option,
        air_leakage_option,
        hvac_option,
        hvac_distribution_option,
        dwhr_option,
        water_heating_option,
        renewable_electric_option,
        appliance_option,
        specifications,
    ):
        self.envelope_option = envelope_option
        self.air_leakage_option = air_leakage_option
        self.hvac_option = hvac_option
        self.hvac_distribution_option = hvac_distribution_option
        self.dwhr_option = dwhr_option
        self.water_heating_option = water_heating_option
        self.renewable_electric_option = renewable_electric_option
        self.appliance_option = appliance_option
        self.specifications = specifications

    @cached_property
    def eligible_building_envelope_credits(self):
        return BUILDING_ENVELOPE_OPTIONS[self.envelope_option]["eligible_credits"]

    @cached_property
    def achieved_building_envelope_credits(self):
        if self.specifications["building_envelope"].meet_requirements:
            return self.eligible_building_envelope_credits
        return self.eligible_building_envelope_credits

    @cached_property
    def eligible_air_leakage_credits(self):
        return AIR_LEAKAGE[self.air_leakage_option]["eligible_credits"]

    @cached_property
    def achieved_air_leakage_credits(self):
        if self.specifications["air_leakage"].meet_requirements:
            return self.eligible_air_leakage_credits
        return self.eligible_air_leakage_credits

    @cached_property
    def eligible_hvac_credits(self):
        return HVAC[self.hvac_option]["eligible_credits"]

    @cached_property
    def achieved_hvac_credits(self):
        if self.specifications["hvac"].meet_requirements:
            return self.eligible_hvac_credits
        return self.eligible_hvac_credits

    @cached_property
    def eligible_hvac_distribution_credits(self):
        return HVAC_DISTRIBUTION[self.hvac_distribution_option]["eligible_credits"]

    @cached_property
    def achieved_hvac_distribution_credits(self):
        if self.specifications["hvac_distribution"].meet_requirements:
            return self.eligible_hvac_distribution_credits
        return self.eligible_hvac_distribution_credits

    @cached_property
    def eligible_dwhr_credits(self):
        return DRAIN_WATER_HEAT_RECOVER[self.dwhr_option]["eligible_credits"]

    @cached_property
    def achieved_dwhr_credits(self):
        if self.specifications["water"].meets_dwhr_requirements:
            return self.eligible_dwhr_credits
        return self.eligible_dwhr_credits

    @cached_property
    def eligible_water_heating_credits(self):
        return HOT_WATER[self.water_heating_option]["eligible_credits"]

    @cached_property
    def achieved_water_heating_credits(self):
        if self.specifications["water"].meets_water_heater_requirements:
            return self.eligible_water_heating_credits
        return None

    @cached_property
    def eligible_renewable_electric_credits(self):
        return RENEWABLES[self.renewable_electric_option]["eligible_credits"]

    @cached_property
    def achieved_renewable_electric_credits(self):
        return self.eligible_renewable_electric_credits

    @cached_property
    def eligible_appliances_credits(self):
        return APPLIANCES[self.appliance_option]["eligible_credits"]

    @cached_property
    def achieved_appliances_credits(self):
        return self.eligible_appliances_credits

    @cached_property
    def eligible_total_credits(self):
        target_values = [
            self.eligible_building_envelope_credits,
            self.eligible_air_leakage_credits,
            self.eligible_hvac_credits,
            self.eligible_hvac_distribution_credits,
            self.eligible_dwhr_credits,
            self.eligible_water_heating_credits,
            self.eligible_renewable_electric_credits,
            self.eligible_appliances_credits,
        ]
        if None in target_values:
            return 0.0
        return sum(target_values)

    @cached_property
    def achieved_total_credits(self):
        target_values = [
            self.achieved_building_envelope_credits,
            self.achieved_air_leakage_credits,
            self.achieved_hvac_credits,
            self.achieved_hvac_distribution_credits,
            self.achieved_dwhr_credits,
            self.achieved_water_heating_credits,
            self.achieved_renewable_electric_credits,
            self.achieved_appliances_credits,
        ]
        if None in target_values:
            return 0.0
        return sum(target_values)

    @cached_property
    def credit_data(self):
        return {
            "building_envelope": {
                "eligible": self.eligible_building_envelope_credits,
                "achieved": self.achieved_building_envelope_credits,
            },
            "air_leakage": {
                "eligible": self.eligible_air_leakage_credits,
                "achieved": self.achieved_air_leakage_credits,
            },
            "hvac": {
                "eligible": self.eligible_hvac_credits,
                "achieved": self.achieved_hvac_credits,
            },
            "hvac_distribution": {
                "eligible": self.eligible_hvac_distribution_credits,
                "achieved": self.achieved_hvac_distribution_credits,
            },
            "dwhr": {
                "eligible": self.eligible_dwhr_credits,
                "achieved": self.achieved_dwhr_credits,
            },
            "water_heater": {
                "eligible": self.eligible_water_heating_credits,
                "achieved": self.achieved_water_heating_credits,
            },
            "renewables": {
                "eligible": self.eligible_renewable_electric_credits,
                "achieved": self.achieved_renewable_electric_credits,
            },
            "appliances": {
                "eligible": self.eligible_appliances_credits,
                "achieved": self.achieved_appliances_credits,
            },
            "total": {
                "eligible": self.eligible_total_credits,
                "achieved": self.achieved_total_credits,
            },
        }

    @cached_property
    def credit_report(self):
        def get_value(label, key, item):
            if label == "total":
                return item[key]
            if item[key] is None:
                return "DNQ"
            return item[key]

        table = [
            (
                label.replace("_", " ").capitalize(),
                get_value(label, "eligible", item),
                get_value(label, "achieved", item),
            )
            for label, item in self.credit_data.items()
        ]
        return tabulate(table, headers=["Savings Category", "Eligible Credits", "Achieved credits"])
