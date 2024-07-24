"""2015_whole_house_remodel.py: """

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

from axis.customer_hirl.models import HIRLProject, HIRLProjectRegistration
from .base import (
    BaseScoringExtraction,
    ScoringExtractionRequirementsFailed,
    ScoringExtractionVersionNotSupported,
    BatchSubmissionCellConfig,
    SamplingConfig,
)


class WholeHouseRemodel2015ScoringExtractionSerializer(serializers.Serializer):
    year_built = serializers.CharField(required=False, allow_blank=True)
    project_description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class WholeHouseRemodel2015ScoringExtraction(BaseScoringExtraction):
    key = "new-2015-whole-house-remodel-scoring-extraction"
    display = "2015 SF/MF Renovation"

    @cached_property
    def rough_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("3.1.4"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="G104:G123",
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
        if version.parse(self.sheet_version) < version.parse("3.1.4"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="H104:H123",
                inspection_date_cell_range="I104:I123",
                sheet="Final Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H84:H133",
            inspection_date_cell_range="I84:I133",
            sheet="Final Summary",
        )

    @cached_property
    def rough_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("3.1.4"):
            return SamplingConfig(
                sheet_name="Rough Sig.",
                total_available_cell="D169",
                total_inspected_cell="E169",
                error_cell="C169",
            )
        elif version.parse(self.sheet_version) < version.parse("3.1.5"):
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
        if version.parse(self.sheet_version) < version.parse("3.1.4"):
            return SamplingConfig(
                sheet_name="Final Sig.",
                total_available_cell="D169",
                total_inspected_cell="E169",
                error_cell="C169",
            )
        elif version.parse(self.sheet_version) < version.parse("3.1.5"):
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

    available_destinations = []

    annotation_data_serializer_class = WholeHouseRemodel2015ScoringExtractionSerializer

    def get_project_id(self):
        ws = self.workbook["Overview (Verification)"]
        hirl_project_id = ws["J61"].value
        return self._clean_str(hirl_project_id)

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("3.1.4"):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P20",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P25",
                },
            }
        elif version.parse("3.0.1") <= version.parse(self.sheet_version) <= version.parse("3.1.3"):
            cell_map = {
                self.to_annotation_name("year-built"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P20",
                },
                self.to_annotation_name("project-description"): {
                    "sheet": "Overview (Verification)",
                    "cell": "P25",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)

        return cell_map

    def validate_wri(self):
        pass

    def validate_sampling(self):
        if version.parse(self.sheet_version) < version.parse("3.1.5"):
            if (
                self.project.registration.project_type
                != HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            ):
                return
        super().validate_sampling()
