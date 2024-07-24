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
from axis.customer_hirl.scoring import scoring_registry, BaseScoringExtraction
from axis.customer_hirl.tests.mixins import (
    HIRLScoringLandDevelopmentTaskMixin,
)
from axis.eep_program.models import EEPProgram
from .mixins import HIRLScoringUploadTestsMixin
from axis.customer_hirl.models import HIRLProject


class HIRLScoringUploadLandDevelopment2020TaskTests(
    HIRLScoringLandDevelopmentTaskMixin,
    AxisTestCase,
    HIRLScoringUploadTestsMixin,
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch(
        "axis.customer_hirl.scoring.land_development_2020.LandDevelopment2020ScoringExtraction.get_project_id"
    )
    def test_scoring_upload_land_development_v1_0_9_task(self, get_project_id_mock):
        data_type = "final"
        key = scoring_registry["land-development-2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-land-development-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_rough_inspection = False
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020NGBSLandDevelopmentScoringWorking-20221026.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_f_name(
                "points-awarded-by-verifier", eep_program.slug
            ): "6",
            BaseScoringExtraction.to_annotation_f_name(
                "rating-level-archived", eep_program.slug
            ): "1 STAR",
            BaseScoringExtraction.to_annotation_f_name(
                "loa-points-awarded-by-verifier", eep_program.slug
            ): "3",
            BaseScoringExtraction.to_annotation_f_name(
                "loa-rating-level-archived", eep_program.slug
            ): "4 STARS",
        }

        # filter only final annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

        with self.subTest("Test with LOA project"):
            project = HIRLProject.objects.get(registration__eep_program=eep_program)
            project.land_development_project_type = HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT
            project.save()

            expected_data_loa = {
                BaseScoringExtraction.to_annotation_f_name(
                    "loa-points-awarded-by-verifier", eep_program.slug
                ): "3",
                BaseScoringExtraction.to_annotation_f_name(
                    "loa-rating-level-archived", eep_program.slug
                ): "4 STARS",
            }

            annotations = self.prepare_scoring_upload_task(
                file_name="2020NGBSLandDevelopmentScoringWorking-20221026.xlsx",
                template_type=key,
                data_type=data_type,
                eep_program=eep_program,
            )

            annotation_data = {}

            # filter only final annotations
            for annotation in annotations:
                if annotation["type__slug"].endswith(f"-{data_type}"):
                    annotation_data[annotation["type__slug"]] = annotation["content"]

            # reset annotations
            del annotation_data[
                BaseScoringExtraction.to_annotation_f_name(
                    "points-awarded-by-verifier", eep_program.slug
                )
            ]
            del annotation_data[
                BaseScoringExtraction.to_annotation_f_name(
                    "rating-level-archived", eep_program.slug
                )
            ]

            self.maxDiff = None
            self.assertDictEqual(annotation_data, expected_data_loa)
