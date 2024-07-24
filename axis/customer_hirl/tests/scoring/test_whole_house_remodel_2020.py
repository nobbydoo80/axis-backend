"""whole_house_remodel_2015.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 21:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest import mock

from django.test import override_settings

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import HIRLProject
from axis.customer_hirl.scoring import scoring_registry, BaseScoringExtraction
from axis.customer_hirl.tests.mixins import (
    HIRLScoring2020WholeHouseRemodelTaskMixin,
)
from axis.eep_program.models import EEPProgram
from .mixins import HIRLScoringUploadTestsMixin


class HIRLScoringUpload2020WholeHouseRemodelTaskTests(
    HIRLScoring2020WholeHouseRemodelTaskMixin,
    AxisTestCase,
    HIRLScoringUploadTestsMixin,
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_whole_house_remodel_v4_1_5_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-2020-whole-house-remodel-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-whole-house-remodel-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF Remodeling Scoring Tool_4.1.5.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name("year-built", eep_program.slug): "1993",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-baseline-year", eep_program.slug
            ): "1995",
            BaseScoringExtraction.to_annotation_r_name(
                "water-baseline-year", eep_program.slug
            ): "1996",
            BaseScoringExtraction.to_annotation_r_name(
                "project-description", eep_program.slug
            ): "Test Description",
            "energy-compliance-path-{}-rough".format(eep_program.slug): "Prescriptive",
            "water-compliance-path-{}-rough".format(eep_program.slug): "Performance",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "33",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-percent-reduction", eep_program.slug
            ): "0.1",
            BaseScoringExtraction.to_annotation_r_name(
                "water-percent-reduction", eep_program.slug
            ): "0.2",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-resilience", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-smart-home", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-universal-design", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name("badge-wellness", eep_program.slug): "#REF!",
            # Zero Water is not exists in template
            BaseScoringExtraction.to_annotation_r_name("badge-zero-water", eep_program.slug): "",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_whole_house_remodel_v4_0_2_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-2020-whole-house-remodel-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-whole-house-remodel-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF Remodeling Scoring Tool_4.0.2.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name("year-built", eep_program.slug): "1969",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-baseline-year", eep_program.slug
            ): "2020",
            BaseScoringExtraction.to_annotation_r_name(
                "water-baseline-year", eep_program.slug
            ): "2020",
            BaseScoringExtraction.to_annotation_r_name(
                "project-description", eep_program.slug
            ): "n/a",
            "energy-compliance-path-{}-rough".format(eep_program.slug): "Performance",
            "water-compliance-path-{}-rough".format(eep_program.slug): "Prescriptive",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "7",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-percent-reduction", eep_program.slug
            ): "0.396",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_whole_house_remodel_v4_1_13_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-2020-whole-house-remodel-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-whole-house-remodel-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF Remodeling Scoring Tool 4.1.13.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name("year-built", eep_program.slug): "1969",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-baseline-year", eep_program.slug
            ): "1970",
            BaseScoringExtraction.to_annotation_r_name(
                "water-baseline-year", eep_program.slug
            ): "1971",
            BaseScoringExtraction.to_annotation_r_name(
                "project-description", eep_program.slug
            ): "test",
            "energy-compliance-path-{}-rough".format(eep_program.slug): "Prescriptive",
            "water-compliance-path-{}-rough".format(eep_program.slug): "Performance",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "0.05",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "0.06",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-percent-reduction", eep_program.slug
            ): "0.05",
            BaseScoringExtraction.to_annotation_r_name("duct-testing", eep_program.slug): "0.06",
            BaseScoringExtraction.to_annotation_r_name(
                "water-percent-reduction", eep_program.slug
            ): "0.06",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-resilience", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-smart-home", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-universal-design", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name(
                "badge-wellness", eep_program.slug
            ): "Not Earned",
            BaseScoringExtraction.to_annotation_r_name("badge-zero-water", eep_program.slug): "",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)
