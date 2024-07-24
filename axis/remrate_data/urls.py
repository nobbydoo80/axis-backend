"""urls.py: Django remrate_data"""


import logging

from django.urls import path
from django.views.generic.base import RedirectView

from .views import RemRateDataDeleteView

__author__ = "Steven Klass"
__date__ = "3/8/13 2:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "remrate_data"

urlpatterns = [
    path("<int:pk>/delete/", RemRateDataDeleteView.as_view(), name="delete"),
    path(
        "",
        RedirectView.as_view(pattern_name="floorplan:input:remrate", permanent=True),
        name="list",
    ),
    path(
        "<int:pk>/",
        RedirectView.as_view(pattern_name="floorplan:input:remrate", permanent=True),
        name="view",
    ),
]
