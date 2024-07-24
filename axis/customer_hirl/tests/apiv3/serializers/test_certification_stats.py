__author__ = "Steven K"
__date__ = "1/2/22 10:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.apps import apps
from django.core import management
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status

from axis.company.models import Company
from axis.core.tests.factories import provider_admin_factory, rater_admin_factory
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import ApiV3Tests
from axis.customer_hirl.api_v3.serializers import CertificationMetricSerializer
from axis.customer_hirl.models import HIRLProjectRegistration, HIRLProject
from axis.customer_hirl.tests.factories import hirl_project_factory
from axis.eep_program.models import EEPProgram
from axis.geographic.models import City
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import eep_program_custom_home_status_factory

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHirlHomeStatusMetricsTests(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        super(CustomerHirlHomeStatusMetricsTests, cls).setUpTestData()
        city = real_city_factory("Midlothian", "VA")

        cls.hirl_user = provider_admin_factory(
            company__city=city,
            company__slug=customer_hirl_app.CUSTOMER_SLUG,
            company__is_eep_sponsor=True,
            username="hirl_admin",
        )
        rater = rater_admin_factory(company__city=city, username="rater")
        # Program
        management.call_command(
            "build_program", "-p", "ngbs-sf-new-construction-2020-new", stdout=DevNull()
        )
        eep_program = EEPProgram.objects.get()
        cls.eep_program = eep_program

        yesterday = timezone.now() - timezone.timedelta(days=1)

        # A Home Status
        home_status = eep_program_custom_home_status_factory(
            company=rater.company,
            eep_program=eep_program,
            home__street_line1="9701 Brading Lane",
            home__city=city,
            home__zipcode="23112",
            home__builder_org__city=city,
        )
        home_status.certification_date = yesterday
        home_status.state = "complete"
        home_status.save()

        cls.home_status = home_status

        registration = HIRLProjectRegistration.objects.create(
            registration_user=rater,
            eep_program=eep_program,
            builder_organization=Company.objects.filter(
                company_type=Company.BUILDER_COMPANY_TYPE
            ).get(id=home_status.home.get_builder().id),
        )
        cls.registration = registration

        cls.project = hirl_project_factory(registration=registration, home_status=home_status)

        cls.serializer = CertificationMetricSerializer()
        cls.queryset = EEPProgramHomeStatus.objects.all()

    def test_setUpData(self):
        self.assertEqual(City.objects.count(), 1)

    def test_serializer_single_family_counts(self):
        key = "single_family"
        data = self.serializer.to_representation(self.queryset)
        with self.subTest("Certified"):
            self.assertEqual(data[key]["program_ids"], [self.eep_program.id])
            self.assertEqual(data[key]["certified_buildings"], 1)
            self.assertEqual(data[key]["certified_units"], 0)
            self.assertEqual(data[key]["in_progress_buildings"], 0)
            self.assertEqual(data[key]["in_progress_units"], 0)
            self.assertEqual(data[key]["abandoned_buildings"], 0)
            self.assertEqual(data[key]["abandoned_units"], 0)

        self.queryset.update(state="in_progress")
        data = self.serializer.to_representation(self.queryset)
        with self.subTest("In-Progress"):
            self.assertEqual(data[key]["certified_buildings"], 0)
            self.assertEqual(data[key]["certified_units"], 0)
            self.assertEqual(data[key]["in_progress_buildings"], 1)
            self.assertEqual(data[key]["in_progress_units"], 0)
            self.assertEqual(data[key]["abandoned_buildings"], 0)
            self.assertEqual(data[key]["abandoned_units"], 0)

        self.queryset.update(state="abandoned")
        data = self.serializer.to_representation(self.queryset)
        with self.subTest("In-Progress"):
            self.assertEqual(data[key]["certified_buildings"], 0)
            self.assertEqual(data[key]["certified_units"], 0)
            self.assertEqual(data[key]["in_progress_buildings"], 0)
            self.assertEqual(data[key]["in_progress_units"], 0)
            self.assertEqual(data[key]["abandoned_buildings"], 1)
            self.assertEqual(data[key]["abandoned_units"], 0)

        self.queryset.update(state="complete")

        HIRLProject.objects.update(number_of_units=10)
        data = self.serializer.to_representation(self.queryset)
        with self.subTest("Unit Count new Style"):
            self.assertEqual(data[key]["certified_buildings"], 1)
            self.assertEqual(data[key]["certified_units"], 10)
            self.assertEqual(data[key]["in_progress_buildings"], 0)
            self.assertEqual(data[key]["in_progress_units"], 0)
            self.assertEqual(data[key]["abandoned_buildings"], 0)
            self.assertEqual(data[key]["abandoned_units"], 0)

    def test_endpoint(self):
        """This os here simply b/c the serializer is doing the real work and I wanted coverage"""
        url = reverse_lazy("api_v3:home_status-hirl-program-stats")
        self.client.force_authenticate(user=self.hirl_user)
        response = self.client.get(url, format="json")
        data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

        key = "single_family"
        with self.subTest("Certified with eep sponsor"):
            self.assertEqual(data[key]["program_ids"], [self.eep_program.id])
            self.assertEqual(data[key]["certified_buildings"], 1)
            self.assertEqual(data[key]["certified_units"], 0)
            self.assertEqual(data[key]["in_progress_buildings"], 0)
            self.assertEqual(data[key]["in_progress_units"], 0)
            self.assertEqual(data[key]["abandoned_buildings"], 0)
            self.assertEqual(data[key]["abandoned_units"], 0)
