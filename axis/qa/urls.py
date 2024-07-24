"""urls.py: Django qa"""


import logging
from django.urls import path, include
from .views import QAListView, QACreateView, QAUpdateView, QADeleteView, QADetailView, SetStateView

__author__ = "Steven Klass"
__date__ = "12/20/13 6:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "qa"

urlpatterns = [
    path("", QAListView.as_view(), name="list"),
    path("add/", QACreateView.as_view(), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", QADetailView.as_view(), name="view"),
                path("update/", QAUpdateView.as_view(), name="update"),
                path("delete/", QADeleteView.as_view(), name="delete"),
                path("update_state/", SetStateView.as_view(), name="set_state"),
            ]
        ),
    ),
]
