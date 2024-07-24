"""Urls."""

from django.urls import include, path

from . import views

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

urlpatterns = [
    path("enroll/", views.ActiveEnrollmentRedirectView.as_view(), name="enroll"),
    path(
        "builder-agreements/",
        include(
            (
                [
                    path("", views.BuilderAgreementFilterView.as_view(), name="list"),
                    path(
                        "enroll/",
                        views.ActiveEnrollmentRedirectView.as_view(),
                        name="add",
                    ),
                ],
                "agreements",
            )
        ),
    ),
]
