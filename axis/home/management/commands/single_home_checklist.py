"""single_home_checklist.py: Django """


import logging.config
import os

from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from axis.eep_program.models import EEPProgram
from axis.home.models import Home, EEPProgramHomeStatus
from axis.home.single_home_checklist import SingleHomeChecklist

__author__ = "Steven Klass"
__date__ = "01/11/2019 10:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = "Upload/Download a single home checklist"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--action",
            action="store",
            dest="action",
            default="write",
            choices=["write", "read"],
            help="Are we reading or writing checklist ('read' requires a template sent via --filename)",
        )
        parser.add_argument("--home", action="store", dest="home", type=int, help="Home ID")
        parser.add_argument(
            "--home-status", action="store", dest="home_status", type=int, help="Project ID"
        )
        parser.add_argument("--program", action="store", dest="program", help="Program ID or Slug")
        parser.add_argument("--user", action="store", dest="user", help="User ID or username")
        parser.add_argument(
            "--filename",
            action="store",
            dest="filename",
            help="Input or Output File (depending on action)",
        )
        parser.add_argument(
            "--no-lock", action="store_false", dest="lock_and_hide", help="Lock and hide sheets"
        )

    def set_options(
        self,
        action=None,
        home=None,
        home_status=None,
        program=None,
        user=None,
        filename=None,
        **options,
    ):
        # if not any([home, home_status, program]):
        #     raise CommandError("You must supply a home, home_status, or program")

        result = {}
        if home:
            try:
                home = Home.objects.get(id=home)
            except Home.DoesNotExist:
                raise CommandError("Home with ID %s does not exist" % home)
            log.info("Using %s" % home)

        if home_status:
            try:
                home_status = EEPProgramHomeStatus.objects.get(id=home_status)
            except EEPProgramHomeStatus.DoesNotExist:
                raise CommandError("EEPProgramHomeStatus with ID %s does not exist" % home_status)
            log.info("Using %s" % home_status)
            result["home_status"] = home_status

        if program:
            try:
                program = EEPProgram.objects.get(id=program)
            except EEPProgram.DoesNotExist:
                raise CommandError("EEPProgram with ID %s does not exist" % program)
            except ValueError:
                try:
                    program = EEPProgram.objects.get(slug=program)
                except EEPProgram.DoesNotExist:
                    raise CommandError("EEPProgram with slug %s does not exist" % program)
            log.info("Using %s" % program)
            result["program"] = program

        if home and not home_status:
            try:
                home_status = home.homestatuses.get()
            except MultipleObjectsReturned:
                if not program:
                    raise CommandError(
                        "Multiple Programs on home with ID %s exist and no program given" % home.pk
                    )
                try:
                    home_status = home.homestatuses.get(eep_program=program)
                except ObjectDoesNotExist:
                    raise CommandError("Program on home with ID %s does not exist" % home.pk)
            log.info("Derived %s" % home_status)
            result["home_status"] = home_status

        if user:
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise CommandError("User with ID %s does not exist" % user)
            except ValueError:
                try:
                    user = User.objects.get(username=user)
                except User.DoesNotExist:
                    raise CommandError("User with username %s does not exist" % user)
            log.info("Using %s" % user)
            result["user"] = user
            log.info("Derived %s" % user.company)
            result["company"] = user.company
        else:
            if home_status:
                user = home_status.company.users.filter(is_active=True).first()
            elif program:
                user = User.objects.filter(is_superuser=True).first()
            else:
                raise CommandError("No user provided given the options")
            log.info("Derived %s" % user)
            result["user"] = user
            log.info("Derived %s" % user.company)
            result["company"] = user.company

        if action == "write":
            if not os.path.exists(os.path.dirname(os.path.expanduser(filename))):
                raise CommandError(
                    "Output Path does not exist %r" % os.path.dirname(os.path.expanduser(filename))
                )
            log.info("Output to %s" % os.path.expanduser(filename))
            result["filename"] = os.path.expanduser(filename)

        else:
            if not os.path.exists(os.path.expanduser(filename)):
                raise CommandError("Input Path does not exist %r" % os.path.expanduser(filename))
            log.info("Input %s" % os.path.expanduser(filename))
            result["filename"] = os.path.expanduser(filename)
        return result

    def handle(self, use_injector=False, *args, **options):
        kwargs = self.set_options(**options)

        single_home = SingleHomeChecklist(user=kwargs["user"], company=kwargs["company"])
        setattr(single_home.log, "set_flags", lambda **kwargs: None)

        if options["action"] == "write":
            single_home.write(
                home_status_id=kwargs["home_status"].pk if kwargs.get("home_status") else None,
                program_id=kwargs["program"].pk if kwargs.get("program") else None,
                output=kwargs["filename"] if kwargs.get("filename") else None,
                lock_and_hide=options.get("lock_and_hide"),
            )
            log.info("Wrote file to %(filename)s", kwargs)
        else:
            single_home.read(kwargs["filename"] if kwargs.get("filename") else None)
            single_home.validate_data()
            single_home.process_data()
            log.info("Processed file to %(filename)s", kwargs)
