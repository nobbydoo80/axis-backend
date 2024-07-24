"""urls.py: Django eep_program"""

import logging

from django.urls import path, include

from axis.eep_program.views import EEPProgramExamineView, EEPProgramListView

__author__ = "Steven Klass"
__date__ = "3/2/12 11:27 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "eep_program"

urlpatterns = [
    path("", EEPProgramListView.as_view(), name="list"),
    path("add/", EEPProgramExamineView.as_view(create_new=True), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", EEPProgramExamineView.as_view(), name="view"),
            ]
        ),
    ),
]
