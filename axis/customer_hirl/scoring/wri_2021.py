"""2020_wri.py: """

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
)


class WRI2021Scoring109ExtractionSerializer(serializers.Serializer):
    """
    Validation serializer for spreadsheet 1.0.9
    """

    baseline_units = serializers.CharField(required=False, allow_blank=True, label="Baseline Units")
    baseline_common_areas = serializers.CharField(
        required=False, allow_blank=True, label="Baseline Common Areas"
    )
    baseline_indoor_total = serializers.CharField(
        required=False, allow_blank=True, label="Baseline Indoor Total"
    )
    baseline_outdoor = serializers.CharField(
        required=False, allow_blank=True, label="Baseline Outdoor"
    )
    designed_units = serializers.CharField(
        required=False, allow_blank=True, label="Baseline Outdoor"
    )
    designed_common_areas = serializers.CharField(
        required=False, allow_blank=True, label="Designed Units"
    )
    designed_less_indoor_credit = serializers.CharField(
        required=False, allow_blank=True, label="Designed Common Areas"
    )
    designed_outdoor = serializers.CharField(
        required=False, allow_blank=True, label="Designed Outdoor"
    )
    designed_indoor = serializers.CharField(
        required=False, allow_blank=True, label="Designed Indoor"
    )
    designed_indoor_total = serializers.CharField(
        required=False, allow_blank=True, label="Designed Indoor Total"
    )
    designed_less_outdoor_credit = serializers.CharField(
        required=False, allow_blank=True, label="Designed Less Indoor Credit"
    )
    designed_outdoor_total = serializers.CharField(
        required=False, allow_blank=True, label="Designed Outdoor Total"
    )
    gallons_saved = serializers.CharField(required=False, allow_blank=True, label="Gallons Saved")
    wri_rating = serializers.CharField(required=False, allow_blank=True, label="WRI Rating")

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class WRI2021ScoringExtraction(BaseScoringExtraction):
    key = "wri-2021-scoring-extraction"
    display = "2020 SF/MF Stand-Alone WRI"

    def get_annotation_data_serializer_class(self):
        return WRI2021Scoring109ExtractionSerializer

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("1.0.9"):
            cell_map = {
                self.to_annotation_name("baseline-units"): self.get_cell_by_defined_name(
                    "desWRIBaseUnits"
                ),
                self.to_annotation_name("baseline-common-areas"): self.get_cell_by_defined_name(
                    "desWRIBaseCommon"
                ),
                self.to_annotation_name("baseline-indoor-total"): self.get_cell_by_defined_name(
                    "desWRIBaseIndoor"
                ),
                self.to_annotation_name("baseline-outdoor"): self.get_cell_by_defined_name(
                    "desWRIBaseOutdoor"
                ),
                self.to_annotation_name("designed-units"): self.get_cell_by_defined_name(
                    "desWRIDesignUnits"
                ),
                self.to_annotation_name("designed-common-areas"): self.get_cell_by_defined_name(
                    "desWRIDesignCommon"
                ),
                self.to_annotation_name(
                    "designed-less-indoor-credit"
                ): self.get_cell_by_defined_name("desWRIDesignIndoorCredit"),
                self.to_annotation_name("designed-indoor-total"): self.get_cell_by_defined_name(
                    "desWRIDesignIndoor"
                ),
                self.to_annotation_name("designed-outdoor"): self.get_cell_by_defined_name(
                    "desWRIDesignOutdoor"
                ),
                self.to_annotation_name(
                    "designed-less-outdoor-credit"
                ): self.get_cell_by_defined_name("desWRIDesignOutdoorCredit"),
                self.to_annotation_name("designed-outdoor-total"): self.get_cell_by_defined_name(
                    "desWRIDesignOutdoorTotal"
                ),
                self.to_annotation_name("gallons-saved"): self.get_cell_by_defined_name(
                    "desWRIGallons"
                ),
                self.to_annotation_name("wri-rating"): self.get_cell_by_defined_name(
                    "desWRIRating"
                ),
            }
        else:
            raise ScoringExtractionVersionNotSupported(self.sheet_version)
        return cell_map

    def validate_batch_submission(self):
        pass

    def validate_sampling(self):
        pass

    def batch_submission(self):
        pass

    def get_batch_submission_project_data(self):
        return []

    def validate_wri(self):
        pass
