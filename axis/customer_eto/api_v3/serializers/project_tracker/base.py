"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "8/21/21 13:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import datetime

from rest_framework import serializers

from ....models import FastTrackSubmission

log = logging.getLogger(__name__)


class BaseXMLSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = ("id",)
        read_only_fields = ("id",)

    def to_internal_value(self, data):
        raise NotImplementedError("Only output supported")

    def add_measure_element(
        self,
        code,
        qty: int = 1,
        cost: int | float = 0,
        incentive: int | float | None = 0.0,
        life: int | float | None = None,
        savings_kwh: int | float | None = None,
        savings_therm: int | float | None = None,
        install_date: datetime.date = datetime.date.today(),
        electric_load_profile: str | None = None,
        gas_load_profile: str | None = None,
        trade_ally: str | None = None,
        **attrs,
    ):
        data = {
            "@ID": None,
            "Code": code,
            "Quantity": qty,
            "InstallDate": install_date.strftime("%Y-%m-%d"),
            "Cost": cost,
            "Incentive": f"{incentive:.2f}",
        }

        if life is not None:
            data["Life"] = life

        if savings_kwh or savings_therm:
            data["Savings"] = {
                "kwh": int(round(savings_kwh, 0)) if savings_kwh else 0,
                "Therm": int(round(savings_therm, 0)) if savings_therm else 0,
            }

        if electric_load_profile or gas_load_profile:
            data["LoadProfile"] = {}
            if electric_load_profile:
                data["LoadProfile"]["kwh"] = electric_load_profile
            if gas_load_profile:
                data["LoadProfile"]["Therm"] = gas_load_profile

        if trade_ally:
            data["trade_ally"] = trade_ally

        if attrs:
            data["Attributes"] = {"Attribute": [{"Name": k, "Value": v} for k, v in attrs.items()]}
        return data

    def to_representation_default(self, instance):
        return {"ERROR": "NOT IMPLEMENTED"}

    def to_representation(self, instance):
        program_slug = instance.home_status.eep_program.slug
        program_method = f'to_representation_{program_slug.replace("-", "_")}'
        attrs = getattr(self, program_method, self.to_representation_default)
        return attrs(instance)
