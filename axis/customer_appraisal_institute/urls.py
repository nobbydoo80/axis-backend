"""urls.py: Django customer_appraisal_institute"""


import logging

from django.urls import path

from .views import GreenEnergyEfficientAddendumView, GreenEnergyEfficientAddendumHomesListView

__author__ = "Steven Klass"
__date__ = "6/2/13 9:04 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "appraisal_institute"

urlpatterns = [
    path(
        "report/green/homes/",
        GreenEnergyEfficientAddendumHomesListView.as_view(),
        name="green_homes",
    ),
    path(
        "report/green/<int:home_status>/",
        GreenEnergyEfficientAddendumView.as_view(),
        name="green_addendum",
    ),
]
