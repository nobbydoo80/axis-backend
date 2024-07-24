"""build_sql_triggers.py: Django """


import logging
import os

from django.core.management import BaseCommand

from ...utils import AEC_Triggers, runcmd

__author__ = "Steven Klass"
__date__ = "01/30/2019 09:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

DEFAULT_TRIGGER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "sql", "triggers.sql")
)


class Command(BaseCommand):
    help = "Creates SQL Trigger file for use when the REM/Rate DB gets updated"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            help="Output SQL Trigger file",
            action="store",
            dest="output",
            type=str,
            default=DEFAULT_TRIGGER,
        )
        parser.add_argument(
            "--no_update", help="Do Not update MySQL", action="store_false", dest="update"
        )
        parser.add_argument(
            "--host", help="MySQL Host", action="store", dest="host", type=str, default="127.0.0.1"
        )
        parser.add_argument(
            "--sql_logging",
            action="store_true",
            dest="sql_logging",
            help="Store log events in SQL as this happens",
        )
        parser.add_argument(
            "-u",
            "--user",
            help="MySQL User",
            action="store",
            dest="user",
            type=str,
            default="axis_test",
        )
        parser.add_argument(
            "-p",
            "--password",
            help="MySQL password",
            action="store",
            dest="password",
            type=str,
            default="password",
        )

    def handle(self, *args, **options):
        trigger = AEC_Triggers(output_file=options["output"], use_sql_log=options["sql_logging"])
        trigger.build()
        trigger.save()
        if options.get("update"):
            cmd = "mysql -u%(user)s -p%(password)s -h%(host)s remrate < " % options
            runcmd(cmd + "%s" % options["output"])
        self.stdout.write("Output SQL saved to %(output)s" % options)
