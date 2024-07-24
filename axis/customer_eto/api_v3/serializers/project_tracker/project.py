"""base.py - Axis"""

__author__ = "Steven K"
__date__ = "8/21/21 13:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from rest_framework import serializers

from ....enumerations import YesNo
from ....models import FastTrackSubmission

from .attributes import ProjectAttributeSerializer
from .measures import MeasureSerializer

log = logging.getLogger(__name__)


class ProjectSerializer(serializers.ModelSerializer):
    attributes = ProjectAttributeSerializer(source="*", read_only=True)
    measures = MeasureSerializer(source="*", read_only=True)

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = ("id", "attributes", "measures")
        read_only_fields = ("id", "attributes", "measures")
        ref_name = "AxisProjectTrackerProjectSerializer"

    def _get_base_subtype(self) -> str | None:
        """Get the subtype based on fuel"""
        electric_territory = self.context.get("electric_utility_code") in ["PGE", "PAC"]
        gas_territory = self.context.get("gas_utility_code") in ["AVI", "CNG", "NWN"]
        home_config = self.context.get("home_config")

        if electric_territory and not gas_territory:
            if home_config == "Gas Heat - Gas DHW":
                return  # "11ET-GG"
            if home_config == "Ele Heat - Ele DHW":
                return "9ET-EE"
            if home_config == "Ele Heat - Gas DHW":
                return "10ET-EG"
            if home_config == "Gas Heat - Ele DHW":
                return  # "8ET-GE"
        if electric_territory and gas_territory:
            if home_config == "Gas Heat - Gas DHW":
                return "1FT-GG"
            if home_config == "Ele Heat - Ele DHW":
                return "3FT-EE"
            if home_config == "Ele Heat - Gas DHW":
                return "4FT-EG"
            if home_config == "Gas Heat - Ele DHW":
                return "2FT-GE"
        if not electric_territory and gas_territory:
            if home_config == "Gas Heat - Gas DHW":
                return "5GT-GG"
            if home_config == "Ele Heat - Ele DHW":
                return  # "N/A"
            if home_config == "Ele Heat - Gas DHW":
                return  # "7GT-EG"
            if home_config == "Gas Heat - Ele DHW":
                return "6GT-GE"

    def to_representation(self, instance: FastTrackSubmission) -> dict:
        data = super(ProjectSerializer, self).to_representation(instance)

        sub_type = self._get_base_subtype()
        if instance.home_status.home.state == "WA":
            sub_type = "WAEPS"

        p_type = "WHH"
        track = "T00000000099"
        phase = "PENDING"
        attributes = data["attributes"]["Attributes"]

        notes = []
        if self.context.get("fire_rebuild_qualification") in [YesNo.YES.value, YesNo.YES]:
            notes.append("Fire Rebuild")
        if self.context.get("payment_redirected") in [YesNo.YES.value, YesNo.YES]:
            notes.append("Payment Redirect")

        if self.context.get("project_type", "ENH") == "SLE":
            p_type = "SLERES"
            track = "T00000000189"
            phase = "PAYMENT"
            sub_type = "ENH"
            attributes = ""
            notes = []

        title = instance.home_status.home.get_home_address_display(
            include_lot_number=False, raw=True
        )

        cert_date = instance.home_status.certification_date or datetime.datetime.today()

        data = {
            "@ID": str(instance.home_status.id),
            "Program": self.context.get("project_type", "ENH"),
            "Track": track,
            "Type": p_type,
            "SubType": sub_type,
            "Title": title,
            "Status": "Active",
            "Phase": phase,
            "StartDate": str(cert_date),
            "Notes": ", ".join(notes),
            "ExternalReferences": {
                "ExternalReference": [
                    {"Type": "0041", "Value": str(instance.home_status.id)},
                    {"Type": "0040", "Value": "1732596E"},
                ]
            },
            "Attributes": attributes,
            "Measures": data["measures"]["Measures"],
        }
        for key in ["Type", "SubType"]:
            if data.get(key) is None:
                data.pop(key)
        return data
