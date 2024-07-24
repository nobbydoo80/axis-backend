"""build_program.py: Django """

__author__ = "Steven Klass"
__date__ = "02/15/2019 08:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import importlib
import inspect
import logging
import os
from collections.abc import Iterable

from django.apps import apps
from django.core.management import BaseCommand, CommandError

from axis.eep_program.models import EEPProgram
from axis.eep_program.program_builder.base import ProgramBuilder

log = logging.getLogger(__name__)

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "program_builder"))


def get_programs():
    """This will return all programs

    Note: If you are looking to add programs to this thing you create your programs
    using the Baseclass of ProgramBuilder and add a method to the app_config named\
    eep_programs like so:

    @property
    def eep_programs(self):
        return [
            symbol_by_name(f"{self.name}.eep_programs:<Name>"),
        ]

    """

    app_configs = apps.get_app_configs()

    programs = []
    for app in app_configs:
        try:
            _programs = app.eep_programs
        except AttributeError:
            continue
        else:
            if not isinstance(_programs, Iterable):
                _programs = [_programs]
            programs += list(_programs)

    return {
        cls.slug: {"object": cls, "roles": cls.measures.keys()}
        for cls in ProgramBuilder.__subclasses__()
        if cls.slug
    }


class Command(BaseCommand):
    """Base command to run program builder"""

    help = "Runs Program Builder for a Program"
    requires_system_checks = []

    def add_arguments(self, parser):
        """Add arguments"""
        parser.add_argument(
            "-p",
            "--program",
            action="store",
            dest="program",
            type=str,
            help="Which program do you want to run this on",
        )
        parser.add_argument(
            "-r",
            "--role",
            action="store",
            dest="role",
            type=str,
            required=False,
            help="Which role do you want to target",
        )
        parser.add_argument(
            "-W",
            "--wipe",
            action="store_true",
            dest="wipe",
            help="Wipe this thing",
            default=None,
        )
        parser.add_argument(
            "--no_close_dates",
            action="store_true",
            dest="no_close_dates",
            help="No close dates - Used on tests.",
            default=False,
        )

        parser.add_argument(
            "--warn_only",
            action="store_true",
            dest="warn_only",
            help="Don't raise validation exceptions",
            default=None,
        )

    def handle(self, *args, **options):
        """Do the work"""

        programs = get_programs()
        if options["program"] not in programs:
            programs = "\n  •".join(programs.keys())
            print("Program was not found in:\n  •%s" % programs)
            raise CommandError(f"Program {options['program']!r} not found")

        roles = programs[options["program"]]["roles"]
        if not roles:
            builder = programs[options["program"]]["roles"]
            roles = ["rater"]
            if hasattr(builder, "is_qa_program") and builder.is_qa_program:
                roles.append("qa")
                if builder.slug.endswith("-qa"):
                    roles = ["qa"]

        program_object = programs[options["program"]]["object"]()
        if options.get("role"):
            if options["role"] not in programs[options["program"]]["roles"]:
                raise CommandError(
                    "Role %r was not found for program %s"
                    % (options["role"], ", ".join(list(options["program"].keys())))
                )
            roles = [options.get("role")]

        kwargs = {}
        if options["wipe"]:
            kwargs["wipe"] = True
        if options["warn_only"]:
            kwargs["warn_only"] = True

        kwargs["stdout"] = self.stdout
        kwargs["stderr"] = self.stderr
        kwargs["from_management_command"] = True

        for role in roles:
            log.info("Building role %s", role)
            program = program_object.build(role, **kwargs)
            if options["no_close_dates"]:
                EEPProgram.objects.filter(id=program.id).update(
                    program_close_date=None,
                    program_submit_date=None,
                    program_end_date=None,
                )
                self.stdout.write(f"No close dates for program {program} are set.\n")
