"""test_eep_program_home_status.py: """

__author__ = "Artem Hruzd"
__date__ = "06/12/2022 19:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
    "Naruhito Kaide",
]

import io
import random
import zipfile

from django.apps import apps
from django.contrib.auth import get_user_model
from hashid_field import Hashid
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from openpyxl import load_workbook
from rest_framework import status

from axis.company.models import SponsorPreferences, Company
from axis.company.tests.factories import (
    provider_organization_factory,
    architect_organization_factory,
    builder_organization_factory,
)
from axis.core.tests.factories import provider_user_factory, SET_NULL, rater_admin_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.core.utils import unrandomize_filename
from axis.customer_hirl.models import HIRLProjectRegistration, BuilderAgreement
from axis.customer_hirl.reports.certificate import CustomerHIRLCertificate
from axis.customer_hirl.tests.factories import (
    hirl_project_factory,
    hirl_project_registration_factory,
    builder_agreement_factory,
)
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import customer_hirl_homes_report_task
from axis.qa.models import QARequirement, QAStatus
from axis.qa.tests.factories import qa_requirement_factory, qa_status_factory

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class EEPProgramHomeStatusViewSetTests(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Gilbert", "AZ")

    def test_customer_hirl_homes_report(self):
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        url = reverse_lazy("api_v3:home_status-customer-hirl-homes-report")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        customer_hirl_homes_report_task()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check for file in response
        # actual response check in task tests
        load_workbook(io.BytesIO(response.content), data_only=True)

    def test_customer_hirl_certified_projects_by_month_metrics(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(company=hirl_company)

        non_customer_hirl_user = provider_user_factory()

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program__owner=hirl_company,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None, home_status=SET_NULL
        )
        today = timezone.now().today()

        sf_project.create_home_status()
        sf_project.refresh_from_db()
        sf_project.home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        sf_project.home_status.certification_date = today
        sf_project.home_status.save()

        url = reverse_lazy("api_v3:home_status-customer-hirl-certified-projects-by-month-metrics")
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(url, format="json")

        first_day_of_month = today.replace(day=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["certification_date_month"], first_day_of_month.strftime("%Y-%m-%d")
        )
        self.assertEqual(response.data[0]["home_status_count"], 1)

        with self.subTest("Restrict access for non HIRL users"):
            self.client.force_authenticate(user=non_customer_hirl_user)
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_hirl_certified_units_by_month_metrics(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        hirl_user = provider_user_factory(company=hirl_company)

        non_customer_hirl_user = provider_user_factory()

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            eep_program__owner=hirl_company,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            number_of_units=1,
        )
        today = timezone.now().today()

        sf_project.create_home_status()
        sf_project.refresh_from_db()
        sf_project.home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        sf_project.home_status.certification_date = today
        sf_project.home_status.save()

        url = reverse_lazy("api_v3:home_status-customer-hirl-certified-units-by-month-metrics")
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(url, format="json")

        first_day_of_month = today.replace(day=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0]["certification_date_month"], first_day_of_month.strftime("%Y-%m-%d")
        )
        self.assertEqual(response.data[0]["units_count"], 2)

        with self.subTest("Restrict access for non HIRL users"):
            self.client.force_authenticate(user=non_customer_hirl_user)
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_certificate_download(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs",
            slug=customer_hirl_app.CUSTOMER_SLUG,
            is_eep_sponsor=True,
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_admin_factory(
            first_name="Verifier User", company__name="Verifier Company"
        )

        SponsorPreferences.objects.get_or_create(
            sponsor=hirl_company, sponsored_company=verifier_user.company
        )

        builder_organization = builder_organization_factory()
        architect_organization = architect_organization_factory()
        builder_agreement_factory(
            owner=hirl_company, company=architect_organization, state=BuilderAgreement.COUNTERSIGNED
        )

        mf_registration = hirl_project_registration_factory(
            registration_user=verifier_user,
            eep_program__slug="ngbs-sf-new-construction-2020-new",
            eep_program__owner=hirl_company,
            eep_program__customer_hirl_per_unit_fee=30,
            eep_program__viewable_by_company_type=f"{Company.PROVIDER_COMPANY_TYPE}, {Company.QA_COMPANY_TYPE}",
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            architect_organization=architect_organization,
            project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            story_count=1,
            number_of_units=1,
        )

        mf_project.registration.active()
        mf_project.create_home_status()
        mf_project.home_status.refresh_from_db()

        requirement = qa_requirement_factory(
            eep_program=mf_registration.eep_program,
            qa_company=hirl_company,
            type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
        )

        qa_status = qa_status_factory(
            requirement=requirement,
            state="correction_required",
            qa_designee=hirl_user,
            home_status=mf_project.home_status,
            hirl_certification_level_awarded=QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED,
        )

        home_status = EEPProgramHomeStatus.objects.get(id=mf_project.home_status.id)
        home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        home_status.certification_date = timezone.now() - timezone.timedelta(days=5)
        home_status.save()

        bulk_certificate_download_url = reverse_lazy("api_v3:home_status-bulk-certificate-download")

        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(bulk_certificate_download_url, data={}, format="json")

        async_document = AsynchronousProcessedDocument.objects.get(id=response.data["id"])
        zf = zipfile.ZipFile(async_document.document.file)

        customer_hirl_certificate = CustomerHIRLCertificate(home_status=home_status, user=hirl_user)

        self.assertEqual(
            zf.namelist(),
            [
                customer_hirl_certificate.get_filename(),
            ],
        )

    def test_customer_hirl_certificate_lookup_list(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs",
            slug=customer_hirl_app.CUSTOMER_SLUG,
            is_eep_sponsor=True,
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_admin_factory(
            first_name="Verifier User", company__name="Verifier Company"
        )

        SponsorPreferences.objects.get_or_create(
            sponsor=hirl_company, sponsored_company=verifier_user.company
        )

        builder_organization = builder_organization_factory()
        architect_organization = architect_organization_factory()
        builder_agreement_factory(
            owner=hirl_company, company=architect_organization, state=BuilderAgreement.COUNTERSIGNED
        )

        mf_registration = hirl_project_registration_factory(
            registration_user=verifier_user,
            eep_program__slug="ngbs-sf-new-construction-2020-new",
            eep_program__owner=hirl_company,
            eep_program__customer_hirl_per_unit_fee=30,
            eep_program__viewable_by_company_type=f"{Company.PROVIDER_COMPANY_TYPE}, {Company.QA_COMPANY_TYPE}",
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            architect_organization=architect_organization,
            project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            story_count=1,
            number_of_units=1,
        )

        mf_project.registration.active()
        mf_project.create_home_status()
        mf_project.home_status.refresh_from_db()

        requirement = qa_requirement_factory(
            eep_program=mf_registration.eep_program,
            qa_company=hirl_company,
            type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
        )

        qa_status = qa_status_factory(
            requirement=requirement,
            state="correction_required",
            qa_designee=hirl_user,
            home_status=mf_project.home_status,
            hirl_certification_level_awarded=QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED,
        )

        home_status = EEPProgramHomeStatus.objects.get(id=mf_project.home_status.id)
        home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        home_status.certification_date = timezone.now() - timezone.timedelta(days=5)
        home_status.save()

        certificate_lookup_url = reverse_lazy(
            "api_v3:home_status-customer-hirl-certificate-lookup-list"
        )
        response = self.client.get(certificate_lookup_url, data={}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["address"], "479 Washington St, Providence, RI, 34342"
        )
        self.assertEqual(response.data["results"][0]["client_name"], architect_organization.name)
        self.assertEqual(response.data["results"][0]["company_info"]["name"], "Verifier Company")
        self.assertEqual(response.data["results"][0]["certification_level"], "Emerald")
        self.assertEqual(
            response.data["results"][0]["certification_date"],
            home_status.certification_date.strftime("%Y-%m-%d"),
        )
        self.assertEqual(
            response.data["results"][0]["certification_path"], mf_registration.eep_program.name
        )
        certification_link = response.data["results"][0]["certification_link"]
        hash_id = Hashid(home_status.id, salt=f"certificate{settings.HASHID_FIELD_SALT}")
        certificate_hash_id = hash_id.hashid
        hash_id = Hashid(
            mf_registration.registration_user.id, salt=f"user{settings.HASHID_FIELD_SALT}"
        )
        user_id = hash_id.hashid
        certification_public_link = reverse_lazy(
            "api_v3:home_status-certificate",
            args=(
                certificate_hash_id,
                user_id,
            ),
        )
        self.assertIn(f"{certification_public_link}", f"{certification_link}")
        response = self.client.get(certification_public_link)
        customer_hirl_certificate = CustomerHIRLCertificate(home_status=home_status, user=hirl_user)
        output_stream = customer_hirl_certificate.generate()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(response.content, output_stream.read())

    def test_public_certificate(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs",
            slug=customer_hirl_app.CUSTOMER_SLUG,
            is_eep_sponsor=True,
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_user = rater_admin_factory(
            first_name="Verifier User", company__name="Verifier Company"
        )

        SponsorPreferences.objects.get_or_create(
            sponsor=hirl_company, sponsored_company=verifier_user.company
        )

        builder_organization = builder_organization_factory()
        architect_organization = architect_organization_factory()
        builder_agreement_factory(
            owner=hirl_company, company=architect_organization, state=BuilderAgreement.COUNTERSIGNED
        )

        mf_registration = hirl_project_registration_factory(
            registration_user=verifier_user,
            eep_program__slug="ngbs-sf-new-construction-2020-new",
            eep_program__owner=hirl_company,
            eep_program__customer_hirl_per_unit_fee=30,
            eep_program__viewable_by_company_type=f"{Company.PROVIDER_COMPANY_TYPE}, {Company.QA_COMPANY_TYPE}",
            project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            architect_organization=architect_organization,
            project_client=HIRLProjectRegistration.PROJECT_CLIENT_ARCHITECT,
        )
        mf_project = hirl_project_factory(
            registration=mf_registration,
            home_address_geocode_response=None,
            home_status=SET_NULL,
            story_count=1,
            number_of_units=1,
        )

        mf_project.registration.active()
        mf_project.create_home_status()
        mf_project.home_status.refresh_from_db()

        requirement = qa_requirement_factory(
            eep_program=mf_registration.eep_program,
            qa_company=hirl_company,
            type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
        )

        qa_status = qa_status_factory(
            requirement=requirement,
            state="correction_required",
            qa_designee=hirl_user,
            home_status=mf_project.home_status,
            hirl_certification_level_awarded=QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED,
        )

        home_status = EEPProgramHomeStatus.objects.get(id=mf_project.home_status.id)
        home_status.state = EEPProgramHomeStatus.COMPLETE_STATE
        home_status.certification_date = timezone.now() - timezone.timedelta(days=5)
        home_status.save()
        certificate_public_url = reverse_lazy(
            "api_v3:home_status-customer-hirl-bulk-certicate-list"
        )
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(certificate_public_url, format="json")
        certification_link = response.data["results"][0]["certification_link"]

        hash_id = Hashid(home_status.id, salt=f"certificate{settings.HASHID_FIELD_SALT}")
        certificate_hash_id = hash_id.hashid
        hash_id = Hashid(hirl_user.id, salt=f"user{settings.HASHID_FIELD_SALT}")
        user_id = hash_id.hashid
        certification_public_link = reverse_lazy(
            "api_v3:home_status-certificate",
            args=(
                certificate_hash_id,
                user_id,
            ),
        )
        self.assertIn(f"{certification_public_link}", f"{certification_link}")
        response = self.client.get(certification_public_link)
        customer_hirl_certificate = CustomerHIRLCertificate(home_status=home_status, user=hirl_user)
        output_stream = customer_hirl_certificate.generate()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(response.content, output_stream.read())
