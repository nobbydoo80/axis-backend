"""urls.py: Django impesonate"""


import logging

from django.urls import path

from impersonate.views import impersonate, stop_impersonate

from .views import ImpersonateListView

__author__ = "Steven Klass"
__date__ = "3/5/12 12:56 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

urlpatterns = [
    path("<int:uid>/", impersonate, name="impersonate-start"),
    path("stop/", stop_impersonate, name="impersonate-stop"),
    path("list/", ImpersonateListView.as_view(), name="impersonate-list"),
]
