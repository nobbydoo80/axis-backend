__author__ = "Michael Jeffrey"
__date__ = "8/5/15 10:22 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import datetime
import random
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core import management
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from axis.annotation.models import Type as AnnotationType, Annotation
from axis.company.models import Company
from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import provider_admin_factory, rater_admin_factory
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase, AxisTestCaseUserMixin
from axis.core.utils import BlockTimer
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import hirl_project_factory
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import eep_program_custom_home_status_factory
from axis.home.tests.mixins import EEPProgramHomeStatusManagerTestMixin
from axis.qa.models import QAStatus, QARequirement
from ..tasks import (
    certify_single_home,
    set_abandoned_homes_task,
    export_home_data,
    export_home_program_report_task,
    new_certification_daily_email_task,
    pending_certification_daily_email_task,
    new_bpa_certification_daily_email_task,
    admin_daily_email_task,
    customer_hirl_homes_report_task,
)

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class CertifySingleHomeTests(AxisTestCase):
    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        from axis.home.tests.factories import certified_home_with_checklist_factory
        from axis.core.tests.factories import provider_admin_factory

        provider_user = provider_admin_factory()
        qc = 50

        for i in range(10):
            certified_home_with_checklist_factory(
                certifying_user=provider_user,
                certify=False,
                company=provider_user.company,
                eep_program__question_count=qc,
                eep_program__no_close_dates=True,
            )

    def test_certify_single_home(self):
        user = User.objects.get(company__company_type="provider")
        stats = EEPProgramHomeStatus.objects.all()
        cert_date = datetime.datetime.today().date()

        for i, stat in enumerate(stats):
            self.assertNotEqual(stat.state, "complete")
            with BlockTimer("certifying", stat=i):
                certify_single_home(user, stat, cert_date)
            stat = EEPProgramHomeStatus.objects.get(id=stat.id)
            self.assertEqual(stat.state, "complete")


class HomeTaskTest(EEPProgramHomeStatusManagerTestMixin, TestCase, AxisTestCaseUserMixin):
    client_class = AxisClient

    def test_set_abandoned_homes(self):
        modified_date = timezone.now() - datetime.timedelta(
            days=settings.HOME_ABANDON_EXPIRE_DAYS + 5
        )

        EEPProgramHomeStatus.objects.all().update(modified_date=modified_date)
        set_abandoned_homes_task()

        in_progress_count = EEPProgramHomeStatus.objects.exclude(
            state__in=["complete", "abandoned"]
        ).count()
        # all homes should be abandoned or completed
        self.assertEqual(in_progress_count, 0)

        with self.subTest("Exclude Customer HIRL Projects"):
            customer_hirl_program_slugs = (
                customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
                + customer_hirl_app.HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS
            )
            eep_program_custom_home_status_factory(
                eep_program__slug=random.choice(customer_hirl_program_slugs),
                state=EEPProgramHomeStatus.QA_PENDING_STATE,
            )

            set_abandoned_homes_task()

            in_progress_count = EEPProgramHomeStatus.objects.exclude(
                state__in=["complete", "abandoned"]
            ).count()

            self.assertEqual(in_progress_count, 1)

    @mock.patch("axis.home.tasks.tasks.messages.HomeStatusExportCompletedMessage.send")
    @mock.patch("axis.home.export_data.BaseHomeStatusDataDump.update_task_progress")
    def test_export_home_data(self, update_task_progress, send_message):
        user = self.user_model.objects.first()

        # prepare task arguments
        apd = AsynchronousProcessedDocument(
            company=user.company, download=True, task_name="export_home_data"
        )
        apd.save()
        export_fields = [
            "home",
            "subdivision",
            "community",
            "relationships",
            "eep_program",
            "floorplan",
            "simulation_basic",
        ]

        export_home_data(result_object_id=apd.pk, user_id=user.pk, export_fields=export_fields)

        update_task_progress.assert_called()
        send_message.assert_called_once()
        self.assertIsNotNone(apd.document)

    @mock.patch("axis.home.tasks.tasks.messages.HomeStatusProgramReportsCompletedMessage.send")
    @mock.patch("celery.app.task.Task.update_state")
    def test_export_home_program_report_task(self, update_task_progress, send_message):
        user = self.user_model.objects.first()

        # prepare task arguments
        apd = AsynchronousProcessedDocument(
            company=user.company, download=True, task_name="export_home_data"
        )
        apd.save()

        eep_program_home_statuses = EEPProgramHomeStatus.objects.filter_by_user(
            user=user
        ).values_list(flat=True)

        export_home_program_report_task(
            user_id=user.pk,
            result_object_id=apd.pk,
            homestatus_ids=list(eep_program_home_statuses),
            filter_info={},
        )

        update_task_progress.assert_called()
        send_message.assert_called_once()
        self.assertIsNotNone(apd.document)

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    def test_new_certification_daily_email_task(self):
        stat = EEPProgramHomeStatus.objects.first()
        stat.company.company_type = "rater"
        stat.certification_date = timezone.now()
        stat.eep_program.slug = "neea-efficient-homes"
        stat.save()
        stat.company.save()
        stat.eep_program.save()

        new_certification_daily_email_task()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Certified Homes in Axis", mail.outbox[0].subject)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Certified Homes", mail.outbox[0].subject)
        self.assertIn(str(stat.company), mail.outbox[0].body)
        self.assertIn(stat.home.get_addr(), mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn("<h5>%s</h5>" % stat.eep_program.name, mail.outbox[0].alternatives[0][0])
        self.assertIn(stat.home.get_addr(), mail.outbox[0].alternatives[0][0])

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    def test_new_certification_daily_email_task_with_custom_query(self):
        stats_list = list(EEPProgramHomeStatus.objects.all().values_list("pk", flat=True))
        new_certification_daily_email_task(stats_list=stats_list)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("Certified Homes in Axis", mail.outbox[0].subject)

    @mock.patch("axis.customer_neea.signals.notify_raterprovider_of_missing_associations_to_neea")
    def test_pending_certification_daily_email_task(self, notify_raterprovider_mock):
        program = basic_eep_program_factory(slug="neea-bpa")

        # prepare our home, set state certification_pending
        # and history of transitions to previous day
        stat = EEPProgramHomeStatus.objects.first()
        stat.eep_program = program
        stat.state = "pending_inspection"
        stat.save()

        # remove all other home_statuses from fixture compiler
        EEPProgramHomeStatus.objects.exclude(id=stat.id).delete()

        admin = stat.get_certification_agent().users.get(is_company_admin=True)

        from axis.messaging.models import MessagingPreference

        MessagingPreference.objects.create(
            message_name="PendingCertificationsDailyEmail",
            user=admin,
            category="home",
            receive_email=True,
            receive_notification=True,
        )

        notify_raterprovider_mock.assert_called_once()

        user = self.random_user
        stat.make_transition(transition="inspection_transition", user=user)
        stat.make_transition(transition="qa_transition", user=user)
        stat.make_transition(transition="certification_transition", user=user)
        stat.save()

        yesterday = timezone.now() - timezone.timedelta(days=1)

        for state_history in stat.state_history.all():
            state_history.start_time = yesterday
            state_history.save()

        pending_certification_daily_email_task()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("1 pending certification in Axis", mail.outbox[0].subject)
        self.assertIn(str(stat.company), mail.outbox[0].body)
        self.assertIn(stat.home.get_addr(), mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn("<h5>%s</h5>" % stat.company, mail.outbox[0].alternatives[0][0])
        self.assertIn(stat.home.get_addr(), mail.outbox[0].alternatives[0][0])

    def test_pending_certification_daily_email_task_with_custom_query(self):
        basic_eep_program_factory(slug="neea-bpa")

        from axis.messaging.models import MessagingPreference

        for stat in EEPProgramHomeStatus.objects.all():
            admin = stat.get_certification_agent().users.get(is_company_admin=True)
            MessagingPreference.objects.create(
                message_name="PendingCertificationsDailyEmail",
                user=admin,
                category="home",
                receive_email=True,
                receive_notification=True,
            )

        stats_list = list(EEPProgramHomeStatus.objects.all().values_list("pk", flat=True))
        pending_certification_daily_email_task(stats_list=stats_list)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("pending certification in Axis", mail.outbox[0].subject)

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    @mock.patch("axis.customer_neea.signals.notify_raterprovider_of_missing_associations_to_neea")
    def test_new_bpa_certification_daily_email_task(self, notify_raterprovider_mock):
        program = basic_eep_program_factory(slug="neea-bpa")

        stat = EEPProgramHomeStatus.objects.first()
        stat.certification_date = timezone.now()
        stat.eep_program = program
        stat.save()

        notify_raterprovider_mock.assert_called_once()

        new_bpa_certification_daily_email_task()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Certified Projects in Axis", mail.outbox[0].subject)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Certified Projects", mail.outbox[0].subject)
        self.assertIn(str(stat.company), mail.outbox[0].body)
        self.assertIn(stat.home.get_addr(), mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn("Contact NEEA's BetterBuiltNW team", mail.outbox[0].alternatives[0][0])
        self.assertIn(stat.home.get_addr(), mail.outbox[0].alternatives[0][0])

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    @mock.patch("axis.customer_neea.signals.notify_raterprovider_of_missing_associations_to_neea")
    def test_new_bpa_certification_daily_email_task_is_one_date_only(
        self, notify_raterprovider_mock
    ):
        program = basic_eep_program_factory(slug="neea-bpa")

        stat = EEPProgramHomeStatus.objects.first()
        stat.certification_date = timezone.now()
        stat.eep_program = program
        stat.save()
        stat = EEPProgramHomeStatus.objects.last()
        stat.certification_date = timezone.now() - datetime.timedelta(days=1)
        stat.eep_program = program
        stat.save()

        new_bpa_certification_daily_email_task()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Certified Projects in Axis", mail.outbox[0].subject)

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    def test_new_bpa_certification_daily_email_task_with_custom_query(self):
        basic_eep_program_factory(slug="neea-bpa")
        stats_list = list(EEPProgramHomeStatus.objects.all().values_list("pk", flat=True))
        new_bpa_certification_daily_email_task(stats_list=stats_list)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("Certified Projects in Axis", mail.outbox[0].subject)

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    def test_admin_daily_email_task(self):
        from axis.company.tests.factories import base_company_factory
        from axis.core.tests.factories import general_super_user_factory

        # created a companies required by certification_admin task
        base_company_factory(slug="eto")
        general_super_user_factory(company__slug="pivotal-energy-solutions")

        admin_daily_email_task()

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual("Light day in Axis.", mail.outbox[0].subject)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn("Incentives Generated", mail.outbox[0].alternatives[0][0])
        self.assertIn("Incentive Distributions created", mail.outbox[0].alternatives[0][0])
        self.assertIn("Programs added to homes", mail.outbox[0].alternatives[0][0])
        self.assertIn("Axis Simulations added", mail.outbox[0].alternatives[0][0])
        self.assertIn("Incentives Generated", mail.outbox[0].alternatives[0][0])
        self.assertIn("Green Building Registry ID", mail.outbox[0].alternatives[0][0])


class CustomerHIRLHomesReportTaskTests(AxisTestCase):
    def test_customer_hirl_homes_report_task(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        self.assertEqual(AsynchronousProcessedDocument.objects.count(), 0)

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

        # NGBS Legacy Home Status
        management.call_command(
            "build_program", "-p", "ngbs-sf-new-construction-2020", stdout=DevNull()
        )

        annotation_type = AnnotationType.objects.get(
            slug="certified-nat-gbs"
        )  # legacy certification-level annotation

        legacy_eep_program = EEPProgram.objects.get(slug="ngbs-sf-new-construction-2020")
        legacy_home_status = eep_program_custom_home_status_factory(
            company=rater.company,
            eep_program=legacy_eep_program,
            home__city=midlothian_city,
            home__builder_org__city=midlothian_city,
        )
        legacy_home_status.certification_date = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=1)
        legacy_home_status.save()

        Annotation.objects.create(
            content_type=ContentType.objects.get_for_model(legacy_home_status),
            object_id=legacy_home_status.id,
            content="Silver",
            type=annotation_type,
        )

        customer_hirl_homes_report_task()
        self.assertEqual(AsynchronousProcessedDocument.objects.count(), 1)
