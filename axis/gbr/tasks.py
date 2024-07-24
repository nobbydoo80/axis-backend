"""tasks.py - axis"""

__author__ = "Steven K"
__date__ = "1/9/23 11:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from io import StringIO

from celery import shared_task
from django.apps import apps
from django.core import management

from infrastructure.utils import elapsed_time
from .gbr import GreenBuildingRegistryAPIConnect
from .models import GbrStatus
from ..home.models import Home

log = logging.getLogger(__name__)

gbp_app = apps.get_app_config("gbr")


@shared_task
def get_or_create_green_building_registry_entry(*_args, home_id: int, assessment: str = "eps"):
    home = Home.objects.get(id=home_id)
    registry = GreenBuildingRegistryAPIConnect(use_sandbox=False)

    try:
        green_building_registry = home.gbr
        if green_building_registry.status == GbrStatus.ASSESSMENT_CREATED:
            return
    except AttributeError:
        # create a record
        green_building_registry = registry.create_property(home)

    if home.homestatuses.filter(
        certification_date__isnull=False, eep_program__owner__slug="eto", state="complete"
    ):
        registry.create_assessment(green_building_registry, assessment=assessment)


@shared_task(time_limit=60 * 60)
def collect_missing_eto_gbr_registry_entries(*_args, **_kw):
    start = datetime.datetime.now()
    args = [
        "create_gbr",
        "--program",
        "eto,eto-2014,eto-2015,eto-2016,eto-2017,eto-2018,eto-2019,eto-2020,eto-2021",
        "--max_count",
        "500",
    ]

    stdout, stderr = StringIO(), StringIO()
    management.call_command(*args, stdout=stdout, stderr=stderr)

    status = "success"
    result = stdout.getvalue()
    error = stderr.getvalue()
    if error:
        status = "fail"

    return {
        "result": result,
        "error": error,
        "status": status,
        "elapsed_time": f"{elapsed_time((datetime.datetime.now() - start).total_seconds()).long_fmt}",
    }
