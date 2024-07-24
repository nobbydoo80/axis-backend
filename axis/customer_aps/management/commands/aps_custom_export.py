"""home_status_export.py - Axis"""

import logging
import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError

from axis.customer_aps.exports.home_data_custom import APSHomeDataCustomExport
from axis.subdivision.models import Subdivision

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "6/11/20 11:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

User = get_user_model()


class Command(BaseCommand):
    help = "Dump APS Custom Subdivision report"
    requires_system_checks = []

    default_report_on = ["subdivision"]

    def add_arguments(self, parser):
        parser.add_argument("--search", action="store", dest="search", help="Search Bar")
        parser.add_argument(
            "--subdivision", action="store", dest="subdivision", help="subdivision", type=int
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

    def set_options(self, filename=None, search=None, max_num=None, subdivision=None, **_options):
        result = {}

        user = User.objects.filter(
            company__slug="aps", is_company_admin=True, is_active=True
        ).first()
        log.info("Using %s" % user)
        result["user_id"] = user.id

        if subdivision:
            try:
                subdivision = Subdivision.objects.get(id=subdivision)
            except Subdivision.DoesNotExist:
                raise CommandError("Subdivision with ID %s does not exist" % subdivision)
            log.info("Using %s" % subdivision)
            result["subdivision_id"] = subdivision.id

        if search:
            result["search_bar"] = search

        result["home_field"] = True
        result["customer_eto_field"] = True
        result["reuse_storage"] = False

        result["report_on"] = self.default_report_on

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

        obj = APSHomeDataCustomExport(**kwargs)
        obj.update_task = update

        output = "APS_Custom_Export.xlsx"
        obj.write(output=output)
        obj.print_sample(max_num=2)

        print("Output saved to: %s" % os.path.abspath(os.path.join(os.curdir, output)))
