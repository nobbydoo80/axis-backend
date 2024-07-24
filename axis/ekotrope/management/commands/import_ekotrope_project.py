"""import_ekotrope_project.py - Axis"""

import logging

from django.core.management import BaseCommand, CommandError

from axis.company.models import Company
from axis.core.merge_objects import safe_delete
from axis.ekotrope.models import EkotropeAuthDetails, Project
from axis.ekotrope.utils import request_project_list, import_project_tree
from axis.floorplan.models import Floorplan
from simulation.models import Simulation

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "8/7/20 11:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class Command(BaseCommand):
    help = "Upload/Download a single home checklist"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--company", action="store", dest="company", help="Company to use for the import"
        )
        parser.add_argument("-p", "--project", action="store", dest="project", help="Project ID")
        parser.add_argument("--reimport", action="store_true", dest="reimport", help="Re-Import")
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Tells Django to NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        """Do the work"""
        project = Project.objects.filter(id=options["project"]).first()
        if project and not options.get("reimport"):
            raise CommandError("Project has already been imported %r" % project)

        if project and not options.get("company"):
            options["company"] = project.company_id

        try:
            company = Company.objects.get(id=options.get("company"))
        except Company.DoesNotExist:
            try:
                company = Company.objects.get(slug=options.get("company"))
            except Company.DoesNotExist:
                raise CommandError("Unable to find company with %r" % options["company"])

        auth_details = EkotropeAuthDetails.objects.filter(user__company=company).first()
        if auth_details is None:
            raise CommandError("Unable to find any auth details for company %r" % company)

        floorplan_id, simulation_id = None, None
        if project and options.get("reimport"):
            houseplan = project.houseplan_set.first()
            try:
                floorplan_id = houseplan.floorplan.id
                simulation_id = houseplan.floorplan.simulation_id
                Floorplan.objects.filter(id=houseplan.floorplan.id).update(
                    ekotrope_houseplan=None, simulation_id=None
                )
            except AttributeError:
                floorplan_id = None
            # print(f"Set {houseplan=} {floorplan_id=} {simulation_id=}")
            safe_delete(project, prompt=options["interactive"])

        projects = request_project_list(auth_details)
        for project_data in projects:
            if project_data["id"] == options["project"]:
                data = import_project_tree(auth_details, options["project"])
                message = f"Successfully {'re' if options['reimport'] else ''}imported"
                if floorplan_id:
                    project = Project.objects.filter(id=options["project"]).get()
                    houseplan = project.houseplan_set.first()
                    Floorplan.objects.filter(id=floorplan_id).update(
                        ekotrope_houseplan=houseplan, simulation_id=data.get("simulation")
                    )
                    message += f" and re-bound to floorplan {floorplan_id}"
                if simulation_id:
                    safe_delete(
                        Simulation.objects.get(id=simulation_id), prompt=options["interactive"]
                    )
                return f"{message} {options['project']!r}"
        raise CommandError("Project %r does not exist for company!" % options["project"])
