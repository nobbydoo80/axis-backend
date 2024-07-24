"""2012_new_construction.py: """

__author__ = "Artem Hruzd"
__date__ = "06/19/2020 18:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.urls import reverse_lazy
from django.utils.functional import cached_property
from packaging import version
from rest_framework import serializers

from .base import (
    BaseScoringExtraction,
    ScoringExtractionVersionNotSupported,
    ScoringExtractionUnknownVersion,
    BatchSubmissionCellConfig,
)
from ..messages import HIRLScoringUploadFinalOutstandingFeeBalanceMessage


class NewConstruction2012ScoringExtractionSerializer(serializers.Serializer):
    energy_path = serializers.CharField(required=False, allow_blank=True, label="Energy Path")
    performance_path_percent_above = serializers.CharField(
        allow_blank=True, required=False, label="Performance Path % Above"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NewConstruction2012ScoringExtraction(BaseScoringExtraction):
    key = "new-construction2012-scoring-extraction"
    display = "2012 SF/MF New Construction"

    available_destinations = [
        "ProjectID",
    ]

    rough_submission_project_id_config = BatchSubmissionCellConfig(
        project_id_cell_range="H65:H84",
        inspection_date_cell_range="I65:I84",
        sheet="Rough Signature",
    )
    final_submission_project_id_config = BatchSubmissionCellConfig(
        project_id_cell_range="H68:H87",
        inspection_date_cell_range="I68:I87",
        sheet="Final Signature",
    )

    annotation_data_serializer_class = NewConstruction2012ScoringExtractionSerializer

    @cached_property
    def sheet_version(self):
        ws = self.workbook["Start Here!"]
        sheet_version = ws["C6"].value

        if sheet_version:
            self.app_log.info("Detect version .xlsx {}".format(sheet_version))
        else:
            raise ScoringExtractionUnknownVersion
        return str(sheet_version)

    def get_project_id(self):
        hirl_project_id = self.destinations["ProjectID"]
        return self._clean_str(hirl_project_id)

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("2.5.3"):
            cell_map = {
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Rpt",
                    "cell": "H331",
                },
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Rpt",
                    "cell": "J363",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)

        return cell_map

    def validate_sampling(self):
        self.app_log.info("Sampling is not supported")

    def finalize_upload(self):
        if self.data_type == self.FINAL_DATA_TYPE:
            verification_report_requires_message = (
                f"<p>The Verification Report requires the "
                f"upload of the following additional collateral:</p>"
                f"<p><strong>- At least one Front Elevation photo</strong></p>"
            )

            if (
                self.validated_annotation_data.get(
                    self.to_annotation_name("performance-path-percent-above")
                )
                != "Prescriptive Path"
            ):
                verification_report_requires_message += (
                    f"<p><strong>- An Energy Analysis Document</strong></p>"
                )

            self.app_log.info(
                verification_report_requires_message,
            )

            if self.project.fee_current_balance > 0:
                HIRLScoringUploadFinalOutstandingFeeBalanceMessage().send(
                    company=self.customer_hirl_provider_organization,
                    context={
                        "project_url": self.project.get_absolute_url(),
                        "project_id": self.project.id,
                        "home_url": reverse_lazy(
                            "home:view", kwargs={"pk": self.project.home_status.home.pk}
                        ),
                        "home_address": self.project.home_status.home.get_home_address_display(),
                    },
                )

        self.app_log.info(
            f'<a href="{self.project.home_status.get_absolute_url()}'
            f'#/tabs/documents">Document created</a>'
            f"<p><h3><a href='{self.project.home_status.get_absolute_url()}#/tabs/qa'>"
            f"Click here to upload photos and additional documentation</a></h3></p>"
        )
