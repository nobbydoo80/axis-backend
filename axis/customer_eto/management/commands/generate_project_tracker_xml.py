"""generate_project_tracker_xml.py: Django """

__author__ = "Steven Klass"
__date__ = "01/15/2019 12:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import json
import logging
import os
from urllib.parse import urlparse

from django.apps import apps
import xmltodict
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from axis.core.models import User
from infrastructure.utils import get_user_input
from axis.home.models import EEPProgramHomeStatus

from ...api_v3.serializers.project_tracker import ProjectTrackerXMLSerializer
from ...api_v3.viewsets import ProjectTrackerXMLViewSet
from ...models import FastTrackSubmission
from ...tasks import submit_fasttrack_xml
from ...tasks.fasttrack import fasttrack_headers

log = logging.getLogger(__name__)
customer_eto_app = apps.get_app_config("customer_eto")


class Command(BaseCommand):
    help = "Generates PT XML home/homestatus"
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
        parser.add_argument("--user", action="store", dest="user", help="User ID or username")
        parser.add_argument(
            "--filename",
            action="store",
            dest="filename",
            help="Output File",
            default="~/Downloads/PT.xml",
        )
        parser.add_argument("--stream", action="store_true", dest="stream", help="Stream it")
        parser.add_argument(
            "--project_type",
            action="store",
            dest="project_type",
            help="Project Type",
            default="ENH",
        )
        parser.add_argument("--send", action="store_true", dest="send_it", help="Send it to PT")
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Tells Django to NOT prompt the user for input of any kind.",
        )

    def handle(
        self,
        *_args,
        home: int = None,
        home_status: int = None,
        filename: str = None,
        stream: bool = False,
        project_type: str = "ENH",
        send_it: bool = False,
        interactive: bool = True,
        user: str | None = None,
        **_options,
    ):
        if not any([home, home_status]):
            raise CommandError("You must supply a home, home_status")

        if filename and not os.path.exists(os.path.dirname(os.path.expanduser(filename))):
            raise CommandError(
                "Output Path does not exist %s" % os.path.dirname(os.path.expanduser(filename))
            )

        if user:
            try:
                user = User.objects.get(id=user)
            except (ObjectDoesNotExist, ValueError):
                try:
                    user = User.objects.get(username=user)
                except ObjectDoesNotExist:
                    raise CommandError(f"User provided {user} does not exist")

        if filename:
            filename = os.path.abspath(os.path.expanduser(filename))
            print(filename)
            if not os.path.exists(os.path.dirname(filename)):
                raise CommandError(f"{os.path.dirname(filename)} does not exist")

        queryset = {
            "eep_program__is_qa_program": False,
            "fasttracksubmission__isnull": False,
        }
        if home:
            queryset["home_id"] = home
        elif home_status:
            queryset["id"] = home_status

        stats = EEPProgramHomeStatus.objects.filter(**queryset)
        if not stats.count():
            raise CommandError(f"{stats.count()} results found with options provided ({queryset})")
        if stats.count() > 1:
            raise CommandError(f"{stats.count()} results found.  ({queryset})")

        for home_status in stats:
            submission = FastTrackSubmission.objects.get(home_status=home_status)

            vs = ProjectTrackerXMLViewSet()
            available = submission.get_project_types()

            if project_type not in available:
                raise CommandError(
                    f"Project type specified ({project_type} not available "
                    f"({','.join(available)}"
                )

            context = vs.get_context_data(submission)
            context["project_type"] = project_type

            if send_it:
                msg = f"Confirm sending Axis ID {home_status.home.id} to {settings.FASTTRACK_API_ENDPOINT}"

                if interactive:
                    confirmed = get_user_input(msg, choices=("Yes", "No"))
                else:
                    confirmed = "Yes"

                if confirmed == "Yes":
                    submit_fasttrack_xml(home_status.pk, project_type=project_type)
                return

            serializer = ProjectTrackerXMLSerializer(instance=submission, context=context)
            xml_data = xmltodict.unparse(
                serializer.data, pretty=True, full_document=True, short_empty_elements=True
            ).encode("utf8")

            if filename:
                with open(filename, "wb") as fh:
                    fh.write(xml_data)
                self.stdout.write(f"Report has been saved to {filename}\n")

                parsed = urlparse(settings.FASTTRACK_API_ENDPOINT)
                postman = {
                    "info": {
                        "name": f"Import of {project_type} Axis ID {home_status.home.id}",
                        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                    },
                    "item": [
                        {
                            "name": f"ETO {project_type} Import",
                            "request": {
                                "method": "POST",
                                "header": [
                                    {"key": k, "value": v, "type": "text"}
                                    for k, v in fasttrack_headers.items()
                                ],
                                "body": {
                                    "mode": "raw",
                                    "raw": xmltodict.unparse(
                                        serializer.data,
                                        full_document=True,
                                        short_empty_elements=True,
                                    ),
                                    "options": {"raw": {"language": "xml"}},
                                },
                                "url": {
                                    "raw": settings.FASTTRACK_API_ENDPOINT,
                                    "protocol": parsed.scheme,
                                    "host": parsed.netloc.split("."),
                                    "path": parsed.path[1:].split("/"),
                                },
                            },
                            "response": [],
                        }
                    ],
                }
                filename = os.path.join(
                    os.path.dirname(filename), "AXIS_Import.postman_collection.json"
                )
                with open(filename, "w") as fh:
                    fh.write(f"{json.dumps(postman, indent=4)}\n")
                self.stdout.write(f"Postman data has been saved to {filename}\n")

            if stream:
                print(xml_data)
