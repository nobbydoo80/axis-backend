import logging

from django.urls import path

from .views import HighPerformanceHomeAddendumView

__author__ = "Michael Jeffrey"
__date__ = "8/9/17 2:51 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)

urlpatterns = [
    path(
        "report/<int:home_status>/", HighPerformanceHomeAddendumView.as_view(), name="eaaa_addendum"
    )
]
