"""2015_new_construction.py: """

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

from .base import (
    BaseScoringExtraction,
    ScoringExtractionVersionNotSupported,
    BatchSubmissionCellConfig,
    SamplingConfig,
)
from ..models import HIRLProjectRegistration


class NewConstruction2015ScoringExtractionSerializer(serializers.Serializer):
    energy_path = serializers.CharField(required=True, label="Energy Path")
    performance_path_percent_above = serializers.CharField(
        allow_blank=True, required=False, label="Performance Path % Above"
    )
    hers_index_percent_less_than_energy_star = serializers.CharField(
        allow_blank=True, required=False, label="HERS Index Percent less than ENERGY STAR"
    )

    energy_star_hers_index_target = serializers.CharField(
        allow_blank=True, required=False, label="ENERGY STAR HERS Index Target"
    )
    as_designed_home_hers = serializers.CharField(
        allow_blank=True, required=False, label="As Designed Home HERS"
    )
    ach50 = serializers.CharField(allow_blank=True, required=False, label="ACH50")
    elr50 = serializers.CharField(allow_blank=True, required=False, label="ELR50")

    def validate(self, attrs):
        energy_path = attrs["energy_path"]
        data_type = self.context.get("data_type")
        if data_type == BaseScoringExtraction.FINAL_DATA_TYPE:
            if energy_path == "Performance Path":
                if not attrs.get("performance_path_percent_above"):
                    raise serializers.ValidationError(
                        {"performance_path_percent_above": "This field is required"}
                    )

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NewConstruction2015ScoringExtraction(BaseScoringExtraction):
    key = "new-construction2015-scoring-extraction"
    display = "2015 SF/MF New Construction"

    @cached_property
    def rough_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("4.2.5"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="G104:G124",
                inspection_date_cell_range="H104:H123",
                sheet="Rough Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H84:H133",
            inspection_date_cell_range="I84:I133",
            sheet="Rough Summary",
        )

    @cached_property
    def final_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("4.2.5"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="H104:H123",
                inspection_date_cell_range="I104:I124",
                sheet="Final Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H84:H133",
            inspection_date_cell_range="I84:I133",
            sheet="Final Summary",
        )

    @cached_property
    def rough_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("4.2.5"):
            return SamplingConfig(
                sheet_name="Rough Sig.",
                total_available_cell="D169",
                total_inspected_cell="E169",
                error_cell="C169",
            )
        elif version.parse(self.sheet_version) < version.parse("4.2.8"):
            return SamplingConfig(
                sheet_name="Rough Summary",
                total_available_cell="D175",
                total_inspected_cell="E175",
                error_cell="C175",
            )
        return SamplingConfig(
            sheet_name="Rough Summary",
            total_available_cell="D177",
            total_inspected_cell="E177",
            error_cell="C177",
        )

    @cached_property
    def final_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("4.2.5"):
            return SamplingConfig(
                sheet_name="Final Sig.",
                total_available_cell="D169",
                total_inspected_cell="E169",
                error_cell="C169",
            )
        elif version.parse(self.sheet_version) < version.parse("4.2.8"):
            return SamplingConfig(
                sheet_name="Final Summary",
                total_available_cell="D175",
                total_inspected_cell="E175",
                error_cell="C175",
            )
        return SamplingConfig(
            sheet_name="Final Summary",
            total_available_cell="D177",
            total_inspected_cell="E177",
            error_cell="C177",
        )

    annotation_data_serializer_class = NewConstruction2015ScoringExtractionSerializer

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("4.2.5"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W776",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W913",
                },
                self.to_annotation_name("energy-star-hers-index-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1225",
                },
                self.to_annotation_name("as-designed-home-hers"): {
                    "sheet": "Verification Report",
                    "cell": "W1227",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W839",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W842",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("4.2.4"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W776",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W913",
                },
                self.to_annotation_name("energy-star-hers-index-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1225",
                },
                self.to_annotation_name("as-designed-home-hers"): {
                    "sheet": "Verification Report",
                    "cell": "W1227",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W839",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W842",
                },
            }
        elif version.parse("4.2.2") <= version.parse(self.sheet_version) <= version.parse("4.2.3"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W776",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W913",
                },
                self.to_annotation_name("energy-star-hers-index-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1222",
                },
                self.to_annotation_name("as-designed-home-hers"): {
                    "sheet": "Verification Report",
                    "cell": "W1224",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W839",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W842",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("4.2.1"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W776",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W912",
                },
                self.to_annotation_name("energy-star-hers-index-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1221",
                },
                self.to_annotation_name("as-designed-home-hers"): {
                    "sheet": "Verification Report",
                    "cell": "W1223",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W838",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W841",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("4.2.0"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W776",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W910",
                },
                self.to_annotation_name("energy-star-hers-index-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1219",
                },
                self.to_annotation_name("as-designed-home-hers"): {
                    "sheet": "Verification Report",
                    "cell": "W1221",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W836",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W839",
                },
            }
        elif version.parse("4.0.5") <= version.parse(self.sheet_version) <= version.parse("4.1.9"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W775",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W909",
                },
                self.to_annotation_name("hers-index-percent-less-than-energy-star"): {
                    "sheet": "Verification Report",
                    "cell": "W1218",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W835",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W838",
                },
            }
        elif version.parse(self.sheet_version) <= version.parse("4.0.4"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W775",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W909",
                },
                self.to_annotation_name("hers-index-percent-less-than-energy-star"): {
                    "sheet": "Verification Report",
                    "cell": "W1217",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W835",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W838",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)

        return cell_map

    def validate_sampling(self):
        if version.parse(self.sheet_version) < version.parse("4.2.8"):
            if (
                self.project.registration.project_type
                != HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            ):
                return
        super().validate_sampling()
