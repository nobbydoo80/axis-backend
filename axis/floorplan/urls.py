__author__ = "Steven Klass"
__date__ = "3/3/12 5:43 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Artem Hruzd"]
import logging

from django.urls import path, re_path, include

from .views import (
    FloorplanInputListView,
    FloorplanInputDetailView,
)


log = logging.getLogger(__name__)

app_name = "floorplan"

urlpatterns = [
    path(
        "input/",
        include(
            (
                [
                    path(
                        "ekotrope/",
                        include(
                            [
                                path(
                                    "",
                                    FloorplanInputListView.as_view(mode="ekotrope"),
                                    name="ekotrope",
                                ),
                                re_path(
                                    r"(?P<pk>\w{8})/$",
                                    FloorplanInputDetailView.as_view(mode="ekotrope"),
                                    name="ekotrope",
                                ),
                            ]
                        ),
                    ),
                    path(
                        "remrate/",
                        include(
                            [
                                path(
                                    "",
                                    FloorplanInputListView.as_view(mode="remrate"),
                                    name="remrate",
                                ),
                                path(
                                    "<int:pk>/",
                                    FloorplanInputDetailView.as_view(mode="remrate"),
                                    name="remrate",
                                ),
                            ]
                        ),
                    ),
                ],
                "input",
            )
        ),
    ),
]
