"""2020_land_development.py: """

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
from axis.customer_hirl.models import HIRLProject

from .base import (
    BaseScoringExtraction,
    ScoringExtractionVersionNotSupported,
    ScoringExtractionUnknownVersion,
)
from ..messages import HIRLScoringUploadFinalOutstandingFeeBalanceMessage


class LandDevelopment2020Scoring121ExtractionSerializer(serializers.Serializer):
    """
    Validation serializer for spreadsheet 1.2.1
    """

    points_awarded_by_verifier = serializers.CharField(
        required=False, allow_blank=True, label="Total Points Awarded by Verifier"
    )
    rating_level_archived = serializers.CharField(
        required=False, allow_blank=True, label="Rating Level Achieved"
    )

    loa_points_awarded_by_verifier = serializers.CharField(
        required=False, allow_blank=True, label="Total Points Awarded by Verifier"
    )
    loa_rating_level_archived = serializers.CharField(
        required=False, allow_blank=True, label="Rating Level Achieved"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class LandDevelopment2020ScoringLOA121ExtractionSerializer(serializers.Serializer):
    """
    Validation serializer for spreadsheet 1.2.1
    """

    loa_points_awarded_by_verifier = serializers.CharField(
        required=False, allow_blank=True, label="Total Points Awarded by Verifier"
    )
    loa_rating_level_archived = serializers.CharField(
        required=False, allow_blank=True, label="Rating Level Achieved"
    )

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class LandDevelopment2020ScoringExtraction(BaseScoringExtraction):
    key = "land-development-2020-scoring-extraction"
    display = "2020 Land Development"

    available_destinations = ["ProjectID", "startVersion"]

    @cached_property
    def sheet_version(self):
        sheet_version = self._clean_str(self.destinations["startVersion"])

        if sheet_version:
            self.app_log.info("Detect version .xlsx {}".format(sheet_version))
        else:
            raise ScoringExtractionUnknownVersion
        return sheet_version

    def get_project_id(self):
        hirl_project_id = self.destinations["ProjectID"]
        return self._clean_str(hirl_project_id)

    def get_annotation_data_serializer_class(self):
        if self.project.land_development_project_type == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT:
            return LandDevelopment2020ScoringLOA121ExtractionSerializer
        return LandDevelopment2020Scoring121ExtractionSerializer

    @cached_property
    def annotations_map(self):
        if version.parse(self.sheet_version) >= version.parse("1.2.1"):
            cell_map = {
                self.to_annotation_name(
                    "loa-points-awarded-by-verifier"
                ): self.get_cell_by_defined_name("LOA.PointsAwardedByVerifier"),
                self.to_annotation_name("loa-rating-level-archived"): self.get_cell_by_defined_name(
                    "LOA.RatingLevelAchieved"
                ),
                self.to_annotation_name(
                    "points-awarded-by-verifier"
                ): self.get_cell_by_defined_name("CompletedDev.PointsAwardedByVerifier"),
                self.to_annotation_name("rating-level-archived"): self.get_cell_by_defined_name(
                    "CompletedDev.LevelAchieved"
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

    def finalize_upload(self):
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

        if self.project.land_development_project_type == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT:
            self.app_log.info(
                f"<p>The Verification Report requires "
                f"the upload of the following additional collateral:</p>"
                f"<p><strong>- A copy of the development plans</strong></p>"
            )

        if self.project.land_development_project_type == HIRLProject.LD_PROJECT_TYPE_PHASE_PROJECT:
            self.app_log.info(
                f"<p>The Verification Report requires "
                f"the upload of the following additional collateral:</p>"
                f"<p><strong>- A copy of the development plans</strong></p>"
                f"<p><strong>- A photo of the main entrance of the development</strong></p>"
            )

        self.app_log.info(
            f'<a href="{self.project.home_status.get_absolute_url()}'
            f'#/tabs/documents">Document created</a>'
            f"<p style='font-size: 23px; margin: 0 0 0px;'>"
            f"<a href='{self.project.home_status.get_absolute_url()}#/tabs/qa'>"
            f"Click here to upload photos and additional documentation</a></p>"
            f"<hr style='margin: 0'>"
        )
