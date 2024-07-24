"""2020_new_construction.py: """

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


class NewConstruction2020Scoring514ExtractionSerializer(serializers.Serializer):
    """
    Validation serializer for spreadsheet 5.1.4 to 5.2.4
    """

    energy_path = serializers.CharField(required=True, label="Energy Path")
    water_path = serializers.CharField(required=True, label="Water Path")
    performance_path_percent_above = serializers.CharField(
        allow_blank=True, required=False, label="Performance Path % Above"
    )
    alternative_bronze_and_silver_level_compliance = serializers.CharField(
        allow_blank=True,
        required=False,
        label="Alternative Bronze and Silver Level Compliance Option",
    )
    epa_national_eri_target = serializers.CharField(
        allow_blank=True, required=False, label="EPA National ERI Target"
    )
    eri_as_designed = serializers.CharField(
        allow_blank=True, required=False, label="ERI As Designed"
    )
    wri_score = serializers.CharField(required=False, allow_blank=True, label="WRI Score")

    ach50 = serializers.CharField(allow_blank=True, required=False, label="ACH50")
    elr50 = serializers.CharField(allow_blank=True, required=False, label="ELR50")

    badge_resilience = serializers.CharField(required=False, label="Badge: Resilience")
    badge_smart_home = serializers.CharField(required=False, label="Badge: Smart Home")
    badge_universal_design = serializers.CharField(required=False, label="Badge: Universal Design")
    badge_wellness = serializers.CharField(required=False, label="Badge: Wellness")
    badge_zero_water = serializers.CharField(required=False, label="Badge: Zero Water")

    def validate(self, attrs):
        required_fields = []
        energy_path = attrs["energy_path"]
        water_path = attrs["water_path"]
        data_type = self.context.get("data_type")

        if data_type == BaseScoringExtraction.FINAL_DATA_TYPE:
            if energy_path == "Alt. Bronze or Silver":
                required_fields += [
                    "alternative_bronze_and_silver_level_compliance",
                ]
            elif energy_path == "Performance path":
                required_fields += [
                    "performance_path_percent_above",
                ]
            elif energy_path == "ERI Target":
                required_fields += [
                    "epa_national_eri_target",
                    "eri_as_designed",
                ]

            if water_path == "Performance Path":
                required_fields += [
                    "wri_score",
                ]

        for required_field_name in required_fields:
            if not attrs.get(required_field_name):
                raise serializers.ValidationError(
                    {
                        required_field_name: [
                            "This field is required",
                        ]
                    }
                )

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NewConstruction2020Scoring525ExtractionSerializer(
    NewConstruction2020Scoring514ExtractionSerializer
):
    """
    Validation serializer for spreadsheet 5.2.5 and higher
    """

    duct_testing = serializers.CharField(required=False, allow_blank=True, label="Duct Testing")

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NewConstruction2020Scoring503ExtractionSerializer(serializers.Serializer):
    """
    Validation serializer for spreadsheet 5.0.3 and higher
    """

    energy_path = serializers.CharField(required=True, label="Energy Path")
    water_path = serializers.CharField(required=True, label="Water Path")
    performance_path_percent_above = serializers.CharField(
        allow_blank=True, required=False, label="Performance Path % Above"
    )
    alternative_bronze_and_silver_level_compliance = serializers.CharField(
        allow_blank=True,
        required=False,
        label="Alternative Bronze and Silver Level Compliance Option",
    )
    epa_national_eri_target = serializers.CharField(
        allow_blank=True, required=False, label="EPA National ERI Target"
    )
    eri_as_designed = serializers.CharField(
        allow_blank=True, required=False, label="ERI As Designed"
    )
    wri_score = serializers.CharField(required=False, allow_blank=True, label="WRI Score")

    def validate(self, attrs):
        required_fields = []
        energy_path = attrs["energy_path"]
        water_path = attrs["water_path"]
        data_type = self.context.get("data_type")

        if data_type == BaseScoringExtraction.FINAL_DATA_TYPE:
            if energy_path == "Alt. Bronze or Silver":
                required_fields += [
                    "alternative_bronze_and_silver_level_compliance",
                ]
            elif energy_path == "Performance path":
                required_fields += [
                    "performance_path_percent_above",
                ]
            elif energy_path == "ERI Target":
                required_fields += [
                    "eri_as_designed",
                ]

            if water_path == "Performance Path":
                required_fields += [
                    "wri_score",
                ]

        for required_field_name in required_fields:
            if not attrs.get(required_field_name):
                raise serializers.ValidationError(
                    {
                        required_field_name: [
                            "This field is required",
                        ]
                    }
                )

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NewConstruction2020Scoring500ExtractionSerializer(serializers.Serializer):
    """
    Validation serializer for spreadsheet 5.0.0 and higher
    """

    energy_path = serializers.CharField(required=True, label="Energy Path")
    water_path = serializers.CharField(required=True, label="Water Path")
    performance_path_percent_above = serializers.CharField(
        allow_blank=True, required=False, label="Performance Path % Above"
    )
    alternative_bronze_and_silver_level_compliance = serializers.CharField(
        allow_blank=True,
        required=False,
        label="Alternative Bronze and Silver Level Compliance Option",
    )
    eri_score_percent_less_than_energy_star = serializers.CharField(
        allow_blank=True, required=False, label="ERI Score Percent Less than ENERGY STAR"
    )
    wri_score = serializers.CharField(allow_blank=True, required=False, label="WRI Score")

    def validate(self, attrs):
        required_fields = []
        energy_path = attrs["energy_path"]
        water_path = attrs["water_path"]
        data_type = self.context.get("data_type")

        if data_type == BaseScoringExtraction.FINAL_DATA_TYPE:
            if energy_path == "Alt. Bronze or Silver":
                required_fields += [
                    "alternative_bronze_and_silver_level_compliance",
                ]
            elif energy_path == "Performance path":
                required_fields += [
                    "performance_path_percent_above",
                ]
            elif energy_path == "ERI Target":
                required_fields += [
                    "eri_score_percent_less_than_energy_star",
                ]

            if water_path == "Performance Path":
                required_fields += [
                    "wri_score",
                ]

        for required_field_name in required_fields:
            if not attrs.get(required_field_name):
                raise serializers.ValidationError(
                    {
                        required_field_name: [
                            "This field is required",
                        ]
                    }
                )

        return attrs

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class NewConstruction2020ScoringExtraction(BaseScoringExtraction):
    key = "new-construction2020-scoring-extraction"
    display = "2020 SF/MF New Construction"

    @cached_property
    def rough_submission_project_id_config(self):
        if version.parse(self.sheet_version) < version.parse("5.2.7"):
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
        if version.parse(self.sheet_version) < version.parse("5.2.7"):
            return BatchSubmissionCellConfig(
                project_id_cell_range="H105:H124",
                inspection_date_cell_range="J105:J124",
                sheet="Final Sig.",
            )
        return BatchSubmissionCellConfig(
            project_id_cell_range="H87:H136",
            inspection_date_cell_range="J87:J136",
            sheet="Final Summary",
        )

    @cached_property
    def rough_sampling_config(self):
        if version.parse(self.sheet_version) < version.parse("5.2.7"):
            return SamplingConfig(
                sheet_name="Rough Sig.",
                total_available_cell="D170",
                total_inspected_cell="E170",
                error_cell="C170",
            )
        elif version.parse(self.sheet_version) < version.parse("5.2.14"):
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
        if version.parse(self.sheet_version) < version.parse("5.2.7"):
            return SamplingConfig(
                sheet_name="Final Sig.",
                total_available_cell="D170",
                total_inspected_cell="E170",
                error_cell="C170",
            )
        elif version.parse(self.sheet_version) < version.parse("5.2.14"):
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
        if version.parse("5.0.0") <= version.parse(self.sheet_version) <= version.parse("5.0.2"):
            return NewConstruction2020Scoring500ExtractionSerializer
        elif version.parse("5.0.2") < version.parse(self.sheet_version) <= version.parse("5.1.3"):
            return NewConstruction2020Scoring503ExtractionSerializer
        elif version.parse("5.2.1") <= version.parse(self.sheet_version) <= version.parse("5.2.4"):
            return NewConstruction2020Scoring514ExtractionSerializer
        return NewConstruction2020Scoring525ExtractionSerializer

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("5.2.5"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1055",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W898",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1417",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W1419",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1642",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "W1868",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W975",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W978",
                },
                self.to_annotation_name("duct-testing"): {
                    "sheet": "Verification Report",
                    "cell": "W1086" if self.data_type == self.ROUGH_DATA_TYPE else "W1088",
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
        elif version.parse("5.2.1") <= version.parse(self.sheet_version) <= version.parse("5.2.4"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1055",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W898",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1414",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W1416",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1639",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "W1865",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W975",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W978",
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
        elif version.parse("5.1.4") <= version.parse(self.sheet_version) <= version.parse("5.1.5"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1053",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W898",
                },
                self.to_annotation_name("eri-score-percent-less-than-energy-star"): {
                    "sheet": "Verification Report",
                    "cell": "W1409",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1412",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W1414",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1637",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "W1863",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W973",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W976",
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
        elif version.parse("5.0.6") <= version.parse(self.sheet_version) <= version.parse("5.1.3"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1052",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W897",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1411",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W1413",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1636",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "W1862",
                },
                self.to_annotation_name("ach50"): {
                    "sheet": "Verification Report",
                    "cell": "W972",
                },
                self.to_annotation_name("elr50"): {
                    "sheet": "Verification Report",
                    "cell": "W975",
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
        elif version.parse(self.sheet_version) == version.parse("5.0.4"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1050",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W895",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1409",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W1411",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1634",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "X26",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("5.0.3"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1050",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W895",
                },
                self.to_annotation_name("epa-national-eri-target"): {
                    "sheet": "Verification Report",
                    "cell": "W1409",
                },
                self.to_annotation_name("eri-as-designed"): {
                    "sheet": "Verification Report",
                    "cell": "W1411",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1634",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "X26",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("5.0.2"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1050",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W895",
                },
                self.to_annotation_name("eri-score-percent-less-than-energy-star"): {
                    "sheet": "Verification Report",
                    "cell": "W1409",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1634",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "X26",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("5.0.1"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W882",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1050",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W895",
                },
                self.to_annotation_name("eri-score-percent-less-than-energy-star"): {
                    "sheet": "Verification Report",
                    "cell": "W1409",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1634",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "X26",
                },
            }
        elif version.parse(self.sheet_version) == version.parse("5.0.0"):
            cell_map = {
                self.to_annotation_name("energy-path"): {
                    "sheet": "Verification Report",
                    "cell": "W872",
                },
                self.to_annotation_name("performance-path-percent-above"): {
                    "sheet": "Verification Report",
                    "cell": "W1038",
                },
                self.to_annotation_name("alternative-bronze-and-silver-level-compliance"): {
                    "sheet": "Verification Report",
                    "cell": "W883",
                },
                self.to_annotation_name("eri-score-percent-less-than-energy-star"): {
                    "sheet": "Verification Report",
                    "cell": "W1397",
                },
                self.to_annotation_name("water-path"): {
                    "sheet": "Verification Report",
                    "cell": "W1624",
                },
                self.to_annotation_name("wri-score"): {
                    "sheet": "Verification Report",
                    "cell": "X26",
                },
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)
        return cell_map

    def validate_sampling(self):
        if version.parse(self.sheet_version) < version.parse("5.2.14"):
            if (
                self.project.registration.project_type
                != HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
            ):
                return
        super().validate_sampling()
