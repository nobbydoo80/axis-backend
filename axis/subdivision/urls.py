"""urls.py: Django subdivision"""


import logging

from django.urls import path, include

from .views import SubdivisionListView, SubdivisionExamineView

__author__ = "Steven Klass"
__date__ = "3/5/12 12:56 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "subdivision"

urlpatterns = [
    path("", SubdivisionListView.as_view(), name="list"),
    path("add/", SubdivisionExamineView.as_view(create_new=True), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", SubdivisionExamineView.as_view(), name="view"),
            ]
        ),
    ),
]
