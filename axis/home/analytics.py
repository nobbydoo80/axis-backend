"""analytics.py: Django analytics"""


import logging
import datetime

from django.db.models import Q

from axis.company.models import Company
from django.contrib.auth import get_user_model
from axis.core.utils import get_previous_day_start_end_times
from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven Klass"
__date__ = "4/10/19 8:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

User = get_user_model()
log = logging.getLogger(__name__)


def get_certified_program_counts(rater_id, builder_id):
    data = {
        "builder_completed_homes_rolling_year": None,
        "rater_completed_homes_rolling_year": None,
    }

    rater = Company.objects.get(id=rater_id)
    builder = Company.objects.get(id=builder_id)

    start, end = get_previous_day_start_end_times()

    stat_filters = Q(
        certification_date__gt=start - datetime.timedelta(days=365),
        certification_date__lte=end,
        state="complete",
    ) | Q(
        certification_date__gt=start - datetime.timedelta(days=365),
        created_date__lte=end,
        home__bulk_uploaded=True,
        certification_date__isnull=False,
        state="complete",
    )

    rater_stats = EEPProgramHomeStatus.objects.filter_by_company(rater).filter(stat_filters)
    builder_stats = EEPProgramHomeStatus.objects.filter_by_company(builder).filter(stat_filters)

    data["rater_completed_homes_rolling_year"] = rater_stats.count()
    data["builder_completed_homes_rolling_year"] = builder_stats.count()
    return data


def get_home_misc_details(rater_of_record_id, climate_zone_id):
    from axis.geographic.models import ClimateZone

    data = {
        "rater_of_record": None,
        "climate_zone": None,
    }
    if rater_of_record_id is not None:
        data["rater_of_record"] = "%s" % User.objects.get(id=rater_of_record_id)
    if climate_zone_id is not None:
        data["climate_zone"] = "%s" % ClimateZone.objects.get(id=climate_zone_id)

    return data
