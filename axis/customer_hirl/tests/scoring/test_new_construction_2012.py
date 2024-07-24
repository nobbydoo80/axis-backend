"""new_construction_2012.py: """

__author__ = "Artem Hruzd"
__date__ = "09/09/2021 10:19 AM"
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
    HIRLScoring2012NewConstructionTaskMixin,
)
from axis.eep_program.models import EEPProgram
from .mixins import HIRLScoringUploadTestsMixin


class HIRLScoringUpload2012NewConstructionTaskTests(
    HIRLScoring2012NewConstructionTaskMixin, AxisTestCase, HIRLScoringUploadTestsMixin
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch(
        "axis.customer_hirl.scoring.new_construction_2012.NewConstruction2012ScoringExtraction.get_project_id"
    )
    def test_scoring_upload_new_construction2012_v2_53_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2012-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2012-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = False
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2012NGBSNewConstructionScoring_2.53.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name("energy-path", eep_program.slug): "33",
            BaseScoringExtraction.to_annotation_r_name(
                "performance-path-percent-above", eep_program.slug
            ): "Prescriptive Path",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)
