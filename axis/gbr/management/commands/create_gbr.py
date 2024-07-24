"""create_gbr.py - axis"""

__author__ = "Steven K"
__date__ = "1/18/23 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import concurrent
import logging
from concurrent.futures import ThreadPoolExecutor

from django.core.management import BaseCommand, CommandError
from django.db.models import Q, QuerySet

from axis.customer_eto.tasks.eps import generate_eto_report
from axis.gbr.models import GreenBuildingRegistry, GbrStatus
from axis.gbr.tasks import get_or_create_green_building_registry_entry
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


def worker(home_status, status, idx, total):
    if status == "complete" and not home_status.home.customer_documents.filter(
        Q(document__contains="eps_report") | Q(document__contains="wacc_report")
    ):
        generate_eto_report(home_status_id=home_status.pk)
        home_status.refresh_from_db()

    get_or_create_green_building_registry_entry(home_id=home_status.home.pk)

    value = f"{idx} / {total} " if total else ""
    return f"{value}retrieved Green Building Registry {home_status.home.gbr}"


class Command(BaseCommand):
    help = "Generates GBR data for a home/homestatus"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--home", action="store", dest="home", type=int, help="Home ID")
        parser.add_argument(
            "--home-status",
            action="store",
            dest="home_status",
            type=int,
            help="Project ID",
        )
        parser.add_argument(
            "--program",
            action="store",
            dest="program",
            help="Run for an entire program",
        )
        parser.add_argument(
            "--status",
            action="store",
            dest="status",
            help="What HomeStatus.status",
            choices=("complete", "qa_pending"),
            default="complete",
        )
        parser.add_argument(
            "--max_count",
            action="store",
            dest="max_count",
            help="Maximum Count",
            type=int,
            required=False,
            default=1000,
        )
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            help="Push even for a completed home",
        )

    def get_queryset(
        self,
        home: int | None = None,
        home_status: int | None = None,
        program: int | str | None = None,
        status: str = "complete",
        max_count: int | None = None,
        force: bool = False,
    ) -> QuerySet:
        queryset = {
            "eep_program__is_qa_program": False,
            "fasttracksubmission__isnull": False,
            "state": status,
        }
        if home:
            queryset["home_id"] = home
        elif home_status:
            queryset["id"] = home_status
        elif program:
            if program.isdigit():
                queryset["eep_program_id"] = program
            else:
                queryset["eep_program__slug__in"] = program.split(",")

        completed = GreenBuildingRegistry.objects.filter(
            status=GbrStatus.ASSESSMENT_CREATED
        ).values_list("home", flat=True)

        stats = EEPProgramHomeStatus.objects.filter(**queryset).exclude(home_id__in=completed)
        if force and home and home in completed:
            self.stdout.write(f"Resetting GBR for {home} to {GbrStatus.NOT_STARTED}")
            GreenBuildingRegistry.objects.filter(home=home).update(status=GbrStatus.NOT_STARTED)
            completed = GreenBuildingRegistry.objects.filter(
                status=GbrStatus.ASSESSMENT_CREATED
            ).values_list("home", flat=True)
            stats = EEPProgramHomeStatus.objects.filter(**queryset).exclude(home_id__in=completed)

        if not stats.count():
            msg = f"{stats.count()} results found with options provided ({queryset})"
            if home_status:
                status = EEPProgramHomeStatus.objects.filter(id=home_status).last()
                if status and status.home_id in completed:
                    msg = f"Home status {home_status} already completed"
            if home and home in completed:
                msg = f"Home {home} already completed"
            raise CommandError(msg)

        capped = ""
        initial_stats = stats = stats.order_by("id")
        if max_count:
            stat_ids = list(initial_stats.values_list("pk", flat=True))[:max_count]
            stats = EEPProgramHomeStatus.objects.filter(pk__in=stat_ids)
            capped = f" capped at {stats.count()}"

        if stats.count() > 1:
            self.stdout.write(f"{initial_stats.count()} have have been identified{capped}\n")
        return stats

    def handle(
        self,
        *_args,
        home: int | None = None,
        home_status: int | None = None,
        program: int | str | None = None,
        status: str = "complete",
        max_count: int | None = None,
        force: bool = False,
        **_options,
    ):
        if not any([home, home_status, program]):
            raise CommandError("You must supply a home, home_status or program")

        home_stats = self.get_queryset(home, home_status, program, status, max_count, force)
        total = home_stats.count() if home_stats.count() > 1 else 0

        # We can use a with statement to ensure threads are cleaned up promptly
        errors = []
        with ThreadPoolExecutor(max_workers=min([home_stats.count(), 25])) as executor:
            # Start the load operations and mark each future with its home_status
            future_home_stats = {
                executor.submit(worker, home_status, status, idx, total): home_status
                for idx, home_status in enumerate(home_stats, start=1)
            }
            for future in concurrent.futures.as_completed(future_home_stats):
                home_status = future_home_stats[future]
                try:
                    data = future.result()
                except CommandError as exc:
                    self.stderr.write(
                        f"Issue with Document /home/{home_status.home.id} {home_status} {exc}"
                    )
                    errors.append(home_status.pk)
                except Exception as exc:
                    self.stderr.write(f"Issue with /home/{home_status.home.id} {home_status} {exc}")
                    errors.append(home_status.pk)
                else:
                    self.stdout.write(data)

        if home_stats.count() > 1:
            if errors:
                self.stderr.write(f"The following home ID's have issues: \n - {errors}\n")
            self.stdout.write(
                f"{home_stats.count()-len(errors)} GBR's have been generated with {len(errors)} errors\n"
            )
