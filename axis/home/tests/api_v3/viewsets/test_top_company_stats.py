__author__ = "Naruhito Kaide"
__date__ = "05/26/2023 13:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Naruhito Kaide",
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
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import hirl_project_factory
from axis.eep_program.models import EEPProgram
from axis.geographic.models import City
from axis.geographic.tests.factories import real_city_factory
from axis.home.tests.factories import eep_program_custom_home_status_factory

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHirlTopCompaniesStatsTests(ApiV3Tests):
    @classmethod
    def setUpTestData(cls):
        super(CustomerHirlTopCompaniesStatsTests, cls).setUpTestData()
        midlothian_city = real_city_factory("Midlothian", "VA")
        cls.midlothian_city = midlothian_city

        phoenix_city = real_city_factory("Phoenix", "AZ")
        cls.phoenix_city = phoenix_city

        cls.hirl_user = provider_admin_factory(
            company__city=midlothian_city,
            company__slug=customer_hirl_app.CUSTOMER_SLUG,
            company__is_eep_sponsor=True,
            username="hirl_admin",
        )
        rater = rater_admin_factory(company__city=midlothian_city, username="rater")
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
            home__city=midlothian_city,
            home__zipcode="23112",
            home__builder_org__city=midlothian_city,
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

        cls.project = hirl_project_factory(
            registration=registration, home_status=home_status, number_of_units=1
        )

        # B Home Status
        home_status2 = eep_program_custom_home_status_factory(
            company=rater.company,
            eep_program=eep_program,
            home__street_line1="7240 N Dreamy Draw",
            home__city=phoenix_city,
            home__zipcode="85020",
            home__builder_org__city=phoenix_city,
        )
        home_status2.certification_date = yesterday
        home_status2.state = "in_progress"
        home_status2.save()

        cls.home_status2 = home_status2

        registration2 = HIRLProjectRegistration.objects.create(
            registration_user=rater,
            eep_program=eep_program,
            builder_organization=Company.objects.filter(
                company_type=Company.BUILDER_COMPANY_TYPE
            ).get(id=home_status2.home.get_builder().id),
        )
        cls.registration2 = registration2

        cls.project2 = hirl_project_factory(
            registration=registration2, home_status=home_status2, number_of_units=1
        )

        cls.rater = rater

    def test_setUpData(self):
        self.assertEqual(City.objects.count(), 2)

    def test_companies_for_certified_by_count(self):
        EEPProgram.objects.update(slug="ngbs-mf-new-construction-2020-new", is_multi_family=True)

        url = reverse_lazy("api_v3:home_status-customer-hirl-top-company-stats")
        self.client.force_authenticate(user=self.hirl_user)
        response = self.client.get(url, format="json")
        data = response.data
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )
        self.assertEqual(
            list(response.data["companies_by_project_count"]),
            [
                {
                    "company_name": self.rater.company.name,
                    "projects_count": 2,
                }
            ],
        )

        self.assertEqual(
            list(response.data["companies_by_unit_count"]),
            [
                {
                    "company_name": self.rater.company.name,
                    "total_units": 4,
                }
            ],
        )
