import io
import logging
import os
from functools import cached_property

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.core.management import BaseCommand, CommandError
from django.db.models import Q, QuerySet

from axis.customer_eto.api_v3.serializers.reports import (
    WashingtonCodeCreditReportSerializer,
)
from axis.customer_eto.api_v3.viewsets.eps_report import get_eps_report
from axis.customer_eto.eep_programs import WashingtonCodeCreditProgram
from axis.customer_eto.reports.washington_code_credit import WashingtonCodeCreditReport
from axis.filehandling.utils import store_document_to_model_instance
from axis.home.models import Home, EEPProgramHomeStatus

__author__ = "Steven Klass"
__date__ = "01/14/2019 13:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from simulation.enumerations import SourceType

log = logging.getLogger(__name__)
User = get_user_model()
DEFAULT_FILENAME = "~/Downloads/Report.pdf"


class Command(BaseCommand):
    help = "Generates EPS Report for a give home/homestatus"
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
            "--simulation_source",
            action="store",
            dest="simulation_source",
            choices=["rem", "ekotrope"],
            required=False,
            help="Only run for a certain simulator",
        )

        parser.add_argument("--user", action="store", dest="user", help="User ID or username")
        parser.add_argument(
            "--filename",
            action="store",
            dest="filename",
            help="Output File",
            default=DEFAULT_FILENAME,
        )
        parser.add_argument(
            "--store", action="store_true", dest="store", help="Bind this to the home."
        )
        parser.add_argument(
            "--max_count",
            action="store",
            dest="max_count",
            help="Maximum Count",
            type=int,
            required=False,
            default=None,
        )

    def get_queryset(
        self,
        home: int | None = None,
        home_status: int | None = None,
        program: int | str | None = None,
        simulation_source: str | None = None,
        store: bool = False,
        max_count: int | None = None,
    ) -> QuerySet:
        queryset = {
            "eep_program__is_qa_program": False,
            "fasttracksubmission__isnull": False,
        }
        if home:
            queryset["home_id"] = home
        elif home_status:
            queryset["id"] = home_status
        elif program:
            if program.isdigit():
                queryset["eep_program_id"] = program
            else:
                queryset["eep_program__slug"] = program
            queryset["state"] = "complete"

        if simulation_source:
            if simulation_source == "ekotrope":
                queryset["floorplan__simulation__source_type"] = SourceType.EKOTROPE
            if simulation_source == "rem":
                queryset["floorplan__simulation__source_type"] = SourceType.REMRATE_SQL

        stats = EEPProgramHomeStatus.objects.filter(**queryset)
        if not stats.count():
            raise CommandError(f"{stats.count()} results found with options provided ({queryset})")

        if store and stats.count() > 1 and not simulation_source:
            # This is store only  # Exclude those completed that are certified
            stats = stats.exclude(
                Q(home__customer_documents__document__contains="eps_report")
                | Q(home__customer_documents__document__contains="wacc_report"),
            )

            self.stdout.write(f"{stats.count()} have have been identified\n")

        capped = ""
        initial_stats = stats = stats.order_by("id")
        if max_count:
            stat_ids = list(initial_stats.values_list("pk", flat=True))[:max_count]
            stats = EEPProgramHomeStatus.objects.filter(pk__in=stat_ids)
            capped = f" capped at {stats.count()}"

        if stats.count() > 1:
            self.stdout.write(f"{initial_stats.count()} have have been identified{capped}\n")
        return stats

    def get_user(self, user=int | str | None) -> User | None:
        if user is None:
            return
        try:
            return User.objects.get(id=user)
        except (ObjectDoesNotExist, ValueError):
            try:
                return User.objects.get(username=user)
            except ObjectDoesNotExist:
                raise CommandError(f"User provided {user} does not exist")

    def get_wacc_report(
        self, home_status: EEPProgramHomeStatus, user: User | None = None
    ) -> io.BytesIO:
        serializer = WashingtonCodeCreditReportSerializer(
            instance=home_status.fasttracksubmission,
        )
        stream = io.BytesIO()
        report = WashingtonCodeCreditReport()
        report.build(user=user, response=stream, data=serializer.data)
        return stream

    def get_eps_report(
        self, home_status: EEPProgramHomeStatus, user: User | None = None
    ) -> io.BytesIO:
        stream, _l = get_eps_report(
            pk=home_status.id,
            user=user,
            return_virtual_workbook=True,
        )
        return stream

    def get_label_stream(
        self, home_status: EEPProgramHomeStatus, user: User | None = None
    ) -> (str, io.BytesIO):
        _label = home_status.home.street_line1.replace(" ", "_").replace(".", "")
        if home_status.eep_program.slug in [WashingtonCodeCreditProgram.slug]:
            label = f"WACC_Report_{_label}.pdf"
            stream = self.get_wacc_report(home_status, user)
        else:
            label = f"EPS_Report_{_label}.pdf"
            stream = self.get_eps_report(home_status, user)
        return label, stream

    @cached_property
    def home_content_type(self) -> ContentType:
        return ContentType.objects.get_for_model(Home)

    def handle(
        self,
        *_args,
        home: int = None,
        home_status: int = None,
        program: int | str = None,
        simulation_source: str | None = None,
        user: int | str = None,
        filename: str = None,
        store: bool = False,
        max_count: int | None = None,
        **_options,
    ):
        if not any([home, home_status, program, simulation_source]):
            raise CommandError("You must supply a home, home_status, program, or simulation_source")

        if filename == DEFAULT_FILENAME and store:
            filename = None

        if filename and not os.path.exists(os.path.dirname(os.path.expanduser(filename))):
            raise CommandError(
                "Output Path does not exist %s" % os.path.dirname(os.path.expanduser(filename))
            )

        user = self.get_user(user)

        home_stats = self.get_queryset(
            home, home_status, program, simulation_source, store, max_count
        )
        total = home_stats.count() if home_stats.count() > 1 else 0

        if home_stats.count() > 1:
            if filename and filename != DEFAULT_FILENAME:
                raise CommandError(
                    f"{home_stats.count()} results found.  Filename {filename} option is not supported."
                )

        errors, doc = [], None
        for idx, home_status in enumerate(home_stats, start=1):
            try:
                label, stream = self.get_label_stream(home_status, user)
            except Exception as exc:
                self.stderr.write(f"Issue with /home/{home_status.home.id} {home_status} {exc}")
                if not total:
                    raise
                errors.append(home_status.home.id)
                continue

            if filename:
                with open(os.path.expanduser(filename), "wb") as file_obj:
                    file_obj.write(stream.getbuffer())

            if store:
                doc = store_document_to_model_instance(
                    home_status.home,
                    label,
                    stream,
                    description=f"{'Final' if home_status.certification_date else 'Preliminary'} Report",
                    is_public=True if home_status.certification_date else False,
                    login_required=False if home_status.certification_date else True,
                    company=home_status.company,
                )

            value = f"{idx} / {total} " if total else ""
            if total:
                self.stdout.write(f"{value}Stored {home_status} report {label}")

        msg = f"Stored document as {doc!r} {doc.id if doc else '-'}"
        if filename:
            msg = f"Report has been saved to {filename}"
            if store:
                msg += f" and stored as document {doc!r} {doc.id}"
        if home_stats.count() > 1:
            msg = (
                f"{home_stats.count()-len(errors)} have been generated with {len(errors)} errors\n"
            )
            if errors:
                self.stderr.write(f"The following home ID's have issues: \n - {errors}\n")
        self.stdout.write(f"{msg}\n")
