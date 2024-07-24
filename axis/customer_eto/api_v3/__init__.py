"""__init__.py - Axis"""

__author__ = "Steven K"
__date__ = "8/10/21 08:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


from .filters import ProjectTrackerFilter

FASTTRACK_SUBMISSION_SEARCH_FIELDS = [
    "home_status__home__place__street_line1",
    "project_id",
    "solar_project_id",
    "submit_user__username",
    "submit_user__first_name",
    "submit_user__last_name",
]
