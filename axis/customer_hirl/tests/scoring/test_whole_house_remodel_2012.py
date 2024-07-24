"""whole_house_remodel_2012.py: """

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
    HIRLScoring2012WholeHouseRemodelTaskMixin,
)
from axis.eep_program.models import EEPProgram
from .mixins import HIRLScoringUploadTestsMixin


class HIRLScoringUpload2012WholeHouseRemodelTaskTests(
    HIRLScoring2012WholeHouseRemodelTaskMixin, AxisTestCase, HIRLScoringUploadTestsMixin
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch(
        "axis.customer_hirl.scoring.whole_house_remodel_2012.WholeHouseRemodel2012ScoringExtraction.get_project_id"
    )
    def test_scoring_upload_whole_house_remodel_v2_0_1_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-2012-whole-house-remodel-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-whole-house-remodel-2012-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2012NGBSRemodelingScoring_2.0.1.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name(
                "energy-percent-reduction", eep_program.slug
            ): "-2100.0000000000005",
            BaseScoringExtraction.to_annotation_r_name(
                "water-percent-reduction", eep_program.slug
            ): "-34.52380952380949",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)
