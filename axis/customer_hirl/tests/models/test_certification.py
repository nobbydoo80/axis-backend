"""certification.py - Axis"""

__author__ = "Steven K"
__date__ = "12/14/21 15:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import random
import string

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.apps import apps

from axis.customer_hirl.models import HIRLLegacyCertification, HIRLProject
from axis.geocoder.models import Geocode

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


def get_base_legacy_certification_data(**kwargs):
    data = {
        "hirl_id": random.randint(1, 100000),
        "scoring_path_name": random.choice(list(app.NGBS_PROGRAM_NAMES.keys())),
        "data": {
            "ID": random.randint(1000, 10000),
            "ERI": None,
            "WRI": None,
            "Zip": "44703",
            "City": "Canton",
            "Notes": None,
            "State": 36,
            "County": "Stark",
            "TotalFee": 4720,
            "AddressL1": "700 McKinley Avenue NW",
            "AddressL2": "#2",
            "BadgesFee": 0,
            "CreatedBy": "lmarchman",
            "HersIndex": None,
            "ProjectID": "747PTL-1",
            "UnitCount": 0,
            "WaterPath": None,
            "ImageTitle": None,
            "ModifiedBy": None,
            "RebateSent": 0,
            "StoryCount": 8,
            "CreatedDate": "2020-09-02T16:46:49",
            "ImageAltTag": None,
            "JamisWorthy": True,
            "Recertified": False,
            "fkBuilderID": 3518,
            "FlickrImages": False,
            "ModifiedDate": None,
            "fkProjectsID": 2935,
            "fkVerifierID": 3664,
            "DesktopReview": False,
            "ImageFileName": None,
            "InvoiceNumber": "043764",
            "PaymentAmount": 0,
            "PurchaseOrder": None,
            "fkCheckListID": 4,
            "FinalUnitCount": None,
            "ImageViewIndex": 900,
            "RoughUnitCount": None,
            "ImageUploadDate": None,
            "InvoiceSentDate": None,
            "JamisMilestoned": False,
            "PaymentRcvdDate": None,
            "RoughInLocation": "700 McKinley Avenue NW",
            "RoughInRcvdDate": None,
            "fkFinalReviewer": None,
            "fkFinalVerifier": None,
            "fkRoughReviewer": None,
            "fkRoughVerifier": None,
            "fkScoringPathID": 41,
            "BuilderChallenge": False,
            "CertificationFee": 4720,
            "CertificateNumber": random.randint(1, 100000),
            "ImageExposedToWeb": False,
            "fkSamplingIDFinal": 0,
            "fkSamplingIDRough": 0,
            "BillsTestRecordTag": 0,
            "CertificateSentDate": "2021-12-01T23:59:59",
            "FinalReviewDuration": 0,
            "RoughReviewDuration": 0,
            "HudDisasterCaseNumber": None,
            "fkCertificationStatus": 7,
            "fkFinalDeliveryMethod": None,
            "FinalBuildersChallenge": False,
            "FinalReviewerStartDate": None,
            "JamisCaptureNotPursing": False,
            "RoughBuildersChallenge": False,
            "RoughReviewerStartDate": None,
            "FinalInspectionRcvdDate": None,
            "FinalVerifierGradeNotes": None,
            "RoughVerifierGradeNotes": None,
            "WaterSenseCertification": False,
            "fkDesktopReviewGradesID": None,
            "fkFinalVerifierGradesID": None,
            "fkRoughVerifierGradesID": None,
            "FinalReviewerCompletedDate": None,
            "RoughReviewerCompletedDate": None,
            "FinalPointsClaimedByBuilder": None,
            "FinalPointsDeniedByReviewer": None,
            "FinalPointsDeniedByVerifier": None,
            "FinalReviewApprovedWellness": False,
            "LoAGreenSubDivPlansRcvdDate": None,
            "RoughPointsClaimedByBuilder": None,
            "RoughPointsDeniedByReviewer": None,
            "RoughPointsDeniedByVerifier": None,
            "FinalPointsAwardedByReviewer": None,
            "FinalPointsAwardedByVerifier": None,
            "FinalRequireVerifierFollowUp": False,
            "FinalReviewApprovedSmartHome": False,
            "FinalReviewApprovedZeroWater": False,
            "RoughPointsAwardedByReviewer": None,
            "RoughPointsAwardedByVerifier": None,
            "RoughRequireVerifierFollowUp": False,
            "fkVerifierCertificationLevel": 0,
            "FinalCertificationTargetLevel": None,
            "FinalReviewApprovedResilience": False,
            "LoAGreenSubDivInvoiceSentDate": None,
            "LoAGreenSubDivPaymentRcvdDate": None,
            "RoughCertificationTargetLevel": 1,
            "CertificationProjectTypeSFMFGS": "MF",
            "BuilderVerifierNotificationDate": None,
            "LoAGreenSubDivApprovalIssueDate": None,
            "FinalReviewApprovedNetZeroEnergy": False,
            "FinalReviewDurationStartDateTime": None,
            "RoughReviewDurationStartDateTime": None,
            "fkFinalCertificationReviewStatus": 1,
            "fkRoughCertificationReviewStatus": 1,
            "FinalReviewApprovedUniversalDesign": False,
            "fkVerifierCertificationEnergyPathID": 0,
            "RemindMeFinalInspectionScheduledDate": None,
            "RemindMeRoughInspectionScheduledDate": None,
            "fkVerifierCertificationLevelChapter7": 0,
            "RemindMeFinalInspectionNotificationDate": None,
            "RemindMeRoughInspectionNotificationDate": None,
            "fkAnticipatedVerifierCertificationLevel": 0,
            "FinalReviewApprovedWaterSenseCertification": False,
            "fkVerificationCertificationMassRegistrationID": 0,
        },
        "convert_to_registration_error": "",
    }
    if "MF" in data["scoring_path_name"] or "multi" in data["scoring_path_name"]:
        data["data"]["UnitCount"] = random.randint(1, 500)

    _kw_data = {}
    if "data" in kwargs:
        _kw_data = kwargs.pop("data")

    data.update(kwargs)
    data["data"].update(_kw_data)

    return data.copy()


class HIRLLegacyCertificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = get_base_legacy_certification_data(
            scoring_path_name="2015 SF New Construction",
            data={"CertificateNumber": "", "fkCertificationStatus": 7, "CertificateSentDate": None},
        )
        cls.single_family_not_certified = HIRLLegacyCertification.objects.create(**data)

        data = get_base_legacy_certification_data(scoring_path_name="2015 SF New Construction")
        cls.single_family_certified = HIRLLegacyCertification.objects.create(**data)

    def test_base_certified(self):
        certified = HIRLLegacyCertification.objects.base_certified().filter(
            scoring_path_name="2015 SF New Construction"
        )

        self.assertEqual(certified.count(), 1)

        certified = certified.get()
        self.assertEqual(certified, self.single_family_certified)

        self.assertIn("700 McKinley Avenue NW", certified.address)
        self.assertIn("#2", certified.address)
        self.assertTrue(certified.is_certified)
        self.assertEqual(certified.unit_count, None, certified.scoring_path_name)

    def test_base_certified_start_end_date(self):
        past = datetime.datetime.now() - datetime.timedelta(days=2)

        data = get_base_legacy_certification_data(
            scoring_path_name="2015 SF New Construction",
            data={"CertificateSentDate": past.strftime("%Y-%m-%dT%H:%M:%S")},
        )
        recent = HIRLLegacyCertification.objects.create(**data)

        with self.subTest("Test Start Date"):
            past_trunc = datetime.datetime(past.year, past.month, past.day).replace(
                tzinfo=datetime.timezone.utc
            )
            certified = HIRLLegacyCertification.objects.base_certified(
                start_datetime=past_trunc
            ).filter(scoring_path_name="2015 SF New Construction")

            self.assertEqual(certified.count(), 1)
            self.assertEqual(certified.get(), recent)

        with self.subTest("Test End Date"):
            past -= datetime.timedelta(days=1)
            past_trunc = datetime.datetime(past.year, past.month, past.day).replace(
                tzinfo=datetime.timezone.utc
            )
            certified = HIRLLegacyCertification.objects.base_certified(
                end_datetime=past_trunc
            ).filter(scoring_path_name="2015 SF New Construction")

            self.assertEqual(certified.count(), 1)
            self.assertEqual(certified.get(), self.single_family_certified)

    def test_base_certified_eep_program(self):
        from axis.eep_program.models import EEPProgram

        name = "2015 MF Remodel Building"
        program = EEPProgram.objects.create(name=name, slug=app.NGBS_PROGRAM_NAMES[name])
        data = get_base_legacy_certification_data(scoring_path_name=name)
        mf_cert = HIRLLegacyCertification.objects.create(**data)

        certified = HIRLLegacyCertification.objects.base_certified(eep_program=program)

        self.assertEqual(certified.count(), 1)
        self.assertEqual(certified.get(), mf_cert)
        self.assertEqual(certified.get().unit_count, data["data"]["UnitCount"])
        self.assertIn(str(certified.get().unit_count), str(certified.get()))

    def test_legacy_certified(self):
        """Legacy Certified do not have a project ID"""
        certified = HIRLLegacyCertification.objects.legacy_certified().filter(
            scoring_path_name="2015 SF New Construction"
        )

        self.assertEqual(certified.count(), 1)
        self.assertEqual(certified.get(), self.single_family_certified)

        self.single_family_certified.project = HIRLProject.objects.create(
            home_address_geocode=Geocode.objects.create(
                raw_address="nowhere ln, gilbert, az, 54829"
            )
        )
        self.single_family_certified.save()

        certified = HIRLLegacyCertification.objects.legacy_certified().filter(
            scoring_path_name="2015 SF New Construction"
        )
        self.assertEqual(certified.count(), 0)

    def test_certified_unaccounted_for(self):
        """These do not have a legacy Project ID (Stored as an annotation)"""
        from axis.annotation.models import Annotation
        from axis.annotation.models import Type as AnnotationType
        from axis.home.models import EEPProgramHomeStatus

        annotation_type = AnnotationType.objects.create(name="Project ID", slug="project-id")
        Annotation.objects.create(
            content_type=ContentType.objects.get_for_model(EEPProgramHomeStatus),
            object_id=1,
            type=annotation_type,
            content="TEST001",
        )

        data = get_base_legacy_certification_data(
            scoring_path_name="2015 SF New Construction",
            data={"ProjectID": "TEST001"},
        )
        HIRLLegacyCertification.objects.create(**data)

        certified = HIRLLegacyCertification.objects.base_certified().filter(
            scoring_path_name="2015 SF New Construction"
        )
        self.assertEqual(certified.count(), 2)

        legacy_certified = HIRLLegacyCertification.objects.legacy_certified().filter(
            scoring_path_name="2015 SF New Construction"
        )
        self.assertEqual(legacy_certified.count(), 2)
