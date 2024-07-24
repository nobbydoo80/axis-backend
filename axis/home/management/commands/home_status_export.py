"""home_status_export.py - Axis"""

import logging
import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError

from axis.eep_program.models import EEPProgram
from axis.home.export_data import HomeDataXLSExport, ReportOn

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/11/20 11:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

User = get_user_model()


class Command(BaseCommand):
    help = "Dump Project export"
    requires_system_checks = False

    default_report_on = list(ReportOn.keys())

    def add_arguments(self, parser):
        parser.add_argument("--search", action="store", dest="search", help="Search Bar")
        parser.add_argument("--program", action="store", dest="program", help="Program ID or Slug")
        parser.add_argument("--user", action="store", dest="user", help="User ID or username")
        parser.add_argument(
            "--report_on",
            action="store",
            dest="report_on",
            help="Report on what areas",
            default=",".join(self.default_report_on),
        )
        parser.add_argument(
            "--max_num",
            action="store",
            dest="max_num",
            type=int,
            help="Maximum number of results",
            required=False,
        )
        parser.add_argument(
            "--filename", action="store", dest="filename", help="Output File (depending on action)"
        )

    def set_options(
        self,
        program=None,
        user=None,
        filename=None,
        search=None,
        report_on=None,
        max_num=None,
        **options,
    ):
        if not any([user]):
            raise CommandError("You must supply a user")

        result = {}

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
        result["user_id"] = user.id

        if program:
            program = program.split(",") if "," in program else [program]
            program_count = len(program)
            try:
                program = EEPProgram.objects.filter(id__in=program)
            except ValueError:
                program = EEPProgram.objects.filter(slug__in=program)
            if not program.count():
                program = EEPProgram.objects.filter(slug__in=program)

            if program.count() != program_count:
                raise CommandError(
                    "Expected %d programs only found %d" % (program_count, program.count())
                )

            log.info("Using %d programs %s", program_count, program.values_list("slug", flat=True))
            result["eep_program_id"] = list(program.values_list("pk", flat=True))

        if search:
            result["search_bar"] = search

        result["home_field"] = True
        result["customer_eto_field"] = True
        result["reuse_storage"] = False

        if report_on is None:
            result["report_on"] = self.default_report_on
            report_on = self.default_report_on
        else:
            report_on = report_on.split(",")
            bad = [x for x in report_on if x not in self.default_report_on]
            if bad:
                msg = "Bad options: %s must be in %r"
                raise CommandError(msg % (", ".join(bad), self.default_report_on))
        result["report_on"] = report_on
        if max_num:
            result["max_num"] = max_num

        if filename:
            if not os.path.exists(os.path.dirname(os.path.expanduser(filename))):
                raise CommandError(
                    "Output Path does not exist %r" % os.path.dirname(os.path.expanduser(filename))
                )
            log.info("Output to %s" % os.path.expanduser(filename))
            result["filename"] = os.path.expanduser(filename)

        return result

    def handle(self, use_injector=False, *args, **options):
        kwargs = self.set_options(**options)

        def update(**kwargs):
            log.debug("Progress Step %(current)s", kwargs)

        obj = HomeDataXLSExport(**kwargs)
        obj.update_task = update

        output = kwargs.get("filename", "HSR_report.xlsx")
        obj.write(output=output)
        obj.print_sample(max_num=2)

        print("Output saved to: %s" % os.path.abspath(os.path.join(os.curdir, output)))
