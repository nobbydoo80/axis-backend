"""2020_whole_house_remodel.py: """

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


class WholeHouseRemodel2020Scoring410ExtractionSerializer(serializers.Serializer):
    energy_compliance_path = serializers.CharField(required=True, label="Energy Path")
    water_compliance_path = serializers.CharField(required=True, label="Water Path")

    year_built = serializers.CharField(allow_blank=True, required=False, label="Year Built")
    energy_baseline_year = serializers.CharField(
        allow_blank=True, required=False, label="Energy Baseline Year"
    )
    water_baseline_year = serializers.CharField(
        allow_blank=True, required=False, label="Water Baseline Year"
    )
    project_description = serializers.CharField(
        allow_blank=True, required=False, label="Project Description"
    )
    energy_percent_reduction = serializers.CharField(
        allow_blank=True, required=False, label="Energy Percent Reduction"
    )
    water_percent_reduction = serializers.CharField(
        allow_blank=True, required=False, label="Water Percent Reduction"
    )

    ach50 = serializers.CharField(allow_blank=True, required=False, label="ACH50")
    elr50 = serializers.CharField(allow_blank=True, required=False, label="ELR50")

    badge_resilience = serializers.CharField(required=False, label="Badge: Resilience")
    badge_smart_home = serializers.CharField(required=False, label="Badge: Smart Home")
    badge_universal_design = serializers.CharField(required=False, label="Badge: Universal Design")
    badge_wellness = serializers.CharField(required=False, label="Badge: Wellness")
    # Zero Water is not exists in template
    badge_zero_water = serializers.CharField(
        required=False, allow_blank=True, label="Badge: Zero Water"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class WholeHouseRemodel2020Scoring4112ExtractionSerializer(
    WholeHouseRemodel2020Scoring410ExtractionSerializer
):
    """
    Validation serializer for spreadsheet 4.1.12 and higher
    """

    duct_testing = serializers.CharField(required=False, allow_blank=True, label="Duct Testing")

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class WholeHouseRemodel2020ScoringExtraction(BaseScoringExtraction):
    key = "new-2020-whole-house-remodel-scoring-extraction"
    display = "2020 SF/MF Renovation"

    @cached_property
    def rough_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("4.1.13"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="G105:G124",
                inspection_date_cell_range="H105:H124",
                sheet="Rough Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H87:H136",
            inspection_date_cell_range="I87:I136",
            sheet="Rough Summary",
        )

    @cached_property
    def final_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("4.1.13"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="H105:H124",
                inspection_date_cell_range="I105:I124",
                sheet="Final Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H87:H136",
            inspection_date_cell_range="I87:I136",
            sheet="Final Summary",
        )

    @cached_property
    def rough_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("4.1.13"):
            return SamplingConfig(
                sheet_name="Rough Sig.",
                total_available_cell="D170",
                total_inspected_cell="E170",
                error_cell="C170",
            )
        elif version.parse(self.sheet_version) < version.parse("4.1.21"):
            return SamplingConfig(
                sheet_name="Rough Summary",
                total_available_cell="D178",
                total_inspected_cell="E178",
                error_cell="C178",
            )
        return SamplingConfig(
            sheet_name="Rough Summary",
            total_available_cell="D180",
            total_inspected_cell="E180",
            error_cell="C180",
        )

    @cached_property
    def final_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("4.1.13"):
            return SamplingConfig(
                sheet_name="Final Sig.",
                total_available_cell="D170",
                total_inspected_cell="E170",
                error_cell="C170",
            )
        elif version.parse(self.sheet_version) < version.parse("4.1.21"):
            return SamplingConfig(
                sheet_name="Final Summary",
                total_available_cell="D178",
                total_inspected_cell="E178",
                error_cell="C178",
            )
        return SamplingConfig(
            sheet_name="Final Summary",
            total_available_cell="D180",
            total_inspected_cell="E180",
            error_cell="C180",
        )

    def get_annotation_data_serializer_class(self):
        if version.parse("4.1.0") <= version.parse(self.sheet_version) <= version.parse("4.1.11"):
            return WholeHouseRemodel2020Scoring410ExtractionSerializer
        return WholeHouseRemodel2020Scoring4112ExtractionSerializer

    @cached_property
    def annotations_map(self):
        if version.parse("4.1.12") <= version.parse(self.sheet_version):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P29",
                },
                self.to_annotation_name("energy-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P30",
                },
                self.to_annotation_name("water-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P31",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P32",
                },
                self.to_annotation_name("energy-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P34",
                },
                self.to_annotation_name("water-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P35",
                },
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1023",
                },
                self.to_annotation_name("water-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1622",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W936",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W939",
                },
                self.to_annotation_name("duct-testing"): {
                    "sheet": "Verification Report",
                    "cell": "W1057" if self.data_type == self.ROUGH_DATA_TYPE else "W1059",
                },
                self.to_annotation_name("badge-resilience"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D3",
                },
                self.to_annotation_name("badge-smart-home"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D4",
                },
                self.to_annotation_name("badge-universal-design"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D5",
                },
                self.to_annotation_name("badge-wellness"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D6",
                },
                self.to_annotation_name("badge-zero-water"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D7",
                },
            }
        elif (
            version.parse("4.1.10") <= version.parse(self.sheet_version) <= version.parse("4.1.11")
        ):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P29",
                },
                self.to_annotation_name("energy-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P30",
                },
                self.to_annotation_name("water-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P31",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P32",
                },
                self.to_annotation_name("energy-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P34",
                },
                self.to_annotation_name("water-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P35",
                },
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1023",
                },
                self.to_annotation_name("water-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1619",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W936",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W939",
                },
                self.to_annotation_name("badge-resilience"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D3",
                },
                self.to_annotation_name("badge-smart-home"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D4",
                },
                self.to_annotation_name("badge-universal-design"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D5",
                },
                self.to_annotation_name("badge-wellness"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D6",
                },
                self.to_annotation_name("badge-zero-water"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D7",
                },
            }
        elif version.parse("4.1.5") <= version.parse(self.sheet_version) <= version.parse("4.1.9"):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P29",
                },
                self.to_annotation_name("energy-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P30",
                },
                self.to_annotation_name("water-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P31",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P32",
                },
                self.to_annotation_name("energy-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P34",
                },
                self.to_annotation_name("water-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P35",
                },
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1023",
                },
                self.to_annotation_name("water-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1616",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W936",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W939",
                },
                self.to_annotation_name("badge-resilience"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D3",
                },
                self.to_annotation_name("badge-smart-home"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D4",
                },
                self.to_annotation_name("badge-universal-design"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D5",
                },
                self.to_annotation_name("badge-wellness"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D6",
                },
                self.to_annotation_name("badge-zero-water"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D7",
                },
            }
        elif version.parse("4.1.0") <= version.parse(self.sheet_version) <= version.parse("4.1.4"):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P29",
                },
                self.to_annotation_name("energy-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P30",
                },
                self.to_annotation_name("water-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P31",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P32",
                },
                self.to_annotation_name("energy-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P34",
                },
                self.to_annotation_name("water-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P35",
                },
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1022",
                },
                self.to_annotation_name("water-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1615",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W935",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W938",
                },
                self.to_annotation_name("badge-resilience"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D3",
                },
                self.to_annotation_name("badge-smart-home"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D4",
                },
                self.to_annotation_name("badge-universal-design"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D5",
                },
                self.to_annotation_name("badge-wellness"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D6",
                },
                self.to_annotation_name("badge-zero-water"): {
                    "sheet": "Badges (Verification)",
                    "cell": "D7",
                },
            }
        elif version.parse("4.0.3") <= version.parse(self.sheet_version) <= version.parse("4.0.9"):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P29",
                },
                self.to_annotation_name("energy-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P30",
                },
                self.to_annotation_name("water-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P31",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P32",
                },
                self.to_annotation_name("energy-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P34",
                },
                self.to_annotation_name("water-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P35",
                },
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1020",
                },
                self.to_annotation_name("water-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1613",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W933",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W936",
                },
            }
        elif version.parse("4.0.0") <= version.parse(self.sheet_version) <= version.parse("4.0.2"):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P29",
                },
                self.to_annotation_name("energy-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P30",
                },
                self.to_annotation_name("water-baseline-year"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P31",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P32",
                },
                self.to_annotation_name("energy-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P34",
                },
                self.to_annotation_name("water-compliance-path"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P35",
                },
                self.to_annotation_name("energy-percent-reduction"): {
                    "sheet": "Verification Report",
                    "cell": "W1020",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W933",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W936",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)
        return cell_map

    def validate_wri(self):
        pass

    def validate_sampling(self):
        if version.parse(self.sheet_version) < version.parse("4.1.21"):
            if (
                self.project.registration.project_type
                != HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            ):
                return
        super().validate_sampling()
