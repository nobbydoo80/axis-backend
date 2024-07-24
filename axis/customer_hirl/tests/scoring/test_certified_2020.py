"""certified_2020.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 21:50"
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
from axis.customer_hirl.tests.mixins import HIRLScoringCertified2020TaskMixin
from axis.customer_hirl.tests.scoring.mixins import HIRLScoringUploadTestsMixin
from axis.eep_program.models import EEPProgram
from axis.qa.models import QAStatus


class HIRLScoringCertified2020TaskTests(
    HIRLScoringCertified2020TaskMixin, AxisTestCase, HIRLScoringUploadTestsMixin
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v1_0_4_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["certified2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-certified-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS Certified Path Scoring Tool_1.0.4.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name(
                "energy-path", eep_program.slug
            ): "Prescriptive Path",
            "total-reference-annual-energy-{}-rough".format(eep_program.slug): "0.22",
            "epa-national-eri-target-{}-rough".format(eep_program.slug): "44",
            "eri-as-designed-{}-rough".format(eep_program.slug): "33",
            "water-path-{}-rough".format(eep_program.slug): "Alt. Compliance Path",
            "wri-score-{}-rough".format(eep_program.slug): "15",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name("total-leakage", eep_program.slug): "1",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    @mock.patch(
        "axis.customer_hirl.messages." "HIRLScoringUploadFinalOutstandingFeeBalanceMessage.send"
    )
    @mock.patch("axis.customer_hirl.messages.HIRLScoringUploadNotificationMessage.send")
    def test_scoring_upload_new_construction2020_final_v1_0_4_task(
        self,
        hirl_scoring_upload_notification_message,
        hirl_scoring_upload_final_outstanding_fee_balance_message,
        get_project_id_mock,
    ):
        # upload rough data first
        self.test_scoring_upload_new_construction2020_v1_0_4_task()

        # set QA to PASS state
        QAStatus.objects.all().update(result=QAStatus.PASS_STATUS)

        data_type = "final"
        key = scoring_registry["certified2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-certified-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS Certified Path Scoring Tool_1.0.4.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "energy-path-{}-final".format(eep_program.slug): "Prescriptive Path",
            "total-reference-annual-energy-{}-final".format(eep_program.slug): "0.22",
            "epa-national-eri-target-{}-final".format(eep_program.slug): "44",
            "eri-as-designed-{}-final".format(eep_program.slug): "33",
            "water-path-{}-final".format(eep_program.slug): "Alt. Compliance Path",
            "wri-score-{}-final".format(eep_program.slug): "15",
            BaseScoringExtraction.to_annotation_f_name("ach50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_f_name("elr50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_f_name("total-leakage", eep_program.slug): "2",
        }
        # filter only final annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

        hirl_scoring_upload_notification_message.assert_called()
        hirl_scoring_upload_final_outstanding_fee_balance_message.assert_called()

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v1_0_9_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["certified2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-certified-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS Certified Path Scoring Tool 1.0.9.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            BaseScoringExtraction.to_annotation_r_name(
                "energy-path", eep_program.slug
            ): "Energy Perform. Path",
            BaseScoringExtraction.to_annotation_r_name(
                "total-reference-annual-energy", eep_program.slug
            ): "0.05",
            BaseScoringExtraction.to_annotation_r_name(
                "epa-national-eri-target", eep_program.slug
            ): "66",
            BaseScoringExtraction.to_annotation_r_name("eri-as-designed", eep_program.slug): "54",
            BaseScoringExtraction.to_annotation_r_name(
                "water-path", eep_program.slug
            ): "Alt. Compliance Path",
            BaseScoringExtraction.to_annotation_r_name("wri-score", eep_program.slug): "54",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "11",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "0.05",
            BaseScoringExtraction.to_annotation_r_name("total-leakage", eep_program.slug): "1",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)
