"""urls.py: Django reso"""


import logging

from django.urls import path

from .views import EDMXView

__author__ = "Steven Klass"
__date__ = "07/23/17 09:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "reso"

urlpatterns = [
    path("edmx/", EDMXView.as_view(), name="edmx"),
]
