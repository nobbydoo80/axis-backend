"""test_eep_program_home_status.py - Axis"""

__author__ = "Michael Jeffrey"
__date__ = "11/5/15 6:08 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import datetime
import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.test import TestCase

from axis.annotation.models import Type as AnnotationType, Annotation
from axis.company.models import BuilderOrganization, Company
from axis.core.tests.factories import provider_admin_factory, rater_admin_factory
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase, AxisTestCaseUserMixin
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import hirl_project_factory
from axis.eep_program.models import EEPProgram
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import eep_program_custom_home_status_factory
from axis.home.tests.mixins import EEPProgramHomeStatusManagerTestMixin
from axis.qa.models import QAStatus, QARequirement

log = logging.getLogger(__name__)
User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class EEPProgramHomeStatusManagerTests(
    EEPProgramHomeStatusManagerTestMixin, TestCase, AxisTestCaseUserMixin
):
    def test_user_can_retrieve_own_home_stat(self):
        """
        The User's company is the company on the status.
        They should always be able to see it.
        """
        general_user = User.objects.get(company__name="Provider1")
        stats = EEPProgramHomeStatus.objects.filter_by_company(general_user.company)

        self.assertGreater(stats.count(), 0)
        self.assertLess(stats.count(), EEPProgramHomeStatus.objects.count())
        # Allow for relationship returned stats.
        self.assertGreaterEqual(
            stats.count(), EEPProgramHomeStatus.objects.filter(company=general_user.company).count()
        )

    def test_user_can_retrieve_mutual_relations_home_stat(self):
        """
        The User's company has a mutual relationship with the Company on the status and EEPProgram.
        They should be able to see it.
        """
        stat_owner = User.objects.get(company__name="Provider1")
        general_user = User.objects.get(company__name="General1")
        # Don't test against that have restrictions.
        relationships_stats = EEPProgramHomeStatus.objects.filter(
            company=stat_owner.company, eep_program__viewable_by_company_type__isnull=True
        )

        # Assert mutual relationship

        stats = EEPProgramHomeStatus.objects.filter_by_company(general_user.company)

        for stat in relationships_stats:
            self.assertIn(stat, list(stats))

    def test_user_can_retrieve_home_stats_belonging_to_companies_eep_program(self):
        """
        The User's company owns the EEPProgram, and is a sponsor.
        They should be able to see it.
        """
        eep_owner = User.objects.get(company__name="EEP1")

        stats = EEPProgramHomeStatus.objects.filter_by_company(eep_owner.company)

        self.assertListEqual(
            list(stats),
            list(EEPProgramHomeStatus.objects.filter(eep_program__owner=eep_owner.company)),
        )

    def test_user_matching_program_restriction_can_retrieve_mutual_relations_home_stat(self):
        """
        The User's company has a mutual relationship with the Company on the Status.
        There is a company_type specified in the viewable_by_company_type field on the program.
        The User's company is one of those types.
        They should be able to see it.
        """
        stat_owner_user = User.objects.get(company__name="Provider1")
        qa_user = User.objects.get(company__name="QA1")
        # Only get stat who's program is restricted to the User's company_type.
        restricted_home_status = EEPProgramHomeStatus.objects.filter(
            company=stat_owner_user.company, eep_program__viewable_by_company_type__contains="qa"
        ).first()

        # Assert mutual relationship

        stats = EEPProgramHomeStatus.objects.filter_by_company(qa_user.company)

        self.assertIn(restricted_home_status, list(stats))

    def test_user_not_matching_program_restriction_cannot_retrieve_mutual_relations_home_stat(self):
        """
        The User's company has a mutual relationship with the Company on the Status.
        There is a company_type specified in teh viewable_by_company_type field on the program.
        The User's company is not one of those types.
        They should not be able to see it.
        """
        stat_owner_user = User.objects.get(company__name="Provider1")
        general_user = User.objects.get(company__name="General1")
        # Check against programs we know have restrictions on them.
        restricted_home_status = EEPProgramHomeStatus.objects.filter(
            company=stat_owner_user.company, eep_program__viewable_by_company_type__isnull=False
        ).first()

        # Assert mutual relationship

        stats = EEPProgramHomeStatus.objects.filter_by_company(general_user.company)

        self.assertNotIn(restricted_home_status, list(stats))

    def test_annotate_customer_hirl_certification_level(self):
        midlothian_city = real_city_factory("Midlothian", "VA")
        phoenix_city = real_city_factory("Phoenix", "AZ")

        hirl_user = provider_admin_factory(
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
        eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020-new")

        # NGBS HIRL Project Home Status
        home_status = eep_program_custom_home_status_factory(
            company=rater.company,
            eep_program=eep_program,
            home__street_line1="9701 Brading Lane",
            home__street_line2="",
            home__zipcode="23112",
            home__city=midlothian_city,
            home__builder_org__city=midlothian_city,
        )
        home_status.certification_date = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=1)
        home_status.save()

        registration = HIRLProjectRegistration.objects.create(
            registration_user=rater,
            eep_program=eep_program,
            builder_organization=Company.objects.get(id=home_status.home.get_builder().id),
        )
        project = hirl_project_factory(
            registration=registration, home_status=home_status, city=midlothian_city
        )

        requirement = QARequirement.objects.create(
            qa_company=hirl_user.company,
            eep_program=eep_program,
            type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
        )
        QAStatus.objects.create(
            owner=hirl_user.company,
            requirement=requirement,
            home_status=home_status,
            hirl_certification_level_awarded=QAStatus.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED,
        )

        certification_levels = (
            EEPProgramHomeStatus.objects.filter(id=home_status.id)
            .annotate_customer_hirl_certification_level()
            .values_list("certification_level", flat=True)
        )

        self.assertEqual(
            list(certification_levels),
            [
                QAStatus.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED,
            ],
        )


class EEPProgramHomeStatusModelVerifyOrCreateTests(AxisTestCase):
    """Test out eep  app"""

    pass
