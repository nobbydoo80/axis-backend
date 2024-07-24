"""attributes.py - Axis"""

__author__ = "Steven K"
__date__ = "8/25/21 12:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.customer_eto.eep_programs.eto_2022 import SolarElements2022
from axis.customer_eto.eep_programs.washington_code_credit import WACCFuelType
from axis.customer_eto.enumerations import YesNo, SolarElements2020
from .base import BaseXMLSerializer

log = logging.getLogger(__name__)


class ProjectAttributeSerializer(BaseXMLSerializer):
    def to_representation_default(self, instance) -> list:
        subdivision = None
        if instance.home_status.home.subdivision:
            subdivision = instance.home_status.home.subdivision.name

        data = [
            ("ANNUALCOSTELEC", self.context.get("annual_cost_electric", 0.0)),
            ("ANNUALCOSTGAS", self.context.get("annual_cost_gas", 0.0)),
            ("CARBONSCORE", self.context.get("carbon_score", 0.0)),
            ("CRBNSCCODE", self.context.get("code_carbon_score", 0.0)),
            ("CARBONSIMILAR", self.context.get("code_carbon_similar", 0.0)),
            ("DVLPMNTNMED", subdivision),
            ("ETOPATH", self.context.get("eto_path")),
            ("HOMECONFIG", self.context.get("home_config")),
            ("EPSCODE", self.context.get("code_eps_score", 0.0)),
            ("EPSSMILIARHOME", self.context.get("eps_similar", 0.0)),
            ("ESTANNKWH", self.context.get("total_kwh", 0.0)),
            ("ESTANNTHERM", self.context.get("total_therms", 0.0)),
            ("ESTAVGENCOST", self.context.get("estimated_annual_cost", 0.0)),
            ("FINALSCORE", self.context.get("eps_score", 0.0)),
            ("MONTHAVG", self.context.get("estimated_monthly_cost", 0.0)),
            (
                "PCTIMPROV",
                "{:.1f}".format(self.context.get("percentage_improvement", 0.0)),
            ),
        ]

        if self.context.get("fire_rebuild_qualification") in [
            YesNo.YES.value,
            YesNo.YES,
        ]:
            data.append(("RESDISASTER", "20WF"))

        elements = self.context.get("solar_elements")
        if elements:
            solar = "NO"
            if elements in [
                SolarElements2022.SOLAR_PV.value,
                SolarElements2022.SOLAR_PV,
                SolarElements2022.NET_ZERO.value,
                SolarElements2022.NET_ZERO,
            ]:
                solar = "SOLARPV"
            elif elements in [
                SolarElements2022.SOLAR_READY.value,
                SolarElements2022.SOLAR_READY,
            ]:
                solar = "SRPV"
            data.append(("PROJSOLAR", solar))

        return data

    def to_representation_washington_code_credit(self, instance):
        subdivision = None
        if instance.home_status.home.subdivision:
            subdivision = instance.home_status.home.subdivision.name

        home_config = "Gas Heat - Gas DHW"
        if self.context["water_heater_fuel"] == WACCFuelType.ELECTRIC.value:
            home_config = "Gas Heat - Ele DHW"

        return [
            ("DVLPMNTNMED", subdivision),
            ("HOMECONFIG", home_config),
            ("ESTANNKWH", self.context.get("total_kwh", 0.0)),
            ("ESTANNTHERM", self.context.get("total_therms", 0.0)),
        ]

    def to_representation(self, instance):
        data = super(ProjectAttributeSerializer, self).to_representation(instance)
        return {
            "Attributes": {"Attribute": [{"Name": name, "Value": value} for (name, value) in data]}
        }
