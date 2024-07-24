"""test_set_fake_emails.py: """

__author__ = "Artem Hruzd"
__date__ = "04/14/2020 11:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.test import override_settings

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.management.commands.set_fake_emails import Command
from axis.core.tests.testcases import AxisTestCase

User = get_user_model()


class SetFakeEmailsCommandTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["utility", "rater", "general"]

    @override_settings(DEBUG=True)
    def test_without_args(self):
        emails = User.objects.values_list("email", flat=True)
        emails_count = len(emails)
        self.assertGreater(emails_count, 0)

        out = StringIO()
        generate_email = Command()
        call_command(generate_email, stdout=out)
        self.assertIn("Changed {} emails".format(emails_count), out.getvalue())

        emails = User.objects.values_list("email", flat=True)
        self.assertTrue(all(email.endswith("@example.com") for email in emails))

    @override_settings(DEBUG=True)
    def test_no_admin(self):
        emails = User.objects.values_list("email", flat=True)
        emails_count = len(emails)
        admins_count = User.objects.filter(is_superuser=True).count()
        self.assertGreater(emails_count, 0)

        generate_email = Command()
        out = StringIO()
        call_command(generate_email, "-a", stdout=out)
        self.assertIn("Changed {} emails".format(emails_count - admins_count), out.getvalue())

        emails = User.objects.filter(is_superuser=False).values_list("email", flat=True)
        self.assertTrue(all(email.endswith("@example.com") for email in emails))

    @override_settings(SERVER_TYPE=settings.PRODUCTION_SERVER_TYPE)
    def test_run_on_production(self):
        out = StringIO()
        with self.assertRaisesRegex(
            CommandError, expected_regex="Command is not available on production"
        ):
            call_command("set_fake_emails", verbosity=3, stdout=out, stderr=out)
