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


class Certified2020ScoringExtractionSerializer(serializers.Serializer):
    energy_path = serializers.CharField(required=True, label="Energy Path")
    water_path = serializers.CharField(required=True, label="Water Path")
    total_reference_annual_energy = serializers.CharField(
        allow_blank=True, required=False, label="Total Reference Annual Energy"
    )
    epa_national_eri_target = serializers.CharField(
        allow_blank=True, required=False, label="EPA National ERI Target"
    )
    eri_as_designed = serializers.CharField(
        allow_blank=True, required=False, label="ERI As Designed"
    )
    wri_score = serializers.CharField(allow_blank=True, required=False, label="WRI Score")
    ach50 = serializers.CharField(allow_blank=True, required=False, label="ACH50")
    elr50 = serializers.CharField(allow_blank=True, required=False, label="ELR50")
    total_leakage = serializers.CharField(allow_blank=True, required=False, label="ELR50")

    def validate(self, attrs):
        energy_path = attrs["energy_path"]
        water_path = attrs["water_path"]

        data_type = self.context.get("data_type")
        if data_type == BaseScoringExtraction.FINAL_DATA_TYPE:
            if energy_path == "Performance path":
                if not attrs.get("total_reference_annual_energy"):
                    raise serializers.ValidationError(
                        {"total_reference_annual_energy": "This field is required"}
                    )
            if energy_path == "ERI Path":
                if not attrs.get("epa_national_eri_target"):
                    raise serializers.ValidationError(
                        {"epa_national_eri_target": "This field is required"}
                    )
                if not attrs.get("eri_as_designed"):
                    raise serializers.ValidationError({"eri_as_designed": "This field is required"})
            if energy_path and water_path:
                if not attrs.get("total_reference_annual_energy"):
                    raise serializers.ValidationError(
                        {"total_reference_annual_energy": "This field is required"}
                    )

            if water_path == "Alt. Compliance Path":
                if not attrs.get("wri_score"):
                    raise serializers.ValidationError({"wri_score": "This field is required"})

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class Certified2020ScoringExtraction(BaseScoringExtraction):
    key = "certified2020-scoring-extraction"
    display = "2020 SF Certified"

    @cached_property
    def rough_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("1.0.9"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="H83:H112",
                inspection_date_cell_range="I83:I112",
                sheet="Rough Sig.",
            )

        return BatchSubmissionCellConfig(
            project_id_cell_range="H69:H118",
            inspection_date_cell_range="I69:I118",
            sheet="Rough Summary",
        )

    @cached_property
    def final_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("1.0.9"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="H83:H112",
                inspection_date_cell_range="I83:I112",
                sheet="Final Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H69:H118",
            inspection_date_cell_range="I69:I118",
            sheet="Final Summary",
        )

    @cached_property
    def rough_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("1.0.9"):
            return SamplingConfig(
                sheet_name="Rough Sig.",
                total_available_cell="D170",
                total_inspected_cell="E170",
                error_cell="C170",
            )
        return SamplingConfig(
            sheet_name="Rough Summary",
            total_available_cell="D170",
            total_inspected_cell="E170",
            error_cell="C170",
        )

    @cached_property
    def final_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("1.0.9"):
            return SamplingConfig(
                sheet_name="Final Sig.",
                total_available_cell="D170",
                total_inspected_cell="E170",
                error_cell="C170",
            )
        return SamplingConfig(
            sheet_name="Final Summary",
            total_available_cell="D170",
            total_inspected_cell="E170",
            error_cell="C170",
        )

    annotation_data_serializer_class = Certified2020ScoringExtractionSerializer

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("1.0.4"):
            annotations_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W106",
                },
                self.to_annotation_name("total-reference-annual-energy"): {
                    "sheet": "Verification Report",
                    "cell": "W186",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W226",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W228",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W233",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "W249",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W155",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W158",
                },
                self.to_annotation_name("total-leakage"): {
                    "sheet": "Verification Report",
                    "cell": "W116" if self.data_type == self.ROUGH_DATA_TYPE else "W120",
                },
            }
        elif version.parse("1.0.3") <= version.parse(self.sheet_version) < version.parse("1.0.4"):
            annotations_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W106",
                },
                self.to_annotation_name("total-reference-annual-energy"): {
                    "sheet": "Verification Report",
                    "cell": "W185",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W225",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W227",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W232",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "W248",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W154",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W157",
                },
                self.to_annotation_name("total-leakage"): {
                    "sheet": "Verification Report",
                    "cell": "W115" if self.data_type == self.ROUGH_DATA_TYPE else "W119",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("1.0.0"):
            annotations_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W105",
                },
                self.to_annotation_name("total-reference-annual-energy"): {
                    "sheet": "Verification Report",
                    "cell": "W182",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W222",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W224",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W229",
                },
                self.to_annotation_name("total-leakage"): {
                    "sheet": "Verification Report",
                    "cell": "W112" if self.data_type == self.ROUGH_DATA_TYPE else "W116",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)

        return annotations_map
