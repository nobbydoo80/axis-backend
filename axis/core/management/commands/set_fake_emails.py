"""
set_fake_emails.py
    Give all users a new email account. Useful for testing in a
    development environment. As such, this command is only available when
    setting.DEBUG is True.
"""


from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

__author__ = "Artem Hruzd"
__date__ = "04/14/2020 11:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


User = get_user_model()
DEFAULT_FAKE_EMAIL = "%(username)s@example.com"


class Command(BaseCommand):
    help = """
    DEBUG only: give all users a new email based on their account data ("%s" by default).
    Possible parameters are: username, first_name, last_name""" % (
        DEFAULT_FAKE_EMAIL,
    )
    requires_system_checks = []

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--email",
            dest="default_email",
            default=DEFAULT_FAKE_EMAIL,
            help="Use this as the new email format.",
        )
        parser.add_argument(
            "-a",
            "--no-admin",
            action="store_true",
            dest="no_admin",
            default=False,
            help="Do not change administrator accounts",
        )

    def handle(self, *args, **options):
        if settings.SERVER_TYPE == settings.PRODUCTION_SERVER_TYPE:
            raise CommandError("Command is not available on production")

        email = options["default_email"]
        no_admin = options["no_admin"]

        users = User.objects.all()
        if no_admin:
            users = users.exclude(is_superuser=True)
        objs = []
        for user in users:
            user.email = email % {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            objs.append(user)
        User.objects.bulk_update(objs, ["email"])
        self.stdout.write(f"Changed {len(objs)} emails")
