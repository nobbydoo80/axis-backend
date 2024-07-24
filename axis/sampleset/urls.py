""" Sampling urls, round 2, ding ding. """


import logging

from django.urls import path

from . import views

__author__ = "Autumn Valenta"
__date__ = "07-30-14 12:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "sampleset"

urlpatterns = [
    path("", views.SampleSetListView.as_view(), name="list"),
    path("subdivision/<int:subdivision_id>/", views.SampleSetListView.as_view(), name="list"),
    path("control_center/", views.SampleSetUIView.as_view(), name="control_center"),
    path("<uuid>/", views.SampleSetDetailView.as_view(), name="view"),
    path("<uuid>/homes/", views.SampleSetAjaxHomeProvider.as_view(), name="homes"),
    path("<uuid>/answers/", views.SampleSetAjaxAnswers.as_view(), name="answers"),
]
