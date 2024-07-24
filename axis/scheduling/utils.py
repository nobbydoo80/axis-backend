"""utils.py: Django scheduling"""


import os
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core import management
from django.utils.timezone import now

from django.contrib.auth import get_user_model
from axis.company.models import Company
from axis.scheduling.models import ConstructionStage

__author__ = "Steven Klass"
__date__ = "7/22/12 9:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()

CONSTRUCTION_STAGES = [
    {
        "company": "D.R. Wastchak",
        "name": "Framing",
        "description": "Framing is complete",
        "order": 10,
    },
    {
        "company": "D.R. Wastchak",
        "name": "Post-Drywall",
        "description": "Post-Drywall",
        "order": 30,
    },
    {
        "company": "D.R. Wastchak",
        "name": "A/C Startup",
        "description": "Air Conditioning is started",
        "order": 70,
    },
    {
        "company": "D.R. Wastchak",
        "name": "Completion",
        "description": "Scheduled completion",
        "order": 90,
    },
]


def add_construction_stages(stages=CONSTRUCTION_STAGES, password="password", dump=False):  # nosec
    """This will add all of the eep_programs"""

    for stage in stages:
        log.info("Adding Construction Stages %s", stage["name"])
    #        admin = AxisTestingCore().get_admin_for_company(stage.pop('company'))
    #        ScheduleTests.create_construction_stage(username=admin, password=password, **stage)

    if dump:
        fixture = os.path.abspath("%s/fixtures/schedule.json" % os.path.dirname(__file__))
        keys = ["scheduling"]
        management.call_command(
            "dumpdata",
            *keys,
            format="json",
            indent=4,
            use_natural_keys=True,
            stdout=open(fixture, "w"),
        )


def add_integral_construction_stages():
    CONSTRUCTION_STAGES = [
        {"company": "integral-building", "name": "Site Work & Foundation", "order": 10},
        {"company": "integral-building", "name": "Rough-in Framing", "order": 30},
        {"company": "integral-building", "name": "MEP Rough-in Complete", "order": 50},
        {"company": "integral-building", "name": "Finishes Installed", "order": 70},
    ]
    for stage in CONSTRUCTION_STAGES:
        stage["owner"] = Company.objects.get(slug=stage.pop("company"))
        ConstructionStage.objects.get_or_create(**stage)


def update_live_construction_stages():
    """This will run through every home on the system and set complete on homes which have all of
    there programs certified"""

    from axis.home.models import Home, EEPProgramHomeStatus
    from axis.scheduling.models import ConstructionStage, ConstructionStatus

    homes = Home.objects.all()

    havent_started, started, completed = 0, 0, 0
    for home in Home.objects.all():
        home_stats = EEPProgramHomeStatus.objects.filter(home=home)
        if not home_stats.count():
            continue

        companies = [stat.company for stat in home_stats]
        if len(companies) > 1:
            print("Multiple Companies for Home {} ({})".format(home, home.id))
            continue
        company = companies[0]
        users = User.objects.filter(company=company, is_admin=True)
        if not users.count():
            continue
        user = users[0]

        current_stage = home.get_current_stage(user)
        if current_stage.stage.name != "Not Started":
            continue

        not_started, in_progress, complete = False, False, False
        start_date = now()
        home_stats = EEPProgramHomeStatus.objects.filter(home=home)
        for stat in home_stats:
            if stat.pct_complete < 0.1:
                not_started = True
                in_progess = False
                complete = False
                break
            if stat.pct_complete < 99.9:
                not_started = False
                in_progress = True
                complete = False
                break
            else:
                not_started = False
                in_progress = False
                if stat.certification_date:
                    complete = True
                    start_date = stat.certification_date
                else:
                    in_progress = True
                    complete = False
                    break

        if len(companies) > 1:
            print("Multiple Companies for Home {} ({})".format(home, home.id))
            continue
        company = companies[0]

        if not_started:
            stage = ConstructionStage.objects.get(name="Not Started", is_public=True, order=0)
            try:
                ConstructionStatus.objects.get(stage=stage, home=home, company=company)
                create = False
            except ObjectDoesNotExist:
                status, create = ConstructionStatus.objects.get_or_create(
                    stage=stage, home=home, company=company, start_date=start_date
                )
            havent_started += 1
            print(
                "{} Home Stage {} for home {} ".format(
                    "Create" if create else "Updated", "Not Started", home
                )
            )
        elif in_progress:
            stage = ConstructionStage.objects.get(name="Started", is_public=True, order=1)
            try:
                ConstructionStatus.objects.get(stage=stage, home=home, company=company)
                create = False
            except ObjectDoesNotExist:
                status, create = ConstructionStatus.objects.get_or_create(
                    stage=stage, home=home, company=company, start_date=start_date
                )
            started += 1
            print(
                "{} Home Stage {} for home {} ".format(
                    "Create" if create else "Updated", "Started", home
                )
            )
        elif complete:
            stage = ConstructionStage.objects.get(name="Completed", is_public=True, order=100)
            try:
                ConstructionStatus.objects.get(stage=stage, home=home, company=company)
                create = False
            except ObjectDoesNotExist:
                status, create = ConstructionStatus.objects.get_or_create(
                    stage=stage, home=home, company=company, start_date=start_date
                )
            completed += 1
            print(
                "{} Home Stage {} for home {} ".format(
                    "Create" if create else "Updated", "Completed", home
                )
            )

    print(
        "Updated {} to Started and {} to Complete ({} Non-Starts)".format(
            started, completed, havent_started
        )
    )
