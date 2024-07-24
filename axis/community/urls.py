"""urls.py: Django community"""


import logging

from django.urls import path, include

from .views import (
    LegacyCommunityListRedirectView,
    CommunityListView,
    CommunityExamineView,
    SatelliteSubdivisionDatatable,
)

__author__ = "Steven Klass"
__date__ = "3/5/12 12:56 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "community"

urlpatterns = [
    path("", LegacyCommunityListRedirectView.as_view(), name="list"),
    path("add/", CommunityExamineView.as_view(create_new=True), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", CommunityExamineView.as_view(), name="view"),
                path(
                    "subdivision/",
                    SatelliteSubdivisionDatatable.as_view(),
                    name="view_subdivisions",
                ),
            ]
        ),
    ),
]
