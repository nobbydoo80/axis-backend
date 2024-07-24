"""wri_2021.py: """

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
    HIRLScoringWRI2021TaskMixin,
)
from axis.eep_program.models import EEPProgram
from .mixins import HIRLScoringUploadTestsMixin


class HIRLScoringUploadWRI2021TaskTests(
    HIRLScoringWRI2021TaskMixin,
    AxisTestCase,
    HIRLScoringUploadTestsMixin,
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.wri_2021.WRI2021ScoringExtraction.get_project_id")
    def test_scoring_upload_wri_v1_0_7_task(self, get_project_id_mock):
        data_type = "final"
        key = scoring_registry["wri-2021-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-wri-2021")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        # WRI program always have is_require_rough_inspection = False
        project.is_require_rough_inspection = False
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 SF WRI Scoring Tool 1.0.9.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_f_name("baseline-units", eep_program.slug): "28",
            BaseScoringExtraction.to_annotation_f_name(
                "baseline-common-areas", eep_program.slug
            ): "66",
            BaseScoringExtraction.to_annotation_f_name(
                "baseline-indoor-total", eep_program.slug
            ): "44",
            BaseScoringExtraction.to_annotation_f_name("baseline-outdoor", eep_program.slug): "55",
            BaseScoringExtraction.to_annotation_f_name("designed-units", eep_program.slug): "74",
            BaseScoringExtraction.to_annotation_f_name(
                "designed-common-areas", eep_program.slug
            ): "67",
            BaseScoringExtraction.to_annotation_f_name(
                "designed-less-indoor-credit", eep_program.slug
            ): "42",
            BaseScoringExtraction.to_annotation_f_name(
                "designed-indoor-total", eep_program.slug
            ): "66",
            BaseScoringExtraction.to_annotation_f_name("designed-outdoor", eep_program.slug): "11",
            BaseScoringExtraction.to_annotation_f_name(
                "designed-less-outdoor-credit", eep_program.slug
            ): "14",
            BaseScoringExtraction.to_annotation_f_name(
                "designed-outdoor-total", eep_program.slug
            ): "22",
            BaseScoringExtraction.to_annotation_f_name("gallons-saved", eep_program.slug): "53",
            BaseScoringExtraction.to_annotation_f_name("wri-rating", eep_program.slug): "69",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)
