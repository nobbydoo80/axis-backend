"""urls.py: Django remrate"""


import logging

from django.urls import path, include

from axis.remrate.views import (
    RemRateUserListView,
    RemRateUserCreateView,
    RemRateUserUpdateView,
    RemRateUserDeleteView,
)

__author__ = "Steven Klass"
__date__ = "1/17/12 9:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "remrate"

urlpatterns = [
    path(
        "remrate/",
        include(
            (
                [
                    path("", RemRateUserListView.as_view(), name="list"),
                    path("add/", RemRateUserCreateView.as_view(), name="add"),
                    path(
                        "<int:pk>/",
                        include(
                            [
                                path("edit/", RemRateUserUpdateView.as_view(), name="update"),
                                path("delete/", RemRateUserDeleteView.as_view(), name="delete"),
                            ]
                        ),
                    ),
                ],
                "user",
            )
        ),
    ),
]
