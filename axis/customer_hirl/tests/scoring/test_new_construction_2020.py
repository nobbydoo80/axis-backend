"""new_construction_2020.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 21:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import datetime
import io
import os
from unittest import skipIf, mock

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.test import override_settings
from django.utils import timezone

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import (
    HIRLProject,
    HIRLProjectRegistration,
    HIRLUserProfile,
    BuilderAgreement,
)
from axis.customer_hirl.scoring import scoring_registry
from axis.customer_hirl.scoring.base import (
    ScoringExtractionRequirementsFailed,
    ScoringExtractionValidationException,
    BaseScoringExtraction,
)
from axis.customer_hirl.tasks import scoring_upload_task
from axis.customer_hirl.tests.factories import (
    hirl_project_registration_factory,
    hirl_project_factory,
    builder_agreement_factory,
)
from axis.customer_hirl.tests.mixins import (
    HIRLScoring2020NewConstructionTaskMixin,
)
from axis.customer_hirl.tests.scoring.mixins import HIRLScoringUploadTestsMixin
from axis.eep_program.models import EEPProgram
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.geographic.models import City
from axis.home.models import EEPProgramHomeStatus
from axis.invoicing.models import Invoice, InvoiceItemGroup
from axis.invoicing.tests.factories import invoice_item_group_factory, invoice_item_factory
from axis.qa.models import QARequirement, QAStatus
from axis.user_management.models import Accreditation
from axis.user_management.tests.factories import accreditation_factory

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLScoringUpload2020NewConstructionTaskTests(
    HIRLScoring2020NewConstructionTaskMixin, AxisTestCase, HIRLScoringUploadTestsMixin
):
    client_class = AxisClient

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_0_0_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS New Construction Scoring Tool 5.0.0.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Bronze",
            # 'epa-national-eri-target-{}-rough'.format(eep_program.slug): '',
            # 'eri-as-designed-{}-rough'.format(eep_program.slug): '',
            "eri-score-percent-less-than-energy-star-{}-rough".format(eep_program.slug): "1",
            "energy-path-{}-rough".format(eep_program.slug): "ERI Target",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.22",
            "wri-score-{}-rough".format(eep_program.slug): "",
            "water-path-{}-rough".format(eep_program.slug): "Prescriptive Path",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_0_1_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS New Construction Scoring Tool 5.0.1.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Bronze",
            # 'epa-national-eri-target-{}-rough'.format(eep_program.slug): '',
            # 'eri-as-designed-{}-rough'.format(eep_program.slug): '',
            "eri-score-percent-less-than-energy-star-{}-rough".format(eep_program.slug): "0.22",
            "energy-path-{}-rough".format(eep_program.slug): "ERI Target",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "1",
            "wri-score-{}-rough".format(eep_program.slug): "",
            "water-path-{}-rough".format(eep_program.slug): "Performance Path",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_0_4_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF New Construction Scoring Tool_5.0.4.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Silver",
            "epa-national-eri-target-{}-rough".format(eep_program.slug): "6",
            "eri-as-designed-{}-rough".format(eep_program.slug): "5",
            # 'eri-score-percent-less-than-energy-star-{}-rough'.format(eep_program.slug): '6',
            "energy-path-{}-rough".format(eep_program.slug): "ERI Target",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "1",
            "wri-score-{}-rough".format(eep_program.slug): "",
            "water-path-{}-rough".format(eep_program.slug): "Performance Path",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_1_4_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF New Construction Scoring Tool_5.1.4.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Silver",
            "epa-national-eri-target-{}-rough".format(eep_program.slug): "11",
            "eri-as-designed-{}-rough".format(eep_program.slug): "11",
            # 'eri-score-percent-less-than-energy-star-{}-rough'.format(eep_program.slug): '',
            "energy-path-{}-rough".format(eep_program.slug): "Performance Path",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.11",
            "wri-score-{}-rough".format(eep_program.slug): "12",
            "water-path-{}-rough".format(eep_program.slug): "Prescriptive Path",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "31",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
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
            BaseScoringExtraction.to_annotation_r_name(
                "badge-zero-water", eep_program.slug
            ): "Not Earned",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysql",
        "Only can be run on MYSQL Engine",
    )
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_scoring_upload_new_construction2020_v5_1_4_sampling_error_task(
        self, get_project_id_mock
    ):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-mf-new-construction-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        registration = HIRLProjectRegistration.objects.filter(eep_program=eep_program).get()

        registration.sampling = HIRLProjectRegistration.ALL_SAMPLING
        registration.save()

        # xlsx using ID: 2 for multifamily project
        with self.assertRaises(ScoringExtractionValidationException):
            company_admin_rater_user = self.get_admin_user(company_type=Company.RATER_COMPANY_TYPE)
            accreditation_factory(
                trainee=company_admin_rater_user,
                name=Accreditation.MASTER_VERIFIER_NAME,
                state=Accreditation.ACTIVE_STATE,
                manual_expiration_date=timezone.now() + timezone.timedelta(days=365),
            )
            self.prepare_scoring_upload_task(
                file_name="2020_SF_new_construction_scoring_tool_5.1.4_sampling_error.xlsx",
                template_type=key,
                data_type=data_type,
                eep_program=eep_program,
            )

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_1_4_no_sampling_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-mf-new-construction-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        registration = HIRLProjectRegistration.objects.filter(eep_program=eep_program).get()

        registration.sampling = HIRLProjectRegistration.TESTING_AND_PRACTICES_ONLY_SAMPLING
        registration.save()

        # xlsx using ID: 2 for multifamily project
        with self.assertRaises(ScoringExtractionRequirementsFailed):
            self.prepare_scoring_upload_task(
                file_name="2020_SF_new_construction_scoring_tool_5.1.4_no_sampling.xlsx",
                template_type=key,
                data_type=data_type,
                eep_program=eep_program,
            )

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_2_4_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF New Construction Scoring Tool_5.2.4.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Silver",
            "epa-national-eri-target-{}-rough".format(eep_program.slug): "25",
            "eri-as-designed-{}-rough".format(eep_program.slug): "15",
            "energy-path-{}-rough".format(eep_program.slug): "ERI Target",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.13",
            "wri-score-{}-rough".format(eep_program.slug): "55",
            "water-path-{}-rough".format(eep_program.slug): "Prescriptive Path",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "31",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
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
            BaseScoringExtraction.to_annotation_r_name(
                "badge-zero-water", eep_program.slug
            ): "Not Earned",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_2_5_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF New Construction Scoring Tool_5.2.5.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Silver",
            "epa-national-eri-target-{}-rough".format(eep_program.slug): "12",
            "eri-as-designed-{}-rough".format(eep_program.slug): "14",
            "energy-path-{}-rough".format(eep_program.slug): "Alt. Bronze or Silver",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.25",
            "wri-score-{}-rough".format(eep_program.slug): "54",
            "water-path-{}-rough".format(eep_program.slug): "Prescriptive Path",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name("duct-testing", eep_program.slug): "0.04",
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
            BaseScoringExtraction.to_annotation_r_name(
                "badge-zero-water", eep_program.slug
            ): "Not Earned",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_2_7_task(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        project = HIRLProject.objects.get(registration__eep_program=eep_program)
        project.is_require_wri_certification = True
        project.save()

        get_project_id_mock.return_value = project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF New Construction Scoring Tool 5.2.7.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        expected_data = {
            "alternative-bronze-and-silver-level-compliance-{}-rough".format(
                eep_program.slug
            ): "Alt. Bronze",
            "epa-national-eri-target-{}-rough".format(eep_program.slug): "66",
            "eri-as-designed-{}-rough".format(eep_program.slug): "55",
            "energy-path-{}-rough".format(eep_program.slug): "Prescriptive Path",
            "performance-path-percent-above-{}-rough".format(eep_program.slug): "0.05",
            "wri-score-{}-rough".format(eep_program.slug): "55",
            "water-path-{}-rough".format(eep_program.slug): "Performance Path",
            BaseScoringExtraction.to_annotation_r_name("ach50", eep_program.slug): "5",
            BaseScoringExtraction.to_annotation_r_name("elr50", eep_program.slug): "1",
            BaseScoringExtraction.to_annotation_r_name("duct-testing", eep_program.slug): "0.05",
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
            BaseScoringExtraction.to_annotation_r_name(
                "badge-zero-water", eep_program.slug
            ): "Not Earned",
        }
        # filter only rough annotations
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]
        self.maxDiff = None
        self.assertDictEqual(annotation_data, expected_data)

    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_home_status_state_update(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        hirl_project_parent = HIRLProject.objects.get(registration__eep_program=eep_program)
        hirl_project_parent.is_require_wri_certification = False
        hirl_project_parent.save()

        get_project_id_mock.return_value = hirl_project_parent.id

        sf_project = (
            HIRLProject.objects.filter(registration__eep_program=eep_program)
            .select_related("home_status")
            .get()
        )

        self.assertEqual(
            sf_project.home_status.state,
            EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE,
        )

        self.prepare_scoring_upload_task(
            file_name="2020 NGBS New Construction Scoring Tool 5.0.0.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        qa_status = sf_project.home_status.qastatus_set.filter(
            requirement__type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE
        ).get()

        qa_status.result = QAStatus.PASS_STATUS
        qa_status.save()

        sf_project.refresh_from_db()

        self.assertEqual(
            sf_project.home_status.state,
            EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_FINAL_QA_STATE,
        )

        data_type = "final"
        self.prepare_scoring_upload_task(
            file_name="2020 NGBS New Construction Scoring Tool 5.0.0.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )

        qa_status = sf_project.home_status.qastatus_set.filter(
            requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
        ).get()

        qa_status.result = QAStatus.PASS_STATUS
        qa_status.save()

        sf_project.refresh_from_db()

        self.assertEqual(
            sf_project.home_status.state,
            EEPProgramHomeStatus.CERTIFICATION_PENDING_STATE,
        )

    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    @mock.patch(
        "axis.customer_hirl.scoring.base.BaseScoringExtraction.get_batch_submission_project_data"
    )
    @mock.patch("axis.invoicing.messages.invoice.InvoiceCreatedNotificationMessage.send")
    def test_scoring_upload_batch_submission(
        self, invoice_created_message_send, batch_submission_project_data_mock, get_project_id_mock
    ):
        """
        Use one project from fixture compiler and create 2 others.
        Add them to excel file batch submission list and upload them
        :return:
        """
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")
        hirl_company = Company.objects.get(slug=customer_hirl_app.CUSTOMER_SLUG)

        builder_organization = Company.objects.get(
            name="PUG Builder", company_type=Company.BUILDER_COMPANY_TYPE
        )
        builder_agreement_factory(
            owner=hirl_company, company=builder_organization, state=BuilderAgreement.COUNTERSIGNED
        )
        verifier_organization = Company.objects.get(company_type=Company.RATER_COMPANY_TYPE)
        key = scoring_registry["new-construction2020-scoring-extraction"].key

        phoenix_city = City.objects.get(name="Phoenix", county__state="AZ")

        hirl_project_parent = HIRLProject.objects.get(registration__eep_program=eep_program)
        hirl_project_parent.is_require_wri_certification = True
        hirl_project_parent.save()

        registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            eep_program=eep_program,
            builder_organization=builder_organization,
            registration_user=verifier_organization.users.first(),
        )

        hirl_project_child1 = hirl_project_factory(
            registration=registration,
            home_status__home__street_line1=f"home address test55",
            home_status__home__lot_number=f"55",
            home_status__home__is_multi_family=eep_program.is_multi_family,
            home_status__home__zipcode=f"{55 * 1000}",
            home_status__home__city=phoenix_city,
            home_status__company=verifier_organization,
            home_status__eep_program=eep_program,
            home_address_geocode_response=None,
            story_count=1,
            number_of_units=1,
            is_require_wri_certification=True,
        )

        group = invoice_item_group_factory(home_status=hirl_project_child1.home_status)
        invoice_item_factory(group=group, cost=50, name="Test fee for hirl_project_child1")

        registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            eep_program=eep_program,
            builder_organization=builder_organization,
            registration_user=verifier_organization.users.first(),
        )

        hirl_project_child2 = hirl_project_factory(
            registration=registration,
            home_status__home__street_line1=f"home address test56",
            home_status__home__lot_number=f"56",
            home_status__home__is_multi_family=eep_program.is_multi_family,
            home_status__home__zipcode=f"{56 * 1000}",
            home_status__home__city=phoenix_city,
            home_status__company=verifier_organization,
            home_status__eep_program=eep_program,
            home_address_geocode_response=None,
            story_count=1,
            number_of_units=1,
            is_require_wri_certification=True,
        )

        group = invoice_item_group_factory(home_status=hirl_project_child2.home_status)
        invoice_item_factory(group=group, cost=50, name="Test fee for hirl_project_child2")
        invoice_item_factory(group=group, cost=50, name="Test fee2 for hirl_project_child2")

        data_type = "rough"

        hirl_company = Company.objects.get(slug=customer_hirl_app.CUSTOMER_SLUG)
        hirl_user = hirl_company.users.first()

        company_admin_rater_user = self.get_admin_user(company_type=Company.RATER_COMPANY_TYPE)
        accreditation_factory(
            trainee=company_admin_rater_user,
            approver=hirl_user,
            name=Accreditation.MASTER_VERIFIER_NAME,
            manual_expiration_date=timezone.now() + timezone.timedelta(days=360),
        )
        HIRLUserProfile.objects.create(user=company_admin_rater_user)

        get_project_id_mock.side_effect = [
            hirl_project_parent.id,
            hirl_project_child1.id,
            hirl_project_child2.id,
        ]

        batch_submission_project_data_mock.return_value = [
            {"project_id": hirl_project_child1.id, "inspection_date": timezone.now()},
            {"project_id": hirl_project_child2.id, "inspection_date": timezone.now()},
        ]

        file_path = os.path.join(
            settings.SITE_ROOT,
            "axis",
            "customer_hirl",
            "sources",
            "tests",
            "2020 NGBS SF New Construction Scoring Tool_5.2.5 batch.xlsx",
        )
        with io.open(file_path, "rb") as f:
            apd = AsynchronousProcessedDocument(
                company=hirl_company,
                download=True,
                task_name="scoring_upload_task",
                document=File(f, name=os.path.basename(file_path)),
            )
            apd.save()

        # mock date within 60 days of inspection date in excel file
        with mock.patch.object(
            timezone,
            "now",
            return_value=timezone.make_aware(datetime.datetime(2015, 10, 8, 11, 00)),
        ):
            scoring_upload_task.delay(
                user_id=company_admin_rater_user.id,
                result_object_id=apd.id,
                template_type=key,
                data_type=data_type,
                verifier_id=company_admin_rater_user.id,
            )

        hirl_project_child1.refresh_from_db()
        hirl_project_child2.refresh_from_db()
        self.assertEqual(hirl_project_child1.vr_batch_submission_parent_rough, hirl_project_parent)
        self.assertEqual(hirl_project_child2.vr_batch_submission_parent_rough, hirl_project_parent)

        # send a message to NGBS, verifier, client and ERFP
        self.assertEqual(invoice_created_message_send.call_count, 4)
        # invoice exists
        invoice = Invoice.objects.get()

        self.assertEqual(
            list(invoice.invoiceitemgroup_set.all().order_by("id")),
            list(
                InvoiceItemGroup.objects.filter(
                    home_status__customer_hirl_project__in=[
                        hirl_project_parent,
                        hirl_project_child1,
                        hirl_project_child2,
                    ]
                ).order_by("id")
            ),
        )

    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_wri_validation(self, get_project_id_mock):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        sf_project = HIRLProject.objects.get(registration__eep_program=eep_program)
        sf_project.is_require_wri_certification = True
        sf_project.save()

        get_project_id_mock.return_value = sf_project.id

        annotations = self.prepare_scoring_upload_task(
            file_name="2020 NGBS SF New Construction Scoring Tool_5.1.4.xlsx",
            template_type=key,
            data_type=data_type,
            eep_program=eep_program,
        )
        annotation_data = {}
        for annotation in annotations:
            if annotation["type__slug"].endswith(f"-{data_type}"):
                annotation_data[annotation["type__slug"]] = annotation["content"]

        self.assertEqual(
            annotation_data[
                BaseScoringExtraction.to_annotation_r_name("wri-score", eep_program.slug)
            ],
            "12",
        )

        with self.subTest("Set is_require_wri_certification to False"):
            sf_project.is_require_wri_certification = False
            sf_project.save()

            with self.assertRaises(ScoringExtractionValidationException):
                annotations = self.prepare_scoring_upload_task(
                    file_name="2020 NGBS SF New Construction Scoring Tool_5.1.4.xlsx",
                    template_type=key,
                    data_type=data_type,
                    eep_program=eep_program,
                )

        with self.subTest("Set is_require_wri_certification=True, but no WRI value provided"):
            sf_project.is_require_wri_certification = True
            sf_project.save()

            with self.assertRaises(ScoringExtractionValidationException):
                # use 5.0.0 file version without wri
                annotations = self.prepare_scoring_upload_task(
                    file_name="2020 NGBS New Construction Scoring Tool 5.0.0.xlsx",
                    template_type=key,
                    data_type=data_type,
                    eep_program=eep_program,
                )

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("axis.customer_hirl.scoring.base.BaseScoringExtraction.get_project_id")
    def test_scoring_upload_new_construction2020_v5_2_14_sf_support_sampling(
        self, get_project_id_mock
    ):
        data_type = "rough"
        key = scoring_registry["new-construction2020-scoring-extraction"].key
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        get_project_id_mock.return_value = HIRLProject.objects.get(
            registration__eep_program=eep_program
        ).id

        registration = HIRLProjectRegistration.objects.filter(eep_program=eep_program).get()

        registration.sampling = HIRLProjectRegistration.TESTING_AND_PRACTICES_ONLY_SAMPLING
        registration.save()

        # xlsx using ID: 1 for a single family project
        with self.assertRaises(ScoringExtractionRequirementsFailed):
            self.prepare_scoring_upload_task(
                file_name="2020 NGBS MF New Construction Scoring Tool 5.2.14.xlsx",
                template_type=key,
                data_type=data_type,
                eep_program=eep_program,
            )
