"""new_construction_2015.py: """

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
    HIRLScoring2015NewConstructionTaskMixin,
)
from axis.eep_program.models import EEPProgram
from .mixins import HIRLScoringUploadTestsMixin


class HIRLScoringUpload2015NewConstructionTaskTests(
    HIRLScoring2015NewConstructionTaskMixin,
    AxisTestCase,
    HIRLScoringUploadTestsMixin,
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2015_v4_0_9_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2015-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2015-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = False
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2015NGBSNewConstructionScoring_4.0.9.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "energy-path-{}-rough".format(eep_program.slug): "HERS Index Target",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.22",
            "hers-index-percent-less-than-energy-star-{}-rough".format(eep_program.slug): "0.22",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "0.35",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "0.4",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2015_v4_2_2_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2015-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2015-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = False
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2015NGBSNewConstructionScoring_4.2.2.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "energy-path-{}-rough".format(eep_program.slug): "Performance Path",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.33",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-star-hers-index-target", eep_program.slug
            ): "33",
            "as-designed-home-hers-{}-rough".format(eep_program.slug): "33",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "33",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2015_v4_2_5_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2015-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2015-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = False
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2015 NGBS New Construction Scoring Tool 4.2.5.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "energy-path-{}-rough".format(eep_program.slug): "Prescriptive Path",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.05",
            BaseScoringExtraction.to_annotation_r_name(
                "energy-star-hers-index-target", eep_program.slug
            ): "0.25",
            "as-designed-home-hers-{}-rough".format(eep_program.slug): "14",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)
