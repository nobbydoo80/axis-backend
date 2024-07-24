"""core.py - Axis"""

__author__ = "Steven K"
__date__ = "8/25/21 11:16"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from django.conf import settings
from rest_framework import serializers

from .project import ProjectSerializer
from .site import SiteSerializer
from .trade_ally import TradeAllySerializer
from ....models import FastTrackSubmission

log = logging.getLogger(__name__)


class ProjectTrackerXMLSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(source="*", read_only=False)
    site = SiteSerializer(source="*", read_only=True)
    trade_allies = TradeAllySerializer(source="*", read_only=True)

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = ("id", "project", "site", "trade_allies")
        read_only_fields = ("id", "project", "site", "trade_allies")

    def to_representation(self, instance):
        data = super(ProjectTrackerXMLSerializer, self).to_representation(instance)

        project = data["project"]

        builder_measures, verifier_measures = [], []
        site = data["site"]
        for measure in project["Measures"]["Measure"]:
            site["Associations"]["Projects"]["Project"]["Measures"]["Measure"].append(
                {"@ID": measure["@ID"]}
            )
            if (
                measure["Code"]
                in [
                    "EPSENHELE",
                    "EPSENHGAS",
                    "DEIBONUSBUILDER",
                    "EPSESH",
                    "EPSNZ",
                    "WACODECREDT",
                    "EPSFRELE",
                    "EPSFRGAS",
                    "EPSFRFRTW",
                    "EPSFRFREI",
                    "EPSFRFRSA",
                ]
                or measure.get("trade_ally") == "BUILDER"
            ):
                builder_measures.append(measure["@ID"])
            if measure["Code"] in [
                "CUSTEPSVERFELE",
                "CUSTEPSVERFGAS",
                "DEIBONUSVERIFIER",
            ] or measure.get("trade_ally") in ["VERIFIER", "SOINSP"]:
                verifier_measures.append(measure["@ID"])
            measure.pop("trade_ally", None)

        trade_allies = data["trade_allies"]
        for trade_ally in trade_allies:
            if trade_ally["Associations"]["Projects"]["Project"]["Role"] == "BUILDER":
                for measure_id in builder_measures:
                    trade_ally["Associations"]["Projects"]["Project"]["Measures"]["Measure"].append(
                        {"@ID": measure_id}
                    )
            if trade_ally["Associations"]["Projects"]["Project"]["Role"] in [
                "VERIFIER",
                "SOINSP",
            ]:
                for measure_id in verifier_measures:
                    trade_ally["Associations"]["Projects"]["Project"]["Measures"]["Measure"].append(
                        {"@ID": measure_id}
                    )

        # print(f"{builder_measures=}")
        # print(f"{verifier_measures=}")

        return {
            "soap:Envelope": {
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "soap:Body": {
                    "FTImportXML": {
                        "@xmlns": "http://tempuri.org/",
                        "xmlIn": {
                            "ETOImport": {
                                "@xmlns": "",
                                "ImportCode": settings.FASTTRACK_IMPORT_CODE,
                                "APIKey": settings.FASTTRACK_API_KEY,
                                "Project": project,
                                "Site": site,
                                "TradeAlly": trade_allies,
                            }
                        },
                    }
                },
            }
        }


class ProjectTrackerSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    submit_user_info = serializers.SerializerMethodField()
    home_id = serializers.IntegerField(source="home_status.home_id")
    project_id = serializers.CharField(source="get_project_id")
    solar_project_id = serializers.CharField(source="get_solar_project_id")
    overall_submission_status = serializers.SerializerMethodField()

    class Meta:
        """Meta Options"""

        model = FastTrackSubmission
        fields = (
            "id",
            "address",
            "project_id",
            "solar_project_id",
            "submit_user",
            "submit_status",
            "solar_submit_status",
            "overall_submission_status",
            "created_date",
            "modified_date",
            "submission_count",
            "submit_user_info",
            "home_id",
        )

    def get_address(self, instance: FastTrackSubmission) -> str:
        address = instance.home_status.home.get_home_address_display(
            include_city_state_zip=True, raw=True, include_lot_number=False
        )
        return address

    def get_overall_submission_status(self, instance: FastTrackSubmission) -> str:
        project_types = instance.get_project_types()
        status = {}
        if "ENH" in project_types:
            status["ENH"] = f"{instance.get_submit_status_display() or 'Not Submitted'}"
        if "SLE" in project_types:
            status["SLE"] = f"{instance.get_solar_submit_status_display() or 'Not Submitted'}"
        if len(project_types) == 1:
            return str(list(status.values())[0])
        return ", ".join([f"{k}: {v}" for k, v in status.items()])

    def get_submit_user_info(self, fast_track_submission: FastTrackSubmission):
        from axis.core.api_v3.serializers.user import UserInfoSerializer

        return UserInfoSerializer(instance=fast_track_submission.submit_user).data
