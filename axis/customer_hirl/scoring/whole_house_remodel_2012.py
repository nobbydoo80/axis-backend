"""2012_whole_house_remodel.py: """

__author__ = "Artem Hruzd"
__date__ = "06/19/2020 18:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.utils.functional import cached_property
from packaging import version
from rest_framework import serializers

from axis.customer_hirl.models import HIRLProject
from .base import (
    BaseScoringExtraction,
    ScoringExtractionRequirementsFailed,
    ScoringExtractionVersionNotSupported,
    ScoringExtractionUnknownVersion,
)


class WholeHouseRemodel2012ScoringExtractionSerializer(serializers.Serializer):
    energy_percent_reduction = serializers.CharField(
        required=False, allow_blank=True, label="Energy Percent Reduction"
    )
    water_percent_reduction = serializers.CharField(
        allow_blank=True, required=False, label="Water Percent Reduction"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class WholeHouseRemodel2012ScoringExtraction(BaseScoringExtraction):
    key = "new-2012-whole-house-remodel-scoring-extraction"
    display = "2012 SF/MF Renovation"

    available_destinations = []

    annotation_data_serializer_class = WholeHouseRemodel2012ScoringExtractionSerializer

    @cached_property
    def sheet_version(self):
        ws = self.workbook["Start Here!"]
        sheet_version = ws["C6"].value

        if sheet_version:
            self.app_log.info("Detect version .xlsx {}".format(sheet_version))
        else:
            raise ScoringExtractionUnknownVersion
        return str(sheet_version).replace("R", "")

    def get_project_id(self):
        ws = self.workbook["Verification Rpt"]
        hirl_project_id = ws["F8"].value
        return self._clean_str(hirl_project_id)

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("2.5.3"):
            cell_map = {
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Rpt",
                    "cell": "H371",
                },
                self.to_annotation_name("water-percent-reduction"): {
                    "sheet": "Verification Rpt",
                    "cell": "G466",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)

        return cell_map

    def validate_batch_submission(self):
        pass

    def batch_submission(self):
        self.app_log.info("Batch submission not supported")

    def validate_sampling(self):
        self.app_log.info("Sampling is not supported")

    def validate_wri(self):
        pass
