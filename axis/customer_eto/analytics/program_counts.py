"""program_counts.py: Django Program Counts"""


import datetime
import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from axis.company.models import Company
from axis.core.utils import get_previous_day_start_end_times
from axis.home.models import EEPProgramHomeStatus, Home
from axis.relationship.models import Relationship

__author__ = "Steven K"
__date__ = "08/30/2019 10:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def get_certified_program_counts(rater_id, builder_id):
    """Returns the number of certified programs for a given rater with a builder"""
    data = {
        "rater_builder_completed_homes": None,
    }
    if rater_id is None or builder_id is None:
        return data

    rater = Company.objects.get(id=rater_id)
    builder = Company.objects.get(id=builder_id)

    start, end = get_previous_day_start_end_times()

    stat_filters = Q(
        certification_date__gt=start - datetime.timedelta(days=365),
        certification_date__lte=end,
        state="complete",
        eep_program__owner__slug="eto",
    ) | Q(
        certification_date__gt=start - datetime.timedelta(days=365),
        created_date__lte=end,
        home__bulk_uploaded=True,
        certification_date__isnull=False,
        state="complete",
        eep_program__owner__slug="eto",
    )

    rater_stats = EEPProgramHomeStatus.objects.filter_by_company(rater).filter(stat_filters)
    rater_stats = set(rater_stats.values_list("pk", flat=True))

    # Builder needs to go a bit differently.
    ct = ContentType.objects.get_for_model(Home)
    home_rels = Relationship.objects.filter(content_type=ct, company_id=builder.id).values_list(
        "object_id", flat=True
    )
    builder_stats = EEPProgramHomeStatus.objects.filter(home_id__in=home_rels).filter(stat_filters)
    builder_stats = set(builder_stats.values_list("pk", flat=True))
    data["rater_builder_completed_homes"] = len(list(rater_stats.intersection(builder_stats)))
    return data
