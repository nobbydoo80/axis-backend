"""test_management.py - axis"""

__author__ = "Steven K"
__date__ = "1/18/23 14:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import os
from unittest import mock, skipIf

from django.conf import settings
from django.core import management
from django.core.management import CommandError

from analytics.builder.builder import EEPProgram
from axis.annotation.models import Annotation
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_eto.tests.program_checks.test_eto_2022 import ETO2022ProgramCompleteTestMixin
from axis.filehandling.models import CustomerDocument
from axis.gbr.models import GreenBuildingRegistry, GbrStatus
from axis.gbr.tasks import collect_missing_eto_gbr_registry_entries
from axis.gbr.tests.mocked_responses import gbr_mocked_response
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


@mock.patch("axis.gbr.gbr.GreenBuildingRegistryAPIConnect.post", side_effect=gbr_mocked_response)
class GBRManagementTests(ETO2022ProgramCompleteTestMixin, AxisTestCase):
    def run_management_command(self, **kw):
        args = ["create_gbr"]

        if kw.get("home"):
            args += [
                "--home",
                kw.get("home").id if hasattr(kw.get("home"), "pk") else kw.get("home"),
            ]
        elif kw.get("home_status"):
            args += [
                "--home-status",
                kw.get("home_status").id
                if hasattr(kw.get("home_status"), "pk")
                else kw.get("home_status"),
            ]
        elif kw.get("program"):
            args += [
                "--program",
                kw.get("program").slug if hasattr(kw.get("program"), "pk") else kw.get("program"),
            ]
        if kw.get("status"):
            args += ["--status", kw.get("status")]
        if kw.get("force"):
            args += ["--force"]
        if kw.get("max_count"):
            args += ["--max_count", kw.get("max_count")]

        with open(os.devnull, "w") as stdout:
            management.call_command(*args, stdout=stdout, stderr=stdout)

    def test_options(self, _mock):
        with self.subTest("No args"):
            self.assertEqual(self.home_status.state, "inspection")
            self.assertRaises(CommandError, self.run_management_command)
        with self.subTest("program"):
            self.assertRaises(CommandError, self.run_management_command, program="eto")
        with self.subTest("home"):
            self.assertRaises(CommandError, self.run_management_command, home=self.home)
        with self.subTest("home_status"):
            self.assertRaises(
                CommandError, self.run_management_command, home_status=self.home_status
            )

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysqlXXX",
        "Only can be run on MYSQL Engine - We are using concurrent threaded operations",
    )
    def test_status_qa_pending(self, _mock):
        Annotation.objects.all().delete()
        EEPProgramHomeStatus.objects.filter(id=self.home_status.id).update(state="qa_pending")
        self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)

        with self.subTest("program"):
            self.run_management_command(
                program=self.home_status.eep_program.id, status="qa_pending"
            )
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(GreenBuildingRegistry.objects.get().status, GbrStatus.PROPERTY_VALID)
            self.assertEqual(CustomerDocument.objects.count(), 0)
        with self.subTest("program slug"):
            GreenBuildingRegistry.objects.all().delete()
            self.run_management_command(
                program=self.home_status.eep_program.slug, status="qa_pending"
            )
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(GreenBuildingRegistry.objects.get().status, GbrStatus.PROPERTY_VALID)
            self.assertEqual(CustomerDocument.objects.count(), 0)
        with self.subTest("home"):
            GreenBuildingRegistry.objects.all().delete()
            self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
            self.run_management_command(home=self.home_status.home.id, status="qa_pending")
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(GreenBuildingRegistry.objects.get().status, GbrStatus.PROPERTY_VALID)
            self.assertEqual(CustomerDocument.objects.count(), 0)
        with self.subTest("home_status"):
            GreenBuildingRegistry.objects.all().delete()
            self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
            self.run_management_command(home_status=self.home_status, status="qa_pending")
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(GreenBuildingRegistry.objects.get().status, GbrStatus.PROPERTY_VALID)
            self.assertEqual(CustomerDocument.objects.count(), 0)

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysqlXXX",
        "Only can be run on MYSQL Engine - We are using concurrent threaded operations",
    )
    def test_status_complete(self, _mock):
        Annotation.objects.all().delete()
        EEPProgramHomeStatus.objects.filter(id=self.home_status.id).update(
            state="complete", certification_date=datetime.datetime.now()
        )
        self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)

        with self.subTest("program"):
            self.run_management_command(program=self.home_status.eep_program.id)
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(
                GreenBuildingRegistry.objects.get().status, GbrStatus.ASSESSMENT_CREATED
            )
            self.assertEqual(CustomerDocument.objects.count(), 1)
        with self.subTest("home"):
            GreenBuildingRegistry.objects.all().delete()
            CustomerDocument.objects.all().delete()
            self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
            self.run_management_command(home=self.home_status.home.id)
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(
                GreenBuildingRegistry.objects.get().status, GbrStatus.ASSESSMENT_CREATED
            )
            self.assertEqual(CustomerDocument.objects.count(), 1)
        with self.subTest("home_status"):
            GreenBuildingRegistry.objects.all().delete()
            CustomerDocument.objects.all().delete()
            self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
            self.run_management_command(home_status=self.home_status)
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(
                GreenBuildingRegistry.objects.get().status, GbrStatus.ASSESSMENT_CREATED
            )
            self.assertEqual(CustomerDocument.objects.count(), 1)

        with self.subTest("Force"):
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertRaises(
                CommandError, self.run_management_command, home_status=self.home_status
            )
            self.run_management_command(home_status=self.home_status, force=True)
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(
                GreenBuildingRegistry.objects.get().status, GbrStatus.ASSESSMENT_CREATED
            )
            self.assertEqual(CustomerDocument.objects.count(), 1)

        with self.subTest("Max Count"):
            GreenBuildingRegistry.objects.all().delete()
            CustomerDocument.objects.all().delete()
            self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
            self.run_management_command(home_status=self.home_status, max_count=1)
            self.assertEqual(GreenBuildingRegistry.objects.count(), 1)
            self.assertEqual(
                GreenBuildingRegistry.objects.get().status, GbrStatus.ASSESSMENT_CREATED
            )
            self.assertEqual(CustomerDocument.objects.count(), 1)

    def test_daily_wrapup_fail(self, _mock):
        Annotation.objects.all().delete()
        EEPProgramHomeStatus.objects.filter(id=self.home_status.id).update(
            state="complete", certification_date=datetime.datetime.now()
        )
        self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)

        EEPProgram.objects.filter(slug="eto-2022").update(slug="eto-2016")

        GreenBuildingRegistry.objects.all().delete()
        result = collect_missing_eto_gbr_registry_entries()
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["result"], "")

    @skipIf(
        settings.DATABASES["default"]["ENGINE"] != "django.db.backends.mysqlXXX",
        "Only can be run on MYSQL Engine - We are using concurrent threaded operations",
    )
    def test_daily_wrapup_success(self, _mock):
        Annotation.objects.all().delete()
        EEPProgramHomeStatus.objects.filter(id=self.home_status.id).update(
            state="complete", certification_date=datetime.datetime.now()
        )
        self.assertEqual(GreenBuildingRegistry.objects.count(), 0)
        self.assertEqual(FastTrackSubmission.objects.count(), 1)

        EEPProgram.objects.filter(slug="eto-2022").update(slug="eto-2016")

        GreenBuildingRegistry.objects.all().delete()
        result = collect_missing_eto_gbr_registry_entries()
        self.assertEqual(result["status"], "success")
        self.assertNotEqual(result["result"], "")
